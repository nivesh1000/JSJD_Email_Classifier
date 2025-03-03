from token_refresher import TokenManager

# Usage Example:

if __name__ == "__main__":
    # Initialize the TokenManager
    token_manager = TokenManager()

    # Refresh and update tokens
    try:
        token_manager.refresh_tokens()
        print("Refreshed tokens successfully")
    except Exception as e:
        print(f"Error during token refresh: {e}")
