"""Tests for the JobPilot tools. No AI is used here, so they are fast and give the same result every time."""

import tools
from tools import compare_skills, mentions, read_posting, save_application


def test_mentions_whole_words_only():
    assert mentions("We use Java", "Java")
    assert not mentions("We use JavaScript", "Java")
    assert not mentions("digital tools", "Git")


def test_read_posting_exact_name():
    text = read_posting("prairie_mutual_ai_developer.txt")
    assert "Prairie Mutual Insurance" in text


def test_read_posting_finds_close_name():
    text = read_posting("riverbend_posting.txt")
    assert "Riverbend Software" in text


def test_read_posting_unknown_name_lists_files():
    result = read_posting("python_docker_azure_job.txt")
    assert result.startswith("No posting called")
    assert "riverbend_dotnet_developer.txt" in result


def test_compare_skills_prairie_is_78_percent():
    text = read_posting("prairie_mutual_ai_developer.txt")
    result = compare_skills(text)
    assert "Match: 78%" in result
    assert "Docker" in result


def test_save_application_writes_a_row(tmp_path, monkeypatch):
    fake_tracker = tmp_path / "tracker.csv"
    monkeypatch.setattr(tools, "TRACKER_FILE", fake_tracker)

    save_application("Test Company", "Test Role")

    lines = fake_tracker.read_text(encoding="utf-8").splitlines()
    assert lines[0] == "date,company,role,status"
    assert "Test Company,Test Role,Interested" in lines[1]