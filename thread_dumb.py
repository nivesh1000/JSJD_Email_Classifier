import threading
import time
import redis
import json
from queue import Queue

# Redis connection (assumes Redis is running locally)
redis_client = redis.Redis(host='localhost', port=6379, db=0)

# Queue to pass emails between threads
email_queue = Queue()

# Event object to signal when fetching is done
fetch_complete_event = threading.Event()

# Mock function to simulate fetching a batch of emails
def fetch_email_batch(batch_size=5):
    emails = []
    for i in range(1, batch_size + 1):
        time.sleep(1)  # Simulate network delay
        email = {
            "id": i,
            "subject": f"Subject of email {i}",
            "from": "sender@example.com",
            "body": f"This is the body of email {i}"
        }
        emails.append(email)
    return emails

# Thread 1: Fetch emails and signal when done
def fetcher_thread():
    print(f"{threading.current_thread().name} starting to fetch emails...")
    
    # Fetch a batch of emails
    email_batch = fetch_email_batch(batch_size=5)
    
    # Put emails into the queue for the storer thread
    for email in email_batch:
        email_queue.put(email)
    
    print(f"{threading.current_thread().name} finished fetching {len(email_batch)} emails.")
    
    # Signal that fetching is complete
    fetch_complete_event.set()
    
    # Thread 1 waits here (optional, could exit instead)
    print(f"{threading.current_thread().name} waiting for storer to finish...")
    time.sleep(5)  # Simulate waiting (or use another Event if needed)
    print(f"{threading.current_thread().name} exiting.")

# Thread 2: Store emails in Redis after fetch is complete
def storer_thread():
    print(f"{threading.current_thread().name} waiting for fetcher to complete...")
    
    # Wait for the fetcher to finish
    fetch_complete_event.wait()
    print(f"{threading.current_thread().name} detected fetch complete, starting storage...")
    
    # Process emails from the queue
    while not email_queue.empty():
        email = email_queue.get()
        redis_key = f"email:{email['id']}"
        redis_client.set(redis_key, json.dumps(email))
        print(f"{threading.current_thread().name} stored email {email['id']} in Redis")
        email_queue.task_done()
    
    print(f"{threading.current_thread().name} finished storing all emails.")

# Main function to manage threads
def main():
    # Initially, the event is not set (False)
    fetch_complete_event.clear()
    
    # Create threads
    fetcher = threading.Thread(target=fetcher_thread, name="Fetcher-Thread")
    storer = threading.Thread(target=storer_thread, name="Storer-Thread")
    
    # Start threads
    fetcher.start()
    storer.start()
    
    # Wait for both threads to complete
    fetcher.join()
    storer.join()
    
    print("Main: All threads have completed!")
    
    # Optional: Verify Redis contents
    print("\nChecking Redis contents:")
    for key in redis_client.keys("email:*"):
        email_data = json.loads(redis_client.get(key))
        print(f"{key.decode()}: {email_data['subject']}")

if __name__ == "__main__":
    main()