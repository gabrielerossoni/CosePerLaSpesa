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

def get_category_emoji(category):
    """
    Restituisce l'emoji corrispondente alla categoria.
    
    Args:
        category: Nome della categoria
        
    Returns:
        Emoji come stringa
    """
    category_emojis = {
        "Frutta e Verdura": "🍎",
        "Carne e Pesce": "🥩",
        "Latticini": "🧀",
        "Pane e Cereali": "🍞",
        "Bevande": "🥤",
        "Surgelati": "❄️",
        "Prodotti da Forno": "🥐",
        "Condimenti": "🧂",
        "Dolci e Snack": "🍬",
        "Prodotti per la Casa": "🏠",
        "Prodotti per l'Igiene": "🧼",
        "Altro": "🛒"
    }
    return category_emojis.get(category, "🛒")

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
    
    # Get list type (group or personal)
    list_type = shopping_list.get_list_type(chat_id)
    
    if not items:
        message = f"{LIST_EMPTY_MSG}\n\n_{list_type}_"
        await update.message.reply_text(message, parse_mode="Markdown")
        return
    
    # Organize items by category with emojis
    categories = {}
    for item in items:
        category = item.get("category", "Altro")
        if category not in categories:
            categories[category] = []
        
        item_text = item["name"]
        if item.get("quantity"):
            item_text += f" ({item['quantity']})"
        
        categories[category].append(item_text)
    
    # Create the formatted message with categories
    message = f"{LIST_HEADER_MSG}\n\n"
    
    # First get all categories and sort them
    sorted_categories = sorted(categories.keys())
    
    # Display items by category
    for i, category in enumerate(sorted_categories):
        # Get emoji for category
        emoji = get_category_emoji(category)
        message += f"{emoji} *{category}*\n"
        
        # List items in this category with their index in the main list
        for j, item_text in enumerate(categories[category]):
            # Find the original index of this item in the complete items list
            original_index = None
            for idx, item in enumerate(items):
                if (item["name"] == item_text.split(" (")[0] if " (" in item_text else item["name"] == item_text):
                    original_index = idx + 1  # +1 because we're displaying indices starting from 1
                    break
                    
            if original_index is not None:
                message += f"  {original_index}. {item_text}\n"
            else:
                message += f"  • {item_text}\n"
        
        message += "\n"
    
    # Add list type at the end
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
            message = f"{ITEM_REMOVED_MSG.format(item=removed_item)}\n\n_{list_type}_"
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

def check_bot_health():
    """Check if the bot token is valid and API is accessible."""
    import requests
    
    # Get the token from environment variable
    token = os.environ.get("TELEGRAM_TOKEN")
    
    if not token:
        logger.error("TELEGRAM_TOKEN environment variable not set!")
        return False, "TELEGRAM_TOKEN environment variable not set!", None
    
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
                return True, f"Connected to @{bot_name}", f"@{bot_name}"
            else:
                return False, f"Invalid token: {data.get('description', 'Unknown error')}", None
        else:
            return False, f"API error: Status {response.status_code}", None
    except Exception as e:
        return False, f"Connection error: {str(e)}", None

def main():
    """Start the bot with proper verification and run it."""
    import asyncio
    
    # First check if the bot is healthy
    is_healthy, message, bot_username = check_bot_health()
    
    if not is_healthy:
        logger.error(f"Bot health check failed: {message}")
        return
    
    logger.info(f"Bot health check passed: {message}")
    
    # Get the token from environment variable
    token = os.environ.get("TELEGRAM_TOKEN")
    if not token:
        logger.error("TELEGRAM_TOKEN environment variable not set!")
        return
    
    # Create a new event loop for this thread
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
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
    logger.info("Bot feature checks are available through the web interface.")
    
    # Start the Bot
    logger.info("Starting bot polling...")
    application.run_polling(allowed_updates=["message"])

def start_bot_thread():
    """Start the Telegram bot in a separate process."""
    global bot_status
    try:
        bot_status["status_message"] = "Starting bot..."
        
        # Check bot health and get bot username
        is_healthy, health_message, bot_username = check_bot_health()
        if is_healthy and bot_username:
            bot_status["bot_username"] = bot_username
            logger.info(f"Bot username set to {bot_username}")
        
        # Use subprocess to run the bot in a separate process
        import subprocess
        import os
        import sys
        
        # Make telegram_bot.py executable if it's not already
        os.chmod("telegram_bot.py", 0o755)
        
        # Create a new Python process
        python_executable = sys.executable
        
        # Install missing packages if needed
        subprocess.run([python_executable, "-m", "pip", "install", "--upgrade", "python-telegram-bot"], 
                      stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # Start the bot process with nohup to ensure it keeps running
        bot_process = subprocess.Popen(
            [python_executable, "telegram_bot.py"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env=os.environ.copy()  # Copy the current environment to ensure TELEGRAM_TOKEN is passed
        )
        
        # Wait a moment to see if it crashes immediately
        import time
        time.sleep(2)
        
        # Check if process is still running
        if bot_process.poll() is None:
            # Process is still running, looks good
            bot_status["running"] = True
            bot_status["status_message"] = "Bot running in separate process"
            bot_status["last_update"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            logger.info("Bot process started successfully")
            
            # Store the process ID for reference
            bot_status["process_id"] = bot_process.pid
        else:
            # Process exited
            stdout, stderr = bot_process.communicate()
            error_msg = stderr.decode('utf-8')
            bot_status["status_message"] = f"Bot process exited: {error_msg}"
            logger.error(f"Bot process exited: {error_msg}")
            
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

# Import keep-alive functionality
from keep_alive import start_keep_alive_server

# Initialize bot when the app starts
try:
    # Start keep-alive server first
    keep_alive_thread = start_keep_alive_server()
    
    # Then start the bot
    start_bot_thread()
    logger.info("Bot initialization completed")
except Exception as e:
    logger.error(f"Failed to initialize bot: {e}")

if __name__ == "__main__":
    # If run directly, start the web server
    app.run(host='0.0.0.0', port=5000, debug=True)
