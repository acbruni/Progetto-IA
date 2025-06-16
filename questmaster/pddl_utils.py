import os
from langchain_core.prompts import PromptTemplate
from langchain_ollama import OllamaLLM
import subprocess

# Imposta il modello
llm = OllamaLLM(model="llama3.2")  

# Prompt per generare PDDL
DOMAIN_PROMPT = PromptTemplate.from_template("""
You are an expert in classical planning and PDDL (Planning Domain Definition Language).

Based on the following fantasy narrative lore, generate a fully valid and logically coherent PDDL domain file. The domain should model the environment, agents, objects, and actions involved in the adventure using strict PDDL 2.1 syntax. Do not include any non-standard syntax or comments that break the format.

LORE:
{lore}
### Requirements:
- Use `:strips` and `:typing` in the `:requirements`.
- Define all necessary `:types` to capture locations, characters, keys, magical items, and obstacles (e.g., `adventurer`, `location`, `creature`, `item`, etc.).
- Declare all relevant `:predicates` representing:
  - location of agents and objects
  - possession of items
  - whether doors are open or blocked
  - whether creatures have been defeated
  - quest state progression (e.g., key found, lantern acquired)
- Include **at least 6 meaningful actions**, each with:
  - Clear parameters and types
  - Non-trivial preconditions and effects
  - Domain logic reflecting the story (e.g., "ask-grandma", "explore-woods", "defeat-wolf", "open-door", "retrieve-lantern", etc.)

### Format:
Output only the PDDL domain file, starting with `(define (domain lantern-of-light)` and valid throughout. Ensure the domain is parsable and usable by planners like Fast Downward.
""")

PROBLEM_PROMPT = PromptTemplate.from_template("""
You are an expert in AI planning using PDDL.

Using the domain named `lantern-of-light`, and based on the following fantasy narrative lore, generate a valid PDDL problem file. The file should include a fully specified initial state, objects, and a goal state that matches the quest described in the lore.

LORE:
{lore}
### Requirements:
- Reference the domain `lantern-of-light`.
- Declare a set of `:objects` reflecting the story, including:
  - An adventurer
  - Grandma Mira
  - The spectral wolf
  - Locations like Valdombra, Misty Woods, Lighthouse
  - Items like the Moon Key and the Lantern of Light
- Define a consistent `:init` state:
  - The adventurer begins in Valdombra
  - The Moon Key is in the Misty Woods
  - The spectral wolf blocks the path
  - The lantern is in the lighthouse
  - The door is closed or blocked
- Set a `:goal` that models the successful completion of the quest:
  - The adventurer has the Lantern of Light
  - Optional: spectral wolf defeated, lighthouse entered

### Format:
Output only the valid PDDL problem file starting with `(define (problem lantern-of-light-problem)` and following standard PDDL 2.1 syntax. Ensure the problem is compatible with the `lantern-of-light` domain and planners like Fast Downward.
""")

def generate_pddl_from_lore(lore: str):
    os.makedirs("pddl_code", exist_ok=True)
    domain_path = "pddl_code/domain.pddl"
    problem_path = "pddl_code/problem.pddl"

    # Genera domain.pddl
    domain_pddl = llm.invoke(DOMAIN_PROMPT.format(lore=lore))
    with open(domain_path, "w") as f:
        f.write(domain_pddl)

    # Genera problem.pddl
    problem_pddl = llm.invoke(PROBLEM_PROMPT.format(lore=lore))
    with open(problem_path, "w") as f:
        f.write(problem_pddl)

    return domain_path, problem_path

FAST_DOWNWARD_PATH = "/Users/annachiarabruni/downward/fast-downward.py"

def validate_pddl(domain_path: str, problem_path: str) -> bool:
    """
    Runs Fast Downward on the provided PDDL files to check if a valid plan exists.
    Returns True if a plan is found, otherwise False.
    """
    print("\n[Validating PDDL with Fast Downward...]")

    try:
        result = subprocess.run(
            [
                "python3", FAST_DOWNWARD_PATH,
                "--alias", "seq-sat-lama-2011",
                domain_path,
                problem_path
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=60  # fail gracefully if too slow
        )

        if "Solution found!" in result.stdout:
            print("[✔] PDDL validation successful.")
            return True
        else:
            print("[✘] Fast Downward did not find a solution.")
            return False

    except subprocess.TimeoutExpired:
        print("[⚠] Fast Downward timed out.")
        return False

    except Exception as e:
        print(f"[❌] Fast Downward error: {e}")
        return False