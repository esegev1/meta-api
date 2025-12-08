import sys
from pathlib import Path
import time

# Add project root to sys.path
# sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from app.scripts.queries import query_builder
from app.services.meta_api import fetch_meta_data_post

from datetime import datetime, timezone

import psycopg2
connection = psycopg2.connect(
    database="meta_api_data"
)

import psycopg2.extras
cursor = connection.cursor(cursor_factory = psycopg2.extras.RealDictCursor)

def update_follower_counts():
    # fetch all posts from last 48 hours
    print(f"Run timestamp: {datetime.now()}")

    results = fetch_meta_data_post('', 'follower_counts_update')
    print("followers: ", results)
    values = [
        results["id"], 
        results["followers_count"]
    ]

    query=query_builder('follower_counts')
    
    cursor.execute(query, values)
    connection.commit()
    cursor.close()
    connection.close() 

update_follower_counts()
