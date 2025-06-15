from langgraph.graph import StateGraph
from langchain_ollama import ChatOllama
from langchain_core.tools import tool
from langgraph.types import interrupt, Command

@tool
def human_review_prompt(query: str) -> str:
    """Chiedi all'utente se approva o vuole modificare il file PDDL."""
    return interrupt({"query": query}).get("data", "")

llm = ChatOllama(model="llama3.2")
llm_with_tools = llm.bind_tools([human_review_prompt])

def reflection_node(state: dict) -> dict:
    response = llm_with_tools.invoke(state["messages"])
    return {"messages": [response]}

def run_reflection_loop(lore, domain_path, problem_path):
    from pathlib import Path

    graph = StateGraph(dict)
    graph.add_node("reflect", reflection_node)
    graph.set_finish_point("reflect")
    graph.set_entry_point("reflect")

    initial_prompt = {
        "role": "user",
        "content": (
            "The PDDL is invalid. Please analyze the issue and suggest specific corrections.\n\n"
            f"--- DOMAIN ---\n{Path(domain_path).read_text()}\n\n"
            f"--- PROBLEM ---\n{Path(problem_path).read_text()}\n\n"
            f"--- LORE ---\n{lore}"
        )
    }

    state = {"messages": [initial_prompt]}
    compiled = graph.compile()

    final_message = None
    for event in compiled.stream(state, {"configurable": {"thread_id": "reflection"}}):
        if "messages" in event:
            final_message = event["messages"][-1]
            print("\n🧠 Reflection Agent suggests:\n")
            print(final_message.content)

    # 🔁 Chiedi approvazione all'utente
    decision_prompt = (
        "Vuoi applicare queste modifiche al file PDDL?\n"
        "Scrivi 'si' per applicarle automaticamente,\n"
        "'no' per modificarle tu a mano,\n"
        "oppure 'esci' per uscire senza cambiare nulla."
    )

    approval = human_review_prompt.invoke(decision_prompt)

    if approval.lower().strip() == "si":
        print("✅ Applico le modifiche automaticamente (da implementare)")
        # TODO: parsing e scrittura nei file domain/problem
        # Per ora ritorna il lore originale
        return lore

    elif approval.lower().strip() == "no":
        print("🛠️ Hai scelto di modificarlo a mano. Interrompo.")
        exit()

    else:
        print("❌ Uscita scelta dall’utente.")
        exit()
