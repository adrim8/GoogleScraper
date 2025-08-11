# app.py
import os
import requests
from flask import Flask, render_template, request, jsonify

# --- Konfigurace ---
# Inicializace Flask aplikace
app = Flask(__name__)

# API klíč pro Serper.dev
SERPER_API_KEY = 'caf2c44fe2d73d78070f15b24d8c9e3513c51414' 
SERPER_API_URL = "https://google.serper.dev/search"

# --- Routy aplikace ---
@app.route('/')
def index():
    """Zobrazí hlavní HTML stránku."""
    return render_template('index.html')

@app.route('/api/search')
def search_api():
    """
    API endpoint, který zavolá Serper API a vrátí strukturované výsledky.
    Nahrazuje původní komplexní Selenium logiku.
    """
    # 1. Získání vyhledávacího dotazu z URL (např. /api/search?q=dotaz)
    query = request.args.get('q', '')
    if not query:
        return jsonify({"error": "Chybí vyhledávací dotaz 'q'."}), 400
    
    # 2. Příprava dat pro odeslání na Serper API
    payload = {
        "q": query,
        "gl": "cz",
        "hl": "cs" 
    }
    headers = {
        'X-API-KEY': SERPER_API_KEY,
        'Content-Type': 'application/json'
    }

    # 3. Odeslání požadavku na API a zpracování odpovědi
    try:
        response = requests.post(SERPER_API_URL, headers=headers, json=payload)
        response.raise_for_status()

        api_data = response.json()
        
        # 4. Zpracování výsledků do požadovaného formátu
        results = []
        for item in api_data.get('organic', []):
            results.append({
                'title': item.get('title'),
                'url': item.get('link') 
            })
        
        return jsonify(results)

    except requests.exceptions.RequestException as e:
        return jsonify({"error": f"Došlo k chybě při komunikaci s API: {e}"}), 500
    except Exception as e:
        return jsonify({"error": f"Nastala neočekávaná chyba: {e}"}), 500

# --- Spuštění aplikace ---
if __name__ == '__main__':
    # Použijte port z proměnné prostředí, což je best practice pro hosting
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=True, host='0.0.0.0', port=port)
