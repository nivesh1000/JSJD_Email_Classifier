import os
import logging
import requests
from dotenv import load_dotenv, set_key
from config import TENANT_ID, CLIENT_ID, SCOPES
import logging

# Configure logger
logger = logging.getLogger()
logger.setLevel(logging.INFO)


class TokenManager:
    """
    A class for managing access and refresh tokens, including refreshing and updating them in the .env file.
    """

    def __init__(self):
        load_dotenv(
            override=True
        )  # Reload environment variables to ensure the latest values are used
        self.tenant_id = TENANT_ID
        self.client_id = CLIENT_ID
        self.scopes = SCOPES
        self.refresh_token = os.getenv("REFRESH_TOKEN")
        self.access_token = os.getenv("ACCESS_TOKEN")
        self.token_url = (
            f"https://login.microsoftonline.com/{self.tenant_id}/oauth2/v2.0/token"
        )

        if not self.tenant_id or not self.client_id:
            logger.error("Missing required credentials in the configuration.")
            raise ValueError("Missing required credentials in the configuration.")

    def refresh_tokens(self):
        """
        Refreshes the access and refresh tokens using the current refresh token.
        Updates the tokens in the .env file.
        """
        if not self.refresh_token:
            logger.error("Missing REFRESH_TOKEN in the environment variables.")
            raise ValueError("Missing REFRESH_TOKEN in the environment variables.")

        payload = {
            "grant_type": "refresh_token",
            "client_id": self.client_id,
            "refresh_token": self.refresh_token,
            "scope": self.scopes,
        }
        headers = {"Content-Type": "application/x-www-form-urlencoded"}

        try:
            response = requests.post(self.token_url, data=payload, headers=headers)
            response.raise_for_status()
            tokens = response.json()

            new_access_token = tokens.get("access_token")
            new_refresh_token = tokens.get("refresh_token", self.refresh_token)

            if new_access_token:
                logger.info("✅ Tokens refreshed successfully!")
                self.update_tokens_in_env(new_access_token, new_refresh_token)
            else:
                logger.error("❌ Received an empty access token.")
                raise Exception("Token refresh failed: Empty access token.")

        except requests.exceptions.RequestException as e:
            logger.error(f"❌ Failed to refresh tokens: {e}")
            raise Exception(f"Token refresh failed: {str(e)}")

    def update_tokens_in_env(self, access_token: str, refresh_token: str):
        """
        Updates the access and refresh tokens in the .env file.

        Args:
            access_token (str): The new access token to save.
            refresh_token (str): The new refresh token to save.
        """
        env_file = ".env"
        set_key(env_file, "ACCESS_TOKEN", access_token)
        set_key(env_file, "REFRESH_TOKEN", refresh_token)

        # Reload environment variables with new values
        load_dotenv(override=True)

        # Update in-memory variables
        self.access_token = access_token
        self.refresh_token = refresh_token

        logger.info("✅ Tokens updated in the .env file and memory.")
