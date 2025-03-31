import os
import json
import aiohttp
import asyncio
import logging
from ai_fallback import LocalAI

logger = logging.getLogger(__name__)

class AIAssistant:
    """Class to provide AI assistance for shopping lists using OpenAI or local fallback."""
    
    def __init__(self):
        """Initialize the AI assistant."""
        self.api_key = os.environ.get("OPENAI_API_KEY")
        if not self.api_key:
            logger.warning("OPENAI_API_KEY environment variable not set!")
        
        # The endpoint for OpenAI API
        self.api_url = "https://api.openai.com/v1/chat/completions"
        
        # Initialize the local AI fallback
        self.local_ai = LocalAI()
    
    async def _get_openai_response(self, messages):
        """
        Get a response from OpenAI API.
        
        Args:
            messages: List of message dictionaries to send to the API
            
        Returns:
            The response content from OpenAI or a fallback response if API is unavailable
        """
        if not self.api_key:
            logger.error("API key is not set!")
            return "L'assistente AI non è disponibile al momento. Controlla la chiave API."
        
        logger.info(f"OpenAI API key present, length: {len(self.api_key)}")
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        
        # Prima proviamo con gpt-4o
        primary_model = "gpt-4o"  # the newest OpenAI model is "gpt-4o" which was released May 13, 2024.
        
        data = {
            "model": primary_model,
            "messages": messages,
            "temperature": 0.7,
            "max_tokens": 600
        }
        
        logger.info(f"Sending request to OpenAI API with model {primary_model}")
        
        try:
            async with aiohttp.ClientSession() as session:
                logger.info(f"Calling OpenAI API at URL: {self.api_url}")
                async with session.post(self.api_url, headers=headers, json=data) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        logger.error(f"OpenAI API error: {response.status} - {error_text}")
                        
                        # Check for quota exceeded error (code 429)
                        if response.status == 429 and "quota" in error_text.lower():
                            logger.warning(f"Quota exceeded for {primary_model}, trying fallback model gpt-3.5-turbo")
                            
                            # Prova con un modello di fallback (gpt-3.5-turbo) che costa meno
                            fallback_model = "gpt-3.5-turbo"
                            fallback_data = {
                                "model": fallback_model,
                                "messages": messages,
                                "temperature": 0.7,
                                "max_tokens": 300  # Ridotto per contenere i costi
                            }
                            
                            try:
                                async with session.post(self.api_url, headers=headers, json=fallback_data) as fallback_response:
                                    if fallback_response.status == 200:
                                        logger.info(f"Successfully used fallback model {fallback_model}")
                                        fallback_response_data = await fallback_response.json()
                                        content = fallback_response_data["choices"][0]["message"]["content"]
                                        return content + f"\n\n⚠️ Nota: Utilizzato modello {fallback_model} invece di {primary_model} per motivi di quota."
                                    else:
                                        # Anche il modello di fallback ha fallito
                                        fallback_error_text = await fallback_response.text()
                                        logger.error(f"Fallback model also failed: {fallback_response.status} - {fallback_error_text}")
                            except Exception as e:
                                logger.error(f"Error with fallback model: {e}")
                            
                            # Se anche il modello di fallback fallisce, usa il sistema di AI locale
                            logger.warning("Using LocalAI for fallback")
                            return self._get_local_ai_response(messages)
                        
                        # Use local AI for other API errors
                        logger.warning(f"Using LocalAI due to API error: {response.status}")
                        return self._get_local_ai_response(messages)
                    
                    logger.info(f"Received successful response from OpenAI API using {primary_model}")
                    response_data = await response.json()
                    return response_data["choices"][0]["message"]["content"]
        except Exception as e:
            logger.error(f"Error calling OpenAI API: {e}")
            logger.warning("Using LocalAI due to exception")
            return self._get_local_ai_response(messages)
    
    def _get_local_ai_response(self, messages):
        """
        Provide a response using the local AI system when external APIs are unavailable.
        
        Args:
            messages: The messages that would have been sent to the API
            
        Returns:
            A response from the local AI system
        """
        # Estrai il contenuto dei messaggi
        system_content = ""
        user_content = ""
        items = []
        question = ""
        
        # Parse i messaggi per identificare richiesta e contenuto
        for msg in messages:
            if msg["role"] == "system":
                system_content = msg["content"].lower()
            elif msg["role"] == "user":
                user_content = msg["content"]
                
                # Estrai elementi della lista della spesa dal contenuto utente
                if "lista della spesa" in user_content and ":" in user_content:
                    content_parts = user_content.split(":")
                    if len(content_parts) >= 2:
                        items_part = content_parts[1].split(".")[0].strip()
                        items = [item.strip() for item in items_part.split(",")]
                
                # Estrai la domanda se presente
                if "domanda è:" in user_content:
                    question_parts = user_content.split("domanda è:")
                    if len(question_parts) >= 2:
                        question = question_parts[1].strip()
        
        logger.info(f"Using local AI system for response. Type identified from system content: {system_content[:50]}...")
        
        # Richiama la funzione appropriata in base al tipo di richiesta
        if "suggerire" in system_content or "suggeri" in system_content:
            return self.local_ai.get_suggestions(items)
            
        elif "categor" in system_content:
            return self.local_ai.categorize_items(items)
            
        elif ("pasti" in system_content or "cucina" in system_content) and "piano" in system_content:
            return self.local_ai.generate_meal_plan(items)
            
        elif "rispondi" in system_content or "domand" in system_content:
            return self.local_ai.answer_question(items, question)
            
        else:
            # Risposta generica per richieste sconosciute
            return """Benvenuto! Sono il tuo assistente della spesa locale.
            
Posso aiutarti a:
- Organizzare la tua lista per categorie
- Suggerire prodotti correlati
- Creare piani dei pasti
- Rispondere a domande sulla spesa e la cucina

Per utilizzare queste funzioni, seleziona uno dei comandi dal menu del bot.

⚠️ Nota: Questo è un sistema AI locale che funziona senza connessione a internet. Non utilizza OpenAI al momento."""
    
    async def get_suggestions(self, items):
        """
        Get suggestions for additional items based on the current shopping list.
        
        Args:
            items: The current items in the shopping list (list of strings or list of dicts with 'name' and 'quantity')
            
        Returns:
            A string with suggestions
        """
        # Ensure we have a list of strings for proper formatting
        if items and isinstance(items, list):
            if isinstance(items[0], dict) and "name" in items[0]:
                # Format items with quantities for better context
                formatted_items = [f"{item['name']} ({item['quantity']})" for item in items]
            else:
                # Already a list of strings
                formatted_items = items
        else:
            formatted_items = []
            
        item_list = ", ".join(formatted_items)
        
        messages = [
            {"role": "system", "content": "Sei un assistente italiano esperto in spesa e cucina. Devi suggerire 3-5 prodotti correlati basandoti sulla lista della spesa dell'utente. Ogni suggerimento deve essere accompagnato da una breve motivazione e un emoji pertinente. Le risposte devono essere in italiano."},
            {"role": "user", "content": f"Ecco la mia lista della spesa: {item_list}. Cosa altro potrei aggiungere?"}
        ]
        
        return await self._get_openai_response(messages)
    
    async def categorize_items(self, items):
        """
        Categorize the items in the shopping list.
        
        Args:
            items: The current items in the shopping list (list of strings or list of dicts with 'name' and 'quantity')
            
        Returns:
            A string with categorized items
        """
        # Ensure we have a list of strings for proper formatting
        if items and isinstance(items, list):
            if isinstance(items[0], dict) and "name" in items[0]:
                # Format items with quantities for better context
                formatted_items = [f"{item['name']} ({item['quantity']})" for item in items]
            else:
                # Already a list of strings
                formatted_items = items
        else:
            formatted_items = []
        
        item_list = ", ".join(formatted_items)
        
        messages = [
            {"role": "system", "content": "Sei un assistente italiano esperto in spesa. Devi organizzare la lista della spesa dell'utente in categorie logiche (come 'Frutta e Verdura', 'Latticini', 'Carne', ecc). Formula la risposta come un elenco ordinato per categorie, con emoji appropriate per ogni categoria. Le risposte devono essere in italiano."},
            {"role": "user", "content": f"Ecco la mia lista della spesa: {item_list}. Organizzala in categorie per me."}
        ]
        
        return await self._get_openai_response(messages)
    
    async def answer_question(self, items, question):
        """
        Answer questions about the shopping list.
        
        Args:
            items: The current items in the shopping list (list of strings or list of dicts with 'name' and 'quantity')
            question: The user's question
            
        Returns:
            A string with the answer
        """
        # Ensure we have a list of strings for proper formatting
        if items and isinstance(items, list):
            if isinstance(items[0], dict) and "name" in items[0]:
                # Format items with quantities for better context
                formatted_items = [f"{item['name']} ({item['quantity']})" for item in items]
            else:
                # Already a list of strings
                formatted_items = items
        else:
            formatted_items = []
        
        item_list = ", ".join(formatted_items)
        
        messages = [
            {"role": "system", "content": "Sei un assistente italiano esperto in spesa e cucina. Rispondi alle domande dell'utente riguardo la sua lista della spesa. Fornisci informazioni utili, consigli e suggerimenti. Le risposte devono essere dettagliate ma concise, in italiano e con un tono amichevole."},
            {"role": "user", "content": f"La mia lista della spesa contiene: {item_list}. La mia domanda è: {question}"}
        ]
        
        return await self._get_openai_response(messages)
    
    async def generate_meal_plan(self, items):
        """
        Generate a meal plan based on the items in the shopping list.
        
        Args:
            items: The current items in the shopping list (list of strings or list of dicts with 'name' and 'quantity')
            
        Returns:
            A string with the meal plan
        """
        # Ensure we have a list of strings for proper formatting
        if items and isinstance(items, list):
            if isinstance(items[0], dict) and "name" in items[0]:
                # Format items with quantities for better context
                formatted_items = [f"{item['name']} ({item['quantity']})" for item in items]
            else:
                # Already a list of strings
                formatted_items = items
        else:
            formatted_items = []
        
        item_list = ", ".join(formatted_items)
        
        messages = [
            {"role": "system", "content": "Sei un assistente italiano esperto in cucina. Devi creare un piano dei pasti per 3 giorni (colazione, pranzo e cena) utilizzando principalmente gli ingredienti disponibili nella lista della spesa dell'utente. Se necessario, puoi suggerire pochi ingredienti aggiuntivi. Le ricette devono essere semplici ma gustose. Organizza il piano in modo chiaro, con emoji appropriate e brevi descrizioni delle ricette. Le risposte devono essere in italiano."},
            {"role": "user", "content": f"Ecco la mia lista della spesa: {item_list}. Puoi crearmi un piano dei pasti per 3 giorni?"}
        ]
        
        return await self._get_openai_response(messages)
