# Bot Telegram Lista della Spesa

Un bot Telegram in italiano per gestire in modo intelligente le liste della spesa con funzionalità AI.

## Funzionalità
- Gestione completa delle liste della spesa (aggiungere, rimuovere, visualizzare, svuotare)
- Supporto per le quantità dei prodotti
- Categorizzazione automatica degli articoli
- Suggerimenti intelligenti basati sulla lista attuale
- Generazione di piani pasti
- Assistenza AI per domande sulla lista

## Comandi
- `/aggiungi [articolo]` - Aggiungi un articolo alla lista
- `/lista` - Mostra la tua lista della spesa
- `/rimuovi [numero]` - Rimuovi un articolo dalla lista
- `/svuota` - Cancella l'intera lista
- `/suggerisci` - Ottieni suggerimenti intelligenti
- `/categorie` - Organizza la lista per categorie
- `/pasti` - Ottieni un piano dei pasti basato sulla lista
- `/ai [domanda]` - Fai una domanda sulla tua lista

## Tecnologie Utilizzate
- Python Telegram Bot API
- OpenAI GPT per funzionalità AI
- Sistema di fallback multilivello per garantire disponibilità
- Storage persistente per mantenere le liste tra i riavvii