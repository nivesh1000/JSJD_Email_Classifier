import threading

fetch_emails = threading.Event()

process_redis = threading.Event()

process_redis.set()
fetch_emails.clear()
