"""JobPilot agent: the agent loop written by hand, no framework."""

import ollama

from tools import compare_skills, read_posting, save_application

MODEL = "llama3.1:8b"
MAX_STEPS = 5

TOOLS = [read_posting, compare_skills, save_application]
TOOLS_BY_NAME = {
    "read_posting": read_posting,
    "compare_skills": compare_skills,
    "save_application": save_application,
}

SYSTEM_PROMPT = (
    "You are JobPilot, an assistant that helps me with my job search. "
    "You can read saved job postings, compare a posting with my skills, "
    "and save jobs to my tracker. "
    "Use a tool only when the request needs one. "
    "If a tool returns an error, read it and try again with the right input. "
    "Never guess what a posting says. Always read it with the tool before answering. "
    "If no tool is needed, just reply normally in one or two sentences, without mentioning tools."
)


def run_agent(request):
    """Run the agent loop for one request. Return the answer and the notebook."""
    notebook = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": request},
    ]

    for step in range(1, MAX_STEPS + 1):
        response = ollama.chat(model=MODEL, messages=notebook, tools=TOOLS, options={"temperature": 0})
        reply = response.message

        notebook.append({
            "role": "assistant",
            "content": reply.content,
            "tool_calls": reply.tool_calls,
        })

        if not reply.tool_calls:
            if '"name"' in (reply.content or ""):
                print("  Llama wrote the tool call as text. Asking it to use the tool.")
                notebook.append({
                    "role": "user",
                    "content": "Do not write the tool call as text. Use the tool directly.",
                })
                continue
            return reply.content, notebook

        for call in reply.tool_calls:
            name = call.function.name
            arguments = call.function.arguments
            print(f"  Step {step}: Llama asks for {name} {arguments}")

            tool = TOOLS_BY_NAME.get(name)
            if tool is None:
                result = f"There is no tool called {name}."
            else:
                result = tool(**arguments)
            print(f"  Result: {result[:100]}".replace("\n", " "))

            notebook.append({"role": "tool", "content": result, "tool_name": name})

    return f"Stopped after {MAX_STEPS} steps without a final answer.", notebook


def show_notebook(notebook):
    """Print every line of the notebook, so we can see what Llama saw."""
    print("\n  --- The notebook ---")
    for number, line in enumerate(notebook, start=1):
        text = line["content"] or ""
        if line.get("tool_calls"):
            text = "asks for " + line["tool_calls"][0].function.name
        print(f"  {number}. [{line['role']}] {text[:80]}".replace("\n", " "))


if __name__ == "__main__":
    requests = [
        "Hi, how are you today?",
        "Read the riverbend posting and tell me the job title.",
        "Which skills am I missing for a job that needs Python, Docker and Azure?",
    ]

    for request in requests:
        print("\n" + "=" * 60)
        print("REQUEST:", request)
        answer, notebook = run_agent(request)
        print("\nFINAL ANSWER:", answer)

        if "riverbend" in request:
            show_notebook(notebook)