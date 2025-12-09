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

def update_post_activity(update_type="rapid"):
    # fetch all posts from last 48 hours
    print(f"🟢 Run timestamp: {datetime.now()}")
    values = ["48 hours", "1 second"] if update_type=='rapid' else ["2 months", "48 hours"]
    
    with get_db_connection() as conn:
        cursor = conn.cursor(cursor_factory = psycopg2.extras.RealDictCursor)
        
        read_query = query_builder("all_posts")
        cursor.execute(read_query, values)
        posts = cursor.fetchall()

        rows = []
        for post in posts:
            # print("posts there: ", posts)
            id=post["id"]
            media_product_type=post["media_product_type"]

            results = fetch_meta_data_post(id, 'post_activity_data_'+media_product_type)
            print(f"post {id} results: ", results)
            
            #if no data comes back go to next post
            if len(results) == 0:
                continue

            flattened_data = {}
            
            for result in results[0]:
                # print("result: ", result)
                flattened_data[result["name"]] = result["values"][0]["value"]


            # print(f"flattened_data: {flattened_data}")

            rows.append([
                id,
                flattened_data["views"] if "views" in flattened_data else 0,
                flattened_data["reach"] if "reach" in flattened_data else 0,
                flattened_data["likes"] if "likes" in flattened_data else 0,
                flattened_data["comments"] if "comments" in flattened_data else 0,
                flattened_data["shares"] if "shares" in flattened_data else 0,
                flattened_data["saved"] if "saved" in flattened_data else 0,

                flattened_data["ig_reels_video_view_total_time"] if "ig_reels_video_view_total_time" in flattened_data else 0,
                flattened_data["total_interactions"] if "total_interactions" in flattened_data else 0,
                flattened_data["follows"] if "follows" in flattened_data else 0,
                flattened_data["profile_activity"] if "profile_activity" in flattened_data else 0,
                flattened_data["profile_visits"] if "profile_visits" in flattened_data else 0,
            ])

        update_query = query_builder("post_activity")
        psycopg2.extras.execute_batch(cursor, update_query, rows)
        conn.commit()
        cursor.close()
        conn.close() 

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("No update_type variable passed")
        sys.exit(1)
    update_type = sys.argv[1]
    # update_type = "rapid"
    update_post_activity(update_type)