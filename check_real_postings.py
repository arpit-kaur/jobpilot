"""Run my skill check on real job postings I saved privately."""

from pathlib import Path

from tools import compare_skills

PRIVATE_DIR = Path(__file__).parent / "data" / "private"

for path in sorted(PRIVATE_DIR.glob("*.txt")):
    text = path.read_text(encoding="utf-8")
    print(path.name)
    print("   ", compare_skills(text))
    print()