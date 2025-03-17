import threading

fetch_emails = threading.Event()

process_redis = threading.Event()