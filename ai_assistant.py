import os
import json
import aiohttp
import asyncio
import logging

logger = logging.getLogger(__name__)

class AIAssistant:
    """Class to provide AI assistance for shopping lists using OpenAI."""
    
    def __init__(self):
        """Initialize the AI assistant."""
        self.api_key = os.environ.get("OPENAI_API_KEY")
        if not self.api_key:
            logger.warning("OPENAI_API_KEY environment variable not set!")
        
        # The endpoint for OpenAI API
        self.api_url = "https://api.openai.com/v1/chat/completions"
    
    async def _get_openai_response(self, messages):
        """
        Get a response from OpenAI API.
        
        Args:
            messages: List of message dictionaries to send to the API
            
        Returns:
            The response content from OpenAI or a fallback response if API is unavailable
        """
        if not self.api_key:
            return "L'assistente AI non è disponibile al momento. Controlla la chiave API."
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        
        data = {
            "model": "gpt-4o",  # the newest OpenAI model is "gpt-4o" which was released May 13, 2024. do not change this unless explicitly requested by the user
            "messages": messages,
            "temperature": 0.7,
            "max_tokens": 600
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(self.api_url, headers=headers, json=data) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        logger.error(f"OpenAI API error: {response.status} - {error_text}")
                        
                        # Check for quota exceeded error (code 429)
                        if response.status == 429 and "quota" in error_text.lower():
                            logger.warning("OpenAI API quota exceeded, using fallback response")
                            return self._get_fallback_response(messages)
                        
                        return "Mi dispiace, c'è stato un errore nel contattare l'assistente AI. Riprova più tardi."
                    
                    response_data = await response.json()
                    return response_data["choices"][0]["message"]["content"]
        except Exception as e:
            logger.error(f"Error calling OpenAI API: {e}")
            return "Mi dispiace, c'è stato un errore nel contattare l'assistente AI. Riprova più tardi."
    
    def _get_fallback_response(self, messages):
        """
        Provide a fallback response when the OpenAI API is unavailable.
        
        Args:
            messages: The messages that would have been sent to the API
            
        Returns:
            A simple fallback response
        """
        # Check the system message to determine what type of request this is
        system_content = ""
        user_content = ""
        for msg in messages:
            if msg["role"] == "system":
                system_content = msg["content"].lower()
            elif msg["role"] == "user":
                user_content = msg["content"]
        
        # Generate appropriate fallback responses based on the request type
        if "suggerire" in system_content or "suggeri" in system_content:
            return """🍎 Frutta di stagione - Completa la tua lista con prodotti freschi
🧀 Formaggio - Un buon complemento per i tuoi pasti
🍞 Pane fresco - Un alimento base per ogni dispensa
🥛 Latte o alternative vegetali - Per colazione o ricette
🧂 Spezie ed erbe - Per arricchire i sapori dei tuoi piatti

⚠️ Nota: L'assistente AI è temporaneamente limitato. Le funzionalità complete torneranno presto."""
            
        elif "categor" in system_content:
            return """🍅 Frutta e Verdura:
- Frutta di stagione
- Verdure fresche

🥩 Proteine:
- Carne
- Pesce
- Legumi

🧀 Latticini:
- Latte
- Formaggi
- Yogurt

🍝 Dispensa:
- Pasta
- Riso
- Cereali

⚠️ Nota: L'assistente AI è temporaneamente limitato. Le funzionalità complete torneranno presto."""
            
        elif "pasti" in system_content or "cucina" in system_content and "piano" in system_content:
            return """📅 Piano dei pasti semplificato:

🌅 Colazione:
- Cereali con latte/yogurt e frutta
- Pane tostato con marmellata o miele

🕛 Pranzo:
- Pasta con verdure
- Insalata mista con proteine

🌙 Cena:
- Proteine (carne/pesce/legumi) con contorno
- Zuppa con pane

⚠️ Nota: L'assistente AI è temporaneamente limitato. Le funzionalità complete torneranno presto."""
            
        else:
            return """Mi dispiace, l'assistente AI è temporaneamente limitato per motivi tecnici. Le funzionalità complete torneranno presto.

Nel frattempo, ecco alcuni consigli generali:
- Organizza la tua lista per categorie (frutta, verdura, carne, ecc.)
- Controlla cosa hai già in dispensa prima di fare la spesa
- Pianifica i pasti della settimana per evitare sprechi
- Considera prodotti di stagione per qualità e convenienza

⚠️ L'assistente tornerà completamente operativo al più presto."""
    
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
