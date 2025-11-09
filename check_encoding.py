import sys
from pathlib import Path

root = Path(".")

def check_file(path: Path):
    try:
        path.read_text(encoding="utf-8")
        return None
    except UnicodeDecodeError as e:
        return f"{path} -> {e}"

def main():
    problems = []
    for p in root.rglob("*.py"):
        res = check_file(p)
        if res:
            problems.append(res)
    if not problems:
        print("All .py files decode as UTF-8.")
    else:
        print("Files with decoding problems:")
        for line in problems:
            print(line)

if __name__ == "__main__":
    main()
