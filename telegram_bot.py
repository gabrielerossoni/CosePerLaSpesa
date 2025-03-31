#!/usr/bin/env python3
"""
Standalone Telegram bot for the shopping list application.
This script is meant to be run as a separate process.
"""

import os
import sys
import re
import time
import logging
import asyncio
from telegram.ext import (
    ApplicationBuilder, CommandHandler, ContextTypes, ConversationHandler,
    CallbackQueryHandler, MessageHandler, filters
)
from telegram import (
    Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup,
    ReplyKeyboardRemove, KeyboardButton
)
from telegram.constants import ParseMode

# Set up logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger("telegram_bot")

# Import required components
from shopping_list import ShoppingList
from ai_assistant import AIAssistant
from constants import (
    START_MSG, HELP_MSG, ITEM_ADDED_MSG, LIST_EMPTY_MSG, LIST_HEADER_MSG,
    ITEM_REMOVED_MSG, LIST_CLEARED_MSG, QUANTITY_UPDATED_MSG, SUGGEST_RESPONSE_MSG,
    QUANTITY_PROMPT, BTN_ADD, BTN_LIST, BTN_REMOVE, BTN_CLEAR, BTN_SUGGEST,
    BTN_CATEGORIES, BTN_MEAL_PLAN, BTN_HELP, BTN_CANCEL, BTN_BACK,
    CB_ADD, CB_REMOVE, CB_SHOW, CB_CLEAR, CB_SUGGEST, CB_CATEGORIES, CB_MEAL,
    CB_CANCEL, CB_BACK, CB_SET_QTY, STATE_WAITING_ITEM, STATE_WAITING_QUANTITY,
    STATE_WAITING_REMOVE, STATE_WAITING_QUESTION, ERROR_MSG
)

# Initialize global variables
shopping_list = ShoppingList()
ai_assistant = AIAssistant()

