#!/usr/bin/env python3
"""
Bot runner module for Telegram shopping list bot.
This module runs the bot in a separate process, specifically designed for Railway deployment.
"""
import os
import logging
import asyncio
import signal
import time
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

from shopping_list import ShoppingList
from ai_assistant import AIAssistant
from constants import (
    START_MSG, HELP_MSG, ITEM_ADDED_MSG, LIST_EMPTY_MSG, 
    LIST_HEADER_MSG, ITEM_REMOVED_MSG, LIST_CLEARED_MSG,
    SUGGEST_RESPONSE_MSG, ERROR_MSG
)

# Set up logging
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Initialize shopping list manager and AI assistant
shopping_list = ShoppingList()
ai_assistant = AIAssistant()

def get_category_emoji(category):
    """
    Restituisce l'emoji corrispondente alla categoria.
    
    Args:
        category: Nome della categoria
        
    Returns:
        Emoji come stringa
    """
    category_emojis = {
        "Frutta e verdura": "🥬",
        "Frutta": "🍎",
        "Verdura": "🥦",
        "Carne": "🥩",
        "Pesce": "🐟",
        "Latticini": "🧀",
        "Uova": "🥚",
        "Pane e pasta": "🍞",
        "Pasta": "🍝",
        "Pane": "🥖",
        "Cereali": "🌾",
        "Riso": "🍚",
        "Bevande": "🥤",
        "Bibite": "🥤",
        "Acqua": "💧",
        "Alcolici": "🍷",
        "Vino": "🍷",
        "Birra": "🍺",
        "Snack": "🍿",
        "Dolci": "🍰",
        "Surgelati": "❄️",
        "Scatolame": "🥫",
        "Conserve": "🥫",
        "Salse": "🍯",
        "Condimenti": "🧂",
        "Spezie": "🌶️",
        "Erbe": "🌿",
        "Igiene personale": "🧼",
        "Pulizia": "🧹",
        "Cura della casa": "🧹",
        "Cura della persona": "🧴",
        "Bambini": "👶",
        "Animali": "🐾",
        "Pet": "🐾",
        "Cibo per animali": "🦴",
        "Cancelleria": "📝",
        "Altro": "📦"
    }
    
    # Controllo case-insensitive e parziale
    for key, emoji in category_emojis.items():
        if category.lower() in key.lower() or key.lower() in category.lower():
            return emoji
    
    return "📦"  # Emoji predefinito per categorie non riconosciute

# Keep track of running status
bot_running = False

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a welcome message when the /start command is issued."""
    user_id = update.effective_user.id
    chat_id = update.effective_chat.id
    
    # Get list type (group or personal)
    list_type = shopping_list.get_list_type(chat_id)
    
    message = f"{START_MSG}\n\n_{list_type}_"
    await update.message.reply_text(message, parse_mode="Markdown")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a help message when the /aiuto command is issued."""
    chat_id = update.effective_chat.id
    
    # Get list type (group or personal)
    list_type = shopping_list.get_list_type(chat_id)
    
    message = f"{HELP_MSG}\n\n_{list_type}_"
    await update.message.reply_text(message, parse_mode="Markdown")

