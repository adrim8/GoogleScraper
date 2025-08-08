# app.py
import requests
from flask import Flask, render_template, request, jsonify
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

# Inicializace Flask aplikace
app = Flask(__name__)

@app.route('/')
def index():
    """Zobrazí hlavní HTML stránku."""
    return render_template('index.html')

@app.route('/api/search')
def search_api():
    """
    API endpoint, který použije Selenium k načtení stránky a vrátí výsledky.
    """
    query = request.args.get('q', '')
    if not query:
        return jsonify({"error": "Chybí vyhledávací dotaz 'q'."}), 400
    
    search_url = f"https://www.google.com/search?q={query.replace(' ', '+')}&hl=cs"

    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)

    driver = None
    try:
        service = ChromeService(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        
        driver.get(search_url)

        # Zpracování cookie souhlasu
        try:
            consent_button = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Přijmout vše')] | //button[contains(., 'Accept all')]"))
            )
            consent_button.click()
            time.sleep(0.5)
        except Exception:
            print("Cookie consent button not found or not needed, continuing.")
            pass

        # Čekání na načtení výsledků (hledáme alespoň jeden prvek, který nás zajímá)
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "a.zReHs h3.LC20lb.MBeuO.DKV0Md"))
        )
        
        html_content = driver.page_source
        
        data = parse_google_results(html_content)
        return jsonify(data)

    except Exception as e:
        return jsonify({"error": f"Došlo k chybě při běhu Selenium: {e}"}), 500
    finally:
        if driver:
            driver.quit()

def parse_google_results(html_content: str) -> list[dict]:
    """
    Zpracuje stažený HTML kód ze stránky Google a extrahuje přirozené výsledky.
    Tato verze je upravena tak, aby hledala <a> s třídou 'zReHs' a v něm <h3> s přesnými třídami.
    """
    soup = BeautifulSoup(html_content, 'html.parser')
    results = []
    seen_urls = set()

    # Cílíme na <a> tagy, které mají třídu 'zReHs'.
    for link_tag in soup.find_all('a', class_='zReHs'):
        # Uvnitř tohoto odkazu hledáme H3 se specifickými třídami.
        h3_tag = link_tag.select_one('h3.LC20lb.MBeuO.DKV0Md')
        
        if h3_tag:
            url = link_tag.get('href')
            title = h3_tag.get_text(strip=True)
            
            # Kontrola platnosti a duplicity
            if url and url.startswith('http') and url not in seen_urls:
                results.append({'title': title, 'url': url})
                seen_urls.add(url)

    return results

if __name__ == '__main__':
    app.run(debug=True)