# Main menu keyboard
def get_main_keyboard():
    """Get the main menu keyboard."""
    keyboard = [
        [KeyboardButton(BTN_ADD), KeyboardButton(BTN_LIST)],
        [KeyboardButton(BTN_REMOVE), KeyboardButton(BTN_CLEAR)],
        [KeyboardButton(BTN_SUGGEST), KeyboardButton(BTN_CATEGORIES)],
        [KeyboardButton(BTN_MEAL_PLAN), KeyboardButton(BTN_HELP)]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

# Define command handlers
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a welcome message when the /start command is issued."""
    await update.message.reply_text(
        START_MSG,
        reply_markup=get_main_keyboard()
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a help message when the /aiuto command is issued."""
    await update.message.reply_text(
        HELP_MSG,
        parse_mode=ParseMode.MARKDOWN
    )

# Conversation handler states
async def start_adding_item(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Start the conversation to add an item."""
    if update.message and update.message.text and update.message.text.startswith("/aggiungi"):
        # Command format: /aggiungi <item>
        text = update.message.text.split(" ", 1)
        if len(text) > 1:
            return await process_add_item(update, context, text[1].strip())
    
    message_text = "Cosa vuoi aggiungere alla tua lista della spesa? Specificando anche la quantità se lo desideri.\n\n" \
                  "Esempi:\n" \
                  "• pane\n" \
                  "• 2 kg di patate\n" \
                  "• mele (6 pezzi)\n\n" \
                  "Per annullare, premi Annulla o digita /annulla."
    
    reply_markup = InlineKeyboardMarkup([[
        InlineKeyboardButton(BTN_CANCEL, callback_data=CB_CANCEL)
    ]])
    
    # Handle both message and callback query
    if update.callback_query:
        # It's a button press
        await update.callback_query.answer()
        await update.callback_query.message.reply_text(
            message_text,
            reply_markup=reply_markup
        )
    else:
        # It's a direct command or text message
        await update.message.reply_text(
            message_text,
            reply_markup=reply_markup
        )
    
    return STATE_WAITING_ITEM

async def process_add_item(update: Update, context: ContextTypes.DEFAULT_TYPE, item_text=None) -> int:
    """Process the item to add to the shopping list."""
    user_id = update.effective_user.id
    
    # Get the item text from the message or the provided argument
    if item_text is None:
        if update.callback_query:
            # Cancel button was pressed
            if update.callback_query.data == CB_CANCEL:
                await update.callback_query.message.edit_text("Operazione annullata.")
                return ConversationHandler.END
            # Nessun altro callback dovrebbe arrivare qui
            await update.callback_query.answer("Si è verificato un errore.")
            return ConversationHandler.END
        
        if not update.message:
            logger.error("Nessun messaggio trovato nell'update")
            return ConversationHandler.END
            
        item_text = update.message.text
    
    success, item_name, quantity = shopping_list.add_item(user_id, item_text)
    
    reply_markup = InlineKeyboardMarkup([[
        InlineKeyboardButton("📋 Mostra Lista", callback_data=CB_SHOW)
    ]])
    
    if success:
        reply_text = ITEM_ADDED_MSG.format(item=item_name, quantity=quantity)
    else:
        reply_text = "Non sono riuscito ad aggiungere l'articolo. Riprova."
    
    # Invia la risposta in base al tipo di update
    if update.callback_query:
        await update.callback_query.answer()
        await update.callback_query.message.reply_text(
            reply_text,
            reply_markup=reply_markup
        )
    else:
        await update.message.reply_text(
            reply_text,
            reply_markup=reply_markup
        )
    
    return ConversationHandler.END

async def show_list(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Display the current shopping list with buttons for each item."""
    user_id = update.effective_user.id
    items = shopping_list.get_items(user_id)
    
    # Handle both message and callback query
    if update.callback_query:
        await update.callback_query.answer()
        message = update.callback_query.message
    else:
        message = update.message
    
    if not items:
        await message.reply_text(LIST_EMPTY_MSG)
        return
    
    message_text = LIST_HEADER_MSG + "\n\n"
    keyboard = []
    
    for index, item in enumerate(items, start=1):
        # Format: 1. Patate (2 kg)
        item_name = item["name"]
        quantity = item["quantity"]
        message_text += f"{index}. {item_name} ({quantity})\n"
        
        # Add buttons for each item
        keyboard.append([
            InlineKeyboardButton(f"🗑️ {index}", callback_data=f"{CB_REMOVE}:{index-1}"),
            InlineKeyboardButton(f"📝 {index}", callback_data=f"{CB_SET_QTY}:{index-1}")
        ])
    
    # Add common action buttons
    keyboard.append([
        InlineKeyboardButton("➕ Aggiungi", callback_data=CB_ADD),
        InlineKeyboardButton("🧹 Svuota", callback_data=CB_CLEAR)
    ])
    
    await message.reply_text(
        message_text,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode=ParseMode.MARKDOWN
    )

async def start_removing_item(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Start the conversation to remove an item."""
    if update.message and update.message.text and update.message.text.startswith("/rimuovi"):
        # Command format: /rimuovi <index>
        text = update.message.text.split(" ", 1)
        if len(text) > 1:
            try:
                index = int(text[1].strip()) - 1
                return await process_remove_item(update, context, index)
            except ValueError:
                await update.message.reply_text("Inserisci un numero valido.")
                return ConversationHandler.END
    
    user_id = update.effective_user.id
    items = shopping_list.get_items(user_id)
    
    # Check if the list is empty
    if not items:
        # Handle both message and callback query
        if update.callback_query:
            await update.callback_query.answer()
            await update.callback_query.message.reply_text("La tua lista della spesa è vuota.")
        else:
            await update.message.reply_text("La tua lista della spesa è vuota.")
        return ConversationHandler.END
    
    message = "Quale articolo vuoi rimuovere? Inserisci il numero:\n\n"
    for index, item in enumerate(items, start=1):
        item_name = item["name"]
        quantity = item["quantity"]
        message += f"{index}. {item_name} ({quantity})\n"
    
    keyboard = []
    row = []
    
    # Create a grid of number buttons, 3 per row
    for index in range(1, len(items) + 1):
        row.append(InlineKeyboardButton(str(index), callback_data=f"{CB_REMOVE}:{index-1}"))
        if len(row) == 3 or index == len(items):
            keyboard.append(row)
            row = []
    
    keyboard.append([InlineKeyboardButton(BTN_CANCEL, callback_data=CB_CANCEL)])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    # Handle both message and callback query
    if update.callback_query:
        await update.callback_query.answer()
        await update.callback_query.message.reply_text(
            message,
            reply_markup=reply_markup
        )
    else:
        await update.message.reply_text(
            message,
            reply_markup=reply_markup
        )
    
    return STATE_WAITING_REMOVE

async def process_remove_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Process callback for removing an item."""
    query = update.callback_query
    await query.answer()
    
    if query.data == CB_CANCEL:
        await query.message.edit_text("Operazione annullata.")
        return ConversationHandler.END
    
    # Extract the index from the callback data
    try:
        _, index_str = query.data.split(":")
        index = int(index_str)
        return await process_remove_item(update, context, index)
    except (ValueError, IndexError):
        await query.message.edit_text("Errore: indice non valido. Riprova.")
        return ConversationHandler.END

async def process_remove_item(update: Update, context: ContextTypes.DEFAULT_TYPE, index) -> int:
    """Remove an item from the shopping list by index."""
    user_id = update.effective_user.id
    
    try:
        removed_item = shopping_list.remove_item(user_id, index)
        
        if removed_item:
            reply_text = ITEM_REMOVED_MSG.format(item=removed_item["name"])
            
            # Reply based on the type of update
            if update.callback_query:
                await update.callback_query.message.edit_text(
                    reply_text,
                    reply_markup=InlineKeyboardMarkup([[
                        InlineKeyboardButton("📋 Mostra Lista", callback_data=CB_SHOW)
                    ]])
                )
            else:
                await update.message.reply_text(
                    reply_text,
                    reply_markup=InlineKeyboardMarkup([[
                        InlineKeyboardButton("📋 Mostra Lista", callback_data=CB_SHOW)
                    ]])
                )
        else:
            reply_text = "Numero non valido. Usa /lista per vedere i numeri degli articoli."
            
            if update.callback_query:
                await update.callback_query.message.edit_text(reply_text)
            else:
                await update.message.reply_text(reply_text)
    except Exception as e:
        logger.error(f"Error removing item: {e}")
        reply_text = "Si è verificato un errore. Riprova."
        
        if update.callback_query:
            await update.callback_query.message.edit_text(reply_text)
        else:
            await update.message.reply_text(reply_text)
    
    return ConversationHandler.END

async def start_setting_quantity(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Start the conversation to set item quantity."""
    query = update.callback_query
    await query.answer()
    
    # Extract the index from the callback data
    try:
        _, index_str = query.data.split(":")
        index = int(index_str)
        user_id = update.effective_user.id
        items = shopping_list.get_items(user_id)
        
        if 0 <= index < len(items):
            item = items[index]
            context.user_data["current_item_index"] = index
            context.user_data["current_item_name"] = item["name"]
            
            await query.message.edit_text(
                QUANTITY_PROMPT.format(item=item["name"]),
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton(BTN_CANCEL, callback_data=CB_CANCEL)
                ]])
            )
            return STATE_WAITING_QUANTITY
        else:
            await query.message.edit_text("Errore: articolo non trovato.")
            return ConversationHandler.END
    except (ValueError, IndexError):
        await query.message.edit_text("Errore: indice non valido. Riprova.")
        return ConversationHandler.END

async def process_set_quantity(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Process the new quantity for an item."""
    if update.callback_query and update.callback_query.data == CB_CANCEL:
        await update.callback_query.message.edit_text("Operazione annullata.")
        return ConversationHandler.END
    
    user_id = update.effective_user.id
    new_quantity = update.message.text.strip()
    
    if "current_item_index" in context.user_data:
        index = context.user_data["current_item_index"]
        item_name = context.user_data["current_item_name"]
        
        success = shopping_list.update_quantity(user_id, index, new_quantity)
        
        if success:
            await update.message.reply_text(
                QUANTITY_UPDATED_MSG.format(item=item_name, quantity=new_quantity),
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton("📋 Mostra Lista", callback_data=CB_SHOW)
                ]])
            )
        else:
            await update.message.reply_text("Si è verificato un errore. Riprova.")
    else:
        await update.message.reply_text("Si è verificato un errore. Riprova dall'inizio.")
    
    # Clear the user data
    if "current_item_index" in context.user_data:
        del context.user_data["current_item_index"]
    if "current_item_name" in context.user_data:
        del context.user_data["current_item_name"]
    
    return ConversationHandler.END

async def clear_list(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Clear the entire shopping list."""
    user_id = update.effective_user.id
    
    # Create confirmation keyboard
    keyboard = [
        [
            InlineKeyboardButton("✅ Sì, svuota la lista", callback_data=f"{CB_CLEAR}:confirm"),
            InlineKeyboardButton("❌ No, mantieni", callback_data=CB_CANCEL)
        ]
    ]
    
    if update.callback_query:
        query = update.callback_query
        await query.answer()
        
        if "confirm" in query.data:
            # User confirmed clearing the list
            shopping_list.clear_list(user_id)
            await query.message.edit_text(LIST_CLEARED_MSG)
        else:
            # Ask for confirmation
            await query.message.edit_text(
                "Sei sicuro di voler svuotare l'intera lista della spesa?",
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
    else:
        # Ask for confirmation
        await update.message.reply_text(
            "Sei sicuro di voler svuotare l'intera lista della spesa?",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

async def cancel_operation(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Cancel the current conversation."""
    if update.callback_query:
        await update.callback_query.answer()
        await update.callback_query.message.edit_text("Operazione annullata.")
    else:
        await update.message.reply_text("Operazione annullata.")
    
    return ConversationHandler.END

async def suggest(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Get AI-powered suggestions based on the current shopping list."""
    user_id = update.effective_user.id
    items = shopping_list.get_items(user_id)
    item_names = [item["name"] for item in items]  # Extract just the names for AI
    
    # Handle both message and callback query
    if update.callback_query:
        await update.callback_query.answer()
        message = update.callback_query.message
    else:
        message = update.message
    
    if not items:
        await message.reply_text("La tua lista è vuota. Aggiungi alcuni articoli prima di chiedere suggerimenti.")
        return
    
    status_message = await message.reply_text("Generando suggerimenti... Questo potrebbe richiedere alcuni secondi.")
    
    try:
        suggestions = await ai_assistant.get_suggestions(item_names)
        await status_message.delete()
        await message.reply_text(
            SUGGEST_RESPONSE_MSG.format(suggestions=suggestions),
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("➕ Aggiungi alla lista", callback_data=CB_ADD)],
                [InlineKeyboardButton("📋 Mostra lista", callback_data=CB_SHOW)]
            ])
        )
    except Exception as e:
        logger.error(f"Error in suggest command: {e}")
        await status_message.delete()
        await message.reply_text(ERROR_MSG)

async def start_ai_question(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Start the conversation to ask AI a question."""
    if update.message and update.message.text and update.message.text.startswith("/ai"):
        # Command format: /ai <question>
        text = update.message.text.split(" ", 1)
        if len(text) > 1:
            question = text[1].strip()
            context.user_data["question"] = question
            return await process_ai_question(update, context)
    
    await update.message.reply_text(
        "Cosa vuoi chiedermi riguardo la tua lista della spesa?\n\n"
        "Esempio: Cosa posso cucinare con questi ingredienti?\n\n"
        "Per annullare, premi Annulla o digita /annulla.",
        reply_markup=InlineKeyboardMarkup([[
            InlineKeyboardButton(BTN_CANCEL, callback_data=CB_CANCEL)
        ]])
    )
    return STATE_WAITING_QUESTION

async def process_ai_question(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Process the AI question."""
    user_id = update.effective_user.id
    
    if "question" in context.user_data:
        question = context.user_data["question"]
    else:
        if update.callback_query:
            if update.callback_query.data == CB_CANCEL:
                await update.callback_query.message.edit_text("Operazione annullata.")
                return ConversationHandler.END
            
        question = update.message.text
    
    items = shopping_list.get_items(user_id)
    item_names = [item["name"] for item in items]  # Extract just the names for AI
    
    if not items:
        if update.callback_query:
            await update.callback_query.message.edit_text("La tua lista è vuota. Aggiungi alcuni articoli prima.")
        else:
            await update.message.reply_text("La tua lista è vuota. Aggiungi alcuni articoli prima.")
        return ConversationHandler.END
    
    if update.callback_query:
        status_message = await update.callback_query.message.edit_text("Pensando... Questo potrebbe richiedere alcuni secondi.")
    else:
        status_message = await update.message.reply_text("Pensando... Questo potrebbe richiedere alcuni secondi.")
    
    try:
        answer = await ai_assistant.answer_question(item_names, question)
        
        # Remove the "thinking" message and send the answer
        if update.message and not update.callback_query:
            await status_message.delete()
            await update.message.reply_text(answer)
        else:
            await status_message.edit_text(answer)
    except Exception as e:
        logger.error(f"Error in ai_help command: {e}")
        if update.message and not update.callback_query:
            await status_message.delete()
            await update.message.reply_text(ERROR_MSG)
        else:
            await status_message.edit_text(ERROR_MSG)
    
    # Clear the user data
    if "question" in context.user_data:
        del context.user_data["question"]
    
    return ConversationHandler.END

async def categorize(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Categorize items in the shopping list."""
    user_id = update.effective_user.id
    items = shopping_list.get_items(user_id)
    item_names = [item["name"] for item in items]  # Extract just the names for AI
    
    # Handle both message and callback query
    if update.callback_query:
        await update.callback_query.answer()
        message = update.callback_query.message
    else:
        message = update.message
    
    if not items:
        await message.reply_text("La tua lista è vuota. Aggiungi alcuni articoli prima di categorizzarli.")
        return
    
    status_message = await message.reply_text("Organizzando la tua lista in categorie... Questo potrebbe richiedere alcuni secondi.")
    
    try:
        categories = await ai_assistant.categorize_items(item_names)
        await status_message.delete()
        await message.reply_text(
            categories,
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("📋 Mostra lista", callback_data=CB_SHOW)],
                [InlineKeyboardButton("💡 Suggerimenti", callback_data=CB_SUGGEST)]
            ])
        )
    except Exception as e:
        logger.error(f"Error in categorize command: {e}")
        await status_message.delete()
        await message.reply_text(ERROR_MSG)

async def meal_plan(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Generate a meal plan based on items in the shopping list."""
    user_id = update.effective_user.id
    items = shopping_list.get_items(user_id)
    item_names = [item["name"] for item in items]  # Extract just the names for AI
    
    # Handle both message and callback query
    if update.callback_query:
        await update.callback_query.answer()
        message = update.callback_query.message
    else:
        message = update.message
    
    if not items:
        await message.reply_text("La tua lista è vuota. Aggiungi alcuni articoli prima di generare un piano pasti.")
        return
    
    status_message = await message.reply_text("Generando un piano dei pasti basato sulla tua lista... Questo potrebbe richiedere alcuni secondi.")
    
    try:
        meal_plan_text = await ai_assistant.generate_meal_plan(item_names)
        await status_message.delete()
        await message.reply_text(
            meal_plan_text,
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("📋 Mostra lista", callback_data=CB_SHOW)],
                [InlineKeyboardButton("💡 Suggerimenti", callback_data=CB_SUGGEST)]
            ])
        )
    except Exception as e:
        logger.error(f"Error in meal_plan command: {e}")
        await status_message.delete()
        await message.reply_text(ERROR_MSG)

async def handle_button_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle messages with main menu button text."""
    text = update.message.text
    
    if text == BTN_ADD:
        return await start_adding_item(update, context)
    elif text == BTN_LIST:
        await show_list(update, context)
    elif text == BTN_REMOVE:
        return await start_removing_item(update, context)
    elif text == BTN_CLEAR:
        await clear_list(update, context)
    elif text == BTN_SUGGEST:
        await suggest(update, context)
    elif text == BTN_CATEGORIES:
        await categorize(update, context)
    elif text == BTN_MEAL_PLAN:
        await meal_plan(update, context)
    elif text == BTN_HELP:
        await help_command(update, context)

async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle callback queries that are not handled by conversation handlers."""
    query = update.callback_query
    data = query.data
    
    if data.startswith(CB_ADD):
        await query.answer()
        return await start_adding_item(update, context)
    elif data == CB_SHOW:
        await query.answer()
        await show_list(update, context)
    elif data.startswith(CB_CLEAR) and not ":" in data:
        await query.answer()
        await clear_list(update, context)
    elif data.startswith(CB_SUGGEST):
        await query.answer()
        await suggest(update, context)
    elif data.startswith(CB_CATEGORIES):
        await query.answer() 
        await categorize(update, context)
    elif data.startswith(CB_MEAL):
        await query.answer()
        await meal_plan(update, context)
    elif data == CB_CANCEL:
        await query.answer()
        await query.message.edit_text("Operazione annullata.")
    else:
        # Per altri callback queries che non vengono gestiti altrove
        await query.answer("Operazione non riconosciuta")


if __name__ == "__main__":
    # This code only runs when the script is executed directly, not when imported
    token = os.environ.get("TELEGRAM_TOKEN")
    if not token:
        logger.error("TELEGRAM_TOKEN environment variable not set!")
        sys.exit(1)
    
    # Create the Application
    application = ApplicationBuilder().token(token).build()
    
    # Add conversation handlers
    add_item_conv = ConversationHandler(
        entry_points=[
            CommandHandler("aggiungi", start_adding_item),
            CallbackQueryHandler(start_adding_item, pattern=f"^{CB_ADD}$")
        ],
        states={
            STATE_WAITING_ITEM: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, process_add_item),
                CallbackQueryHandler(cancel_operation, pattern=f"^{CB_CANCEL}$")
            ],
        },
        fallbacks=[CommandHandler("annulla", cancel_operation)],
    )
    
    remove_item_conv = ConversationHandler(
        entry_points=[
            CommandHandler("rimuovi", start_removing_item),
            CallbackQueryHandler(process_remove_callback, pattern=f"^{CB_REMOVE}:")
        ],
        states={
            STATE_WAITING_REMOVE: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, process_remove_item),
                CallbackQueryHandler(process_remove_callback, pattern=f"^{CB_REMOVE}:"),
                CallbackQueryHandler(cancel_operation, pattern=f"^{CB_CANCEL}$")
            ],
        },
        fallbacks=[CommandHandler("annulla", cancel_operation)],
    )
    
    set_quantity_conv = ConversationHandler(
        entry_points=[
            CallbackQueryHandler(start_setting_quantity, pattern=f"^{CB_SET_QTY}:")
        ],
        states={
            STATE_WAITING_QUANTITY: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, process_set_quantity),
                CallbackQueryHandler(cancel_operation, pattern=f"^{CB_CANCEL}$")
            ],
        },
        fallbacks=[CommandHandler("annulla", cancel_operation)],
    )
    
    ai_question_conv = ConversationHandler(
        entry_points=[
            CommandHandler("ai", start_ai_question)
        ],
        states={
            STATE_WAITING_QUESTION: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, process_ai_question),
                CallbackQueryHandler(cancel_operation, pattern=f"^{CB_CANCEL}$")
            ],
        },
        fallbacks=[CommandHandler("annulla", cancel_operation)],
    )
    
    # Add command handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("aiuto", help_command))
    application.add_handler(CommandHandler("lista", show_list))
    application.add_handler(CommandHandler("svuota", clear_list))
    application.add_handler(CommandHandler("suggerisci", suggest))
    application.add_handler(CommandHandler("categorie", categorize))
    application.add_handler(CommandHandler("pasti", meal_plan))
    
    # Add conversation handlers
    application.add_handler(add_item_conv)
    application.add_handler(remove_item_conv)
    application.add_handler(set_quantity_conv)
    application.add_handler(ai_question_conv)
    
    # Add handlers for button messages
    application.add_handler(MessageHandler(
        filters.TEXT & ~filters.COMMAND,
        handle_button_message
    ))
    
    # Add callback query handler
    application.add_handler(CallbackQueryHandler(handle_callback))
    
    # Start the Bot
    logger.info("Starting bot polling...")
    application.run_polling(allowed_updates=["message", "callback_query"])