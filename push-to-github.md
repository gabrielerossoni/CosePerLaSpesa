# Come caricare il codice su GitHub

## Opzione 1: Usa l'interfaccia di Replit

Il modo più semplice è:

1. Nella barra laterale di Replit, clicca sull'icona Git (il simbolo che assomiglia a una ramificazione)
2. Nella scheda che si apre, clicca su "Connect to GitHub Repository"
3. Segui le istruzioni per autorizzare l'accesso
4. Seleziona il tuo repository `Telegram-Shopping-List`
5. Clicca su "Push" o "Sync" per caricare i tuoi commit

## Opzione 2: Usa il terminale Replit con credenziali memorizzate

```bash
# Configura git per salvare le credenziali
git config --global credential.helper store

# Prova a fare push (ti chiederà le credenziali solo la prima volta)
git push -u origin main
```

## Opzione 3: Configura il remote con il token incorporato

```bash
# Rimuovi il remote attuale
git remote remove origin

# Aggiungi un nuovo remote con il token incorporato
git remote add origin https://TUO-TOKEN-GITHUB@github.com/gabborosso/Telegram-Shopping-List.git

# Fai push senza che ti chieda credenziali
git push -u origin main
```

Sostituisci `TUO-TOKEN-GITHUB` con il tuo Personal Access Token di GitHub.

## Opzione 4: Download dei file e caricamento manuale

Se le opzioni sopra non funzionano:

1. Scarica tutti i file dal tuo Replit usando l'opzione "Download as zip" dal menu
2. Vai sul tuo repository GitHub
3. Usa il pulsante "Upload files" per caricare manualmente i file