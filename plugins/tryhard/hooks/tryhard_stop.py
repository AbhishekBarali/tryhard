#!/usr/bin/env python3
"""Tryhard Stop hook for Codex.

Codex runs this script when the agent is about to end its turn. It reads the
Stop event as JSON on stdin and either prints nothing (the turn ends normally)
or prints {"decision": "block", "reason": "..."}, which makes Codex continue
the turn with the reason as the next prompt.

Three cheap, conservative checks look at the final message:

  handback     The message ends by offering work or asking permission
               ("Want me to...?", "Shall I...?", "I can also ... if you'd like").
  own-work     The message ends with a question that names files, paths or IDs
               that never appear in the user's own messages, so they come from
               the agent's own work and it can look them up itself.
  readability  A long final message whose opening is packed with code names,
               whose prose stacks semicolons, or whose opening runs very long.

Limits:
  * Never blocks when stop_hook_active is true, so it pushes at most once per
    turn.
  * Each check goes quiet for the rest of the session after it has fired on
    3 turns in a row.
  * Offers and questions about deleting, overwriting, publishing or paying
    are left alone, because those really are the user's call.
  * Any error or unexpected input means no output and exit status 0 (the
    turn ends as usual). Long messages and transcripts are read only up to
    fixed limits, so a run stays well inside Codex's hook timeout.

Settings (environment variables, read when Codex starts the hook):
  TRYHARD_HOOK=off               turn the whole hook off
  TRYHARD_CHECKS=handback,...    run only the listed checks
                                 (handback, own-work, readability,
                                 or "all" / "none")

Only the Python 3 standard library is used.
"""

import json
import os
import re
import stat
import sys
import tempfile
import time

CHECKS = ("handback", "own-work", "readability")
STREAK_LIMIT = 3
MAX_STDIN_BYTES = 8 * 1024 * 1024
MAX_TRANSCRIPT_BYTES = 256 * 1024 * 1024
TRANSCRIPT_SECONDS = 4.0  # give up on the transcript after this long
MAX_STATE_FILES = 200
STALE_TEMP_SECONDS = 3600
# The checks look at the start (readability) or the end (the other two) of a
# message, so only that much of a very long message is examined. Runs of more
# than LONG_TOKEN_CHARS non-space characters (base64, minified code) are
# shortened first; real names are shorter, and long runs slow the regexes.
MAX_ANALYSED_CHARS = 20000
LONG_TOKEN_CHARS = 200

OFF_VALUES = {"0", "off", "false", "no", "disable", "disabled"}
CHECK_ALIASES = {
    "handback": "handback",
    "hand-back": "handback",
    "handoff": "handback",
    "hand-off": "handback",
    "offer": "handback",
    "own-work": "own-work",
    "ownwork": "own-work",
    "own-files": "own-work",
    "own": "own-work",
    "readability": "readability",
    "readable": "readability",
    "report": "readability",
}

FOOTER = (
    "(Automatic check from the Tryhard plugin. The last message you send is the one the user reads, "
    "so make it complete on its own. Don't mention this note or apologise.)"
)


# ---------------------------------------------------------------------------
# Settings


def hook_disabled(env):
    value = (env.get("TRYHARD_HOOK") or "").strip().lower()
    return value in OFF_VALUES


def enabled_checks(env):
    """Return the checks to run, in their fixed order."""
    raw = env.get("TRYHARD_CHECKS")
    if raw is None or not raw.strip():
        return list(CHECKS)
    wanted = set()
    for part in re.split(r"[\s,;]+", raw.strip().lower()):
        if not part:
            continue
        if part == "all":
            return list(CHECKS)
        if part == "none":
            return []
        name = CHECK_ALIASES.get(part.replace("_", "-"))
        if name:
            wanted.add(name)
    return [name for name in CHECKS if name in wanted]


# ---------------------------------------------------------------------------
# Text helpers

FENCE_RE = re.compile(r"^[ \t]*(```|~~~).*?^[ \t]*\1[^\n]*$", re.M | re.S)
CODE_SPAN_RE = re.compile(r"`([^`\n]{1,300})`")
LIST_ITEM_RE = re.compile(r"^\s*(?:[-*+]|\d+[.)])\s+")
SENTENCE_SPLIT_RE = re.compile(r"(?<=[.!?])[\"')\]*_]*\s+")
# Characters that can follow the last word of a sentence (rstrip, not a regex,
# so a long run of them cannot slow anything down).
TRAILING_DECOR = " \t\r\n\f\v*_\"'`)]"
LONG_TOKEN_RE = re.compile(r"(?<![^\s`])[^\s`]{%d,}" % (LONG_TOKEN_CHARS + 1))


def _shorten_token(match):
    token = match.group(0)
    return "\u2026" + (token[-1] if token[-1] in ".,;:!?)" else "")


def strip_code_blocks(text):
    text = FENCE_RE.sub("\n", text)
    # An unclosed fence hides the rest of the message from the prose checks.
    match = re.search(r"^[ \t]*(```|~~~)", text, re.M)
    if match:
        text = text[: match.start()]
    return text


