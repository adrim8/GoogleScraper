# test_app.py
import unittest
import json
from unittest.mock import patch, MagicMock
import requests

# Importujeme 'app' z tvého souboru app.py
from app import app

class AppTestCase(unittest.TestCase):
    
    def setUp(self):
        """Tato metoda se spustí před každým testem."""
        app.config['TESTING'] = True
        self.client = app.test_client()

    @patch('app.requests.post') # Nahradíme 'requests.post' v modulu 'app' naším dvojníkem
    def test_search_success(self, mock_post):
        """Testuje úspěšné vyhledávání."""
        # 1. Připravíme si falešnou odpověď od API
        fake_api_response = {
            "organic": [
                {
                    "title": "Test Title 1",
                    "link": "http://example.com/1",
                    "snippet": "Description 1"
                },
                {
                    "title": "Test Title 2",
                    "link": "http://example.com/2",
                    "snippet": "Description 2"
                }
            ]
        }
        
        # 2. Nastavíme našeho "dvojníka" (mock), aby vrátil tuto odpověď
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = fake_api_response
        mock_response.raise_for_status.return_value = None 
        mock_post.return_value = mock_response

        # 3. Zavoláme náš endpoint
        response = self.client.get('/api/search?q=testovaci dotaz')
        
        # 4. Ověříme výsledky
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        
        # Zkontrolujeme, zda výstup odpovídá našemu očekávanému formátu
        expected_data = [
            {'title': 'Test Title 1', 'url': 'http://example.com/1'},
            {'title': 'Test Title 2', 'url': 'http://example.com/2'}
        ]
        self.assertEqual(data, expected_data)

        # Ověříme, že náš "dvojník" byl zavolán přesně jednou
        mock_post.assert_called_once()

    def test_search_missing_query(self):
        """Testuje, co se stane, když chybí parametr 'q'."""
        response = self.client.get('/api/search')
        
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertIn('error', data)
        self.assertEqual(data['error'], "Chybí vyhledávací dotaz 'q'.")

    @patch('app.requests.post')
    def test_search_api_error(self, mock_post):
        """Testuje, co se stane, když externí API vrátí chybu."""
        # Nastavíme "dvojníka", aby při zavolání vyhodil výjimku
        mock_post.side_effect = requests.exceptions.RequestException("API je nedostupné")
        
        response = self.client.get('/api/search?q=nejaky dotaz')
        
        self.assertEqual(response.status_code, 500)
        data = json.loads(response.data)
        self.assertIn('error', data)
        self.assertIn("Došlo k chybě při komunikaci s API", data['error'])