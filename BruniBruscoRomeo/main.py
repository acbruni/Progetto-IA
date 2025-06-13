import os
import subprocess
# Importazioni da LangChain
from langchain_community.chat_models import ChatOllama
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser, BaseOutputParser
from langchain_core.exceptions import OutputParserException

# --- CONFIGURAZIONE (invariata) ---
LORE_FILE = '/Users/annachiarabruni/Progetti/Progetto IA/BruniBruscoRomeo/lore_input.txt'
DOMAIN_PDDL_FILE = '/Users/annachiarabruni/Progetti/Progetto IA/domain.pddl'
PROBLEM_PDDL_FILE = '/Users/annachiarabruni/Progetti/Progetto IA/problem.pddl'
FAST_DOWNWARD_PATH = '/Users/annachiarabruni/downward/fast-downward.py'
MODEL_FOR_CODE = 'codellama'
MODEL_FOR_LOGIC = 'llama3.2'

# --- 1. PARSER PERSONALIZZATO PER L'OUTPUT PDDL ---
# Questo è un grande vantaggio di LangChain: creiamo un parser per strutturare l'output.
class PddlOutputParser(BaseOutputParser):
    """Estrae i blocchi di codice PDDL dal testo di output dell'LLM."""
    def parse(self, text: str):
        try:
            domain_part = text.split('---domain.pddl---')[1].split('---problem.pddl---')[0].strip()
            problem_part = text.split('---problem.pddl---')[1].strip()
            if not domain_part or not problem_part:
                raise OutputParserException("Marcatori PDDL trovati ma sezioni vuote.")
            return {"domain": domain_part, "problem": problem_part}
        except IndexError:
            raise OutputParserException(f"Impossibile trovare i marcatori '---domain.pddl---' e '---problem.pddl---' nell'output: {text}")

# --- 2. FUNZIONI REFACTORIZZATE CON LANGCHAIN ---

def generate_pddl_from_lore(lore_text):
    """Chiama Ollama tramite LangChain per generare i file PDDL."""
    print(f"-> Contatto Ollama ({MODEL_FOR_CODE}) via LangChain per generare il PDDL...")
    
    # Definiamo il template del prompt in modo strutturato
    prompt_template = ChatPromptTemplate.from_template(
        """Basandoti sulla seguente lore, genera un file di dominio PDDL e un file di problema PDDL.

        Assicurati che il codice generato sia sintatticamente corretto e semanticamente valido per il planner Fast Downward.

        Durante la generazione, rispetta le seguenti direttive per garantire la compatibilità:

        Requisiti del Dominio (:requirements):

        Utilizza solo requisiti supportati da Fast Downward, come :strips, :typing, :adl, :conditional-effects, e :negative-preconditions.
        Evita requisiti non supportati come :numeric-fluents (eccetto per i costi delle azioni in (:metric)) o :durative-actions.
        Tipi (:types):

        Definisci una gerarchia di tipi chiara e semplice.
        Azioni e Effetti:

        Struttura le azioni con parametri, precondizioni (:precondition) ed effetti (:effect).
        Gli effetti condizionali (when) sono permessi, ma evita annidamenti complessi.
        Le precondizioni possono includere congiunzioni (and), disgiunzioni (or) e negazioni (not).
        File di Problema:

        Definisci chiaramente tutti gli oggetti in (:objects).
        Inizializza lo stato del mondo in (:init) in modo coerente con la lore, usando solo i predicati definiti nel dominio.
        Definisci un obiettivo (:goal) raggiungibile e significativo.
        FORMATO DI OUTPUT:

        Usa il marcatore ---domain.pddl--- per iniziare il file di dominio.
        Usa il marcatore ---problem.pddl--- per iniziare il file di problema.
        Aggiungi un commento PDDL (usando ;) dopo ogni riga di codice significativa per spiegare la sua funzione e il suo collegamento con la lore.

        LORE:
        {lore}"""
    )
    
    # Inizializziamo il modello LLM
    llm = ChatOllama(model=MODEL_FOR_CODE)
    
    # Creiamo la "catena" che collega prompt, modello e parser
    chain = prompt_template | llm | PddlOutputParser()
    
    try:
        # Eseguiamo la catena
        pddl_output = chain.invoke({"lore": lore_text})
        
        # Salviamo i file usando l'output già parsato
        with open(DOMAIN_PDDL_FILE, 'w') as f:
            f.write(pddl_output['domain'])
        with open(PROBLEM_PDDL_FILE, 'w') as f:
            f.write(pddl_output['problem'])
            
        print("-> File PDDL generati correttamente.")
        return True
    except Exception as e:
        print(f"!! Errore durante l'esecuzione della catena LangChain: {e}")
        return False

def get_refinement_suggestion(lore_text, pddl_domain, pddl_problem):
    """Chiede all'agente di riflessione (via LangChain) perché il PDDL non è valido."""
    print(f"-> Chiedo un suggerimento al Reflection Agent ({MODEL_FOR_LOGIC}) via LangChain...")
    
    prompt_template = ChatPromptTemplate.from_template(
        """Il seguente modello PDDL, basato sul lore fornito, non è risolvibile.
        Analizza il lore e il PDDL per identificare l'incoerenza logica.
        Suggerisci una singola, specifica e concisa modifica da fare al testo del file di lore per risolvere il problema.

        LORE: {lore}
        DOMAIN PDDL: {domain}
        PROBLEM PDDL: {problem}"""
    )
    llm = ChatOllama(model=MODEL_FOR_LOGIC)
    # Per un output di tipo stringa, usiamo lo StrOutputParser
    chain = prompt_template | llm | StrOutputParser()
    
    try:
        suggestion = chain.invoke({
            "lore": lore_text,
            "domain": pddl_domain,
            "problem": pddl_problem
        })
        return suggestion
    except Exception as e:
        print(f"!! Errore durante la richiesta di suggerimento: {e}")
        return None

