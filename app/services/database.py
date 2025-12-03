import psycopg2
connection = psycopg2.connect(
    database="meta_api_data"
)

import psycopg2.extras
cursor = connection.cursor(cursor_factory = psycopg2.extras.RealDictCursor)

def execute_query(query, rows):
    psycopg2.extras.execute_batch(cursor, query, rows)
    connection.commit()
    print(f"Upserted {len(rows)} posts into post_metadata.")