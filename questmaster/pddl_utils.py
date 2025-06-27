import os
import subprocess
from langchain_ollama import OllamaLLM
from langchain_core.prompts import PromptTemplate

def update_pddl_from_lore(lore_path: str, domain_path: str, problem_path: str):
    """
    Force regeneration of domain and problem PDDL files from a given lore file.
    """
    print("[PDDL Update] Regenerating PDDL files from lore...")

    # Carica la lore
    with open(lore_path) as f:
        lore = f.read()

    # Genera i nuovi domain e problem
    domain, problem = generate_pddl_from_lore(lore)

    # Scrive i file aggiornati
    write_file(domain_path, domain)
    write_file(problem_path, problem)

    print("[PDDL Update Completed] I file sono stati sovrascritti.")

def check_balanced_parentheses(pddl: str) -> bool:
    count = 0
    for char in pddl:
        if char == '(':
            count += 1
        elif char == ')':
            count -= 1
        if count < 0:
            return False
    return count == 0

def write_file(path, content):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w') as f:
        f.write(content)

def sanitize_pddl(text: str) -> str:
    lines = text.splitlines()
    clean_lines = []
    for line in lines:
        line = line.strip()
        if (
            line.startswith("```")
            or line.lower().startswith("this domain")
            or line.lower().startswith("this problem")
            or "defined to capture" in line.lower()
            or "pddl" in line.lower()
        ):
            continue
        clean_lines.append(line)
    return "\n".join(clean_lines)

llm = OllamaLLM(model="deepseek-coder:6.7b")

def generate_pddl_from_lore(lore: str):
    # ===== PROMPT DOMAIN =====
    domain_prompt = PromptTemplate.from_template("""
You are an expert in AI Planning and PDDL.

Your task is to generate a *domain.pddl* file for the domain 'lantern-of-light' based on the narrative LORE below.
The lore is only an inspiration: it does NOT specify all the actions or details.
You MUST invent and expand all missing logical elements, types, predicates, and actions necessary to make a fully interactive, multi-step planning domain, strictly coherent with the setting.

STRICT INSTRUCTIONS:
- The output must be valid PDDL 1.2, 100% compatible with Fast Downward.
- DO NOT include any comments, explanations, markdown, or text outside the PDDL code.
- Declare at least 5 meaningful actions.
- Only use variables (no fixed objects) in action parameters.
- All types and predicates must be clearly declared and used consistently.
- Each predicate must have clear names and types. Prefer 1-3 arguments per predicate.
- DO NOT use any PDDL ADL constructs (no 'when', 'forall', 'exists', 'or', 'imply', '=' etc).
- Use ONLY one (:types ...) block and one (:predicates ...) block.
- DO NOT use type-checking predicates like (is-person ?p).
- Action definitions must use only predicates declared in (:predicates).
- Parentheses must be perfectly balanced.

FILE STRUCTURE:
1. Begin with: (define (domain lantern-of-light)
2. Then include:
   - (:requirements :strips :typing)
   - (:types ...)
   - (:predicates ...)
   - At least 5 (:action ...) blocks

LORE CONTEXT (for inspiration only):
{lore}

Return ONLY the valid, plain PDDL code for domain.pddl. No other text.
""")

    # ===== PROMPT PROBLEM =====
    problem_prompt = PromptTemplate.from_template("""
You are an expert in AI Planning and PDDL.

Your task is to generate a *problem.pddl* file for the domain 'lantern-of-light' based on the narrative LORE below.

STRICT INSTRUCTIONS:
- The problem file must use ONLY types and predicates declared in the domain file, with the EXACT same spelling, names, and structure.
- DO NOT invent or modify predicates, types, or object names.
- DO NOT include any comments, explanations, markdown, or text outside the PDDL code.
- All objects must be assigned to the types declared in the domain.
- Use only one (:objects ...) block.
- The (:init ...) and (:goal ...) must reference only the predicates in the domain.
- The initial state must require at least 2-3 steps to achieve the goal (avoid trivial problems).
- Parentheses must be perfectly balanced.

FILE STRUCTURE:
1. Begin with: (define (problem lantern-of-light-problem)
2. Then include:
   - (:domain lantern-of-light)
   - (:objects ...)
   - (:init ...)
   - (:goal ...)

LORE CONTEXT (for inspiration only):
{lore}

Return ONLY the valid, plain PDDL code for problem.pddl. No other text.
""")

    domain_raw = llm.invoke(domain_prompt.format(lore=lore)).strip()
    problem_raw = llm.invoke(problem_prompt.format(lore=lore)).strip()

    # Sanitize the LLM output
    domain = sanitize_pddl(domain_raw)
    problem = sanitize_pddl(problem_raw)

    return domain, problem

def validate_pddl_with_fast_downward(domain_path: str, problem_path: str) -> bool:
    try:
        result = subprocess.run(
            [
                "python3", "/Users/annachiarabruni/downward/fast-downward.py",
                domain_path,
                problem_path,
                "--search", "lazy_greedy([ff()], preferred=[ff()])"
            ],
            capture_output=True,
            text=True,
            timeout=30
        )

        print("[Fast Downward Output]")
        print(result.stdout)
        print(result.stderr)

        return "Solution found!" in result.stdout
    except Exception as e:
        print(f"Error during planning: {e}")
        return False