def prose_of(message, end=False):
    """The message without code blocks, cut to the part the checks look at.

    end=True keeps the last MAX_ANALYSED_CHARS characters (for checks on how
    the message ends); otherwise the first ones are kept.
    """
    text = LONG_TOKEN_RE.sub(_shorten_token, message.replace("\r\n", "\n"))
    text = strip_code_blocks(text)
    if len(text) <= MAX_ANALYSED_CHARS:
        return text
    if end:
        text = text[-MAX_ANALYSED_CHARS:]
        return text[text.find("\n") + 1 :]
    text = text[:MAX_ANALYSED_CHARS]
    return text[: text.rfind("\n") + 1] or text


def paragraphs(text):
    blocks = re.split(r"\n[ \t]*\n", text.replace("\r\n", "\n"))
    return [block.strip() for block in blocks if block.strip()]


def is_list_block(block):
    lines = [line for line in block.splitlines() if line.strip()]
    return bool(lines) and all(LIST_ITEM_RE.match(line) or line.startswith("  ") for line in lines)


HEADING_LINE_RE = re.compile(r"#{1,6}(?:\s.*)?|\*\*[^*]{1,80}\*\*:?|__[^_]{1,80}__:?")
LABEL_LINE_RE = re.compile(r"[A-Z][\w /&-]{0,40}:")


def is_heading_line(line, labels=False):
    line = line.strip()
    return bool(HEADING_LINE_RE.fullmatch(line) or (labels and LABEL_LINE_RE.fullmatch(line)))


def is_heading_block(block):
    lines = [line for line in block.splitlines() if line.strip()]
    return all(is_heading_line(line) for line in lines)


def without_heading(block):
    """The block minus heading lines at its top ("**Summary**", "Testing:")."""
    lines = [line for line in block.splitlines() if line.strip()]
    while len(lines) > 1 and is_heading_line(lines[0], labels=True):
        lines = lines[1:]
    return "\n".join(lines)


def ends_with_question(block):
    return block.rstrip(TRAILING_DECOR).endswith("?")


def sentences(block):
    flat = " ".join(line.strip() for line in block.splitlines() if line.strip())
    flat = LIST_ITEM_RE.sub("", flat)
    return [part.strip() for part in SENTENCE_SPLIT_RE.split(flat) if part.strip()]


def plain(text):
    """Lowercase text with markdown emphasis removed, for phrase matching."""
    text = re.sub(r"[*_]{1,3}", "", text)
    return text.replace("\u2019", "'").lower()


def shorten(text, limit=160):
    text = " ".join(text.split())
    if len(text) <= limit:
        return text
    return text[: limit - 1].rstrip() + "\u2026"


def join_names(names):
    quoted = ["`%s`" % name for name in names]
    if len(quoted) == 1:
        return quoted[0]
    return ", ".join(quoted[:-1]) + " and " + quoted[-1]


# ---------------------------------------------------------------------------
# Check 1: hand-back offers

LEAD_IN = r"^(?:(?:so|now|also|next|then|or|and|ok|okay|alternatively|otherwise),?\s+)?"
OFFER_START_PATTERNS = [
    re.compile(LEAD_IN + r"(?:shall|should) (?:i|we)\b.*\?$"),
    re.compile(LEAD_IN + r"(?:do|would) you (?:like|want) (?:me|us) to\b"),
    re.compile(LEAD_IN + r"(?:want|wanna) me to\b"),
    re.compile(LEAD_IN + r"would you like (?:for )?me to\b"),
    re.compile(LEAD_IN + r"is it (?:ok|okay|alright|all right|fine) (?:if i|for me to|to)\b.*\?$"),
    re.compile(
        LEAD_IN
        + r"(?:can|may) i (?:go ahead|proceed|continue|start|apply|implement|make|fix|run|update|add|wire)\b.*\?$"
    ),
]
OFFER_ANYWHERE_PATTERNS = [
    re.compile(r"\blet me know (?:if|whether|when) you(?:'d| would)? (?:like|want) me to\b"),
    re.compile(r"\b(?:if you(?:'d| would)? like|if you want|if you prefer|if that helps|if useful|if helpful),? i (?:can|could|will|'ll)\b"),
    re.compile(r"\bi (?:can|could) (?:also |then |next |additionally |easily )?[^.?!]{0,160}?\bif you(?:'d| would)? (?:like|want)\b"),
    re.compile(r"\bhappy to [^.?!]{0,160}?\bif you(?:'d| would)? (?:like|want)\b"),
    re.compile(r"\bwant me to\b[^.!]*\?"),
    re.compile(r"\b(?:should|shall) i (?:go ahead|proceed|continue|keep going)\b"),
    re.compile(r"\bjust say (?:the word|so|go)\b"),
]
# Generic closers that offer nothing specific ("Let me know if you'd like me
# to change anything") are not treated as a hand-back.
VAGUE_OFFER_RE = re.compile(
    r"\b(?:me to|i can|i could|i will|i'll|happy to|should i|shall i)\s+"
    r"(?:make |do |help with |change |adjust |tweak )?"
    r"(?:any(?:thing)?|something|further|other|more|else)\b"
    r"(?! (?:test|tests|file|files|fix|fixes|check|checks|step|steps|endpoint|page|screen|feature)s?\b)"
)
# "Should I use Postgres or SQLite?" or "Do you want me to use your account or
# the company one?" asks how to do the asked work, which is a choice, not an
# offer. It is still an offer when it adds work ("Should I also add tests, or
# docs?") or when the other option is to stop ("..., or leave it here?").
OFFER_CHOICE_RE = re.compile(r"\b(?:or|either|versus|vs)\b")
EXTRA_WORK_RE = re.compile(r"\b(?:also|too|as well|next(?! to\b)|additionally|another)\b")
STOP_OPTION_RE = re.compile(
    r"\bor (?:not|leave|stop|skip|move on|call it|wrap|is (?:that|this) (?:enough|it|fine|ok|okay|good)|"
    r"are you good|keep (?:it|things|this) (?:as is|as-is|there|here))\b"
)
# Deleting, overwriting, publishing, deploying to production, sending
# messages and spending money really are the user's call, so neither an
# offer nor a question about them is pushed back. The word has to be the
# action ("Should I delete...", "...to be overwritten"), so "add a delete
# button" is still ordinary work.
USER_CALL_RE = re.compile(
    r"\b(?:to|i|we|i'll|we'll|you|be|and|or)\s+(?:(?:can|could|will|should|shall|may|also|just|now|then|"
    r"permanently|go ahead and)\s+){0,2}"
    r"(?:delet\w*|drop(?:ped|ping)?|wip(?:e|ed|ing)|purg\w*|eras(?:e|ed|ing)|destroy\w*|overwr\w*|truncat\w*|"
    r"force[- ]?push\w*|rm -rf|publish\w*|pay|paid|paying|purchas\w*|buy|buying|spend\w*|"
    r"deploy\w* (?:\S+ ){0,4}(?:to |on |in(?:to)? )?(?:the )?(?:prod|production|live)|"
    r"send\w* (?:\S+ ){0,4}(?:emails?|messages?|invoices?|newsletters?|notifications?))\b"
)


