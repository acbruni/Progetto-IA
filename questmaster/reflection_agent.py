from langgraph.graph import StateGraph
from langchain_ollama import ChatOllama
from langchain_core.tools import tool
from langgraph.types import Command, interrupt

@tool
def human_review_prompt(query: str) -> str:
    """Requests human input when automated reflection is insufficient."""
    return interrupt({"query": query}).get("data", "")

llm = ChatOllama(model="llama3.2")
llm_with_tools = llm.bind_tools([human_review_prompt])

def reflection_node(state: dict) -> dict:
    response = llm_with_tools.invoke(state["messages"])
    return {"messages": [response]}

def run_reflection_loop(lore, domain_path, problem_path):
    graph = StateGraph(dict)
    graph.add_node("reflect", reflection_node)
    graph.set_finish_point("reflect")
    graph.set_entry_point("reflect")

    initial_state = {
        "messages": [
            {
                "role": "user",
                "content": (
                    "The current PDDL does not produce a valid plan. "
                    "Please review the following content and propose specific corrections:\n\n"
                    f"--- DOMAIN ---\n{open(domain_path).read()}\n\n"
                    f"--- PROBLEM ---\n{open(problem_path).read()}\n\n"
                    f"--- LORE ---\n{lore}"
                )
            }
        ]
    }

    thread_id = "reflection-thread"
    compiled_graph = graph.compile()

    final_message = None

    for event in compiled_graph.stream(initial_state, {"configurable": {"thread_id": thread_id}}):
        if "messages" in event and event["messages"]:
            final_message = event["messages"][-1]
            print("\n🧠 Reflection Agent Output:\n")
            print(final_message.content)

    return lore  # in futuro: modifica dinamica
