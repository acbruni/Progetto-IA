from langchain_ollama import OllamaLLM

from pddl_utils import (
    validate_pddl_with_fast_downward,
    sanitize_pddl,
    check_balanced_parentheses  
)

llm = OllamaLLM(model="deepseek-coder:6.7b")

def run_reflection_loop(lore, domain_path, problem_path):
    with open(domain_path) as f: domain = f.read()
    with open(problem_path) as f: problem = f.read()

    for i in range(5):
        print(f"\n[Reflection Attempt {i+1}]")

        prompt = f"""
You are an expert in AI planning. The following PDDL files are invalid or fail to produce a plan.

Please:
- Identify and correct any syntax or logic issues.
- Regenerate a valid PDDL DOMAIN starting with (define (domain lantern-of-light)
- Regenerate a valid PDDL PROBLEM starting with (define (problem lantern-of-light-problem)

DO NOT include explanations, comments, or markdown. Return only valid raw PDDL.

### LORE:
{lore}

### CURRENT DOMAIN:
{domain}

### CURRENT PROBLEM:
{problem}
"""

        output = llm.invoke(prompt).strip()
        
        if "(define (domain" in output and "(define (problem" in output:
            try:
                domain_part, problem_part = output.split("(define (problem", 1)
                domain_clean = sanitize_pddl(domain_part.strip())
                problem_clean = sanitize_pddl("(define (problem" + problem_part.strip())

                # Mostra la proposta del reflection agent
                print("\n--- PROPOSTA DEL REFLECTION AGENT ---\n")
                print("========== DOMAIN ==========")
                print(domain_clean)
                print("========== PROBLEM ==========")
                print(problem_clean)
                print("\n--- FINE PROPOSTA ---\n")

                # Human-in-the-loop: scegli cosa fare
                while True:
                    print("Cosa vuoi fare?")
                    print("1. Applica automaticamente questa correzione e valida")
                    print("2. Modifica manualmente i file (verrai bloccato finché non premi invio per continuare)")
                    print("3. Esci dal reflection loop")
                    scelta = input("Scegli (1/2/3): ").strip()
                    if scelta in {"1", "2", "3"}:
                        break

                if scelta == "1":
                    # Controllo sintassi
                    if not (
                        check_balanced_parentheses(domain_clean)
                        and check_balanced_parentheses(problem_clean)
                    ):
                        print("[❌ Parentesi non bilanciate] Non applico. Provo di nuovo.")
                        continue

                    with open(domain_path, "w") as f: f.write(domain_clean)
                    with open(problem_path, "w") as f: f.write(problem_clean)

                    print("[Aggiornamento dei file PDDL effettuato] Validazione in corso...")
                    if validate_pddl_with_fast_downward(domain_path, problem_path):
                        print("[✅ PDDL corretto e validato!]")
                        return lore
                    else:
                        print("[❌ Ancora non valido] Si riprova...\n")
                        # continua il loop
                elif scelta == "2":
                    print(f"\nModifica manualmente '{domain_path}' e '{problem_path}', poi premi INVIO per continuare il reflection loop...")
                    input("Premi INVIO per continuare. (Se vuoi interrompere, premi Ctrl+C)")
                    # Reload file (magari hai modificato a mano)
                    with open(domain_path) as f: domain = f.read()
                    with open(problem_path) as f: problem = f.read()
                    continue  # Non aumenta i tentativi: lascia che l'utente provi a mano
                else:  # scelta == "3"
                    print("Reflection interrotto su richiesta dell'utente.")
                    return lore

            except Exception as e:
                print(f"[Parsing Error] {e}")
        else:
            print("[Invalid reflection output] Missing 'define' blocks")
            with open("debug_reflection_output.txt", "w") as f:
                f.write(output)
            print("❗ Debug salvato in 'debug_reflection_output.txt'\n")

    print("[Reflection failed after 5 attempts]")
    return lore
