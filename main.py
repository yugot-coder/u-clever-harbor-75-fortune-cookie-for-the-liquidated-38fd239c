"""Fortune cookie entry: write one fixed fortune line to /output/entry.txt.

The program holds a single pre-written fortune cookie message as a
constant and writes it out verbatim. Before writing, it sanity-checks
the text (length within the allowed window, word count within the
limit, not blank, encodable as UTF-8) so a bad constant fails loudly
instead of producing an invalid entry. Only the Python standard
library is used, and the output is fully deterministic: same bytes on
every run, no trailing newline.
"""

import hashlib
import os
import sys

# The fortune itself. Kept as one plain string so what is checked below
# is exactly what lands on disk.
FORTUNE = (
    "Fortune favors the bold. Tonight it favored the exchange, "
    "and the exchange kept the change."
)

OUTPUT_PATH = "/output/entry.txt"
MIN_CHARS = 1
MAX_CHARS = 160
MAX_WORDS = 20


def validate(text):
    """Return an error message if text is not a legal entry, else None."""
    if not MIN_CHARS <= len(text) <= MAX_CHARS:
        return "entry must be %d-%d characters, got %d" % (
            MIN_CHARS,
            MAX_CHARS,
            len(text),
        )
    if len(text.split()) > MAX_WORDS:
        return "entry must be at most %d words, got %d" % (
            MAX_WORDS,
            len(text.split()),
        )
    if not text.strip():
        return "entry must not be whitespace only"
    try:
        text.encode("utf-8")
    except UnicodeEncodeError as exc:
        return "entry is not encodable as UTF-8: %s" % exc
    return None


def main():
    problem = validate(FORTUNE)
    if problem is not None:
        raise SystemExit(problem)

    out_dir = os.path.dirname(OUTPUT_PATH)
    if out_dir:
        os.makedirs(out_dir, exist_ok=True)

    # newline="" keeps the file free of any platform line-ending
    # translation; the fortune is written with no trailing newline.
    with open(OUTPUT_PATH, "w", encoding="utf-8", newline="") as handle:
        handle.write(FORTUNE)

    # Read-back verification: the bytes on disk must hash to exactly
    # the fortune's sha256 digest; fail loudly on any drift.
    with open(OUTPUT_PATH, "rb") as handle:
        written = handle.read()
    digest = hashlib.sha256(written).hexdigest()
    if hashlib.sha256(written).digest() != hashlib.sha256(
        FORTUNE.encode("utf-8")
    ).digest():
        raise SystemExit("read-back mismatch: written bytes differ")
    print("wrote %s (%d chars, %d words, sha256 %s)" % (
        OUTPUT_PATH,
        len(FORTUNE),
        len(FORTUNE.split()),
        digest,
    ))
    return 0


if __name__ == "__main__":
    sys.exit(main())
