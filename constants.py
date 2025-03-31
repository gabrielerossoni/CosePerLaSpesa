# Constants for bot messages

# Welcome and help messages
START_MSG = """
👋 Benvenuto alla tua Lista della Spesa personale!

Puoi usare i seguenti comandi:
/aggiungi [articolo] - Aggiungi un articolo alla lista
/lista - Mostra la tua lista della spesa
/rimuovi [numero] - Rimuovi un articolo dalla lista
/svuota - Cancella l'intera lista
/suggerisci - Ottieni suggerimenti intelligenti
/categorie - Organizza la lista per categorie
/pasti - Ottieni un piano dei pasti basato sulla lista
/ai [domanda] - Fai una domanda sulla tua lista

Digita /aiuto per vedere questo messaggio di nuovo.
"""

HELP_MSG = """
📝 *Comandi della Lista della Spesa*

/aggiungi [articolo] - Aggiungi un articolo alla lista
Esempio: `/aggiungi pane`

/lista - Mostra la tua lista della spesa attuale

/rimuovi [numero] - Rimuovi un articolo dalla lista usando il suo numero
Esempio: `/rimuovi 1`

/svuota - Cancella l'intera lista

*Funzioni AI* 🧠

/suggerisci - Ottieni suggerimenti per altri articoli in base alla tua lista attuale

/categorie - Organizza la tua lista per categorie (latticini, frutta, ecc.)

/pasti - Genera un piano dei pasti basato sugli articoli nella tua lista

/ai [domanda] - Fai una domanda sulla tua lista della spesa
Esempio: `/ai Cosa posso cucinare con questi ingredienti?`
"""

# Shopping list messages
ITEM_ADDED_MSG = "✅ \"{item}\" aggiunto alla tua lista della spesa!"
LIST_EMPTY_MSG = "📝 La tua lista della spesa è vuota. Aggiungi qualcosa con /aggiungi [articolo]"
LIST_HEADER_MSG = "📝 *La tua lista della spesa:*"
ITEM_REMOVED_MSG = "🗑️ \"{item}\" rimosso dalla lista!"
LIST_CLEARED_MSG = "🧹 La tua lista della spesa è stata svuotata!"

# AI suggestion messages
SUGGEST_RESPONSE_MSG = """
🧠 *Ecco alcuni suggerimenti in base alla tua lista:*

{suggestions}
"""

# Error message
ERROR_MSG = "❌ Mi dispiace, c'è stato un errore. Riprova più tardi."
