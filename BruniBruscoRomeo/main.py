import os
import subprocess
from langchain_ollama import OllamaLLM
from langchain_core.prompts import PromptTemplate

# ===============================
# CONFIGURAZIONE INIZIALE
# ===============================
OLLAMA_MODEL = "llama3.2"   # Modello Ollama
LORE_FILE = "/Users/annachiarabruni/Progetti/Progetto IA/BruniBruscoRomeo/lore_input.txt"  # File di input della lore (testo)
PDDL_DOMAIN_FILE = "/Users/annachiarabruni/Progetti/Progetto IA/BruniBruscoRomeo/pddl_code/domain.pddl"  # Output PDDL dominio
PDDL_PROBLEM_FILE = "/Users/annachiarabruni/Progetti/Progetto IA/BruniBruscoRomeo/pddl_code/problem.pddl"  # Output PDDL problema
FAST_DOWNWARD_PATH = "/Users/annachiarabruni/downward/fast-downward.py" 
HTML_OUTPUT_FILE = "quest_interactive.html"  # Output HTML finale

# ===============================
# FUNZIONI UTILI
# ===============================

def print_step(msg):
    """Stampa un messaggio per evidenziare l'avanzamento del processo"""
    print(f"\n=== {msg} ===\n")

def carica_lore(percorso):
    """Carica la lore dal file di testo"""
    with open(percorso, "r") as f:
        return f.read()

def salva_file(contenuto, percorso):
    """Salva un contenuto di testo su file"""
    with open(percorso, "w") as f:
        f.write(contenuto)

def valida_pddl(domain_path, problem_path, fast_downward_path):
    """Esegue Fast Downward e restituisce True/False se trova una soluzione"""
    try:
        cmd = [
            "python3", fast_downward_path,
            domain_path, problem_path,
            "--search-options", "--search", "astar(blind())"
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)
        if "Solution found!" in result.stdout:
            return True, result.stdout
        else:
            return False, result.stdout
    except Exception as e:
        return False, str(e)

def extract_between(text, start, end):
    """Estrae una porzione di testo tra due delimitatori"""
    s = text.find(start)
    e = text.find(end)
    if s == -1 or e == -1:
        return ""
    return text[s+len(start):e]

# ===============================
# PROMPT PER LLM (molto dettagliati)
# ===============================

PDDL_PROMPT = """
You are an expert in Automated Planning and Narrative Design. Given the following lore document describing a fantasy quest and design constraints, your task is to generate a **logically correct PDDL domain file and PDDL problem file** for the adventure, in strict compliance with classical planning conventions.  

**Input Lore Document:**  
{lore}

**Instructions:**
- The domain file must define predicates, actions, and types coherent with the quest's entities, constraints, and possible player actions.
- The problem file must correctly encode the initial state and the goal, as well as all relevant objects/entities.
- Respect the branching factor and depth constraints as much as possible.
- Make sure there are no logical contradictions: the initial state must allow at least one valid plan to reach the goal.

**Output format:**  
Write the **domain PDDL first** (fully valid), then the **problem PDDL**. Clearly mark the start and end of each file with a delimiter:  
`===DOMAIN START===` ... `===DOMAIN END===`  
`===PROBLEM START===` ... `===PROBLEM END===`

Do not add any additional text outside these delimiters.  
"""

REFLECTION_PROMPT = """
You are a Reflection Agent specializing in fixing logical errors in PDDL code for interactive narrative planning.  
Given the lore document and the current PDDL domain/problem files, carefully analyze and identify any logical inconsistencies or narrative gaps that prevent planning.  
Suggest *specific* corrections (clearly explain what to change and why), then regenerate the corrected PDDL files, again with inline comments.  
Wrap your new files with the delimiters:
`===DOMAIN START===` ... `===DOMAIN END===`
`===PROBLEM START===` ... `===PROBLEM END===`
Only provide the corrected PDDL code with the explanations as inline comments.

**Lore:**  
{lore}

**Domain PDDL:**  
{domain}

**Problem PDDL:**  
{problem}
"""

HTML_PROMPT = """
You are a web developer and narrative designer.  
Given the following adventure lore and the finalized PDDL model (domain + problem), generate a single HTML file that lets users play the quest interactively.  
The interface must:
- Present the story state, player choices (based on available actions), and narrative context at each step.
- Update the state and available actions after each choice.
- Include clear narrative text and titles.
- Add comments in the HTML to explain each section.
- You can use basic JavaScript for interactivity.

**Lore:**  
{lore}

**Domain PDDL:**  
{domain}

**Problem PDDL:**  
{problem}
"""

# ===============================
# FASI DI GENERAZIONE PDDL e REFLECTION
# ===============================

