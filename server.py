from flask import Flask, request, jsonify
app = Flask(__name__)

from flask_cors import CORS
CORS(app)

# Only allow your React frontend DO THIS FOR DEPLOYMENT 
# CORS(app, resources={
#     r"/*": {
#         "origins": ["http://localhost:5173", "https://yourdomain.com"],
#         "methods": ["GET", "POST", "PUT", "DELETE"],
#         "allow_headers": ["Content-Type"]
#     }
# })

# ADD THIS - Load environment variables from .env file
from dotenv import load_dotenv
load_dotenv()

import os
import hashlib
import hmac

from app.services.webhook import *
from app.services.database import DBService

# Load environment variables
VERIFY_TOKEN = os.getenv('META_VERIFY_TOKEN')
APP_SECRET = os.getenv('META_SECRET_KEY')
PORT = os.getenv('PORT')

# Debug: Check if loaded
print("="*60)
print("🔍 ENVIRONMENT VARIABLES:")
print(f"VERIFY_TOKEN: {VERIFY_TOKEN}")
print(f"APP_SECRET: {APP_SECRET[:10] if APP_SECRET else None}... (loaded: {bool(APP_SECRET)})")
print("="*60)

@app.before_request
def log_all_requests():
    print(f'\n>>> Incoming: {request.method} {request.full_path}')
    print(f'>>> From: {request.remote_addr}')
    print('\n' + '='*60)
    print(f'📥 REQUEST RECEIVED')
    print(f'Method: {request.method}')
    print(f'Path: {request.path}')
    print(f'Full Path: {request.full_path}')
    print(f'URL: {request.url}')
    print(f'Remote Address: {request.remote_addr}')
    print(f'Args: {dict(request.args)}')
    print('='*60 + '\n')

# Homepage
@app.route("/", methods=['GET'])  # Fixed from @app.get()
def homepage():
    return 'hello'

# Webhook verification (GET)
@app.route('/webhook', methods=['GET'])
def webhook_verify():
    print('=' * 50)
    print('WEBHOOK GET REQUEST')
    print('=' * 50)
    
    mode = request.args.get('hub.mode')
    token = request.args.get('hub.verify_token')
    challenge = request.args.get('hub.challenge')
    
    print(f"Mode: '{mode}'")
    print(f"Token received: '{token}'")
    print(f"VERIFY_TOKEN expected: '{VERIFY_TOKEN}'")
    print(f"Match: {token == VERIFY_TOKEN}")
    
    if mode == 'subscribe' and token == VERIFY_TOKEN:
        print('✓ SUCCESS - Returning challenge')
        return challenge, 200
    else:
        print('✗ FAILED')
        if mode != 'subscribe':
            print(f"  - Mode is wrong: '{mode}' (expected 'subscribe')")
        if token != VERIFY_TOKEN:
            print(f"  - Token mismatch!")
            print(f"    Got: '{token}'")
            print(f"    Expected: '{VERIFY_TOKEN}'")
        return 'Forbidden', 403

# Webhook events (POST)
@app.route('/webhook', methods=['POST'])
def webhook_receive():
    webhook_processing(request)
    # print('\n' + '='*60)
    # print('🔔 WEBHOOK POST TRIGGERED')
    # print('='*60)

    # print('Webhook recieved: ', request.get_json())
    
    # signature = request.headers.get('X-Hub-Signature-256')
    
    # if signature and APP_SECRET:
    #     print(f'Verifying signature... (APP_SECRET set: {bool(APP_SECRET)})')
    #     if not verify_signature(request.get_data(), signature):
    #         print('❌ Invalid signature!')
    #         return 'Forbidden', 403
    #     print('✅ Signature valid!')
    # else:
    #     print(f'⚠️  Skipping verification - signature: {bool(signature)}, APP_SECRET: {bool(APP_SECRET)}')

    # data = request.get_json()
    # print('Data: ', data)
    
    # if data.get('object') == 'user':
    #     print('📸 Calling Instagram handler...')
    #     handle_user_webhook(data)
    # else:
    #     print(f'⚠️  Unknown object type: {data.get("object")}')

    # print('Returning EVENT_RECEIVED')
    # print('='*60 + '\n')
    return 'EVENT_RECEIVED', 200





# Initialize the service (do this once, maybe in app setup)
db_service = DBService()

# Posts API routes
# @app.route("/posts", methods=['GET'])
# def query_all_posts():
#     return db_service.get_all_posts()

# @app.route("/posts/<id>", methods=['GET'])
# def query_post_by_id(id):
#     return db_service.get_post_by_id(id)

