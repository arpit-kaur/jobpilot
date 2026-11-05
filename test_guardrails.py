"""Tests for the guardrail that catches false claims about saving."""


from guardrails import check_save_claim


def test_true_claim_is_left_alone():
    answer = "I saved the job to your tracker."
    assert check_save_claim(answer, ["read_posting", "save_application"]) == answer


def test_false_claim_gets_a_warning():
    answer = "I saved the job to your tracker."
    result = check_save_claim(answer, ["read_posting", "compare_skills"])
    assert "Warning" in result
    assert "Nothing was saved" in result


def test_answer_that_says_not_saved_is_left_alone():
    answer = "The job was not saved because you did not approve it."
    assert check_save_claim(answer, ["read_posting"]) == answer