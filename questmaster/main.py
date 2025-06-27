import os
from phase1_story_generation import story_generation_phase
from phase2_html_generator import generate_interactive_html

def main():
    lore_path = "/Users/annachiarabruni/Progetti/Progetto IA/questmaster/lore.txt"
    domain_path = "/Users/annachiarabruni/Progetti/Progetto IA/questmaster/pddl_code/domain.pddl"
    problem_path = "/Users/annachiarabruni/Progetti/Progetto IA/questmaster/pddl_code/problem.pddl"
    output_html_path = "/Users/annachiarabruni/Progetti/Progetto IA/questmaster/output/story.html"

    print("[Phase 1 Triggered] Generating PDDL files from lore...")
    domain, problem, lore = story_generation_phase(lore_path, domain_path, problem_path)

    print("[Phase 1 Skipped] Using existing domain and problem files.")
    with open(domain_path) as f:
        domain = f.read()
    with open(problem_path) as f:
        problem = f.read()
    with open(lore_path) as f:
        lore = f.read()

    print("[Phase 1 Completed]")

    generate_interactive_html(lore, domain, problem, output_html_path)
    print("[Phase 2 Completed] HTML game generated at:", output_html_path)

if __name__ == "__main__":
    main()
