from langchain_ollama import ChatOllama

def generate_html_from_lore_and_pddl(lore, domain_path, problem_path):
    llm = ChatOllama(model="llama3.2")
    pddl = open(domain_path).read() + "\n" + open(problem_path).read()
    prompt = f"Create a simple HTML interactive story interface based on the following lore and PDDL:\nLORE:\n{lore}\n\nPDDL:\n{pddl}"
    html_output = llm.invoke(prompt)
    with open("story_output.html", "w") as f:
        f.write(html_output.content)
