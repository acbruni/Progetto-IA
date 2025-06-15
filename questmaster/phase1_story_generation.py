from reflection_agent import run_reflection_loop
from pddl_utils import generate_pddl_from_lore, validate_pddl
from lore_loader import load_lore

def story_generation_phase(lore_path):
    lore = load_lore(lore_path)

    domain_path, problem_path = generate_pddl_from_lore(lore)
    success = validate_pddl(domain_path, problem_path)

    retries = 0
    max_retries = 5
    while not success and retries < max_retries:
        print(f"\n[PDDL validation failed. Running Reflection Agent... Attempt {retries + 1}]")
        updated_lore = run_reflection_loop(lore, domain_path, problem_path)
        lore = updated_lore
        domain_path, problem_path = generate_pddl_from_lore(updated_lore)
        success = validate_pddl(domain_path, problem_path)
        retries += 1

    if not success:
        print("Final attempt failed. Please check PDDL manually.")
    else:
        print("Valid PDDL files generated.")

    return domain_path, problem_path, lore