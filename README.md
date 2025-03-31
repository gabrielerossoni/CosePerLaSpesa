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
- Flask + Gunicorn per l'interfaccia web di monitoraggio

## Deployment

### Local (Replit)
Il bot può essere eseguito direttamente su Replit utilizzando il workflow configurato. Assicurati di impostare le variabili d'ambiente:
- `TELEGRAM_TOKEN`: Il token del tuo bot Telegram
- `OPENAI_API_KEY`: La tua chiave API OpenAI

### Railway (24/7 Hosting)
Per un hosting continuo anche quando il PC è spento, segui le istruzioni nel file `railway-deploy.md` per deployare su Railway.

1. Push del codice su GitHub (già configurato con repository: `https://github.com/gabrielerossoni/CosePerLaSpesa`)
2. Connessione del repository a Railway
3. Configurazione delle variabili d'ambiente
4. Deploy automatico

Per istruzioni dettagliate, vedi il file `railway-deploy.md`.