async def add_item(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Add an item to the shopping list."""
    user_id = update.effective_user.id
    chat_id = update.effective_chat.id
    
    # Get list type (group or personal)
    list_type = shopping_list.get_list_type(chat_id)
    
    if not context.args:
        message = f"Per favore, specifica un articolo da aggiungere. Esempio: /aggiungi pane\n\n_{list_type}_"
        await update.message.reply_text(message, parse_mode="Markdown")
        return
    
    item = " ".join(context.args)
    success, item_name, quantity, category = shopping_list.add_item(chat_id, item, user_id)
    
    if success:
        if quantity:
            message = f"{ITEM_ADDED_MSG.format(item=item_name)} ({quantity})\n\n_{list_type}_"
        else:
            message = f"{ITEM_ADDED_MSG.format(item=item_name)}\n\n_{list_type}_"
        await update.message.reply_text(message, parse_mode="Markdown")
    else:
        message = f"Non sono riuscito ad aggiungere l'articolo.\n\n_{list_type}_"
        await update.message.reply_text(message, parse_mode="Markdown")

async def show_list(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Display the current shopping list."""
    user_id = update.effective_user.id
    chat_id = update.effective_chat.id
    items = shopping_list.get_items(chat_id, user_id)
    
    if not items:
        # Get list type (group or personal)
        list_type = shopping_list.get_list_type(chat_id)
        message = f"{LIST_EMPTY_MSG}\n\n_{list_type}_"
        await update.message.reply_text(message, parse_mode="Markdown")
        return
    
    # Organize items by category
    categories = {}
    for item in items:
        category = item.get("category", "Altro")
        if category not in categories:
            categories[category] = []
        categories[category].append(item)
    
    # Get list type (group or personal)
    list_type = shopping_list.get_list_type(chat_id)
    
    # Build the message
    message = LIST_HEADER_MSG + "\n\n"
    
    # Display each category
    item_count = 1
    
    for category, cat_items in sorted(categories.items()):
        # Add category header with emoji
        emoji = get_category_emoji(category)
        message += f"*{emoji} {category}*\n"
        
        # Add items in this category
        for item in cat_items:
            name = item.get("name", "")
            quantity = item.get("quantity", "")
            
            if quantity:
                message += f"{item_count}. {name} ({quantity})\n"
            else:
                message += f"{item_count}. {name}\n"
            
            item_count += 1
        
        message += "\n"
    
    message += f"_{list_type}_"
    
    await update.message.reply_text(message, parse_mode="Markdown")

async def remove_item(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Remove an item from the shopping list."""
    user_id = update.effective_user.id
    chat_id = update.effective_chat.id
    
    # Get list type (group or personal)
    list_type = shopping_list.get_list_type(chat_id)
    
    if not context.args:
        message = f"Per favore, specifica il numero dell'articolo da rimuovere. Esempio: /rimuovi 1\n\n_{list_type}_"
        await update.message.reply_text(message, parse_mode="Markdown")
        return
    
    try:
        index = int(context.args[0]) - 1
        removed_item = shopping_list.remove_item(chat_id, index, user_id)
        
        if removed_item:
            message = f"{ITEM_REMOVED_MSG.format(item=removed_item['name'])}\n\n_{list_type}_"
            await update.message.reply_text(message, parse_mode="Markdown")
        else:
            message = f"Non ho trovato questo articolo nella tua lista.\n\n_{list_type}_"
            await update.message.reply_text(message, parse_mode="Markdown")
    except (ValueError, IndexError):
        message = f"Per favore, inserisci un numero valido. Usa /lista per vedere i numeri degli articoli.\n\n_{list_type}_"
        await update.message.reply_text(message, parse_mode="Markdown")

async def clear_list(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Clear the entire shopping list."""
    user_id = update.effective_user.id
    chat_id = update.effective_chat.id
    
    # Get list type (group or personal)
    list_type = shopping_list.get_list_type(chat_id)
    
    shopping_list.clear_list(chat_id, user_id)
    message = f"{LIST_CLEARED_MSG}\n\n_{list_type}_"
    await update.message.reply_text(message, parse_mode="Markdown")

async def suggest(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Get AI-powered suggestions based on the current shopping list."""
    user_id = update.effective_user.id
    chat_id = update.effective_chat.id
    items = shopping_list.get_items(chat_id, user_id)
    item_names = [item["name"] for item in items]  # Extract just the names for AI
    
    # Get list type (group or personal)
    list_type = shopping_list.get_list_type(chat_id)
    
    if not items:
        message = f"La tua lista della spesa è vuota. Aggiungi qualche articolo prima di chiedere suggerimenti!\n\n_{list_type}_"
        await update.message.reply_text(message, parse_mode="Markdown")
        return
    
    await update.message.reply_text("Sto pensando a dei suggerimenti per te... 🧠")
    
    try:
        # Get suggestions from AI assistant
        suggestions = await ai_assistant.get_suggestions(item_names)
        message = f"{SUGGEST_RESPONSE_MSG.format(suggestions=suggestions)}\n\n_{list_type}_"
        await update.message.reply_text(message, parse_mode="Markdown")
    except Exception as e:
        logger.error(f"Error in suggest command: {e}")
        await update.message.reply_text(ERROR_MSG)

async def ai_help(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Get AI assistance with shopping list or meal planning."""
    user_id = update.effective_user.id
    chat_id = update.effective_chat.id
    items = shopping_list.get_items(chat_id, user_id)
    item_names = [item["name"] for item in items]  # Extract just the names for AI
    
    # Get list type (group or personal)
    list_type = shopping_list.get_list_type(chat_id)
    
    query = " ".join(context.args) if context.args else ""
    
    if not query:
        message = f"Cosa vuoi sapere sulla tua lista della spesa? Esempio: /ai Come posso usare questi ingredienti per una cena?\n\n_{list_type}_"
        await update.message.reply_text(message, parse_mode="Markdown")
        return
    
    if not items:
        message = f"La tua lista della spesa è vuota. Aggiungi qualche articolo prima di chiedere aiuto all'IA!\n\n_{list_type}_"
        await update.message.reply_text(message, parse_mode="Markdown")
        return
    
    await update.message.reply_text("Sto analizzando la tua richiesta... 🧠")
    
    try:
        # Get AI response
        response = await ai_assistant.answer_question(item_names, query)
        message = f"{response}\n\n_{list_type}_"
        await update.message.reply_text(message, parse_mode="Markdown")
    except Exception as e:
        logger.error(f"Error in ai_help command: {e}")
        await update.message.reply_text(ERROR_MSG)

async def categorize(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Categorize items in the shopping list."""
    user_id = update.effective_user.id
    chat_id = update.effective_chat.id
    items = shopping_list.get_items(chat_id, user_id)
    item_names = [item["name"] for item in items]  # Extract just the names for AI
    
    # Get list type (group or personal)
    list_type = shopping_list.get_list_type(chat_id)
    
    if not items:
        message = f"La tua lista della spesa è vuota. Aggiungi qualche articolo prima di chiedere una categorizzazione!\n\n_{list_type}_"
        await update.message.reply_text(message, parse_mode="Markdown")
        return
    
    await update.message.reply_text("Sto organizzando la tua lista per categorie... 🧠")
    
    try:
        # Categorize items
        categorized = await ai_assistant.categorize_items(item_names)
        message = f"{categorized}\n\n_{list_type}_"
        await update.message.reply_text(message, parse_mode="Markdown")
    except Exception as e:
        logger.error(f"Error in categorize command: {e}")
        await update.message.reply_text(ERROR_MSG)

async def meal_plan(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Generate a meal plan based on items in the shopping list."""
    user_id = update.effective_user.id
    chat_id = update.effective_chat.id
    items = shopping_list.get_items(chat_id, user_id)
    item_names = [item["name"] for item in items]  # Extract just the names for AI
    
    # Get list type (group or personal)
    list_type = shopping_list.get_list_type(chat_id)
    
    if not items:
        message = f"La tua lista della spesa è vuota. Aggiungi qualche articolo prima di chiedere un piano dei pasti!\n\n_{list_type}_"
        await update.message.reply_text(message, parse_mode="Markdown")
        return
    
    await update.message.reply_text("Sto preparando un piano dei pasti per te... 🧠")
    
    try:
        # Generate meal plan
        meal_plan_text = await ai_assistant.generate_meal_plan(item_names)
        message = f"{meal_plan_text}\n\n_{list_type}_"
        await update.message.reply_text(message, parse_mode="Markdown")
    except Exception as e:
        logger.error(f"Error in meal_plan command: {e}")
        await update.message.reply_text(ERROR_MSG)

def handle_sigterm(signum, frame):
    """Handle termination signals correctly"""
    logger.info("Received SIGTERM, shutting down bot...")
    global bot_running
    bot_running = False
    # Wait for cleanup
    time.sleep(2)
    logger.info("Bot gracefully shut down")
    exit(0)

def run_bot_forever():
    """Run the bot with proper error handling and recovery"""
    global bot_running
    bot_running = True
    
    # Set up signal handlers
    signal.signal(signal.SIGTERM, handle_sigterm)
    signal.signal(signal.SIGINT, handle_sigterm)
    
    while bot_running:
        try:
            logger.info("Starting Telegram bot...")
            # Run the bot asynchronously
            asyncio.run(run_bot())
        except Exception as e:
            logger.error(f"Bot error: {e}")
            logger.info("Restarting bot in 10 seconds...")
            time.sleep(10)

async def run_bot():
    """Run the bot with proper shutdown handling"""
    # Get the token from environment variable
    token = os.environ.get("TELEGRAM_TOKEN")
    if not token:
        logger.error("TELEGRAM_TOKEN environment variable not set!")
        return
    
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
    
    # Notify the user to interact with the bot through Telegram
    logger.info("The bot is running. Please interact with it through Telegram.")
    
    # Start the Bot with proper shutdown
    stop_signal = asyncio.Future()
    
    # Run the bot and handle shutdown
    await application.initialize()
    await application.start()
    
    logger.info("Bot is up and running!")
    
    # Keep the bot running until stop_signal is set
    while not stop_signal.done() and bot_running:
        try:
            await asyncio.sleep(1)
        except asyncio.CancelledError:
            break
    
    # Proper shutdown
    logger.info("Shutting down bot...")
    await application.stop()
    await application.shutdown()

if __name__ == "__main__":
    run_bot_forever()