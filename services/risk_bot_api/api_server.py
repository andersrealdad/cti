import os
import json
import psycopg2
from flask import Flask, request, jsonify
from openai import OpenAI 

# Initialisering av Flask
app = Flask(__name__)

# --- LLM KLIENT INITIALISERING ---

# 1. Initialisering av OpenAI klient (Brukes for RAG, kontekstforklaring, og formatering/fallback)
try:
    openai_client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
except Exception as e:
    print(f"Advarsel: Kunne ikke initialisere OpenAI-klient. Feil: {e}")
    openai_client = None

# 2. Initialisering av Llama-klient (Brukes for kjernevirksomheten /analyze)
try:
    llama_client = OpenAI(
        api_key="sk-local-llama", # Irrelevant for lokal hosting, men må settes
        base_url="http://llama-service:8000/v1" # Endepunktet til vLLM/Llama-tjenesten i Podman
    )
    print("Suksess: Llama-klient initialisert mot http://llama-service:8000/v1")
except Exception as e:
    print(f"Advarsel: Kunne ikke initialisere Llama-klient. Sjekk at llama-service kjører. Feil: {e}")
    llama_client = None

# --- DATABASE HJELPEFUNKSJONER ---

def get_db_connection():
    """ Hjelpefunksjon for å koble til PostgreSQL (Database: empire) """
    try:
        conn = psycopg2.connect(
            host=os.environ.get("POSTGRES_HOST", "postgres"),
            database=os.environ.get("POSTGRES_DB", "empire"),
            user=os.environ.get("POSTGRES_USER", "user"),
            password=os.environ.get("POSTGRES_PASSWORD", "password")
        )
        return conn
    except Exception as e:
        print(f"Feil ved tilkobling til database: {e}")
        return None

# ===============================================
# --- 1. FINANSIELL FUNKSJONER (KLIENT/BUFFETT-AI) ---
# ===============================================

@app.route('/register_key', methods=['POST'])
def register_key():
    """
    Endepunkt for å registrere en ekstern API-nøkkel for en klient/bruker (f.eks. Finnhub).
    """
    data = request.get_json()
    user_id = data.get('user_id')
    api_key = data.get('api_key')

    if not user_id or not api_key:
        return jsonify({"status": "error", "message": "Mangler user_id eller api_key"}), 400

    conn = get_db_connection()
    if conn is None:
        return jsonify({"status": "error", "message": "Kunne ikke koble til DB"}), 503

    try:
        with conn.cursor() as cur:
            # Sikker lagring av API-nøkkelen i user_api_keys tabellen
            cur.execute("""
                INSERT INTO user_api_keys (user_id, api_key)
                VALUES (%s, %s)
                ON CONFLICT (user_id) DO UPDATE SET api_key = EXCLUDED.api_key;
            """, (user_id, api_key))
            conn.commit()
        return jsonify({"status": "success", "message": f"API-nøkkel registrert for bruker {user_id}"}), 200
    except Exception as e:
        conn.rollback()
        return jsonify({"status": "error", "details": str(e)}), 500
    finally:
        conn.close()

