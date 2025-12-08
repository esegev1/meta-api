import sys
import os

# Get the project root directory (meta-api/)
# project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
# sys.path.insert(0, project_root)

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

import psycopg2
connection = psycopg2.connect(
    database="meta_api_data"
)

import psycopg2.extras
cursor = connection.cursor(cursor_factory = psycopg2.extras.RealDictCursor)

def update_post_metadata(post_id):
    print(f"Fetching metadata for post: {post_id}")
    post_metadata = fetch_meta_data_post(post_id, 'new_post_data')
    print("post_metadata: ", post_metadata)
    print(f"Type: {type(post_metadata)}, Length: {len(post_metadata) if post_metadata else 0}")

    caption = post_metadata[0].get("caption") or "" #to handle None
    values =[
            post_metadata[0]["id"],
            post_metadata[0]["timestamp"],
            post_metadata[0]["media_type"],
            caption[:50],
            caption,
            post_metadata[0]["is_shared_to_feed"]
        ]
    
    query=query_builder('new_post_data')
    
    cursor.execute(query, values)
    connection.commit()
    cursor.close()
    connection.close() 

# update_post_metadata("17841405389209828")