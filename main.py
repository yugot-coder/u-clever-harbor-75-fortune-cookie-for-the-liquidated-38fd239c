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


def output_path():
    """Entry destination: $MAKEFUN_OUTPUT_DIR/entry.txt, else /output."""
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR")
    if out_dir:
        return os.path.join(out_dir, "entry.txt")
    return OUTPUT_PATH


def verify_written_bytes(written, intended):
    """Byte-exact read-back verification: same length, same bytes,
    same sha256 digest; fail loudly on any drift."""
    if len(written) != len(intended):
        raise SystemExit("read-back byte length mismatch")
    if written != intended:
        raise SystemExit("read-back mismatch: written bytes differ")
    if hashlib.sha256(written).digest() != hashlib.sha256(intended).digest():
        raise SystemExit("read-back digest mismatch")


def main():
    problem = validate(FORTUNE)
    if problem is not None:
        raise SystemExit(problem)

    path = output_path()
    out_dir = os.path.dirname(path)
    if out_dir:
        os.makedirs(out_dir, exist_ok=True)

    # newline="" keeps the file free of any platform line-ending
    # translation; the fortune is written with no trailing newline.
    with open(path, "w", encoding="utf-8", newline="") as handle:
        handle.write(FORTUNE)

    # Read-back verification: the bytes on disk must be exactly the
    # fortune's bytes; fail loudly on any drift.
    with open(path, "rb") as handle:
        written = handle.read()
    verify_written_bytes(written, FORTUNE.encode("utf-8"))
    digest = hashlib.sha256(written).hexdigest()
    print("wrote %s (%d chars, %d words, sha256 %s)" % (
        path,
        len(FORTUNE),
        len(FORTUNE.split()),
        digest,
    ))
    return 0


if __name__ == "__main__":
    sys.exit(main())