def handback_sentences(prose):
    """The last two sentences, plus the lead-in of a list that ends the message."""
    blocks = paragraphs(prose)
    if not blocks:
        return []
    tail = sentences(blocks[-1])[-2:]
    if len(blocks) > 1 and is_list_block(blocks[-1]):
        # "If you'd like, I can also:" followed by a list of extra work.
        lead = sentences(blocks[-2])[-1:]
        if lead and lead[0].rstrip(TRAILING_DECOR).endswith(":"):
            tail = lead + tail
    return tail


def check_handback(message):
    """Return the offering sentence when the message ends on a hand-back."""
    for sentence in reversed(handback_sentences(prose_of(message, end=True))):
        text = plain(sentence)
        if USER_CALL_RE.search(text):
            continue
        if (
            ends_with_question(text)
            and OFFER_CHOICE_RE.search(text)
            and not EXTRA_WORK_RE.search(text)
            and not STOP_OPTION_RE.search(text)
        ):
            continue
        hit = any(pattern.search(text) for pattern in OFFER_START_PATTERNS) or any(
            pattern.search(text) for pattern in OFFER_ANYWHERE_PATTERNS
        )
        if hit and not VAGUE_OFFER_RE.search(text):
            return sentence
    return None


def handback_reason(sentence):
    return (
        'Your last message ends by offering more work ("%s"). If that work is part of what the user '
        "asked for and can be undone, do it now, then write your final report covering all of it. If "
        "it needs the user (it deletes something you didn't create, leaves this machine, spends money "
        "or changes the goal), don't do it: state it as one open item with the default you applied. "
        "If the user only asked a question or asked for a review or a plan, send your answer again "
        "without the offer." % shorten(sentence)
    )


# ---------------------------------------------------------------------------
# Check 2: questions about the agent's own work

EXTENSIONS = (
    "py|pyi|ipynb|js|mjs|cjs|jsx|ts|tsx|json|jsonl|md|mdx|txt|csv|tsv|yaml|yml|toml|ini|cfg|conf|"
    "env|lock|rs|go|java|kt|kts|swift|c|h|cc|cpp|hpp|cs|rb|php|sh|bash|zsh|ps1|sql|html|htm|css|"
    "scss|less|vue|svelte|dart|lua|scala|gradle|proto|graphql|tf|xml|svg|png|jpg|jpeg|gif|webp|"
    "bmp|ico|mp4|mov|mkv|webm|avi|mp3|wav|flac|ogg|pdf|log|out|err|diff|patch|zip|tar|gz|tgz|"
    "bin|pt|ckpt|safetensors|onnx|npy|npz|pkl|parquet|h5|db|sqlite|xlsx|docx|pptx|wasm|dll|so|"
    "exe|dmg|apk|ipa|plist|gguf"
)
FILENAME_RE = re.compile(r"(?<![\w/.\\-])([\w-][\w.-]*\.(?:%s))(?![\w-])" % EXTENSIONS, re.I)
PATH_RE = re.compile(
    r"(?<![\w:/.~\\-])((?:~|\.{1,2})?/(?:[\w.@+-]+/)*[\w.@+-]+|(?:[\w.@+-]+/)+[\w@+-]+\.(?:%s))(?![\w/-])"
    % EXTENSIONS,
    re.I,
)
HEX_ID_RE = re.compile(r"(?<![\w-])(?=[0-9a-f]*\d)(?=[0-9a-f]*[a-f])[0-9a-f]{7,40}(?![\w-])")
UUID_RE = re.compile(r"\b[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}\b", re.I)
RUN_ID_RE = re.compile(
    r"(?<![\w-])((?:run|wt|exp|trial|attempt|iter|job|batch|worker|agent|subagent|draft|variant|"
    r"candidate|take|shard|ckpt|checkpoint)[-_]?\d+[a-z]?|\d+_[a-z]+\d+\w*)(?![\w-])",
    re.I,
)
# Names of tools and frameworks that look like file names.
TECH_NAMES = {
    "node.js", "next.js", "vue.js", "react.js", "three.js", "d3.js", "express.js", "nuxt.js",
    "ember.js", "backbone.js", "chart.js", "p5.js", "alpine.js", "solid.js", "angular.js",
    "socket.io", "moment.js", "pixi.js", "babylon.js", "phaser.js", "tone.js", "paper.js",
    "fabric.js", "matter.js", "leaflet.js", "preact.js", "nest.js", "deno.js", "bun.sh",
    "anime.js", "video.js", "hammer.js", "immer.js", "htmx.js", "gatsby.js", "remix.js",
}


