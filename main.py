import os
import logging
import threading
from datetime import datetime
from flask import Flask, render_template, jsonify
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters

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

# Create Flask app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "telegram_shopping_list_bot")

# Bot status
bot_status = {
    "running": False,
    "status_message": "Bot not started",
    "users_count": 0,
    "last_update": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a welcome message when the /start command is issued."""
    user_id = update.effective_user.id
    await update.message.reply_text(START_MSG)

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a help message when the /aiuto command is issued."""
    await update.message.reply_text(HELP_MSG)

async def add_item(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Add an item to the shopping list."""
    user_id = update.effective_user.id
    
    if not context.args:
        await update.message.reply_text("Per favore, specifica un articolo da aggiungere. Esempio: /aggiungi pane")
        return
    
    item = " ".join(context.args)
    shopping_list.add_item(user_id, item)
    await update.message.reply_text(ITEM_ADDED_MSG.format(item=item))

async def show_list(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Display the current shopping list."""
    user_id = update.effective_user.id
    items = shopping_list.get_items(user_id)
    
    if not items:
        await update.message.reply_text(LIST_EMPTY_MSG)
        return
    
    message = LIST_HEADER_MSG + "\n"
    for i, item in enumerate(items, 1):
        message += f"{i}. {item}\n"
    
    await update.message.reply_text(message)

async def remove_item(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Remove an item from the shopping list."""
    user_id = update.effective_user.id
    
    if not context.args:
        await update.message.reply_text("Per favore, specifica il numero dell'articolo da rimuovere. Esempio: /rimuovi 1")
        return
    
    try:
        index = int(context.args[0]) - 1
        removed_item = shopping_list.remove_item(user_id, index)
        
        if removed_item:
            await update.message.reply_text(ITEM_REMOVED_MSG.format(item=removed_item))
        else:
            await update.message.reply_text("Non ho trovato questo articolo nella tua lista.")
    except (ValueError, IndexError):
        await update.message.reply_text("Per favore, inserisci un numero valido. Usa /lista per vedere i numeri degli articoli.")

async def clear_list(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Clear the entire shopping list."""
    user_id = update.effective_user.id
    shopping_list.clear_list(user_id)
    await update.message.reply_text(LIST_CLEARED_MSG)

async def suggest(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Get AI-powered suggestions based on the current shopping list."""
    user_id = update.effective_user.id
    items = shopping_list.get_items(user_id)
    
    if not items:
        await update.message.reply_text("La tua lista della spesa è vuota. Aggiungi qualche articolo prima di chiedere suggerimenti!")
        return
    
    await update.message.reply_text("Sto pensando a dei suggerimenti per te... 🧠")
    
    try:
        # Get suggestions from AI assistant
        suggestions = await ai_assistant.get_suggestions(items)
        await update.message.reply_text(SUGGEST_RESPONSE_MSG.format(suggestions=suggestions))
    except Exception as e:
        logger.error(f"Error in suggest command: {e}")
        await update.message.reply_text(ERROR_MSG)

async def ai_help(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Get AI assistance with shopping list or meal planning."""
    user_id = update.effective_user.id
    items = shopping_list.get_items(user_id)
    
    query = " ".join(context.args) if context.args else ""
    
    if not query:
        await update.message.reply_text("Cosa vuoi sapere sulla tua lista della spesa? Esempio: /ai Come posso usare questi ingredienti per una cena?")
        return
    
    await update.message.reply_text("Sto analizzando la tua richiesta... 🧠")
    
    try:
        # Get AI response
        response = await ai_assistant.answer_question(items, query)
        await update.message.reply_text(response)
    except Exception as e:
        logger.error(f"Error in ai_help command: {e}")
        await update.message.reply_text(ERROR_MSG)

async def categorize(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Categorize items in the shopping list."""
    user_id = update.effective_user.id
    items = shopping_list.get_items(user_id)
    
    if not items:
        await update.message.reply_text("La tua lista della spesa è vuota. Aggiungi qualche articolo prima di chiedere una categorizzazione!")
        return
    
    await update.message.reply_text("Sto organizzando la tua lista per categorie... 🧠")
    
    try:
        # Categorize items
        categorized = await ai_assistant.categorize_items(items)
        await update.message.reply_text(categorized)
    except Exception as e:
        logger.error(f"Error in categorize command: {e}")
        await update.message.reply_text(ERROR_MSG)

async def meal_plan(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Generate a meal plan based on items in the shopping list."""
    user_id = update.effective_user.id
    items = shopping_list.get_items(user_id)
    
    if not items:
        await update.message.reply_text("La tua lista della spesa è vuota. Aggiungi qualche articolo prima di chiedere un piano dei pasti!")
        return
    
    await update.message.reply_text("Sto preparando un piano dei pasti per te... 🧠")
    
    try:
        # Generate meal plan
        meal_plan = await ai_assistant.generate_meal_plan(items)
        await update.message.reply_text(meal_plan)
    except Exception as e:
        logger.error(f"Error in meal_plan command: {e}")
        await update.message.reply_text(ERROR_MSG)

def check_bot_health():
    """Check if the bot token is valid and API is accessible."""
    import requests
    
    # Get the token from environment variable
    token = os.environ.get("TELEGRAM_TOKEN")
    
    if not token:
        logger.error("TELEGRAM_TOKEN environment variable not set!")
        return False, "TELEGRAM_TOKEN environment variable not set!"
    
    # Check if OpenAI API key is set
    openai_key = os.environ.get("OPENAI_API_KEY")
    if not openai_key:
        logger.warning("OPENAI_API_KEY environment variable not set! AI features will not work.")
    
    # Test Telegram API connection
    try:
        url = f"https://api.telegram.org/bot{token}/getMe"
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data.get('ok'):
                bot_name = data.get('result', {}).get('username', 'Unknown')
                return True, f"Connected to @{bot_name}"
            else:
                return False, f"Invalid token: {data.get('description', 'Unknown error')}"
        else:
            return False, f"API error: Status {response.status_code}"
    except Exception as e:
        return False, f"Connection error: {str(e)}"

def main():
    """Start the bot with proper verification."""
    # First check if the bot is healthy
    is_healthy, message = check_bot_health()
    
    if not is_healthy:
        logger.error(f"Bot health check failed: {message}")
        return
    
    logger.info(f"Bot health check passed: {message}")
    
    # Notify the user to interact with the bot through Telegram
    logger.info("The bot is running. Please interact with it through Telegram.")
    logger.info("Bot feature checks are available through the web interface.")
    
    # Keep the thread alive but don't consume resources
    import time
    while True:
        time.sleep(60)

def start_bot_thread():
    """Start the Telegram bot in a separate thread."""
    global bot_status
    try:
        bot_status["status_message"] = "Starting bot..."
        bot_thread = threading.Thread(target=main)
        bot_thread.daemon = True
        bot_thread.start()
        bot_status["running"] = True
        bot_status["status_message"] = "Bot running"
        bot_status["last_update"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        logger.info("Bot thread started successfully")
    except Exception as e:
        bot_status["status_message"] = f"Error starting bot: {str(e)}"
        logger.error(f"Error starting bot: {e}")

@app.route('/')
def index():
    """Main page route."""
    return render_template('index.html', bot_status=bot_status)

@app.route('/status')
def status():
    """API endpoint to get bot status."""
    return jsonify(bot_status)

# Initialize bot when the app starts
try:
    start_bot_thread()
    logger.info("Bot initialization completed")
except Exception as e:
    logger.error(f"Failed to initialize bot: {e}")

if __name__ == "__main__":
    # If run directly, start the web server
    app.run(host='0.0.0.0', port=5000, debug=True)