@app.route('/analyze', methods=['POST'])
def analyze_risk():
    """
    Henter API-nøkkel fra DB og kjører finansiell analyse ved hjelp av LLAMA/GPT.
    Dette er kjernevirksomheten (Buffett-AI).
    """
    if llama_client is None and openai_client is None:
        return jsonify({"status": "error", "message": "Ingen LLM-klient er tilgjengelig"}), 503

    data = request.get_json()
    ticker = data.get('ticker')
    user_id = data.get('user_id')

    if not ticker or not user_id:
        return jsonify({"status": "error", "message": "Mangler ticker eller user_id"}), 400

    conn = get_db_connection()
    if conn is None:
        return jsonify({"status": "error", "message": "Kunne ikke koble til DB"}), 503

    # Hent ekstern API-nøkkel fra DB for å hente rådata
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT api_key FROM user_api_keys WHERE user_id = %s;", (user_id,))
            result = cur.fetchone()
            external_api_key = result[0] if result else None
    except Exception as e:
        return jsonify({"status": "error", "message": f"Feil ved henting av API-nøkkel: {e}"}), 500
    finally:
        # Lukk kun hvis vi er ferdige med DB her
        if 'analysis' not in locals(): 
            conn.close()

    if not external_api_key:
        return jsonify({"status": "error", "message": "API-nøkkel ikke funnet for denne brukeren"}), 404

    # --- STEG 1: Hent RÅDATA (SIMULERT) ---
    # *Ekte logikk for å kalle ekstern Finnhub/annen kilde via external_api_key går her*
    financial_summary = f"Rådata for {ticker}: EPS var 5.20, P/E er 30.5. Selskapet har et sterkt nettverkseffekt-fortrinn (moat)."
    
    # --- STEG 2: KJØR LLM-ANALYSE (BRUK LLAMA/FALLBACK) ---
    client_to_use = llama_client if llama_client else openai_client
    model_to_use = "finetuned-llama-model" if llama_client else "gpt-4o" 

    system_prompt = f"""
    Du er Warren Buffett-inspirert analytiker spesialisert i å identifisere og vurdere 'moats' (konkurransefortrinn).
    Analyser følgende rådata for {ticker} og vurder:
    1. Selskapets viktigste moat.
    2. En tillitsscore (1-10) for moatens holdbarhet.
    3. En advarsel/risiko basert på dataen.
    """
    
    try:
        response = client_to_use.chat.completions.create(
            model=model_to_use, 
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Analyser følgende data: {financial_summary}"}
            ]
        )
        
        analysis = response.choices[0].message.content
        return jsonify({
            "status": "success",
            "model_used": model_to_use,
            "analysis": analysis,
            "ticker": ticker # Viktig for neste steg /generate_report
        }), 200

    except Exception as e:
        return jsonify({"status": "error", "details": f"LLM-kall feilet: {e}"}), 500

@app.route('/generate_report', methods=['POST'])
def generate_report():
    """
    Tar imot en ferdig AI-analyse og formaterer den til et Markdown-manus 
    for en presentasjon (Slides/Rapport).
    """
    if openai_client is None:
        return jsonify({"status": "error", "message": "OpenAI klient er ikke tilgjengelig for formatering"}), 503

    data = request.get_json()
    analysis_text = data.get('analysis_text')
    ticker = data.get('ticker', 'Generell Analyse')

    if not analysis_text:
        return jsonify({"status": "error", "message": "Mangler analysis_text i forespørselen"}), 400

    # Bruker en sterk GPT-modell for presis formatering
    system_prompt = f"""
    Du er en profesjonell rapportskriver. TONEN skal være formell, men tillitsvekkende. 
    Formater den vedlagte finansielle analysen for {ticker} til et presentasjonsmanus i rent Markdown-format.

    Bruk følgende struktur (minst 4 slides) for enkel konvertering til lysbilder:
    # SLIDE 1: Tittel og Ticker
    # SLIDE 2: Problemet (Risiko-analysen)
    # SLIDE 3: Hedge/Løsning (Anbefalt Handling)
    # SLIDE 4: Konklusjon og Overbevisning
    """

    try:
        response = openai_client.chat.completions.create(
            model="gpt-4o", 
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Formater følgende analyse: {analysis_text}"}
            ]
        )
        
        markdown_report = response.choices[0].message.content
        return jsonify({
            "status": "success",
            "markdown_report": markdown_report
        }), 200

    except Exception as e:
        return jsonify({"status": "error", "details": str(e)}), 500

# =============================================
# --- 2. KONTEKST MENTOR FUNKSJON (DATTER) ---
# =============================================

