# BookLens — Package src
import sys
import io

# Fix Windows console encoding for emoji/unicode characters
# This prevents UnicodeEncodeError on Windows with cp1252 encoding
if sys.platform == "win32":
    try:
        if hasattr(sys.stdout, 'buffer'):
            sys.stdout = io.TextIOWrapper(
                sys.stdout.buffer, encoding='utf-8', errors='replace'
            )
        if hasattr(sys.stderr, 'buffer'):
            sys.stderr = io.TextIOWrapper(
                sys.stderr.buffer, encoding='utf-8', errors='replace'
            )
    except Exception:
        pass  # Already wrapped or not wrappable
