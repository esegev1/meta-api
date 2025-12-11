import os
import jwt
import bcrypt
from datetime import datetime, timedelta
from functools import wraps
from flask import request, jsonify

# JWT Configuration
SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'opie-will-bite-your-butt-off')
ALGORITHM = 'HS256'

# Token lifetimes
ACCESS_TOKEN_EXPIRE_MINUTES = 30  # Short-lived for API requests
REFRESH_TOKEN_EXPIRE_DAYS = 30     # Long-lived for getting new access tokens

class AuthService:
    @staticmethod
    def hash_password(password):
        """
        Hash a password for secure storage in the database.
        
        Uses bcrypt, which:
        - Automatically generates a salt (random data added to password)
        - Is slow by design (prevents brute force attacks)
        - Returns a string that includes the salt and hash
        
        Args:
            password (str): Plain text password from user
            
        Returns:
            str: Hashed password safe to store in database
        """
        return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    @staticmethod
    def verify_password(plain_password, hashed_password):
        """
        Verify a plain text password against a stored hash.
        
        Used during login to check if the password is correct.
        
        Args:
            plain_password (str): Password user entered during login
            hashed_password (str): Hashed password from database
            
        Returns:
            bool: True if password matches, False otherwise
        """
        return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))
    
    @staticmethod
    def create_access_token(data):
        """
        Create a short-lived JWT access token for API requests.
        
        This token expires after 30 minutes. When it expires, the client
        should use the refresh token to get a new access token.
        
        Args:
            data (dict): User information to encode (e.g., {"user_id": 1, "username": "john"})
            
        Returns:
            str: JWT access token
        """
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        to_encode.update({
            "exp": expire,
            "type": "access"  # Mark this as an access token
        })
        return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    
    @staticmethod
    def create_refresh_token(data):
        """
        Create a long-lived JWT refresh token.
        
        This token expires after 30 days and is used ONLY to get new
        access tokens. It should never be used for API requests.
        
        Args:
            data (dict): User information to encode (e.g., {"user_id": 1, "username": "john"})
            
        Returns:
            str: JWT refresh token
        """
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
        to_encode.update({
            "exp": expire,
            "type": "refresh"  # Mark this as a refresh token
        })
        return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    
    @staticmethod
    def decode_token(token, token_type=None):
        """
        Decode and verify a JWT token.
        
        Args:
            token (str): JWT token to decode
            token_type (str): Expected token type ('access' or 'refresh')
                            If provided, will verify the token is the correct type
            
        Returns:
            dict: Decoded payload if valid
            None: If token is invalid, expired, or wrong type
        """
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            
            # If token_type specified, verify it matches
            if token_type and payload.get('type') != token_type:
                return None
                
            return payload
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None

def token_required(f):
    """
    Decorator to protect Flask routes with JWT authentication.
    
    This decorator specifically checks for ACCESS tokens, not refresh tokens.
    Refresh tokens should only be used with the /auth/refresh endpoint.
    
    Usage:
        @app.route('/protected')
        @token_required
        def protected_route():
            return jsonify({'data': 'secret stuff'})
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        
        # Extract token from Authorization header
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            try:
                token = auth_header.split(" ")[1]  # "Bearer <token>"
            except IndexError:
                return jsonify({'message': 'Token format invalid'}), 401
        
        if not token:
            return jsonify({'message': 'Token is missing'}), 401
        
        try:
            # Decode and verify this is an ACCESS token
            payload = AuthService.decode_token(token, token_type='access')
            if payload is None:
                return jsonify({'message': 'Token is invalid or expired'}), 401
            
            # Attach user info to request
            request.current_user = payload
            
        except Exception as e:
            return jsonify({'message': 'Token is invalid'}), 401
        
        return f(*args, **kwargs)
    
    return decorated