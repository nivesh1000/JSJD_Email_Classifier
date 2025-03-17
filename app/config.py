import os
import redis
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Credentials
CLIENT_ID = os.getenv("CLIENT_ID")
TENANT_ID = os.getenv("TENANT_ID")
DELETE_BASE_URL = os.getenv("DELETE_BASE_URL")
EMAIL_API_BASE_URL = os.getenv("EMAIL_API_BASE_URL", "https://graph.microsoft.com/v1.0")
# scope_string = os.getenv("SCOPES")

SCOPES = os.getenv("SCOPES").split(",")

CELERY_BROKER = os.getenv("CELERY_BROKER")
CELERY_BACKEND = os.getenv("CELERY_BACKEND")

ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")

# Redis intialize
redis_client = redis.Redis(host="localhost", port=6379, db=0, decode_responses=True)

redis_lock = redis_client.lock("redis-mutex")
