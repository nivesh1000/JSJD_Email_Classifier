import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Required variables — Ensures essential values are always present
REQUIRED_VARS = ["CLIENT_ID", "TENANT_ID", "DELETE_BASE_URL", "EMAIL_API_BASE_URL","GET_FILTER_API", "SCOPES"]

# Validate required variables are present
missing_vars = [var for var in REQUIRED_VARS if not os.getenv(var)]
if missing_vars:
    raise EnvironmentError(f"Missing required environment variables: {', '.join(missing_vars)}")

# Load variables
CLIENT_ID = os.getenv("CLIENT_ID")
TENANT_ID = os.getenv("TENANT_ID")
DELETE_BASE_URL = os.getenv("DELETE_BASE_URL")
EMAIL_API_BASE_URL = os.getenv("EMAIL_API_BASE_URL")
GET_FILTER_API = os.getenv("GET_FILTER_API")
SCOPES = os.getenv("SCOPES").split(",")