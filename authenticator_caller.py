from authenticator import UserAuthenticator
# Usage Example:
if __name__ == "__main__":
    # Initialize the singleton
    authenticator = UserAuthenticator()

    # Retrieve the singleton instance
    auth_instance = UserAuthenticator.get_instance()

    # Authenticate the user and retrieve the access token
    access_token = auth_instance.authenticate_user()