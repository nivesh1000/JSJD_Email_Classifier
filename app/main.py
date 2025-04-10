from threading import Thread
from app.Delete_Emails.delete_emails import delete_emails
from app.Logger.logger import JsJdLogger, LineFileProvider
from flask import Flask, jsonify, request, abort
from app.Config.settings import API_AUTHENTICATION_KEY
from app.Scheduler.scheduler import fetch_process_post_emails
from apscheduler.schedulers.background import BackgroundScheduler
import os
# Logger initialize
logger = JsJdLogger()

# Flask app setup
app = Flask(__name__)


@app.route("/delete-emails", methods=["POST"])
def email_deletion():
    client_key = os.getenv("API_AUTHENTICATION_KEY")

    if client_key != API_AUTHENTICATION_KEY:
        abort(403, description="Forbidden: Invalid API Key")
    try:
        data = request.json
        if not data or "delete_emails" not in data:
            return jsonify({"error": "Invalid request. Provide 'delete_emails'."}), 400

        emails_to_remove = data["delete_emails"]
        return delete_emails(emails_to_remove)

    except Exception as e:
        logger.error(
            f"Error in email_deletion API: {e}", LineFileProvider().get_file_info()
        )
        return jsonify({"error": "Internal server error"}), 500


def run_fetch_process_post_emails():
    """This function runs fetch_process_post_emails inside a new thread and joins it."""
    thread = Thread(target=fetch_process_post_emails)
    thread.start()
    thread.join()  # Ensure the thread completes before moving on


def start_scheduler():
    """Scheduler runs fetch_process_post_emails inside a new thread each time."""
    scheduler = BackgroundScheduler()
    scheduler.add_job(run_fetch_process_post_emails, "cron", minute="*/3")  # Every n min
    scheduler.start()


# Start scheduler
start_scheduler()

# Run Flask app
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
