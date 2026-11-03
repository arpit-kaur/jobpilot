"""JobPilot tools: plain Python functions the agent will be allowed to use."""

import csv
import re
from datetime import date
from pathlib import Path

DATA_DIR = Path(__file__).parent / "data"
POSTINGS_DIR = DATA_DIR / "postings"
SKILLS_FILE = DATA_DIR / "my_skills.txt"
TRACKER_FILE = DATA_DIR / "tracker.csv"

KNOWN_SKILLS = [
    "C#", ".NET", "ASP.NET Core", "Entity Framework", "SQL Server",
    "Angular", "React", "TypeScript", "JavaScript", "Java", "Python",
    "Azure", "Docker", "Kubernetes", "Git", "REST", "CI/CD", "LangChain",
    "AWS", "Node.js", "MongoDB", "Kotlin",
]


def mentions(text, skill):
    """Return True if the skill appears in the text as a whole word."""
    pattern = r"(?<![a-z0-9])" + re.escape(skill.lower()) + r"(?![a-z0-9])"
    return re.search(pattern, text.lower()) is not None


def read_posting(filename: str) -> str:
    """Read a saved job posting and return its full text.

    Args:
        filename: The posting's file name, for example prairie_mutual_ai_developer.txt
    """
    path = POSTINGS_DIR / filename
    if not path.exists():
        word = Path(filename).stem.lower().split("_")[0]
        matches = [p for p in POSTINGS_DIR.glob("*.txt") if word in p.name.lower()]
        if len(matches) == 1:
            path = matches[0]
        else:
            available = [p.name for p in POSTINGS_DIR.glob("*.txt")]
            return f"No posting called {filename}. Available postings: {available}"
    return path.read_text(encoding="utf-8")


def compare_skills(posting_text: str) -> str:
    """Compare a job posting with my skills and return the match and missing skills.

    My skills are already saved, so only the posting text is needed.
    Use this after read_posting, passing the posting text it returned.

    Args:
        posting_text: The full text of the job posting, as returned by read_posting
    """
    my_skills = SKILLS_FILE.read_text(encoding="utf-8").splitlines()
    my_skills = [skill.strip().lower() for skill in my_skills if skill.strip()]

    wanted = [skill for skill in KNOWN_SKILLS if mentions(posting_text, skill)]
    have = [skill for skill in wanted if skill.lower() in my_skills]
    missing = [skill for skill in wanted if skill.lower() not in my_skills]

    if not wanted:
        return "No known skills found in this posting."

    match = round(len(have) / len(wanted) * 100)
    return f"Match: {match}%. I have: {have}. Missing: {missing}."


def save_application(company: str, role: str, status: str = "Interested") -> str:
    """Save a job to my application tracker.

    Args:
        company: The company name
        role: The job title
        status: Application status. Use Interested if the user did not say.
    """
    is_new_file = not TRACKER_FILE.exists()
    with open(TRACKER_FILE, "a", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        if is_new_file:
            writer.writerow(["date", "company", "role", "status"])
        writer.writerow([date.today().isoformat(), company, role, status])
    return f"Saved to tracker: {role} at {company} ({status})."


if __name__ == "__main__":
    print("--- Tool 1: read_posting ---")
    text = read_posting("prairie_mutual_ai_developer.txt")
    print(text[:120], "...")
    print(read_posting("wrong_name.txt"))

    print("\n--- Tool 2: compare_skills ---")
    print(compare_skills(text))
    other = read_posting("riverbend_dotnet_developer.txt")
    print(compare_skills(other))

    print("\n--- Tool 3: save_application ---")
    print(save_application("Prairie Mutual Insurance", "AI Developer"))