def _clean_identifier(token):
    token = token.strip().strip("\"'()[]{}<>,;")
    token = re.sub(r":\d+(?::\d+)?$", "", token)  # file.py:12
    return token.rstrip(".:")


def _looks_like_identifier(token):
    if not token or len(token) > 200 or "://" in token or " " in token.strip():
        return False
    if token.lower() in TECH_NAMES:
        return False
    if "/" in token or "\\" in token:
        return bool(re.search(r"[A-Za-z0-9]", token)) and not re.fullmatch(r"[\d/]+", token)
    return bool(
        FILENAME_RE.fullmatch(token)
        or HEX_ID_RE.fullmatch(token)
        or UUID_RE.fullmatch(token)
        or RUN_ID_RE.fullmatch(token)
    )


def extract_identifiers(text):
    """File names, paths and work IDs named in text, in order of appearance."""
    found = []

    def add(token):
        token = _clean_identifier(token)
        if _looks_like_identifier(token) and not any(token in known for known in found):
            found.append(token)

    for match in CODE_SPAN_RE.finditer(text):
        add(match.group(1))
    outside = CODE_SPAN_RE.sub(" ", text)
    outside = re.sub(r"\b[a-z][a-z0-9+.-]*://\S+", " ", outside, flags=re.I)
    spans = []
    for pattern in (PATH_RE, FILENAME_RE, UUID_RE, HEX_ID_RE, RUN_ID_RE):
        for match in pattern.finditer(outside):
            spans.append((match.start(), match.group(match.lastindex or 0)))
    # Longest match first where two start together ("24_g521.mp4" before "24_g521").
    for _, _, token in sorted((start, -len(token), token) for start, token in spans):
        add(token)
    return found


def _squash(text):
    return re.sub(r"[\s_\-]+", "", text.lower())


def known_to_user(identifier, user_text, user_squashed):
    lowered = identifier.lower()
    if lowered in user_text:
        return True
    base = re.split(r"[/\\]", lowered.rstrip("/\\"))[-1]
    if len(base) >= 3 and base in user_text:
        return True
    squashed = _squash(identifier)
    return len(squashed) >= 3 and squashed in user_squashed


CHOICE_RE = re.compile(r"\b(?:which|or|either|between|one of|prefer|versus|vs)\b")


def question_parts(message):
    """Split the end of the message into (question, context) when it ends on a question.

    The question is the final sentence that ends with "?". The context is what
    a choice question can refer to: the sentence before it, the paragraph before
    it, or a list of options right after it. Returns None when the message does
    not end with a question.
    """
    blocks = paragraphs(prose_of(message, end=True))
    if not blocks:
        return None
    options = ""
    if ends_with_question(blocks[-1]):
        question_block, before = blocks[-1], blocks[:-1]
    elif len(blocks) > 1 and is_list_block(blocks[-1]) and ends_with_question(blocks[-2]):
        question_block, before, options = blocks[-2], blocks[:-2], blocks[-1]
    else:
        return None
    if is_list_block(question_block):
        items = re.split(r"\n(?=\s*(?:[-*+]|\d+[.)])\s+)", question_block)
        question_block = items[-1]
    parts = sentences(question_block)
    if not parts:
        return None
    question = parts[-1]
    if len(parts) > 1:
        context = parts[-2]
    elif before:
        context = before[-1] if is_list_block(before[-1]) else (sentences(before[-1]) or [""])[-1]
    else:
        context = ""
    return question, "\n".join(part for part in (context, options) if part)


# "Can you add the key in ~/.ssh/id_ed25519.pub to the server?" asks the user
# to do something only they can do, which is fine even when it names a file.
# Asking them to confirm, check or pick something is not.
USER_ACTION_RE = re.compile(
    r"^(?:(?:so|and|also|then|ok|okay),?\s+)?(?:please\s+)?(?:can|could|would|will) you\s+(?:please\s+)?"
    r"(?!(?:confirm|check|tell|clarify|verify|let me know|say|decide|choose|pick|look|see|remind|point)\b)\w"
)
# A question about taste or voice ("Does the tone in launch.md fit your
# customers?") needs the user's judgement even when it names a file.
TASTE_RE = re.compile(r"\b(?:tone|voice|wording|phrasing|brand|taste|audience|customers?|readers)\b")


