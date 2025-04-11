import os
import redis
from dotenv import load_dotenv
# import threading


# Load environment variables from .env file
load_dotenv()

# Load variables
CLIENT_ID = os.getenv("CLIENT_ID")

TENANT_ID = os.getenv("TENANT_ID")

DELETE_BASE_URL = os.getenv("DELETE_BASE_URL")

EMAIL_API_BASE_URL = os.getenv("EMAIL_API_BASE_URL")

GET_FILTER_API = os.getenv("GET_FILTER_API")

USER_EMAIL_ADDRESS = os.getenv("USER_EMAIL_ADDRESS")

SCOPES = os.getenv("SCOPES").split(",")

API_AUTHENTICATION_KEY = os.getenv("API_AUTHENTICATION_KEY")

# Redis intialize
redis_client = redis.Redis(host="localhost", port=6379, db=0, decode_responses=True)

redis_lock = redis_client.lock("redis-mutex", timeout=60.0)


# redis_lock = threading.RLock()