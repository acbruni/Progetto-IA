import subprocess
import os
from langchain_ollama import ChatOllama

from langchain_ollama import ChatOllama

def generate_pddl_from_lore(lore: str):
    domain_path = "domain.pddl"
    problem_path = "problem.pddl"

    llm = ChatOllama(model="llama3.2")

    domain_prompt = f"""
    Generate a valid PDDL DOMAIN file for this fantasy quest.

    LORE:
    {lore}
    """

    problem_prompt = f"""
    Generate a valid PDDL PROBLEM file for this fantasy quest.

    LORE:
    {lore}
    """

    print("🛠️ Generating domain.pddl...")
    domain_code = llm.invoke(domain_prompt).content
    print(domain_code)  # Così lo viri

    print("🛠️ Generating problem.pddl...")
    problem_code = llm.invoke(problem_prompt).content
    print(problem_code)

    with open(domain_path, "w") as d:
        d.write(domain_code)
    with open(problem_path, "w") as p:
        p.write(problem_code)

    return domain_path, problem_path


def validate_pddl(domain_file, problem_file):
    try:
        result = subprocess.run(
            ["python3", "/path/to/fast-downward.py", domain_file, problem_file, "--search", "astar(lmcut)"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=30,
        )
        return b"Solution found" in result.stdout
    except Exception as e:
        print("Validation error:", e)
        return False
