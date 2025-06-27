from reflection_agent import run_reflection_loop
from pddl_utils import generate_pddl_from_lore, write_file, validate_pddl_with_fast_downward, sanitize_pddl

def story_generation_phase(lore_path, domain_path, problem_path):
    with open(lore_path) as f:
        lore = f.read()

    domain, problem = generate_pddl_from_lore(lore)
    domain = sanitize_pddl(domain)
    problem = sanitize_pddl(problem)

    write_file(domain_path, domain)
    write_file(problem_path, problem)

    success = validate_pddl_with_fast_downward(domain_path, problem_path)

    if not success:
        lore = run_reflection_loop(lore, domain_path, problem_path)

    return domain, problem, lore
