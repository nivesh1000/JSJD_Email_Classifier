import msal
import logging
import os
import time

class Authenticator:
    _instance = None

    @staticmethod
    def get_instance():
        if Authenticator._instance is None:
            raise Exception("Authenticator not initialized. Use the constructor.")
        return Authenticator._instance

    def __init__(self, tenant_id, client_id, cert_thumbprint, private_key_path):
        if Authenticator._instance is not None:
            raise Exception("This class is a singleton!")
        else:
            Authenticator._instance = self

        # Store credentials
        self.tenant_id = tenant_id
        self.client_id = client_id
        self.cert_thumbprint = cert_thumbprint
        self.private_key_path = private_key_path

        # Load private key
        with open(self.private_key_path, "r") as key_file:
            self.private_key = key_file.read()

        # Ensure that the private key and thumbprint are valid
        if not self.private_key or not self.cert_thumbprint:
            raise ValueError("Certificate thumbprint or private key is missing or invalid.")

        # Create MSAL confidential client with the correct client_credential format
        self.app = msal.ConfidentialClientApplication(
            self.client_id,
            authority=f"https://login.microsoftonline.com/{self.tenant_id}",
            client_credential={
                "thumbprint": self.cert_thumbprint,
                "private_key": self.private_key
            },
        )
        self.token_info = None

    def acquire_token(self):
        try:
            # If the token has expired, refresh it
            if self.token_info and self.is_token_expired():
                logging.info("Token expired, refreshing...")
                self.token_info = None  # Clear expired token

            if not self.token_info:
                # Acquire new token
                result = self.app.acquire_token_for_client(scopes=["https://graph.microsoft.com/.default"])
                if "access_token" in result:
                    self.token_info = result
                    logging.info("Access token acquired successfully.")
                else:
                    raise Exception("Failed to acquire access token.")
            return self.token_info["access_token"]
        except Exception as e:
            logging.error(f"Error acquiring token: {str(e)}")
            raise