def genera_pddl(llm, lore):
    """Genera i file PDDL (dominio e problema) a partire dalla lore"""
    prompt = PromptTemplate.from_template(PDDL_PROMPT).format(lore=lore)
    output = llm.invoke(prompt)
    domain = extract_between(output, "===DOMAIN START===", "===DOMAIN END===")
    problem = extract_between(output, "===PROBLEM START===", "===PROBLEM END===")
    return domain.strip(), problem.strip()

def rifinisci_pddl_raw(llm, lore, domain, problem):
    """
    Invoca il Reflection Agent e ritorna il testo completo con le correzioni e spiegazioni,
    per permettere la valutazione umana prima dell'eventuale applicazione automatica.
    """
    prompt = PromptTemplate.from_template(REFLECTION_PROMPT).format(
        lore=lore, domain=domain, problem=problem)
    return llm.invoke(prompt)

# ===============================
# MAIN WORKFLOW
# ===============================

def main():
    print_step("INIZIO DEL PROCESSO QuestMaster - Fase 1: Story Generation")
    # Inizializza LLM
    llm = OllamaLLM(model=OLLAMA_MODEL)

    print_step("Caricamento della lore")
    lore = carica_lore(LORE_FILE)
    tentativi = 0
    successo = False

    # Ciclo massimo di 5 tentativi (generazione + riflessioni)
    while tentativi < 5:
        tentativi += 1
        if tentativi == 1:
            # Primo tentativo: generazione classica dei PDDL
            print_step(f"Generazione dei file PDDL (tentativo {tentativi})")
            domain, problem = genera_pddl(llm, lore)
        else:
            # Tentativi successivi: intervento del Reflection Agent
            print_step(f"Invocazione del Reflection Agent per la correzione dei file PDDL (tentativo {tentativi})")
            riflessione_output = rifinisci_pddl_raw(llm, lore, domain, problem)
            # Stampa all'utente la proposta completa del Reflection Agent
            print("\n--- PROPOSTA DEL REFLECTION AGENT (da valutare) ---\n")
            print(riflessione_output)
            print("\n--- FINE PROPOSTA ---\n")

            # Scelta utente: 1=applica, 2=modifica manuale, 3=interrompi
            scelta = ""
            while scelta not in ['1', '2', '3']:
                print("Scegli un'opzione:")
                print("[1] Applica automaticamente la correzione proposta dal Reflection Agent")
                print("[2] Modifica manualmente i file e chiudi l'esecuzione")
                print("[3] Interrompi l'esecuzione e esci")
                scelta = input("Inserisci 1, 2 o 3: ").strip()

            if scelta == '2':
                print("Esecuzione terminata: puoi modificare manualmente i file PDDL.")
                return
            elif scelta == '3':
                print("Esecuzione interrotta dall'utente.")
                return
            # Se l'utente sceglie 1, applica direttamente le modifiche del Reflection Agent
            domain = extract_between(riflessione_output, "===DOMAIN START===", "===DOMAIN END===")
            problem = extract_between(riflessione_output, "===PROBLEM START===", "===PROBLEM END===")

        # Salva i file PDDL aggiornati
        salva_file(domain, PDDL_DOMAIN_FILE)
        salva_file(problem, PDDL_PROBLEM_FILE)

        print_step("Validazione dei file PDDL tramite Fast Downward")
        valido, log = valida_pddl(PDDL_DOMAIN_FILE, PDDL_PROBLEM_FILE, FAST_DOWNWARD_PATH)
        if valido:
            print_step("Validazione superata: il PDDL consente almeno una soluzione.")
            successo = True
            break
        else:
            print_step("Il modello PDDL NON è valido: non esiste alcuna soluzione.")
            print("Log del planner:")
            print(log)
            # Alla prossima iterazione verrà invocato il Reflection Agent (se non si raggiunge il max tentativi)

    if not successo:
        print_step("Fase 1 NON completata con successo. Nessun modello PDDL valido trovato.")
        return

    # ======= FINE FASE 1 =======
    print_step("FASE 1 COMPLETATA: PDDL e lore finale pronti.")
    print_step("INIZIO DELLA FASE 2: Generazione del gioco HTML interattivo")

    # ===============================
    # FASE 2: Generazione HTML interattivo
    # ===============================
    prompt_html = PromptTemplate.from_template(HTML_PROMPT).format(
        lore=lore, domain=domain, problem=problem
    )
    html_output = llm.invoke(prompt_html)
    salva_file(html_output, HTML_OUTPUT_FILE)
    print_step(f"FASE 2 COMPLETATA: File HTML '{HTML_OUTPUT_FILE}' generato con successo.")

# ===============================
# AVVIO DEL PROGRAMMA PRINCIPALE
# ===============================
if __name__ == "__main__":
    main()
