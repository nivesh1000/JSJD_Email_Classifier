import threading

fetch_emails = threading.Event() 
process_redis = threading.Event()
shutdown = threading.Event() 

def set_initial_events():
    """Set events to their initial state."""
    
    process_redis.set()  # True

    fetch_emails.clear()  # False

    shutdown.clear()