@app.route("/postlist", methods=['GET'])
def query_post_list():
    conn = None

    try:
        # 1. ACQUIRE CONNECTION
        conn = db_service.get_db_connection()
        
        # 2. PASS CONNECTION TO SERVICE METHOD
        data = db_service.get_post_list(conn)
        
        # 3. COMMIT (if applicable, though SELECTs don't need it)
        conn.commit() 
        
        # 4. RETURN RESPONSE
        return jsonify(data)
    
    except Exception as e:
        # Log the error for debugging
        print(f"Database error during request: {e}")
        # Rollback any pending transactions on failure
        if conn:
            conn.rollback()
        # Re-raise the error to let Flask handle the 500 status
        raise
        
    finally:
        # 5. ENSURE CONNECTION IS CLOSED
        if conn:
            conn.close() # <--- THIS IS THE CRITICAL FIX


@app.route("/activity", methods=['GET'])
def query_all_activity():
    conn = None

    try:
        # 1. ACQUIRE CONNECTION
        conn = db_service.get_db_connection()
        
        # 2. PASS CONNECTION TO SERVICE METHOD
        data = db_service.get_all_activity(conn)
        
        # 3. COMMIT (if applicable, though SELECTs don't need it)
        conn.commit() 
        
        # 4. RETURN RESPONSE
        return jsonify(data)
    
    except Exception as e:
        # Log the error for debugging
        print(f"Database error during request: {e}")
        # Rollback any pending transactions on failure
        if conn:
            conn.rollback()
        # Re-raise the error to let Flask handle the 500 status
        raise
        
    finally:
        # 5. ENSURE CONNECTION IS CLOSED
        if conn:
            conn.close() # <--- THIS IS THE CRITICAL FIX

@app.route("/activity/latest", methods=['GET'])
def query_latest_activity():
    conn = None

    try:
        # 1. ACQUIRE CONNECTION
        conn = db_service.get_db_connection()
        
        # 2. PASS CONNECTION TO SERVICE METHOD
        data = db_service.get_latest_activity(conn)
        
        # 3. COMMIT (if applicable, though SELECTs don't need it)
        conn.commit() 
        
        # 4. RETURN RESPONSE
        return jsonify(data)
    
    except Exception as e:
        # Log the error for debugging
        print(f"Database error during request: {e}")
        # Rollback any pending transactions on failure
        if conn:
            conn.rollback()
        # Re-raise the error to let Flask handle the 500 status
        raise
        
    finally:
        # 5. ENSURE CONNECTION IS CLOSED
        if conn:
            conn.close() # <--- THIS IS THE CRITICAL FIX

@app.route("/activity/<id>", methods=['GET'])
def query_activity_by_id(id):
    conn = None

    try:
        # 1. ACQUIRE CONNECTION
        conn = db_service.get_db_connection()
        
        # 2. PASS CONNECTION TO SERVICE METHOD
        print("id: ", id)
        data = db_service.get_activity_by_id(conn, id)
        
        # 3. COMMIT (if applicable, though SELECTs don't need it)
        conn.commit() 
        
        # 4. RETURN RESPONSE
        return jsonify(data)
    
    except Exception as e:
        # Log the error for debugging
        print(f"Database error during request: {e}")
        # Rollback any pending transactions on failure
        if conn:
            conn.rollback()
        # Re-raise the error to let Flask handle the 500 status
        raise
        
    finally:
        # 5. ENSURE CONNECTION IS CLOSED
        if conn:
            conn.close() # <--- THIS IS THE CRITICAL FIX
    # return db_service.get_activity_by_id(id)

# @app.route("/followers", methods=['GET'])
# def query_follower_counts():
#     return db_service.get_follower_counts()

# @app.route("/followers/now", methods=['GET'])
# def query_latest_followers():
#     return db_service.get_latest_followers()

@app.route("/execsummary", methods=['GET'])
def query_exec_summary_data():
    conn = None

    try:
        # 1. ACQUIRE CONNECTION
        conn = db_service.get_db_connection()
        
        # 2. PASS CONNECTION TO SERVICE METHOD
        data = db_service.get_exec_summary_data(conn)
        
        # 3. COMMIT (if applicable, though SELECTs don't need it)
        conn.commit() 
        
        # 4. RETURN RESPONSE
        return jsonify(data)
    
    except Exception as e:
        # Log the error for debugging
        print(f"Database error during request: {e}")
        # Rollback any pending transactions on failure
        if conn:
            conn.rollback()
        # Re-raise the error to let Flask handle the 500 status
        raise
        
    finally:
        # 5. ENSURE CONNECTION IS CLOSED
        if conn:
            conn.close() # <--- THIS IS THE CRITICAL FIX

    # return db_service.get_exec_summary_data()


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=PORT, debug=True)