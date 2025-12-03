from dotenv import load_dotenv
load_dotenv()

import os
import hashlib
import hmac
import json

# from app.services.meta_api import fetch_meta_data_post
from app.scripts.update_post_metadata import *

import psycopg2
connection = psycopg2.connect(
    database="meta_api_data"
)

import psycopg2.extras
cursor = connection.cursor(cursor_factory = psycopg2.extras.RealDictCursor)

# Load environment variables
VERIFY_TOKEN = os.getenv('META_VERIFY_TOKEN')
APP_SECRET = os.getenv('META_SECRET_KEY')

def webhook_processing(request):
    print('\n' + '='*60)
    print('🔔 WEBHOOK POST TRIGGERED')
    print('='*60)

    print('Webhook recieved: ', request.get_json())
    with open('./app/logs/webhook.log', 'a') as f:
        log_data = request.get_json()
        f.write('NEW WEBHOOK:' + '\n') 
        f.write(json.dumps(log_data) + '\n')  # Convert to string and add newline

    
    signature = request.headers.get('X-Hub-Signature-256')
    
    if signature and APP_SECRET:
        print(f'Verifying signature... (APP_SECRET set: {bool(APP_SECRET)})')
        if not verify_signature(request.get_data(), signature):
            print('❌ Invalid signature!')
            return 'Forbidden', 403
        print('✅ Signature valid!')
    else:
        print(f'⚠️  Skipping verification - signature: {bool(signature)}, APP_SECRET: {bool(APP_SECRET)}')

    data = request.get_json()
    print('Data: ', data)
    
    if data.get('object') == 'user':
        print('📸 Calling Instagram handler...')
        handle_user_webhook(data)
    else:
        print(f'⚠️  Unknown object type: {data.get("object")}')

    print('Returning EVENT_RECEIVED')
    print('='*60 + '\n')    

def handle_user_webhook(data):
    """Handle Instagram webhooks"""
    print('\n🎯 INSTAGRAM WEBHOOK HANDLER')
    print('='*60)
    
    for entry in data.get('entry', []):
        print(f'Processing entry: {entry.get("id")}')
        
        # Handle changes (new posts, etc.)
        for change in entry.get('changes', []):
            field = change.get('field')
            value = change.get('value')
            
            print(f'Field: {field}')
            print(f'Value: {value}')
            
            # When a new post is uploaded
            if field == 'feed':
                post_id = value.get('post_id')
                print(f'🎉 NEW POST DETECTED! Media ID: {post_id}')
                
                update_post_metadata(post_id)
                # all_posts = fetch_meta_data_post(post_id, edge)


                #CALL META API TO BRING BACK DATA PER POST, including trial reel tag
                
                # YOUR CUSTOM LOGIC HERE
                # Example: Save to database
                # try:
                #     cursor.execute(
                #         "INSERT INTO post_metadata (id, post_timestamp, caption, media_type) VALUES (%s, NOW(), %s, %s)",
                #         (media_id, 'New post from webhook', 'IMAGE')
                #     )
                #     connection.commit()
                #     print('✅ Post saved to database!')
                # except Exception as e:
                #     print(f'❌ Error: {e}')
                #     connection.rollback()
        
        # Handle messages
        for messaging_event in entry.get('messaging', []):
            sender_id = messaging_event['sender']['id']
            
            if messaging_event.get('message'):
                message_text = messaging_event['message'].get('text', '')
                print(f'💬 Instagram message from {sender_id}: {message_text}')
    
    print('='*60 + '\n')

def verify_signature(payload, signature):
    """Verify the request signature from Meta"""
    print(f"Verifying signature...")
    print(f"Signature from Meta: {signature}")
    print(f"APP_SECRET: {APP_SECRET[:10]}... (length: {len(APP_SECRET)})")
    
    expected_signature = hmac.new(
        APP_SECRET.encode('utf-8'),
        payload,
        hashlib.sha256
    ).hexdigest()
    
    expected_full = f"sha256={expected_signature}"
    print(f"Expected signature: {expected_full[:30]}...")
    print(f"Match: {hmac.compare_digest(expected_full, signature)}")
    
    return hmac.compare_digest(expected_full, signature)