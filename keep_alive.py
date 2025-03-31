
"""
Keep alive module for Replit projects.
This prevents the bot from going to sleep when deployed.
"""

from flask import Flask, jsonify
from threading import Thread
import time
import logging

logger = logging.getLogger(__name__)

# Small Flask app for keep-alive pings
keep_alive_app = Flask('keep_alive')

@keep_alive_app.route('/')
def home():
    """Home route that confirms the bot is alive."""
    return jsonify({
        "status": "online",
        "message": "Bot server is active",
        "timestamp": time.time()
    })

def run_keep_alive():
    """Run the Flask app on a separate port."""
    # Use a different port than the main app (5000)
    keep_alive_app.run(host='0.0.0.0', port=9191)

def start_keep_alive_server():
    """Start the keep-alive server in a separate thread."""
    logger.info("Starting keep-alive server on port 9191...")
    keep_alive_thread = Thread(target=run_keep_alive)
    # Set as daemon so it automatically terminates when main program exits
    keep_alive_thread.daemon = True
    keep_alive_thread.start()
    logger.info("Keep-alive server started")
    return keep_alive_thread
