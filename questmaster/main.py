from phase1_story_generation import story_generation_phase
from phase2_html_generator import generate_html_from_lore_and_pddl

def main():
    lore_path = "/Users/annachiarabruni/Progetti/Progetto IA/questmaster/lore.txt"
    domain, problem, lore = story_generation_phase(lore_path)
    generate_html_from_lore_and_pddl(lore, domain, problem)

if __name__ == "__main__":
    main()
