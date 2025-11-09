import shutil
from pathlib import Path

root = Path(".")
for p in root.rglob("*.py"):
    try:
        # Try reading as utf-8 first
        p.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        bak = p.with_suffix(p.suffix + ".bak")
        print(f"Fixing {p} (backup -> {bak})")
        shutil.copy2(p, bak)
        # Read as latin-1 to preserve raw byte values, then write utf-8
        raw = p.read_text(encoding="latin-1")
        p.write_text(raw, encoding="utf-8")
        print(f"Re-encoded {p} as UTF-8")
