from flask import Flask, jsonify, request, abort
import sys
from apscheduler.schedulers.background import BackgroundScheduler
from threading import Thread
from dotenv import load_dotenv
import os
from Email_Deletion.delete_emails import delete_emails
from logger import get_logger
from Scheduler.scheduler import fetch_process_post_emails

logger = get_logger()

# Load environment variables
load_dotenv()

ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
if not ACCESS_TOKEN:
    logger.error("ACCESS_TOKEN is missing from environment variables.")
    sys.exit(1)  # Exit since ACCESS_TOKEN is mandatory.

API_KEY = os.getenv("API_KEY")
if not API_KEY:
    logger.error("API_KEY is missing from environment variables. Continue executing...")


# Flask app setup
app = Flask(__name__)


@app.route('/delete-emails', methods=['POST'])
def email_deletion():

    client_key = request.headers.get("X-API-KEY")

    if client_key != API_KEY:
        abort(403, description="Forbidden: Invalid API Key")
    try:
        data = request.json
        if not data or 'delete_emails' not in data:
            return jsonify({"error": "Invalid request. Provide 'delete_emails'."}), 400

        emails_to_remove = data['delete_emails']

        return delete_emails(emails_to_remove, ACCESS_TOKEN)

    except Exception as e:
        logger.error(f"Error in email_deletion API: {e}")
        return jsonify({"error": "Internal server error"}), 500

# # Scheduler setup to run fetch_process_post_emails at 12 AM UTC
# def start_scheduler():
#     scheduler = BackgroundScheduler()
#     scheduler.add_job(fetch_process_post_emails, 'cron', hour=0, minute=0)
#     scheduler.start()


# Scheduler setup to run fetch_process_post_emails every 5 minutes
def start_scheduler():
    scheduler = BackgroundScheduler()
    scheduler.add_job(fetch_process_post_emails, 'cron', minute='*/5')  # Every 5 minutes
    scheduler.start()

# Start scheduler in a separate thread
Thread(target=start_scheduler).start()

# Run Flask app
if __name__ == '__main__':
    app.run(debug=True)
