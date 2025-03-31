# Constants for bot messages

# Welcome and help messages
START_MSG = """
👋 Benvenuto alla tua Lista della Spesa personale!

Puoi usare i seguenti comandi:
/aggiungi [articolo] - Aggiungi un articolo alla lista (es. /aggiungi 2 kg di patate)
/lista - Mostra la tua lista della spesa
/rimuovi [numero] - Rimuovi un articolo dalla lista
/svuota - Cancella l'intera lista
/suggerisci - Ottieni suggerimenti intelligenti
/categorie - Organizza la lista per categorie
/pasti - Ottieni un piano dei pasti basato sulla lista
/ai [domanda] - Fai una domanda sulla tua lista

🛈 Ogni comando ha anche un pulsante equivalente!
"""

HELP_MSG = """
📝 *Comandi della Lista della Spesa*

/aggiungi [articolo] - Aggiungi un articolo alla lista
📌 Puoi specificare quantità in questi formati:
  • `/aggiungi 2 kg di patate` (quantità + unità + "di" + nome)
  • `/aggiungi 3 mele` (quantità + nome)
  • `/aggiungi pomodori (500g)` (nome + quantità tra parentesi)

/lista - Mostra la tua lista della spesa attuale

/rimuovi [numero] - Rimuovi un articolo dalla lista usando il suo numero
  • Esempio: `/rimuovi 1`

/svuota - Cancella l'intera lista

*Funzioni AI* 🧠

/suggerisci - Ottieni suggerimenti per altri articoli in base alla tua lista attuale

/categorie - Organizza la tua lista per categorie (latticini, frutta, ecc.)

/pasti - Genera un piano dei pasti basato sugli articoli nella tua lista

/ai [domanda] - Fai una domanda sulla tua lista della spesa
  • Esempio: `/ai Cosa posso cucinare con questi ingredienti?`
"""

# Shopping list messages
ITEM_ADDED_MSG = "✅ \"{item}\" aggiunto alla tua lista della spesa! (Quantità: {quantity})"
LIST_EMPTY_MSG = "📝 La tua lista della spesa è vuota. Aggiungi qualcosa con /aggiungi [articolo]"
LIST_HEADER_MSG = "📝 *La tua lista della spesa:*"
ITEM_REMOVED_MSG = "🗑️ \"{item}\" rimosso dalla lista!"
LIST_CLEARED_MSG = "🧹 La tua lista della spesa è stata svuotata!"
QUANTITY_UPDATED_MSG = "✏️ Quantità aggiornata per \"{item}\": {quantity}"

# AI suggestion messages
SUGGEST_RESPONSE_MSG = """
🧠 *Ecco alcuni suggerimenti in base alla tua lista:*

{suggestions}
"""

# Input prompts
QUANTITY_PROMPT = "Inserisci la quantità per \"{item}\" (es. 2 kg, 3 pezzi, 500g):"

# Button labels
BTN_ADD = "➕ Aggiungi Articolo"
BTN_LIST = "📋 Mostra Lista"
BTN_REMOVE = "🗑️ Rimuovi"
BTN_CLEAR = "🧹 Svuota Lista"
BTN_SUGGEST = "💡 Suggerimenti"
BTN_CATEGORIES = "📊 Categorie"
BTN_MEAL_PLAN = "🍽️ Piano Pasti"
BTN_HELP = "❓ Aiuto"
BTN_CANCEL = "❌ Annulla"
BTN_BACK = "⬅️ Indietro"

# Callback data prefixes
CB_ADD = "add"
CB_REMOVE = "remove"
CB_SHOW = "show"
CB_CLEAR = "clear"
CB_SUGGEST = "suggest"
CB_CATEGORIES = "categories"
CB_MEAL = "meal"
CB_CANCEL = "cancel"
CB_BACK = "back"
CB_SET_QTY = "setqty"

# States for conversation handlers
STATE_WAITING_ITEM = "waiting_item"
STATE_WAITING_QUANTITY = "waiting_quantity"
STATE_WAITING_REMOVE = "waiting_remove"
STATE_WAITING_QUESTION = "waiting_question"

# Error message
ERROR_MSG = "❌ Mi dispiace, c'è stato un errore. Riprova più tardi."
