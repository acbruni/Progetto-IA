from langchain_ollama import OllamaLLM
from langchain_core.prompts import PromptTemplate

def generate_interactive_html(lore: str, domain: str, problem: str, output_path: str):
    llm = OllamaLLM(model="deepseek-coder:6.7b")

    prompt = PromptTemplate.from_template("""You are a system that generates HTML-based interactive fiction games. Based on the following inputs:

    LORE:
    {lore}

    PDDL DOMAIN:
    {domain}

    PDDL PROBLEM:
    {problem}

    Generate a full HTML page that tells the story as an interactive text game. Include the title, instructions, dynamic text choices (like buttons), and basic CSS for styling. 
    Do not use external libraries. Output a single self-contained HTML file.
    """)

    html_code = llm.invoke(prompt.format(lore=lore, domain=domain, problem=problem))

    with open(output_path, "w") as f:
        f.write(html_code)