@app.route('/store_context', methods=['POST'])
def store_user_context():
    """
    Lagrer brukerens tekst og genererer en vektor (embedding) for RAG.
    Brukes for å bygge den personlige AI-hjernen.
    """
    if openai_client is None:
        return jsonify({"status": "error", "message": "OpenAI klient er ikke tilgjengelig"}), 503
        
    data = request.get_json()
    user_id = data.get('user_id')
    text = data.get('text')
    
    if not user_id or not text:
        return jsonify({"status": "error", "message": "Mangler user_id eller tekst"}), 400

    conn = get_db_connection()
    if conn is None:
        return jsonify({"status": "error", "message": "Kunne ikke koble til DB"}), 503

    try:
        # Steg 1: Generer embedding
        embedding_response = openai_client.embeddings.create(
            model="text-embedding-ada-002",
            input=text
        )
        embedding_vector = embedding_response.data[0].embedding
        
        # Steg 2: Sett inn i databasen
        with conn.cursor() as cur:
            # Konverter Python-listen til Postgres' vector-format
            vector_str = "[" + ",".join(map(str, embedding_vector)) + "]"
            
            cur.execute("""
                INSERT INTO user_contexts (user_id, original_text, embedding)
                VALUES (%s, %s, %s);
            """, (user_id, text, vector_str))
            conn.commit()
        
        return jsonify({"status": "success", "message": "Kontekst lagret og vektorisert."}), 200
    except Exception as e:
        conn.rollback()
        return jsonify({"status": "error", "details": str(e)}), 500
    finally:
        conn.close()

@app.route('/explain_context', methods=['POST'])
def explain_context():
    """
    Henter personlig kontekst (RAG) og bruker LLM til å forklare/veilede (Sosial Coach).
    """
    if openai_client is None:
        return jsonify({"status": "error", "message": "OpenAI klient er ikke tilgjengelig"}), 503

    data = request.get_json()
    #user_id = data.get('user_id') # Brukes for RAG-søk (ikke implementert her, men klart for det)
    text_to_explain = data.get('text')
    
    # Simuler RAG-kontekst hentet fra user_contexts tabellen...
    
    # Dette er den magiske delen: system prompt for AI
    system_prompt = f"""
    Du er en personlig, støttende sosial coach for en tenåring. 
    Din oppgave er å forklare situasjonen/teksten, gi tre alternative MÅTER å reagere på (uten å gi et ferdig svar), og forklare den voksne/sosiale konteksten.
    Hold tonen lett, ikke-dømmende, og fokuser på å bygge brukerens selvtillit (Lommelykt-prinsippet).
    """
    
    try:
        response = openai_client.chat.completions.create(
            model="gpt-4o", 
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Vennligst forklar dette og gi handlingsforslag: '{text_to_explain}'"}
            ]
        )
        
        explanation = response.choices[0].message.content
        return jsonify({
            "status": "success",
            "explanation": explanation
        }), 200

    except Exception as e:
        return jsonify({"status": "error", "details": str(e)}), 500

# ===============================================
# --- 3. FINETUNING DATASAMLING (MASTER FILE) ---
# ===============================================

@app.route('/store_moat_data', methods=['POST'])
def store_moat_data():
    """
    Tar imot strukturert og godkjent data (Master File) fra n8n/Human-in-the-loop.
    Dataen lagres i moat_datasets for Llama finetuning.
    """
    data = request.get_json()

    # Sjekk at dataen inneholder de fire nødvendige feltene
    required_fields = ['ticker', 'moat_type', 'moat_description', 'confidence_score']
    if not all(field in data for field in required_fields):
        return jsonify({"status": "error", "message": "Mangler nødvendige felt: ticker, moat_type, moat_description, confidence_score"}), 400

    ticker = data['ticker']
    moat_type = data['moat_type']
    moat_description = data['moat_description']
    try:
        confidence_score = float(data['confidence_score'])
    except ValueError:
        return jsonify({"status": "error", "message": "confidence_score må være et gyldig tall."}), 400

    conn = get_db_connection()
    if conn is None:
        return jsonify({"status": "error", "message": "Kunne ikke koble til DB"}), 503

    try:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO moat_datasets (ticker, moat_type, moat_description, confidence_score)
                VALUES (%s, %s, %s, %s);
            """, (ticker, moat_type, moat_description, confidence_score))
            conn.commit()

        return jsonify({
            "status": "success", 
            "message": f"Moat data for {ticker} lagret i finetuning dataset (Master File)."
        }), 200

    except Exception as e:
        conn.rollback()
        return jsonify({"status": "error", "details": str(e)}), 500
    finally:
        conn.close()


if __name__ == '__main__':
    # Kjør serveren, standard port 8080 (se docker-compose.yml)
    app.run(debug=True, host='0.0.0.0', port=8080)
