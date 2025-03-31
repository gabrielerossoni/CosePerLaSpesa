#!/usr/bin/env python3
"""
Standalone Telegram bot for the shopping list application.
This script is meant to be run as a separate process.
"""

import os
import sys
import time
import logging
import asyncio
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from telegram import Update

# Set up logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger("telegram_bot")

# Import required components
from shopping_list import ShoppingList
from ai_assistant import AIAssistant

# Initialize global variables
shopping_list = ShoppingList()
ai_assistant = AIAssistant()

# Define command handlers
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a welcome message when the /start command is issued."""
    await update.message.reply_text(
        "Benvenuto alla tua Lista della Spesa!\n"
        "Usa /aggiungi per aggiungere articoli alla tua lista.\n"
        "Usa /lista per vedere cosa hai nella tua lista.\n"
        "Usa /aiuto per vedere tutti i comandi disponibili."
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a help message when the /aiuto command is issued."""
    await update.message.reply_text(
        "Ecco i comandi disponibili:\n"
        "/aggiungi [articolo] - Aggiungi un articolo alla lista\n"
        "/lista - Mostra la tua lista della spesa\n"
        "/rimuovi [numero] - Rimuovi un articolo specificando il suo numero\n"
        "/svuota - Cancella tutti gli articoli dalla lista\n"
        "/suggerisci - Ottieni suggerimenti basati sulla tua lista\n"
        "/categorie - Organizza la tua lista in categorie\n"
        "/pasti - Ottieni idee per pasti basati sulla tua lista\n"
        "/ai [domanda] - Chiedi aiuto all'assistente AI"
    )

async def add_item(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Add an item to the shopping list."""
    user_id = update.effective_user.id
    text = update.message.text.split(" ", 1)
    
    if len(text) < 2:
        await update.message.reply_text("Usa: /aggiungi [articolo]")
        return
    
    item = text[1].strip()
    shopping_list.add_item(user_id, item)
    await update.message.reply_text(f"Aggiunto: {item}")

async def show_list(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Display the current shopping list."""
    user_id = update.effective_user.id
    items = shopping_list.get_items(user_id)
    
    if not items:
        await update.message.reply_text("La tua lista della spesa è vuota.")
        return
    
    message = "La tua lista della spesa:\n"
    for index, item in enumerate(items, start=1):
        message += f"{index}. {item}\n"
    
    await update.message.reply_text(message)

async def remove_item(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Remove an item from the shopping list."""
    user_id = update.effective_user.id
    text = update.message.text.split(" ", 1)
    
    if len(text) < 2:
        await update.message.reply_text("Usa: /rimuovi [numero]")
        return
    
    try:
        index = int(text[1].strip()) - 1
        removed_item = shopping_list.remove_item(user_id, index)
        
        if removed_item:
            await update.message.reply_text(f"Rimosso: {removed_item}")
        else:
            await update.message.reply_text("Numero non valido. Usa /lista per vedere i numeri degli articoli.")
    except ValueError:
        await update.message.reply_text("Inserisci un numero valido. Usa /lista per vedere i numeri degli articoli.")

async def clear_list(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Clear the entire shopping list."""
    user_id = update.effective_user.id
    shopping_list.clear_list(user_id)
    await update.message.reply_text("La tua lista della spesa è stata svuotata.")

async def suggest(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Get AI-powered suggestions based on the current shopping list."""
    user_id = update.effective_user.id
    items = shopping_list.get_items(user_id)
    
    if not items:
        await update.message.reply_text("La tua lista è vuota. Aggiungi alcuni articoli prima di chiedere suggerimenti.")
        return
    
    await update.message.reply_text("Generando suggerimenti... Questo potrebbe richiedere alcuni secondi.")
    
    try:
        suggestions = await ai_assistant.get_suggestions(items)
        await update.message.reply_text(suggestions)
    except Exception as e:
        await update.message.reply_text(f"Mi dispiace, non sono riuscito a generare suggerimenti. Errore: {str(e)}")

async def ai_help(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Get AI assistance with shopping list or meal planning."""
    user_id = update.effective_user.id
    text = update.message.text.split(" ", 1)
    
    if len(text) < 2:
        await update.message.reply_text("Usa: /ai [domanda sulla tua lista o sulla cucina]")
        return
    
    question = text[1].strip()
    items = shopping_list.get_items(user_id)
    
    await update.message.reply_text("Pensando... Questo potrebbe richiedere alcuni secondi.")
    
    try:
        answer = await ai_assistant.answer_question(items, question)
        await update.message.reply_text(answer)
    except Exception as e:
        await update.message.reply_text(f"Mi dispiace, non sono riuscito a rispondere. Errore: {str(e)}")

async def categorize(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Categorize items in the shopping list."""
    user_id = update.effective_user.id
    items = shopping_list.get_items(user_id)
    
    if not items:
        await update.message.reply_text("La tua lista è vuota. Aggiungi alcuni articoli prima di categorizzarli.")
        return
    
    await update.message.reply_text("Organizzando la tua lista in categorie... Questo potrebbe richiedere alcuni secondi.")
    
    try:
        categories = await ai_assistant.categorize_items(items)
        await update.message.reply_text(categories)
    except Exception as e:
        await update.message.reply_text(f"Mi dispiace, non sono riuscito a categorizzare la lista. Errore: {str(e)}")

async def meal_plan(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Generate a meal plan based on items in the shopping list."""
    user_id = update.effective_user.id
    items = shopping_list.get_items(user_id)
    
    if not items:
        await update.message.reply_text("La tua lista è vuota. Aggiungi alcuni articoli prima di generare un piano pasti.")
        return
    
    await update.message.reply_text("Generando un piano pasti basato sulla tua lista... Questo potrebbe richiedere alcuni secondi.")
    
    try:
        meal_plan = await ai_assistant.generate_meal_plan(items)
        await update.message.reply_text(meal_plan)
    except Exception as e:
        await update.message.reply_text(f"Mi dispiace, non sono riuscito a generare un piano pasti. Errore: {str(e)}")


if __name__ == "__main__":
    # This code only runs when the script is executed directly, not when imported
    token = os.environ.get("TELEGRAM_TOKEN")
    if not token:
        logger.error("TELEGRAM_TOKEN environment variable not set!")
        sys.exit(1)
    
    # Create the Application
    application = ApplicationBuilder().token(token).build()
    
    # Add command handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("aiuto", help_command))
    application.add_handler(CommandHandler("aggiungi", add_item))
    application.add_handler(CommandHandler("lista", show_list))
    application.add_handler(CommandHandler("rimuovi", remove_item))
    application.add_handler(CommandHandler("svuota", clear_list))
    application.add_handler(CommandHandler("suggerisci", suggest))
    application.add_handler(CommandHandler("ai", ai_help))
    application.add_handler(CommandHandler("categorie", categorize))
    application.add_handler(CommandHandler("pasti", meal_plan))
    
    # Start the Bot
    logger.info("Starting bot polling...")
    application.run_polling(allowed_updates=["message"])