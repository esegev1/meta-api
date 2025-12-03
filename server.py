from flask import Flask, request
app = Flask('main')

from flask_cors import CORS
CORS(app)

# ADD THIS - Load environment variables from .env file
from dotenv import load_dotenv
load_dotenv()

import os
import hashlib
import hmac

from app.services.webhook import *

# Load environment variables
VERIFY_TOKEN = os.getenv('META_VERIFY_TOKEN')
APP_SECRET = os.getenv('META_SECRET_KEY')

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



# Posts API routes
@app.route("/posts", methods=['GET'])  # Fixed from @app.get()
def index():
    connection.rollback()
    cursor.execute("SELECT * FROM post_metadata")
    return cursor.fetchall()

@app.route("/posts/<id>", methods=['GET'])  # Fixed from @app.get()
def show():
    connection.rollback()
    cursor.execute("SELECT * FROM post_metadata WHERE id=%s", [id])
    return cursor.fetchall()

@app.route("/activity", methods=['GET'])  # Fixed from @app.get()
def index():
    connection.rollback()
    cursor.execute("SELECT * FROM post_activity")
    return cursor.fetchall()

@app.route("/activity/<id>", methods=['GET'])  # Fixed from @app.get()
def index():
    connection.rollback()
    cursor.execute("SELECT * FROM post_activity WHERE id=%s", [id])
    return cursor.fetchall()








# @app.route("/posts/", methods=['POST'])  # Fixed from @app.post()
# def create():
#     cursor.execute("INSERT INTO post_metadata (id, post_timestamp, caption, media_type) VALUES ('18116623174560971', '2025-11-21T16:04:49+0000', 'Artichoke and spinach potato gratin', 'VIDEO')")
#     connection.commit()
#     return {
#         "success": True
#     }

# @app.route("/posts/<id>", methods=['DELETE'])  # Fixed from @app.delete()
# def delete(id):
#     cursor.execute("DELETE FROM post_metadata WHERE id = %s", [id])
#     connection.commit()
#     return {
#         "success": True
#     }

# @app.route("/posts/<id>", methods=['PUT'])  # Fixed from @app.put()
# def update(id):
#     cursor.execute("UPDATE post_metadata SET caption = %s WHERE id = %s", ('testing...1...2', id))
#     connection.commit()
#     return {
#         "success": True
#     }

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)