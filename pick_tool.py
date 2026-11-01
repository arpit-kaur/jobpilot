"""Llama picks a tool for each request. Code runs it."""

import ollama

from tools import compare_skills, read_posting, save_application

TOOLS = [read_posting, compare_skills, save_application]
TOOLS_BY_NAME = {
    "read_posting": read_posting,
    "compare_skills": compare_skills,
    "save_application": save_application,
}


def pick_and_run(request):
    """Ask Llama which tool fits the request, then run that tool ourselves."""
    response = ollama.chat(
        model="llama3.1:8b",
        messages=[{"role": "user", "content": request}],
        tools=TOOLS,
    )

    if not response.message.tool_calls:
        print("No tool chosen. Llama replied:", response.message.content)
        return

    for call in response.message.tool_calls:
        name = call.function.name
        arguments = call.function.arguments
        print("Llama chose: ", name)
        print("Arguments:   ", arguments)

        tool = TOOLS_BY_NAME[name]
        result = tool(**arguments)
        print("Tool result: ", result[:200])


if __name__ == "__main__":
    requests = [
        "Read the posting prairie_mutual_ai_developer.txt",
        "Save the .NET Developer job at Riverbend Software to my tracker",
        "Which skills am I missing for a job that needs Python, Docker and Azure?",
        "Hi, how are you today?",
    ]

    for request in requests:
        print("\n" + "=" * 60)
        print("REQUEST:", request)
        pick_and_run(request)