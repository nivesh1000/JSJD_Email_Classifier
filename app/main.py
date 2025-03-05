from flask import Flask, jsonify, request
from apscheduler.schedulers.background import BackgroundScheduler
import threading
import time
from Token_Refresher.token_refresher import TokenManager
from api.get_filters import fetch_groups

app = Flask(__name__)

# Function that fetches, filters, groups, and posts emails
def fetch_process_post_emails():
    token_manager = TokenManager()
    try:
        token_manager.refresh_tokens()
        print("Refreshed tokens successfully")
    except Exception as e:
        print(f"Error during token refresh: {e}")
    


# Function to delete emails from inbox (API-based)
@app.route('/delete-emails', methods=['POST'])
def delete_emails():
    pass

    return jsonify({'message': 'Emails deleted successfully!'}), 200


# Scheduler setup to run fetch_process_post_emails at 12 AM UTC
scheduler = BackgroundScheduler()
scheduler.add_job(fetch_process_post_emails, 'cron', hour=0, minute=0)
scheduler.start()

# Run Flask app
if __name__ == '__main__':
    app.run(debug=True, use_reloader=False)  # `use_reloader=False` avoids duplicate jobs
