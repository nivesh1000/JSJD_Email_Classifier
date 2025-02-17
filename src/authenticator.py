import msal

def authenticate(tenant_id: str, client_id: str, cert_thumbprint: str, private_key_path: str) -> str:
    """
    Authenticate with Azure AD using MSAL and return the access token.

    Args:
        tenant_id (str): Azure tenant ID.
        client_id (str): Azure app client ID.
        cert_thumbprint (str): Certificate thumbprint from Azure AD.
        private_key_path (str): Path to the private key file.

    Returns:
        str: Access token if authentication is successful.

    Raises:
        Exception: If authentication fails.
    """
    try:
        # Load the private key
        with open(private_key_path, "r") as key_file:
            private_key = key_file.read()

        # Create MSAL confidential client
        app = msal.ConfidentialClientApplication(
            client_id,
            authority=f"https://login.microsoftonline.com/{tenant_id}",
            client_credential={"thumbprint": cert_thumbprint, "private_key": private_key},
        )

        # Acquire token
        scopes = ["https://graph.microsoft.com/.default"]
        result = app.acquire_token_for_client(scopes=scopes)

        if "access_token" in result:
            return result["access_token"]
        else:
            raise Exception(f"Authentication failed: {result.get('error_description')}")

    except Exception as e:
        raise Exception(f"Error in authentication: {str(e)}")
