from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)

# CORS Configuration - Allow credentials and specific origins
CORS(app, resources={
    r"/*": {
        "origins": ["http://localhost:5173", "https://dash.segsy.xyz"],
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"],
        "supports_credentials": True
    }
})

# Import services
from app.services.webhook import webhook_processing
from app.services.database import DBService
from app.services.auth import AuthService, token_required
from app.utils.db_helpers import with_db_connection

# Load environment variables
VERIFY_TOKEN = os.getenv('META_VERIFY_TOKEN')
APP_SECRET = os.getenv('META_SECRET_KEY')
PORT = os.getenv('PORT')

# Startup logging - simplified and secure
print("="*60)
print("🚀 SERVER STARTING")
print(f"✓ VERIFY_TOKEN loaded: {bool(VERIFY_TOKEN)}")
print(f"✓ APP_SECRET loaded: {bool(APP_SECRET)}")
print(f"✓ PORT: {PORT}")
print("="*60)

# Initialize database service
db_service = DBService()

# ============================================
# REQUEST LOGGING (only in debug mode)
# ============================================
if os.getenv('FLASK_DEBUG', 'False') == 'True':
    @app.before_request
    def log_requests():
        print(f'📥 {request.method} {request.path} from {request.remote_addr}')

# ============================================
# PUBLIC ROUTES
# ============================================

@app.route("/", methods=['GET'])
@token_required
def homepage():
    """Health check endpoint"""
    return jsonify({'status': 'ok', 'message': 'API is running'})

# ============================================
# WEBHOOK ROUTES
# ============================================

@app.route('/webhook', methods=['GET'])
def webhook_verify():
    print("webhook trigger")
    """Webhook verification for Meta"""
    mode = request.args.get('hub.mode')
    token = request.args.get('hub.verify_token')
    challenge = request.args.get('hub.challenge')
    
    print(f'🔔 Webhook verification attempt: mode={mode}, token={token}, token_match={token == VERIFY_TOKEN}')
    
    if mode == 'subscribe' and token == VERIFY_TOKEN:
        print('✓ Webhook verification successful')
        return challenge, 200
    
    print('✗ Webhook verification failed')
    return 'Forbidden', 403

@app.route('/webhook', methods=['POST'])
def webhook_receive():
    """Webhook event receiver from Meta"""
    webhook_processing(request)
    return 'EVENT_RECEIVED', 200

# ============================================
# PROTECTED DATA ROUTES
# ============================================

@app.route("/postlist", methods=['GET'])
@token_required
@with_db_connection(db_service)
def query_post_list(conn):
    """Get list of all posts"""
    data = db_service.get_post_list(conn)
    return jsonify(data)

@app.route("/latest/<count>", methods=['GET'])
@token_required
@with_db_connection(db_service)
def query_latest_activity(conn, count):
    """Get latest N posts"""
    data = db_service.get_latest_activity(conn, count)
    return jsonify(data)

@app.route("/activity", methods=['GET'])
@token_required
@with_db_connection(db_service)
def query_all_activity(conn):
    """Get all post activity"""
    data = db_service.get_all_activity(conn)
    return jsonify(data)

@app.route("/activity/<id>", methods=['GET'])
@token_required
@with_db_connection(db_service)
def query_activity_by_id(conn, id):
    """Get activity for specific post"""
    data = db_service.get_activity_by_id(conn, id)
    return jsonify(data)

@app.route("/execsummary", methods=['GET'])
@token_required
@with_db_connection(db_service)
def query_exec_summary_data(conn):
    """Get executive summary data"""
    print('execsummary')
    data = db_service.get_exec_summary_data(conn)
    return jsonify(data)

# ============================================
# AUTHENTICATION ROUTES
# ============================================

@app.route('/auth/login', methods=['POST'])
def login():
    """Login - returns access and refresh tokens"""
    try:
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        
        if not username or not password:
            return jsonify({'message': 'Username and password are required'}), 400
        
        conn = db_service.get_db_connection()
        try:
            user = db_service.get_user_by_username(conn, username)
            
            if not user or not AuthService.verify_password(password, user['password_hash']):
                return jsonify({'message': 'Invalid username or password'}), 401
            
            token_data = {'user_id': user['id'], 'username': user['username']}
            access_token = AuthService.create_access_token(token_data)
            refresh_token = AuthService.create_refresh_token(token_data)
            
            return jsonify({
                'access_token': access_token,
                'refresh_token': refresh_token,
                'user': {'id': user['id'], 'username': user['username'], 'email': user['email']}
            }), 200
        finally:
            conn.close()
            
    except Exception as e:
        print(f"Login error: {str(e)}")
        return jsonify({'message': 'An error occurred during login'}), 500

@app.route('/auth/refresh', methods=['POST'])
def refresh():
    """Exchange refresh token for new access token"""
    try:
        data = request.get_json()
        refresh_token = data.get('refresh_token')
        
        if not refresh_token:
            return jsonify({'message': 'Refresh token is required'}), 400
        
        payload = AuthService.decode_token(refresh_token, token_type='refresh')
        if payload is None:
            return jsonify({'message': 'Invalid or expired refresh token'}), 401
        
        new_token_data = {'user_id': payload['user_id'], 'username': payload['username']}
        new_access_token = AuthService.create_access_token(new_token_data)
        
        return jsonify({'access_token': new_access_token}), 200
        
    except Exception as e:
        print(f"Refresh error: {str(e)}")
        return jsonify({'message': 'An error occurred during token refresh'}), 500

@app.route('/auth/register', methods=['POST'])
def register():
    """Create new user account"""
    try:
        data = request.get_json()
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')
        
        if not username or not email or not password:
            return jsonify({'message': 'Username, email, and password are required'}), 400
        
        if len(password) < 8:
            return jsonify({'message': 'Password must be at least 8 characters'}), 400
        
        password_hash = AuthService.hash_password(password)
        conn = db_service.get_db_connection()
        
        try:
            new_user = db_service.create_user(conn, username, email, password_hash)
            return jsonify({
                'message': 'User created successfully',
                'user': {'id': new_user['id'], 'username': new_user['username'], 'email': new_user['email']}
            }), 201
            
        except Exception as db_error:
            if 'duplicate key' in str(db_error).lower():
                return jsonify({'message': 'Username or email already exists'}), 409
            raise
        finally:
            conn.close()
            
    except Exception as e:
        print(f"Registration error: {str(e)}")
        return jsonify({'message': 'An error occurred during registration'}), 500

@app.route('/auth/verify', methods=['GET'])
@token_required
def verify_token():
    """Verify if access token is valid"""
    return jsonify({'valid': True, 'user': request.current_user}), 200

# ============================================
# SERVER STARTUP
# ============================================

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=PORT, debug=True)
