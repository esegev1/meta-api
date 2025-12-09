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

import psycopg2
import psycopg2.extras

def get_db_connection():
    db_url = os.getenv("DATABASE_URL")
    return psycopg2.connect(db_url)


def update_follower_counts():
    print(f"🟢 Run timestamp: {datetime.now()}")
    
    results = fetch_meta_data_post('', 'follower_counts_update')
    print("followers: ", results)

    values = [[
        results[0]["id"], 
        results[0]["followers_count"]
    ]]

    # print("values: ", values)


    with get_db_connection() as conn:
        cursor = conn.cursor(cursor_factory = psycopg2.extras.RealDictCursor)
        
        query = query_builder("follower_counts")
        psycopg2.extras.execute_batch(cursor, query, values)
        conn.commit()
        cursor.close()

if __name__ == '__main__':
    update_follower_counts()
