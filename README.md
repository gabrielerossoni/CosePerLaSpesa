# Bot Telegram "Lista della Spesa"

Un bot Telegram per gestire la tua lista della spesa con supporto per quantità e funzionalità AI.

## Funzionalità

- ✅ Gestione completa della lista della spesa (aggiungi, rimuovi, visualizza, svuota)
- ✅ Supporto per specificare quantità (es. "2 kg di patate")
- ✅ Pulsanti interattivi per un'esperienza utente migliore
- ✅ Suggerimenti intelligenti grazie all'AI
- ✅ Categorizzazione automatica degli articoli
- ✅ Generazione di piani pasti basati sulla tua lista
- ✅ Risposte a domande sulla tua lista della spesa

## Come rendere il bot attivo 24/7 su Replit

Per mantenere il bot attivo 24/7 anche quando chiudi il computer, segui questi passaggi:

1. **Deploy su Replit**:
   - Vai alla tab "Deployment" nella barra laterale di Replit
   - Clicca su "Deploy" per creare una versione in produzione del bot
   - Nelle impostazioni del deployment, attiva l'opzione "Always On"

2. **Usa un servizio di ping esterno**:
   - Registrati su [UptimeRobot](https://uptimerobot.com/) (gratuito)
   - Crea un nuovo monitor di tipo "HTTP(s)"
   - URL da monitorare: `https://tuorepl.replit.app/` (sostituisci con il tuo URL di deployment)
   - Imposta un intervallo di controllo di 5 minuti
   - Questo "pinga" il tuo bot regolarmente per tenerlo attivo

3. **Verifica che i segreti siano configurati**:
   - Assicurati che `TELEGRAM_TOKEN` e `OPENAI_API_KEY` siano configurati nei segreti di Replit

## Struttura del progetto

Il progetto è strutturato in modo da avere:

- `main.py`: Applicazione web Flask e gestione del bot
- `telegram_bot.py`: Implementazione del bot Telegram
- `ai_assistant.py`: Funzionalità di intelligenza artificiale
- `shopping_list.py`: Gestione della lista della spesa
- `storage.py`: Persistenza dei dati
- `keep_alive.py`: Servizio per mantenere attivo il bot

## Come usare il bot

1. Cerca `@CosePerLaSpesaBot` su Telegram
2. Invia `/start` per iniziare
3. Usa i pulsanti o i comandi per interagire con il bot
4. Aggiungi articoli con quantità (es. `/aggiungi 2 kg di patate`)
5. Visualizza la tua lista con `/lista`
6. Usa l'AI per suggerimenti, categorie e piani pasti

## Note tecniche

- Il bot utilizza python-telegram-bot v20
- Le funzionalità AI sono basate su OpenAI gpt-4o
- I dati sono salvati in formato JSON
- L'applicazione web monitora lo stato del bot