def own_work_candidates(message):
    parts = question_parts(message)
    if parts is None:
        return []
    question, context = parts
    text = plain(question)
    if USER_ACTION_RE.match(text) or USER_CALL_RE.search(text) or TASTE_RE.search(text):
        return []
    names = extract_identifiers(question)
    if CHOICE_RE.search(text):
        names += [name for name in extract_identifiers(context) if name not in names]
    return names


def check_own_work(message, user_texts):
    """Return identifiers in the final question that the user never mentioned."""
    candidates = own_work_candidates(message)
    if not candidates or not user_texts:
        return []
    user_text = "\n".join(user_texts).lower()
    user_squashed = _squash(user_text)
    return [name for name in candidates if not known_to_user(name, user_text, user_squashed)][:3]


def own_work_reason(names):
    return (
        "Your last message asks the user about %s, which never appear in their messages, so they "
        "come from your own work. Look at them yourself (open, list, compare, check timestamps or "
        "the output that produced them), pick using that evidence, say in one line what you picked, "
        "and carry on. Don't delete or overwrite anything you didn't create to settle it. If the "
        "answer truly depends on something only the user knows, keep the question as one open item "
        "with the default you applied." % join_names(names)
    )


# ---------------------------------------------------------------------------
# Check 3: hard-to-read reports

LONG_MESSAGE_CHARS = 400
DENSE_MIN_WORDS = 30
DENSE_MIN_CODE = 7
DENSE_RATIO = 0.15
SEMICOLON_LIMIT = 3
MIXED_SEMICOLONS = 2
MIXED_CODE = 4
LONG_OPENING_WORDS = 150
LONG_FIRST_SENTENCE_WORDS = 70

CODE_NAME_PATTERNS = (
    PATH_RE,
    FILENAME_RE,
    RUN_ID_RE,
    re.compile(r"\b[a-z0-9]+_[a-z0-9_]+\b"),  # snake_case
    re.compile(r"\b[A-Z0-9]+_[A-Z0-9_]+\b"),  # SCREAMING_CASE
    re.compile(r"\b[a-z]+[A-Z][A-Za-z0-9]{2,}\b"),  # lowerCamelCase
    re.compile(r"\b\w+(?:\.\w+)*\(\)"),  # call()
    re.compile(r"\b\w+::\w+"),  # paths::like::this
    re.compile(r"(?<![\w-])--[a-z][\w-]+"),  # --flags
    re.compile(r"\b[A-Za-z_][\w-]*=[^\s,;]+"),  # KEY=value
)
LOWER_CAMEL_WORDS = {"iphone", "ipad", "ipados", "macos", "ios", "ebay", "youtube", "javascript"}


def count_code_names(text):
    """Count code spans plus distinct code-style names written outside them."""
    count = len(CODE_SPAN_RE.findall(text))
    outside = CODE_SPAN_RE.sub(" ", text)
    outside = re.sub(r"\b[a-z][a-z0-9+.-]*://\S+", " ", outside, flags=re.I)
    spans = []
    for pattern in CODE_NAME_PATTERNS:
        for match in pattern.finditer(outside):
            if match.group(0).lower() not in LOWER_CAMEL_WORDS and match.group(0).lower() not in TECH_NAMES:
                spans.append(match.span())
    end = -1
    for start, stop in sorted(spans):
        if start >= end:  # overlapping matches count once
            count += 1
        end = max(end, stop)
    return count


def word_count(text):
    return len(re.findall(r"\S+", text))


# Greek uses ";" as its question mark.
GREEK_QUESTION_RE = re.compile(r"(?<=[\u0370-\u03ff\u1f00-\u1fff])[\"'\u00bb)]*;")


def semicolons(text):
    text = CODE_SPAN_RE.sub(" ", text)
    return text.count(";") - len(GREEK_QUESTION_RE.findall(text))


LINE_BREAK_END_RE = re.compile(r"(?:[.!?:)]|  |\\)$")


def units(block):
    """Split a block into what a reader sees as separate pieces.

    List items and lines that end in a hard break or a full stop each count on
    their own; a paragraph that is merely wrapped across lines stays whole.
    """
    if is_list_block(block):
        return [unit for unit in re.split(r"\n(?=\s*(?:[-*+]|\d+[.)])\s+)", block) if unit.strip()]
    lines = [line for line in block.split("\n") if line.strip()]
    if len(lines) > 1 and sum(1 for line in lines[:-1] if LINE_BREAK_END_RE.search(line)) == len(lines) - 1:
        return lines
    return [block]


def opening_unit(blocks):
    """The first piece of prose, skipping headings and lists.

    A message that opens with "**Summary**" and a list of changes has no
    opening paragraph to judge, so this returns "" for it.
    """
    for block in blocks:
        block = without_heading(block)
        if not is_heading_block(block) and not is_list_block(block):
            return units(block)[0]
    return ""


