import sys
import os
from pathlib import Path
import time

# Add project root to sys.path
# sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

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

def bulk_load_posts():
    # feetch last 200 posts in case you need to reset post_metadata table
    print(f"🟢 Run timestamp: {datetime.now()}")

    results = fetch_meta_data_post('',"post_metadata_rebuild",230)

    rows = []
    for result in results[0]:
        # print("result: ", result)

        rows.append([
            result["id"],
            result["timestamp"],
            result["media_type"],
            result["media_product_type"],
            result["caption"][:50],
            result["caption"],
            not result["is_shared_to_feed"] if "is_shared_to_feed" in result else True,
        ])

    with get_db_connection() as conn:
        cursor = conn.cursor(cursor_factory = psycopg2.extras.RealDictCursor)
        query = query_builder("populate_post_metadata")
        psycopg2.extras.execute_batch(cursor, query, rows)
        conn.commit()
        cursor.close()
        conn.close() 

bulk_load_posts()