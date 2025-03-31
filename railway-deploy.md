# Guida al Deploy su Railway

Questa guida ti aiuterà a deployare il tuo Telegram Bot su Railway in modo che rimanga attivo 24/7 anche quando spegni il PC.

## 1. Preparazione

Il tuo progetto è già pronto per il deploy! Ecco cosa abbiamo già fatto:

- ✅ Abbiamo configurato Gunicorn come server WSGI
- ✅ Il tuo bot lavora con una struttura web app + bot Telegram
- ✅ Le dipendenze sono tutte elencate in `pyproject.toml`

## 2. Crea un Account Railway

1. Vai su [Railway](https://railway.app/)
2. Registrati (puoi usare il tuo account GitHub per semplificare il processo)

## 3. Crea un Nuovo Progetto

1. Nella dashboard di Railway, clicca su "New Project"
2. Seleziona "Deploy from GitHub repo"
3. Seleziona il tuo repository `CosePerLaSpesa`
4. Railway chiederà di autorizzare l'accesso al repository - approva la richiesta

## 4. Configura le Variabili d'Ambiente

Queste sono le tue chiavi segrete che il bot utilizzerà:

1. Vai alla sezione "Variables" del tuo progetto
2. Aggiungi le seguenti variabili:
   - `TELEGRAM_TOKEN`: Il token del tuo bot Telegram
   - `OPENAI_API_KEY`: La tua chiave API di OpenAI
   - `SESSION_SECRET`: Una stringa casuale per le sessioni (puoi usare un generatore online di password)

## 5. Configura il Comando di Avvio

1. Vai alla sezione "Settings" del tuo progetto
2. Clicca su "Deploy"
3. Nel campo "Start Command", inserisci:
   ```
   gunicorn --bind 0.0.0.0:$PORT --reuse-port main:app
   ```
   (Railway utilizza la variabile $PORT per assegnare automaticamente la porta)

## 6. Deploy

1. Railway dovrebbe deployare automaticamente il progetto dopo che hai configurato il comando di avvio
2. Se non lo fa, vai alla sezione "Deployments" e clicca su "Deploy Now"

## 7. Verifica del Funzionamento

1. Una volta completato il deploy, Railway ti fornirà un URL per il tuo progetto
2. Accedi all'URL per verificare che il server web sia attivo
3. Prova a interagire con il tuo bot su Telegram per confermare che funzioni correttamente

## 8. Monitoraggio

Railway fornisce statistiche di utilizzo e logs:
1. Vai alla sezione "Metrics" per vedere l'utilizzo di CPU/memoria
2. Controlla i logs nella sezione "Logs" se incontri problemi

## Nota sulla Persistenza dei Dati

Il tuo bot attualmente salva i dati delle liste della spesa nel file `shopping_lists.json`. Su Railway, questo file verrà ricreato ogni volta che il progetto viene riavviato. 

Per una soluzione più robusta in futuro, potresti voler considerare di usare un database come PostgreSQL (che Railway può fornire come servizio aggiuntivo).