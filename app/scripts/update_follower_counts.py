import sys
import os
from pathlib import Path
import time


# --- Path Injection for Cron Jobs ---
# Calculate the path to the project root (meta-api) directory.
# The script is 3 levels deep: /scripts/ -> /app/ -> /meta-api/
current_dir = os.path.dirname(os.path.abspath(__file__))
app_dir = os.path.dirname(current_dir)
project_root = os.path.dirname(app_dir)

# Add the project root to the system path, allowing absolute imports like 'from app...'
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from app.scripts.queries import query_builder
from app.services.meta_api import fetch_meta_data_post

from datetime import datetime, timezone

# import psycopg2
# connection = psycopg2.connect(
#     database="meta_api_data"
# )

# import psycopg2.extras
# cursor = connection.cursor(cursor_factory = psycopg2.extras.RealDictCursor)

# def get_db_connection():
#     # It is safer to read the connection URL inside the function
#     # to handle connection failures gracefully during a request.
#     db_url = os.environ.get('DATABASE_URL')
#     if not db_url:
#         raise ValueError("DATABASE_URL environment variable is not set.")
        
#     # The connection attempt now only happens when this function is called
#     return psycopg2.connect(db_url)



# def update_follower_counts():
#     # fetch all posts from last 48 hours
#     print(f"Run timestamp: {datetime.now()}")

#     results = fetch_meta_data_post('', 'follower_counts_update')
#     print("followers: ", results)
#     values = [
#         results["id"], 
#         results["followers_count"]
#     ]

#     query=query_builder('follower_counts')
    
#     cursor.execute(query, values)
#     connection.commit()
#     cursor.close()
#     connection.close() 


import psycopg2
import psycopg2.extras

def get_db_connection():
    db_url = os.getenv("DATABASE_URL")
    return psycopg2.connect(db_url)

def update_follower_counts():
    print(f"Run timestamp: {datetime.now()}")
    
    results = fetch_meta_data_post('', 'follower_counts_update')
    print("followers: ", results)

    values = [[
        results[0]["id"], 
        results[0]["followers_count"]
    ]]

    with get_db_connection() as conn:
        cursor = conn.cursor(cursor_factory = psycopg2.extras.RealDictCursor)
        
        query = query_builder("follower_counts")
        psycopg2.extras.execute_batch(cursor, query, values)
        conn.commit()
        cursor.close()

if __name__ == '__main__':
    update_follower_counts()
