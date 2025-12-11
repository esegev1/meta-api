import psycopg2
from  psycopg2.extras import RealDictCursor
import os

from app.scripts.queries import query_builder

class DBService:
    def __init__(self):
        pass
    
    def get_db_connection(self):
        """Creates and returns a fresh connection object"""
        # Connection details here (use os.getenv in production)
        DATABASE_URL = os.getenv('DATABASE_URL')

        return psycopg2.connect(
            DATABASE_URL,
            cursor_factory=RealDictCursor
        )
    
    def execute_query(self, connection, query, params=None):
        """Execute a query and return results"""
        connection.rollback()
        with connection.cursor() as cursor: # Use a context manager for the cursor
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            return cursor.fetchall()
    
    def get_exec_summary_data(self, connection):
        query=query_builder('exec_summary_data')
        results = self.execute_query(connection, query)
        # print("exec sum results: ", results)
        return results
    
    # Activity
    def get_post_list(self, connection):
        query=query_builder('post_list')
        results = self.execute_query(connection, query)
        # print("activity result: ", results)

        return results
    
    def get_all_activity(self, connection):
        query=query_builder('all_post_activity')
        results = self.execute_query(connection, query)
        # print("activity result: ", results)

        return results
    
    def get_latest_activity(self, connection, count):
        query=query_builder('last_x_posts')
        results = self.execute_query(connection, query, [count])
        # print("latest activity result: ", results)
        return results
    
    def get_activity_by_id(self, connection, post_id):
        query=query_builder('activity_by_id')
        results = self.execute_query(connection, query, [post_id])
        # print("latest activity result: ", results)
        return results    

    def close(self):
        """Close cursor and connection"""
        self.cursor.close()
        self.connection.close()

    def get_user_by_username(self, connection, username):
        """
        Retrieve a user from the database by their username.
        
        Used during login to:
        1. Check if the user exists
        2. Get their hashed password for verification
        3. Get their user ID and other info for the JWT token
        
        Args:
            connection: Active database connection
            username (str): Username to look up
            
        Returns:
            dict: User record with keys like 'id', 'username', 'password_hash', 'email'
            None: If user not found or is inactive
        """
        # Only get active users (is_active = TRUE)
        query = "SELECT * FROM users WHERE username = %s AND is_active = TRUE"
        results = self.execute_query(connection, query, [username])
        
        # Return first result if found, otherwise None
        return results[0] if results else None

    def create_user(self, connection, username, email, password_hash):
        """
        Create a new user in the database.
        
        Used for user registration. The password should already be hashed
        before calling this method.
        
        Args:
            connection: Active database connection
            username (str): Unique username
            email (str): User's email address
            password_hash (str): Already hashed password (from AuthService.hash_password)
            
        Returns:
            dict: Newly created user record (id, username, email, created_at)
            
        Note:
            This will raise an error if username or email already exists
            due to UNIQUE constraints in the database
        """
        query = """
            INSERT INTO users (username, email, password_hash) 
            VALUES (%s, %s, %s) 
            RETURNING id, username, email, created_at
        """
        
        # We use a cursor directly here because we need to commit and return the result
        with connection.cursor() as cursor:
            cursor.execute(query, [username, email, password_hash])
            connection.commit()  # Save the new user to the database
            return cursor.fetchone()  # Return the newly created user's info