def check_readability(message):
    """Return a short description of what makes the report hard to read."""
    prose = prose_of(message)
    lines = [line for line in prose.splitlines() if not line.lstrip().startswith("|")]
    prose = "\n".join(lines)
    if len(prose.strip()) < LONG_MESSAGE_CHARS:
        return None
    blocks = [block for block in paragraphs(prose) if not is_heading_block(block)]
    if not blocks:
        return None

    opening = opening_unit(blocks)
    words = word_count(opening)
    code = count_code_names(opening)
    opening_semis = semicolons(opening)
    if words >= DENSE_MIN_WORDS and code >= DENSE_MIN_CODE and code / float(words) >= DENSE_RATIO:
        return "its opening paragraph packs %d code names into %d words" % (code, words)
    if opening_semis >= MIXED_SEMICOLONS and code >= MIXED_CODE:
        return "its opening paragraph strings %d clauses together with semicolons around %d code names" % (
            opening_semis + 1,
            code,
        )

    for block in blocks:
        for unit in units(block):
            count = semicolons(unit)
            if count >= SEMICOLON_LIMIT:
                return "one paragraph strings %d clauses together with semicolons" % (count + 1)

    if words >= LONG_OPENING_WORDS:
        return "its opening paragraph runs %d words before the reader gets a break" % words
    first = sentences(opening)[:1]
    if first and word_count(first[0]) >= LONG_FIRST_SENTENCE_WORDS:
        return "its first sentence runs %d words" % word_count(first[0])
    return None


def readability_reason(detail):
    return (
        "Your final message is hard to follow for someone who saw only their own request (%s). "
        "Rewrite just the message, without redoing any work, as short plain paragraphs. Start with "
        "the answer or result, then say what changed, how it was checked and what was not, what is "
        "still open, and any decisions you made that they may want to change. Use plain names for "
        "things and keep a path only where the reader will want to open the file." % detail
    )


# ---------------------------------------------------------------------------
# Transcript


HARNESS_PREFIXES = (
    "<environment_context>",
    "<user_instructions>",
    "<permissions instructions>",
    "<hook_prompt",
    "<turn_aborted>",
    "<subagent_notification>",
    "<collaboration_mode>",
    "# agents.md instructions",
    "<skill>",
)


TYPED_MARKERS = ('"UserMessage"', '"user_message"', '"task_started"', '"turn_context"')


class Transcript(object):
    def __init__(self):
        self.user_texts = []
        self.plan_mode = False


def _texts_from_content(content, allowed_types):
    if isinstance(content, str):
        return [content]
    texts = []
    if isinstance(content, list):
        for part in content:
            if isinstance(part, dict) and part.get("type") in allowed_types:
                text = part.get("text")
                if isinstance(text, str):
                    texts.append(text)
    return texts


def _is_harness_text(text):
    return text.lstrip().lower().startswith(HARNESS_PREFIXES)


def read_transcript(path):
    """Read the user's own messages and the current mode from a rollout file.

    Codex writes one JSON object per line: {"timestamp", "type", "payload"}.
    Newer ("paginated") rollouts store typed user input as
    event_msg/item_completed with an item of type "UserMessage"; legacy rollouts
    store event_msg/user_message. Both also keep the raw model input as
    response_item messages with role "user", which mix in harness text such as
    <environment_context> and Stop-hook prompts; those are used only when
    nothing better is present. Claude Code transcripts ({"type": "user",
    "message": {...}}) are read too. Returns None when nothing usable is found.
    """
    if not isinstance(path, str) or not path or path.endswith(".zst"):
        return None
    try:
        if not os.path.isfile(path) or os.path.getsize(path) > MAX_TRANSCRIPT_BYTES:
            return None
        handle = open(path, "r", encoding="utf-8", errors="replace")
    except (OSError, ValueError):
        return None

    items, legacy, raw, claude = [], [], [], []
    mode = None
    deadline = time.monotonic() + TRANSCRIPT_SECONDS
    with handle:
        for count, line in enumerate(handle):
            if count % 512 == 0 and time.monotonic() > deadline:
                return None
            # Only these record kinds matter. Raw "user" records are a fallback,
            # so they are skipped once typed user messages have been seen.
            if not any(marker in line for marker in TYPED_MARKERS) and (
                items or legacy or '"user"' not in line
            ):
                continue
            try:
                record = json.loads(line)
            except ValueError:
                continue
            if not isinstance(record, dict):
                continue
            kind = record.get("type")
            payload = record.get("payload")
            if isinstance(payload, dict):
                ptype = payload.get("type")
                if kind == "event_msg" and ptype == "item_completed":
                    item = payload.get("item")
                    if isinstance(item, dict) and item.get("type") == "UserMessage":
                        items.extend(_texts_from_content(item.get("content"), ("text",)))
                elif kind == "event_msg" and ptype == "user_message":
                    message = payload.get("message")
                    if isinstance(message, str):
                        legacy.append(message)
                elif kind == "event_msg" and ptype == "task_started":
                    if isinstance(payload.get("collaboration_mode_kind"), str):
                        mode = payload["collaboration_mode_kind"]
                elif kind == "turn_context":
                    collab = payload.get("collaboration_mode")
                    if isinstance(collab, dict) and isinstance(collab.get("mode"), str):
                        mode = collab["mode"]
                elif kind == "response_item" and ptype == "message" and payload.get("role") == "user":
                    raw.extend(_raw_user_texts(payload))
            elif kind == "user" and isinstance(record.get("message"), dict):
                message = record["message"]
                if message.get("role") == "user" and not record.get("isMeta"):
                    for text in _texts_from_content(message.get("content"), ("text",)):
                        if not text.lstrip().startswith("<"):
                            claude.append(text)

    transcript = Transcript()
    transcript.plan_mode = isinstance(mode, str) and mode.lower() == "plan"
    if items or legacy:
        texts = items + [text for text in legacy if text not in items]
    elif raw:
        texts = raw
    else:
        texts = claude
    transcript.user_texts = [text for text in texts if text.strip() and not _is_harness_text(text)]
    if not transcript.user_texts:
        return None
    return transcript


