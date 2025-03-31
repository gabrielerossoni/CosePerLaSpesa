"""
Fallback AI Module
Questo modulo fornisce semplici risposte AI generate direttamente nel codice,
senza dipendere da API esterne come OpenAI.
"""

import random

class LocalAI:
    """Una semplice classe che fornisce risposte AI generate localmente."""
    
    def __init__(self):
        """Inizializza la classe LocalAI."""
        self.product_suggestions = [
            {
                "item": "Frutta di stagione",
                "emoji": "🍎",
                "reason": "Ottima per una alimentazione sana ed equilibrata"
            },
            {
                "item": "Cereali integrali",
                "emoji": "🌾",
                "reason": "Fonte di energia a lento rilascio, ideali per la colazione"
            },
            {
                "item": "Yogurt",
                "emoji": "🥛",
                "reason": "Ricco di probiotici, ottimo per la digestione"
            },
            {
                "item": "Uova",
                "emoji": "🥚",
                "reason": "Fonte completa di proteine, versatili in cucina"
            },
            {
                "item": "Pane integrale",
                "emoji": "🍞",
                "reason": "Base per colazione o pranzo, ricco di fibre"
            },
            {
                "item": "Legumi",
                "emoji": "🌱",
                "reason": "Proteine vegetali, economici e nutrienti"
            },
            {
                "item": "Pesce",
                "emoji": "🐟",
                "reason": "Ricco di omega-3, importante per la salute cardiovascolare"
            },
            {
                "item": "Verdure a foglia verde",
                "emoji": "🥬",
                "reason": "Ricche di vitamine e minerali, poche calorie"
            },
            {
                "item": "Formaggio",
                "emoji": "🧀",
                "reason": "Fonte di calcio e proteine, ottimo come snack"
            },
            {
                "item": "Olio d'oliva",
                "emoji": "🫒",
                "reason": "Grassi sani, base della dieta mediterranea"
            },
            {
                "item": "Frutta secca",
                "emoji": "🌰",
                "reason": "Snack nutriente ricco di grassi sani"
            },
            {
                "item": "Erbe aromatiche",
                "emoji": "🌿",
                "reason": "Per insaporire i piatti senza aggiungere sale"
            },
            {
                "item": "Pomodori",
                "emoji": "🍅",
                "reason": "Versatili, si prestano a molte preparazioni"
            },
            {
                "item": "Aglio",
                "emoji": "🧄",
                "reason": "Insaporitore naturale con proprietà benefiche"
            },
            {
                "item": "Cipolle",
                "emoji": "🧅",
                "reason": "Base per molti piatti, ricche di antiossidanti"
            }
        ]
        
        self.categories = [
            {
                "name": "Frutta e Verdura",
                "emoji": "🍅",
                "items": ["mele", "banane", "arance", "carote", "zucchine", "pomodori", "insalata", "spinaci", 
                          "fragole", "kiwi", "pesche", "melanzane", "broccoli", "patate", "cipolle", "aglio"]
            },
            {
                "name": "Proteine",
                "emoji": "🥩",
                "items": ["carne", "pollo", "pesce", "uova", "tofu", "legumi", "lenticchie", "ceci", 
                          "fagioli", "tacchino", "salmone", "tonno", "maiale", "manzo", "seitan", "tempeh"]
            },
            {
                "name": "Latticini",
                "emoji": "🧀",
                "items": ["latte", "formaggio", "yogurt", "burro", "panna", "mozzarella", "ricotta",
                          "parmigiano", "pecorino", "stracchino", "scamorza", "mascarpone", "kefir"]
            },
            {
                "name": "Pane e Cereali",
                "emoji": "🍞",
                "items": ["pane", "pasta", "riso", "cereali", "farina", "crackers", "grissini", "pizza",
                          "avena", "orzo", "farro", "quinoa", "cous cous", "mais", "muesli"]
            },
            {
                "name": "Dolci e Snack",
                "emoji": "🍪",
                "items": ["biscotti", "cioccolato", "gelato", "caramelle", "torta", "merendine", "patatine",
                          "croissant", "brioche", "marmellata", "miele", "nutella", "wafer", "snack"]
            },
            {
                "name": "Bevande",
                "emoji": "🥤",
                "items": ["acqua", "succo", "tè", "caffè", "vino", "birra", "soda", "limonata", 
                          "aranciata", "cola", "energy drink", "tisana", "smoothie", "spremuta"]
            },
            {
                "name": "Condimenti",
                "emoji": "🧂",
                "items": ["sale", "pepe", "olio", "aceto", "spezie", "erbe", "salsa", "maionese",
                          "ketchup", "senape", "zucchero", "tabasco", "soia", "pesto"]
            },
            {
                "name": "Surgelati",
                "emoji": "❄️",
                "items": ["surgelati", "gelato", "verdure surgelate", "pesce surgelato", "pizza surgelata",
                          "patatine surgelate", "bastoncini", "fruttifera"]
            }
        ]
        
        self.meal_plan_templates = [
            """📅 Piano dei pasti per 3 giorni:

🌅 Giorno 1:
- Colazione: Yogurt con frutta fresca e cereali
- Pranzo: Pasta al pomodoro con insalata mista
- Cena: Petto di pollo alla griglia con verdure saltate

🌅 Giorno 2:
- Colazione: Toast con uova strapazzate
- Pranzo: Insalata di riso con tonno e verdure
- Cena: Pesce al forno con patate

🌅 Giorno 3:
- Colazione: Smoothie di frutta con biscotti integrali
- Pranzo: Panino con formaggio e verdure grigliate
- Cena: Zuppa di legumi con crostini di pane

Buon appetito! 😋""",

            """📅 Piano alimentare personalizzato:

🍳 Giorno 1:
- Colazione: Porridge di avena con frutta secca
- Pranzo: Riso integrale con verdure saltate e uova
- Cena: Minestrone di verdure con crostini

🥗 Giorno 2:
- Colazione: Pancake integrali con miele
- Pranzo: Bowl di quinoa con legumi e verdure
- Cena: Frittata di verdure con insalata mista

🍲 Giorno 3:
- Colazione: Yogurt greco con frutta fresca e muesli
- Pranzo: Wrap con hummus e verdure
- Cena: Risotto con zucchine e formaggio

Consiglio: prepara porzioni extra per avere avanzi per il giorno dopo! 👨‍🍳""",

            """📅 Menù settimanale (primi 3 giorni):

🌞 Giorno 1:
- Colazione: Fette biscottate con marmellata e tè
- Pranzo: Pasta integrale al pesto
- Cena: Merluzzo al vapore con piselli

☀️ Giorno 2:
- Colazione: Yogurt con cereali e miele
- Pranzo: Insalata di farro con pomodorini e mozzarella
- Cena: Frittata di verdure con pane integrale

🌤️ Giorno 3:
- Colazione: Frullato di frutta con biscotti secchi
- Pranzo: Zuppa di lenticchie con crostini
- Cena: Pizza fatta in casa con verdure

Suggerimento: bevi almeno 1,5 litri di acqua al giorno! 💧"""
        ]
        
        self.general_answers = [
            "In base alla tua lista della spesa, ti suggerisco di organizzare i pasti settimanali in anticipo per utilizzare al meglio gli ingredienti.",
            "Gli ingredienti nella tua lista sembrano ottimi per preparare piatti equilibrati. Ricorda di includere sempre proteine, carboidrati e verdure in ogni pasto.",
            "Per risparmiare, controlla sempre cosa hai già in dispensa prima di fare la spesa e approfitta delle offerte stagionali.",
            "Considera di aggiungere più varietà di frutta e verdura alla tua lista per garantire un apporto completo di nutrienti.",
            "Con questi ingredienti potresti preparare diversi piatti in anticipo e congelarli per avere pasti pronti durante la settimana.",
            "Per ridurre gli sprechi, pianifica i pasti in modo da utilizzare gli ingredienti più deperibili per primi.",
            "La tua lista sembra ben bilanciata. Ricorda che una buona regola è riempire metà del piatto con verdure, un quarto con proteine e un quarto con carboidrati.",
            "Prova a sperimentare nuove ricette con gli ingredienti che hai scelto per aggiungere varietà alla tua alimentazione.",
            "Gli alimenti nella tua lista si prestano bene a preparazioni veloci e salutari, perfette per chi ha poco tempo per cucinare.",
            "Ricorda che una buona conservazione degli alimenti è fondamentale per mantenerne la freschezza e ridurre gli sprechi."
        ]
    
    def get_suggestions(self, items):
        """
        Genera suggerimenti per prodotti aggiuntivi.
        
        Args:
            items: Lista di prodotti attualmente nella lista della spesa
            
        Returns:
            Una stringa con suggerimenti per altri prodotti
        """
        # Prendiamo 3-5 suggerimenti casuali dalla lista
        num_suggestions = random.randint(3, 5)
        selected_suggestions = random.sample(self.product_suggestions, num_suggestions)
        
        suggestions_text = ""
        for suggestion in selected_suggestions:
            suggestions_text += f"{suggestion['emoji']} {suggestion['item']} - {suggestion['reason']}\n"
        
        return suggestions_text + "\n⚠️ Nota: Utilizzando il sistema di suggerimenti locale. Sistema AI avanzato non disponibile al momento."
    
    def categorize_items(self, items):
        """
        Categorizza i prodotti nella lista della spesa.
        
        Args:
            items: Lista di prodotti da categorizzare
            
        Returns:
            Una stringa con i prodotti categorizzati
        """
        # Estrai solo i nomi degli articoli se vengono forniti come dizionari
        item_names = []
        if items and isinstance(items, list):
            if isinstance(items[0], dict) and "name" in items[0]:
                item_names = [item["name"].lower() for item in items]
            else:
                item_names = [str(item).lower() for item in items]
        
        # Dizionario per tenere traccia degli articoli assegnati ad ogni categoria
        categorized = {}
        
        # Prova a categorizzare gli articoli in base alla corrispondenza con le categorie predefinite
        for item_name in item_names:
            assigned = False
            for category in self.categories:
                for category_item in category["items"]:
                    if category_item in item_name or item_name in category_item:
                        if category["name"] not in categorized:
                            categorized[category["name"]] = {
                                "emoji": category["emoji"],
                                "items": []
                            }
                        categorized[category["name"]]["items"].append(item_name)
                        assigned = True
                        break
                if assigned:
                    break
            
            # Se l'articolo non è stato assegnato, mettiamolo in "Altro"
            if not assigned:
                if "Altro" not in categorized:
                    categorized["Altro"] = {
                        "emoji": "📦",
                        "items": []
                    }
                categorized["Altro"]["items"].append(item_name)
        
        # Generiamo il testo della risposta
        response = ""
        for category_name, data in categorized.items():
            response += f"{data['emoji']} {category_name}:\n"
            for item in data["items"]:
                response += f"- {item.capitalize()}\n"
            response += "\n"
        
        return response + "⚠️ Nota: Utilizzando il sistema di categorizzazione locale. Sistema AI avanzato non disponibile al momento."
    
    def answer_question(self, items, question):
        """
        Risponde a una domanda sulla lista della spesa.
        
        Args:
            items: Lista di prodotti nella lista della spesa
            question: La domanda posta dall'utente
            
        Returns:
            Una stringa con la risposta
        """
        # Semplice risposta casuale dalla lista di risposte generali
        response = random.choice(self.general_answers)
        
        return response + "\n\n⚠️ Nota: Utilizzando il sistema di risposte locale. Sistema AI avanzato non disponibile al momento."
    
    def generate_meal_plan(self, items):
        """
        Genera un piano pasti basato sulla lista della spesa.
        
        Args:
            items: Lista di prodotti nella lista della spesa
            
        Returns:
            Una stringa con il piano pasti
        """
        # Seleziona un piano pasti casuale tra quelli predefiniti
        meal_plan = random.choice(self.meal_plan_templates)
        
        return meal_plan + "\n\n⚠️ Nota: Utilizzando il sistema di pianificazione pasti locale. Sistema AI avanzato non disponibile al momento."