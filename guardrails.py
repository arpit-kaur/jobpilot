"""Checks that run on the model's answer in code, so they do not depend on the model behaving."""


def check_save_claim(answer, tools_used):
    """Add a warning if the answer says the job was saved but the save tool never ran."""
    text = (answer or "").lower()
    says_saved = "saved" in text and "not saved" not in text and "wasn't saved" not in text
    if says_saved and "save_application" not in tools_used:
        return (
            (answer or "")
            + "\n\nWarning: the answer says the job was saved, but the save tool never ran. Nothing was saved."
        )
    return answer