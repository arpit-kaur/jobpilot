"""JobPilot agent rebuilt with LangGraph. Same job as agent.py, written with a framework."""

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_ollama import ChatOllama
from langgraph.errors import GraphRecursionError
from langgraph.graph import START, MessagesState, StateGraph
from langgraph.prebuilt import ToolNode, tools_condition

from agent import MODEL, SYSTEM_PROMPT
from tools import compare_skills, read_posting, save_application
from guardrails import check_save_claim

TOOLS = [read_posting, compare_skills, save_application]
MAX_STEPS = 5

model = ChatOllama(model=MODEL, temperature=0).bind_tools(TOOLS)


def call_model(state: MessagesState):
    """The model reads the notebook and decides what to do next."""
    messages = [SystemMessage(content=SYSTEM_PROMPT)] + state["messages"]
    reply = model.invoke(messages)

    if not reply.content and not reply.tool_calls:
        print("  The model's reply came back empty. Asking it to continue.")
        nudge = HumanMessage(content="Continue with my request. Use the next tool you need.")
        reply = model.invoke(messages + [nudge])

    reply.tool_calls = reply.tool_calls[:1]
    return {"messages": [reply]}


builder = StateGraph(MessagesState)
builder.add_node("model", call_model)
builder.add_node("tools", ToolNode(TOOLS))
builder.add_edge(START, "model")
builder.add_conditional_edges("model", tools_condition)
builder.add_edge("tools", "model")
graph = builder.compile()


def run_agent(request):
    """Run the graph for one request and return the final answer."""
    try:
        result = graph.invoke(
            {"messages": [HumanMessage(content=request)]},
            {"recursion_limit": MAX_STEPS * 2 + 1},
        )
    except GraphRecursionError:
        return f"Stopped after {MAX_STEPS} steps without a final answer."

    messages = result["messages"]
    for message in messages:
        if message.type == "ai" and message.tool_calls:
            call = message.tool_calls[0]
            print(f"  Model asks for {call['name']} {call['args']}")
        elif message.type == "tool":
            print(f"  Result: {message.content[:100]}".replace("\n", " "))

    tools_used = [message.name for message in messages if message.type == "tool"]
    print(f"  Tools actually used: {tools_used}")
    return check_save_claim(messages[-1].content, tools_used)


if __name__ == "__main__":
    requests = [
        "Hi, how are you today?",
        "Read the riverbend posting and tell me the job title.",
        "Which skills am I missing for a job that needs Python, Docker and Azure?",
        "Read the prairie posting, check my skills against it, and save it to my tracker.",
    ]

    for request in requests:
        print("\n" + "=" * 60)
        print("REQUEST:", request)
        answer = run_agent(request)
        print("\nFINAL ANSWER:", answer)