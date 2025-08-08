# test_app.py
import unittest
from app import parse_google_results

# Ukázkové HTML, které přesně simuluje strukturu ze screenshotu.
FAKE_GOOGLE_HTML = """
<html><body>
    <!-- Validní výsledek 1 -->
    <a class="zReHs" href="https://www.example.com/prvni-vysledek">
        <h3 class="LC20lb MBeuO DKV0Md">Toto je první titulek</h3>
    </a>
    
    <!-- Validní výsledek 2 -->
    <a class="zReHs" href="http://www.example.org/druhy-vysledek">
        <h3 class="LC20lb MBeuO DKV0Md">Toto je druhý titulek</h3>
    </a>

    <!-- Nevalidní: špatná třída u H3 -->
    <a class="zReHs" href="http://www.example.com/spatne-h3">
        <h3 class="jina-trida">Špatný titulek</h3>
    </a>

    <!-- Nevalidní: špatná třída u A -->
    <a class="jina-trida" href="http://www.example.com/spatne-a">
        <h3 class="LC20lb MBeuO DKV0Md">Další špatný titulek</h3>
    </a>

    <!-- Duplicitní URL -->
    <a class="zReHs" href="https://www.example.com/prvni-vysledek">
        <h3 class="LC20lb MBeuO DKV0Md">Toto je duplicitní titulek</h3>
    </a>

    <!-- Nevalidní: relativní URL -->
    <a class="zReHs" href="/relativni-odkaz">
        <h3 class="LC20lb MBeuO DKV0Md">Relativní odkaz</h3>
    </a>

    <!-- Nevalidní: chybí href -->
    <a class="zReHs">
        <h3 class="LC20lb MBeuO DKV0Md">Odkaz bez href</h3>
    </a>
</body></html>
"""

class TestParser(unittest.TestCase):

    def test_parse_results_with_specific_classes(self):
        """Testuje parsování s vysoce specifickými třídami."""
        results = parse_google_results(FAKE_GOOGLE_HTML)
        self.assertEqual(len(results), 2)
        self.assertEqual(results[0]['title'], "Toto je první titulek")
        self.assertEqual(results[0]['url'], "https://www.example.com/prvni-vysledek")
        self.assertEqual(results[1]['title'], "Toto je druhý titulek")
        self.assertEqual(results[1]['url'], "http://www.example.org/druhy-vysledek")

    def test_parse_empty_html(self):
        """Testuje chování funkce při prázdném HTML vstupu."""
        results = parse_google_results("<html><body></body></html>")
        self.assertEqual(len(results), 0)

    def test_duplicate_and_invalid_urls_are_ignored(self):
        """
        Testuje, že duplicitní, relativní a chybějící URL jsou správně ignorovány.
        FAKE_GOOGLE_HTML obsahuje tyto případy.
        """
        results = parse_google_results(FAKE_GOOGLE_HTML)
        self.assertEqual(len(results), 2, "Měly by být nalezeny pouze 2 unikátní a validní výsledky.")

if __name__ == '__main__':
    unittest.main(verbosity=2)
