from flask import Flask, jsonify, request
from apscheduler.schedulers.background import BackgroundScheduler
from threading import Thread
from dotenv import load_dotenv
import os
from Email_Deletion.delete_emails import delete_emails
from logger import get_logger
from Scheduler.scheduler import fetch_process_post_emails

logger = get_logger(__name__)

# Load environment variables
load_dotenv()

ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")

# Flask app setup
app = Flask(__name__)


# Function to delete emails from inbox (API-based)
@app.route('/delete-emails', methods=['POST'])
def email_deletion():
    try:
        data = request.json
        if not data or 'delete_emails' not in data:
            return jsonify({"error": "Invalid request. Provide 'delete_emails'."}), 400

        emails_to_remove = data['delete_emails']
        success, deleted_count = delete_emails(emails_to_remove, ACCESS_TOKEN)
        
        if success:
            return jsonify({"message": f"{deleted_count} emails deleted successfully"}), 200
        else:
            return jsonify({"error": "Failed to delete some emails"}), 500

    except Exception as e:
        logger.error(f"Error in email_deletion API: {e}")
        return jsonify({"error": "Internal server error"}), 500

# Scheduler setup to run fetch_process_post_emails at 12 AM UTC
def start_scheduler():
    scheduler = BackgroundScheduler()
    scheduler.add_job(fetch_process_post_emails, 'cron', hour=0, minute=0)
    scheduler.start()

# Start scheduler in a separate thread
Thread(target=start_scheduler).start()

# Run Flask app
if __name__ == '__main__':
    app.run(debug=True, use_reloader=False)  # `use_reloader=False` avoids duplicate jobs
