# Guida al Deploy su Railway

Questa guida ti aiuterà a deployare il tuo Telegram Bot su Railway in modo che rimanga attivo 24/7 anche quando spegni il PC.

## 1. Preparazione

Il tuo progetto è già pronto per il deploy! Ecco cosa abbiamo già fatto:

- ✅ Abbiamo configurato Gunicorn come server WSGI
- ✅ Abbiamo creato un runner dedicato per il bot Telegram
- ✅ Abbiamo configurato il Procfile e il file .railway.json
- ✅ Le dipendenze sono tutte elencate in `pyproject.toml`
- ✅ Abbiamo aggiunto gestione corretta dei segnali per spegnere il bot in modo pulito

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
   - `PORT`: Lascia che Railway la imposti automaticamente

## 5. Il Deploy

Railway leggerà automaticamente le configurazioni dai file:
- `Procfile`: Contiene il comando di avvio principale
- `.railway.json`: Contiene configurazioni avanzate per il deployment

Il comando di avvio configurato è:
```
python bot_runner.py & gunicorn --bind 0.0.0.0:$PORT --workers=2 --timeout=240 main:app
```

Questo comando:
1. Avvia in background (`&`) il runner del bot Telegram
2. Avvia il server web Gunicorn con 2 worker e un timeout esteso

## 6. Verifica del Funzionamento

1. Una volta completato il deploy, Railway ti fornirà un URL per il tuo progetto
2. Accedi all'URL per verificare che il server web sia attivo
3. Prova a interagire con il tuo bot su Telegram per confermare che funzioni correttamente

## 7. Risoluzione dei Problemi Comuni

Se il bot si ferma dopo pochi minuti, controlla:

1. **Log di Railway**: Cerca errori nei log per capire cosa sta causando l'interruzione
2. **Variabili d'ambiente**: Assicurati che TELEGRAM_TOKEN e OPENAI_API_KEY siano impostati correttamente
3. **Monitoraggio delle risorse**: Se il bot usa troppa CPU o memoria, Railway potrebbe fermarlo

Per ripristinare il servizio:
1. Vai a "Deployments" in Railway
2. Clicca su "Redeploy" per riavviare il servizio

## 8. Monitoraggio

Railway fornisce statistiche di utilizzo e logs:
1. Vai alla sezione "Metrics" per vedere l'utilizzo di CPU/memoria
2. Controlla i logs nella sezione "Logs" se incontri problemi
3. Imposta alerting se desideri ricevere notifiche in caso di interruzioni

## Nota sulla Persistenza dei Dati

Il tuo bot attualmente salva i dati delle liste della spesa nel file `shopping_lists.json`. Su Railway, questo file verrà ricreato ogni volta che il progetto viene riavviato. 

Per una soluzione più robusta in futuro, potresti voler considerare di usare un database come PostgreSQL (che Railway può fornire come servizio aggiuntivo).