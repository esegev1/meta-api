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

def bulk_load_posts():
    # feetch last 200 posts in case you need to reset post_metadata table
    print(f"Run timestamp: {datetime.now()}")

    results = fetch_meta_data_post('',"post_metadata_rebuild",230)

    rows = []
        
    for result in results:
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

    update_query = query_builder("populate_post_metadata")
    psycopg2.extras.execute_batch(cursor, update_query, rows)
    connection.commit()
    cursor.close()
    connection.close() 

# bulk_load_posts()