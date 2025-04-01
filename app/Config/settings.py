import os
import redis
from dotenv import load_dotenv
import threading


# Load environment variables from .env file
load_dotenv()

# Required variables — Ensures essential values are always present
REQUIRED_VARS = [
    "CLIENT_ID",
    "TENANT_ID",
    "DELETE_BASE_URL",
    "EMAIL_API_BASE_URL",
    "GET_FILTER_API",
    "SCOPES",
    "API_AUTHENTICATION_KEY",
]

# Validate required variables are present
missing_vars = [var for var in REQUIRED_VARS if not os.getenv(var)]
if missing_vars:
    raise EnvironmentError(
        f"Missing required environment variables: {', '.join(missing_vars)}"
    )

# Load variables
CLIENT_ID = os.getenv("CLIENT_ID")

TENANT_ID = os.getenv("TENANT_ID")

DELETE_BASE_URL = os.getenv("DELETE_BASE_URL")

EMAIL_API_BASE_URL = os.getenv("EMAIL_API_BASE_URL")

GET_FILTER_API = os.getenv("GET_FILTER_API")

SCOPES = os.getenv("SCOPES").split(",")

API_AUTHENTICATION_KEY = os.getenv("API_AUTHENTICATION_KEY")

# Redis intialize
redis_client = redis.Redis(host="localhost", port=6379, db=0, decode_responses=True)

# redis_lock = redis_client.lock("redis-mutex")


redis_lock = threading.RLock()