def _raw_user_texts(payload):
    texts = _texts_from_content(payload.get("content"), ("input_text", "text"))
    passthrough = payload.get("internal_chat_message_metadata_passthrough")
    metadata = passthrough.get("content_item_metadata") if isinstance(passthrough, dict) else None
    if isinstance(metadata, list) and len(metadata) == len(texts):
        kept = []
        for text, meta in zip(texts, metadata):
            provenance = meta.get("provenance") if isinstance(meta, dict) else None
            if not isinstance(provenance, dict) or provenance.get("type") == "user":
                kept.append(text)
        return kept
    return texts


# ---------------------------------------------------------------------------
# What the user asked for

ANSWER_ONLY_RE = re.compile(
    r"\b(?:plan|planning|proposal|propose|design doc|just report|report only|only report|"
    r"don't (?:change|edit|modify|touch|fix|implement)|do not (?:change|edit|modify|touch|fix|implement)|"
    r"no (?:code )?changes|without (?:changing|editing|modifying)|read[- ]only|dry[- ]run|review)\b"
)
ASK_ME_RE = re.compile(
    r"\b(?:ask me|interview me|check with me|confirm with me|ask before|ask first|"
    r"before you (?:start|change|edit|do|implement))\b"
)
# A sentence that starts with an instruction ("Fix ...", "Can you add ...",
# "Please run ...") makes the request a task.
INSTRUCTION_RE = re.compile(
    r"^(?:(?:ok|okay|so|now|then|also|and|great|thanks|cool|good|perfect|looks good),?\s+)*"
    r"(?:please\s+|(?:can|could|would|will) you\s+(?:please\s+)?|i (?:need|want) you to\s+|"
    r"(?:go ahead and|let's|lets)\s+)?"
    r"(?:fix|implement|add|build|create|make|update|change|refactor|write|remove|delete|migrate|"
    r"set up|setup|install|run|test|debug|qa|finish|complete|do|resolve|patch|optimi[sz]e|improve|"
    r"rename|move|convert|port|upgrade|clean up|wire|ship|deploy|generate|draft|cut|export|get|put|"
    r"use|try|continue|keep going|go ahead|redo|rewrite|replace|split|merge|bump|speed up|check|"
    r"verify|find and fix|investigate and fix)\b"
)
WH_QUESTION_RE = re.compile(r"^(?:what|why|how|when|where|which|who|whose|explain|tell me)\b")
YES_NO_QUESTION_RE = re.compile(r"^(?:is|are|was|were|does|do|did|has|have|should|can|could|would|will)\b")


def wants_answer_only(user_text):
    """True when the latest request reads as a question, a review or a plan."""
    text = plain(user_text).strip()
    if not text:
        return False
    if ANSWER_ONLY_RE.search(text) or ASK_ME_RE.search(text):
        return True
    parts = sentences(text) or [text]
    if any(INSTRUCTION_RE.match(part) for part in parts):
        return False
    return any(
        WH_QUESTION_RE.match(part) or (part.endswith("?") and YES_NO_QUESTION_RE.match(part))
        for part in parts
    )


# ---------------------------------------------------------------------------
# Per-session state


def state_dir(env):
    for key in ("PLUGIN_DATA", "CLAUDE_PLUGIN_DATA"):
        value = env.get(key)
        if value:
            return os.path.join(value, "stop-hook")
    uid = getattr(os, "getuid", lambda: "user")()
    return os.path.join(tempfile.gettempdir(), "tryhard-%s" % uid, "stop-hook")


def private_dir_ok(directory):
    """Create the fallback state folder under the shared temp folder safely.

    Codex always sets PLUGIN_DATA, so this only matters when the hook runs
    some other way. Another user could have created the folder (or a symlink
    to somewhere else) first, so it must be a real folder owned by this user.
    """
    getuid = getattr(os, "getuid", None)
    try:
        os.makedirs(directory, mode=0o700, exist_ok=True)
        if getuid is None:
            return True
        for path in (os.path.dirname(directory), directory):
            info = os.lstat(path)
            if not stat.S_ISDIR(info.st_mode) or info.st_uid != getuid():
                return False
    except OSError:
        return False
    return True


def state_path(directory, session_id):
    safe = re.sub(r"[^A-Za-z0-9_.-]", "_", session_id)[:120] or "session"
    return os.path.join(directory, safe + ".json")


def load_state(path):
    try:
        with open(path, "r", encoding="utf-8") as handle:
            state = json.load(handle)
    except (OSError, ValueError):
        return {}
    return state if isinstance(state, dict) else {}


