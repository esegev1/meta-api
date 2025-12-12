import os
import requests
from datetime import datetime
from dotenv import load_dotenv, set_key

load_dotenv()

BASE_URL = os.getenv('META_BASE_URL')
print(f"Base URL: {BASE_URL}")

def check_and_refresh_token():
    """Check token expiry and refresh if needed"""
    
    
    current_token = os.getenv('META_ACCESS_TOKEN')
    app_id = os.getenv('META_APP_ID')
    app_secret = os.getenv('META_SECRET_KEY')
    
    # Check token info
    debug_url = f"{BASE_URL}/debug_token"
    params = {
        'input_token': current_token,
        'access_token': current_token
    }
    
    response = requests.get(debug_url, params=params)
    print("response", response)
    token_info = response.json()['data']
    
    expires_at = token_info.get('expires_at', 0)
    print("expires: ", expires_at)
    
    # If token expires in less than 7 days, refresh it
    if expires_at > 0:
        days_until_expiry = (expires_at - datetime.now().timestamp()) / 86400
        
        if days_until_expiry < 200:
            print(f"Token expires in {days_until_expiry:.1f} days. Refreshing...")
            
            # Exchange for new long-lived token
            refresh_url = f"{BASE_URL}/oauth/access_token"
            refresh_params = {
                'grant_type': 'fb_exchange_token',
                'client_id': app_id,
                'client_secret': app_secret,
                'fb_exchange_token': current_token
            }
            
            refresh_response = requests.get(refresh_url, params=refresh_params)
            print("refresh response: ", refresh_response)
            new_token = refresh_response.json()['access_token']
            
            # Update .env file
            set_key('.env', 'META_ACCESS_TOKEN', new_token, quote_mode='never')
            print("Token refreshed successfully!")
            
            return new_token
        else:
            print(f"Token still valid for {days_until_expiry:.1f} days")
            return current_token
    
    return current_token

if __name__ == "__main__":
    check_and_refresh_token()