def apply_refinement_to_lore(lore_text, suggestion):
    """Usa LangChain per riscrivere il lore applicando il suggerimento."""
    print(f"-> Applico la modifica al lore con {MODEL_FOR_LOGIC} via LangChain...")
    
    prompt_template = ChatPromptTemplate.from_template(
        """Riscrivi il seguente documento di lore, incorporando questa modifica: '{suggestion}'.
        Mantieni la formattazione originale con le intestazioni '== ... =='.
        Non aggiungere commenti o testo extra, solo il lore aggiornato.

        LORE ORIGINALE:
        {lore}"""
    )
    llm = ChatOllama(model=MODEL_FOR_LOGIC)
    chain = prompt_template | llm | StrOutputParser()
    
    try:
        new_lore = chain.invoke({"lore": lore_text, "suggestion": suggestion})
        with open(LORE_FILE, 'w') as f:
            f.write(new_lore)
        print("-> File di lore aggiornato.")
    except Exception as e:
        print(f"!! Errore durante l'aggiornamento del lore: {e}")

def generate_html_game():
    """Usa LangChain per generare il gioco HTML interattivo."""
    print("\n--- AVVIO FASE 2: Generazione Gioco HTML con LangChain ---")
    
    with open(LORE_FILE, 'r') as f: lore_final = f.read()
    with open(DOMAIN_PDDL_FILE, 'r') as f: domain_pddl = f.read()
    with open(PROBLEM_PDDL_FILE, 'r') as f: problem_pddl = f.read()
    
    prompt_template = ChatPromptTemplate.from_template(
        """Sei un esperto sviluppatore front-end. Genera una singola pagina HTML5 autonoma
        con CSS e JavaScript interni.
        Questa pagina deve essere un gioco narrativo interattivo basato sui seguenti dati.
        - Usa il LORE per i testi descrittivi.
        - Usa il PDDL per la logica di gioco in JavaScript. Il JS deve tracciare lo stato del gioco.
        - Il gioco deve essere stilisticamente piacevole, con un tema fantasy.

        LORE: {lore}
        DOMAIN PDDL: {domain}
        PROBLEM PDDL: {problem}"""
    )
    llm = ChatOllama(model=MODEL_FOR_CODE, temperature=0.5)
    chain = prompt_template | llm | StrOutputParser()

    try:
        print(f"-> Contatto Ollama ({MODEL_FOR_CODE}) per generare l'HTML...")
        html_content = chain.invoke({
            "lore": lore_final,
            "domain": domain_pddl,
            "problem": problem_pddl
        })
        
        if html_content.startswith("```html"):
            html_content = html_content[7:-4].strip()

        with open('storia_interattiva.html', 'w') as f:
            f.write(html_content)
        
        print("✅ FASE 2 COMPLETATA: 'storia_interattiva.html' generato!")
        return True
    except Exception as e:
        print(f"!! Errore durante la generazione dell'HTML: {e}")
        return False

# --- 3. WORKFLOW PRINCIPALE (logica invariata, ma chiama le nuove funzioni) ---

def validate_pddl():
    """Funzione di validazione (invariata)."""
    if not os.path.exists(FAST_DOWNWARD_PATH):
        print(f"!! Errore: Planner non trovato in '{FAST_DOWNWARD_PATH}'.")
        return False
    print("-> Avvio validazione con Fast Downward...")
    command = ['python3', FAST_DOWNWARD_PATH, DOMAIN_PDDL_FILE, PROBLEM_PDDL_FILE, '--search', 'astar(lmcut())']
    result = subprocess.run(command, capture_output=True, text=True)
    if "Solution found." in result.stdout:
        print("✅ Validazione PDDL riuscita: soluzione trovata!")
        return True
    else:
        print("❌ Validazione PDDL fallita: nessuna soluzione trovata.")
        print(f"Output del planner:\n{result.stdout}\n{result.stderr}")
        return False

def run_phase_1():
    """Esegue l'intero workflow della Fase 1 usando le funzioni LangChain."""
    max_attempts = 5
    for attempt in range(max_attempts):
        print(f"\n--- TENTATIVO {attempt + 1}/{max_attempts} ---")
        with open(LORE_FILE, 'r') as f:
            current_lore = f.read()
        if not generate_pddl_from_lore(current_lore):
            continue
        if validate_pddl():
            print("\n🎉 FASE 1 COMPLETATA: PDDL valido generato e verificato!")
            return True
        
        print("-> Avvio l'agente di riflessione.")
        with open(DOMAIN_PDDL_FILE, 'r') as f: domain_content = f.read()
        with open(PROBLEM_PDDL_FILE, 'r') as f: problem_content = f.read()

        suggestion = get_refinement_suggestion(current_lore, domain_content, problem_content)
        if not suggestion:
            continue

        print("\n🤔 SUGGERIMENTO DALL'IA:")
        print(suggestion)
        user_choice = input("Vuoi applicare questa modifica? (s/n): ").lower()
        if user_choice == 's':
            apply_refinement_to_lore(current_lore, suggestion)
        else:
            print("Modifica rifiutata. Interruzione del processo.")
            return False
            
    print("\n!! Raggiunto il numero massimo di tentativi.")
    return False

if __name__ == '__main__':
    if run_phase_1():
        generate_html_game()
    else:
        print("\nProcesso interrotto. Impossibile generare il gioco.")