def save_state(path, state):
    directory = os.path.dirname(path)
    os.makedirs(directory, exist_ok=True)
    fd, tmp = tempfile.mkstemp(prefix=".state-", dir=directory)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            json.dump(state, handle)
        os.replace(tmp, path)
    except BaseException:
        try:
            os.unlink(tmp)
        except OSError:
            pass
        raise
    _prune(directory)


def _prune(directory):
    """Keep the newest MAX_STATE_FILES session files and drop leftover temp files."""
    try:
        entries = []
        now = time.time()
        for name in os.listdir(directory):
            path = os.path.join(directory, name)
            try:
                mtime = os.lstat(path).st_mtime
                if name.startswith(".state-") and now - mtime > STALE_TEMP_SECONDS:
                    os.unlink(path)  # left behind by a run that was killed mid-write
                elif name.endswith(".json"):
                    entries.append((mtime, path))
            except OSError:
                continue
        entries.sort()
        for _, old in entries[: max(0, len(entries) - MAX_STATE_FILES)]:
            try:
                os.unlink(old)
            except OSError:
                pass
    except OSError:
        pass


# ---------------------------------------------------------------------------
# Main decision


def evaluate(payload, env, transcript_reader=read_transcript):
    """Return the JSON text to print, or None to let the turn end."""
    if hook_disabled(env) or not isinstance(payload, dict):
        return None
    if payload.get("hook_event_name", "Stop") != "Stop":
        return None
    if payload.get("stop_hook_active") is not False:
        # Missing or true: this turn was already pushed once (or we can't tell).
        return None
    message = payload.get("last_assistant_message")
    session_id = payload.get("session_id")
    if not isinstance(message, str) or not message.strip():
        return None
    if not isinstance(session_id, str) or not session_id:
        return None
    if str(payload.get("permission_mode", "")).lower() == "plan" or "<proposed_plan>" in message:
        # Codex sends no plan permission mode today; plan mode is read from
        # the transcript below. The tag is a cheap extra signal.
        return None

    checks = enabled_checks(env)
    if not checks:
        return None
    directory = state_dir(env)
    if not (env.get("PLUGIN_DATA") or env.get("CLAUDE_PLUGIN_DATA")) and not private_dir_ok(directory):
        return None
    path = state_path(directory, session_id)
    state = load_state(path)
    quiet = set(state.get("quiet") or [])
    streak = state.get("streak") if isinstance(state.get("streak"), dict) else {}
    turn_id = payload.get("turn_id")
    if isinstance(turn_id, str) and turn_id and state.get("last_block_turn") == turn_id:
        return None
    active = [name for name in checks if name not in quiet]

    # Cheap message-only screening first; the transcript is read only if needed.
    offer = check_handback(message) if "handback" in active else None
    candidates = own_work_candidates(message) if "own-work" in active else []
    detail = check_readability(message) if "readability" in active else None

    fired = {}
    if offer or candidates or detail:
        transcript = transcript_reader(payload.get("transcript_path"))
        if transcript is not None and transcript.plan_mode:
            return None
        latest = transcript.user_texts[-1] if transcript is not None else ""
        answer_only = bool(latest) and wants_answer_only(latest)
        if offer and not answer_only:
            fired["handback"] = handback_reason(offer)
        if candidates and transcript is not None and not ASK_ME_RE.search(plain(latest)):
            names = check_own_work(message, transcript.user_texts)
            if names:
                fired["own-work"] = own_work_reason(names)
        if detail:
            fired["readability"] = readability_reason(detail)

    new_streak = {}
    new_quiet = set(quiet)
    for name in active:
        count = int(streak.get(name, 0) or 0) + 1 if name in fired else 0
        if count:
            new_streak[name] = count
        if count >= STREAK_LIMIT:
            new_quiet.add(name)

    if not fired:
        if any(streak.get(name) for name in active):
            state.update({"streak": new_streak, "updated": int(time.time())})
            save_state(path, state)
        return None

    state.update(
        {
            "session_id": session_id,
            "streak": new_streak,
            "quiet": sorted(new_quiet),
            "last_block_turn": turn_id if isinstance(turn_id, str) else None,
            "updated": int(time.time()),
        }
    )
    save_state(path, state)  # if this fails, the caller prints nothing
    reason = "\n\n".join([fired[name] for name in CHECKS if name in fired] + [FOOTER])
    return json.dumps({"decision": "block", "reason": reason})


def read_input(stdin):
    """Read the event as UTF-8 whatever the locale (Windows pipes default to the ANSI code page)."""
    source = getattr(stdin, "buffer", stdin)
    data = source.read(MAX_STDIN_BYTES + 1)
    if len(data) > MAX_STDIN_BYTES:
        return None
    if isinstance(data, bytes):
        data = data.decode("utf-8", errors="replace")
    return data.lstrip("\ufeff")


def main(stdin=None, stdout=None, env=None):
    try:
        stdin = stdin if stdin is not None else sys.stdin
        stdout = stdout if stdout is not None else sys.stdout
        env = env if env is not None else os.environ
        if hook_disabled(env):
            return 0
        data = read_input(stdin)
        if not data or not data.strip():
            return 0
        output = evaluate(json.loads(data), env)
        if output:
            stdout.write(output + "\n")
            stdout.flush()
    except BaseException:
        pass
    return 0


if __name__ == "__main__":
    sys.exit(main())
