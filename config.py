import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Credentials
CLIENT_ID = os.getenv("CLIENT_ID")
TENANT_ID = os.getenv("TENANT_ID")
EMAIL_API_BASE_URL = os.getenv("EMAIL_API_BASE_URL", "https://graph.microsoft.com/v1.0")
# scope_string = os.getenv("SCOPES")
SCOPES = os.getenv("SCOPES").split(",")
