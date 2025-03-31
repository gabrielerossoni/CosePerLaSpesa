#!/usr/bin/env python3
"""
Test script for OpenAI API.
"""

import os
import sys
import json
import requests

def test_openai_api():
    """Test if the OpenAI API is working."""
    # Get the API key
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        print("ERRORE: Chiave API di OpenAI non trovata nelle variabili d'ambiente!")
        return False
    
    # The endpoint for OpenAI API
    api_url = "https://api.openai.com/v1/chat/completions"
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    
    data = {
        "model": "gpt-3.5-turbo",  # Utilizziamo un modello meno costoso per il test
        "messages": [
            {"role": "system", "content": "Sei un assistente di test."},
            {"role": "user", "content": "Rispondi solo con 'OK' se ricevi questo messaggio."}
        ],
        "temperature": 0.7,
        "max_tokens": 20  # Riduciamo i token per minimizzare il costo
    }
    
    try:
        response = requests.post(api_url, headers=headers, json=data)
        
        if response.status_code != 200:
            print(f"ERRORE: La chiamata API ha restituito lo stato {response.status_code}")
            print(f"Risposta dettagliata: {response.text}")
            
            # Analizziamo l'errore per fornire maggiori dettagli
            try:
                error_json = json.loads(response.text)
                
                # Verifichiamo il tipo di errore
                if response.status_code == 429:
                    if "quota" in response.text.lower():
                        print("\nERRORE DI QUOTA: La chiave API ha raggiunto il limite di utilizzo.")
                        print("Soluzione: Attendere che la quota si rinnovi o utilizzare una nuova chiave API.")
                    else:
                        print("\nERRORE DI LIMITE FREQUENZA: Troppe richieste in poco tempo.")
                        print("Soluzione: Attendere qualche minuto e riprovare.")
                elif response.status_code == 401:
                    print("\nERRORE DI AUTENTICAZIONE: La chiave API non è valida o è scaduta.")
                    print("Soluzione: Verificare che la chiave API sia corretta.")
            except json.JSONDecodeError:
                pass  # Non è possibile analizzare la risposta come JSON
            
            return False
        
        response_data = response.json()
        message = response_data["choices"][0]["message"]["content"]
        
        print(f"RISPOSTA API OPENAI: {message}")
        return True
    except Exception as e:
        print(f"ERRORE durante la chiamata API: {e}")
        return False

if __name__ == "__main__":
    print("Iniziando il test dell'API OpenAI...")
    success = test_openai_api()
    
    if success:
        print("TEST SUPERATO: La comunicazione con l'API OpenAI funziona!")
        sys.exit(0)
    else:
        print("TEST FALLITO: C'è un problema nella comunicazione con l'API OpenAI!")
        sys.exit(1)