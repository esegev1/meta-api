import psycopg2
from  psycopg2.extras import RealDictCursor
import os

from app.scripts.queries import query_builder

class DBService:
    def __init__(self):
        pass
        # self.connection = psycopg2.connect(
        #     # host=os.getenv('DB_HOST'),
        #     database='meta_api_data',
        #     # user=os.getenv('DB_USER'),
        #     # password=os.getenv('DB_PASSWORD'),
        #     # port=os.getenv('DB_PORT', 5432)
        #     cursor_factory=RealDictCursor
        # )
        # self.cursor = self.connection.cursor()
    
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
            # The cursor is automatically closed here
        # if params:
        #     self.cursor.execute(query, params)
        # else:
        #     self.cursor.execute(query)
        # return self.cursor.fetchall()
    
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
    
    def get_latest_activity(self, connection):
        query=query_builder('latest_post_activity')
        results = self.execute_query(connection, query)
        # print("latest activity result: ", results)
        return results
    
    def get_activity_by_id(self, connection, post_id):
        query=query_builder('activity_by_id')
        results = self.execute_query(connection, query, [post_id])
        # print("latest activity result: ", results)
        return results    
        # query = "SELECT * FROM post_activity WHERE id=%s"
        # return self.execute_query(query, [activity_id])
    
    # Followers
    # def get_follower_counts(self):
    #     query = "SELECT * FROM follower_counts"
    #     return self.execute_query(query)
    
    # def get_latest_followers(self):
    #     query = "SELECT * FROM follower_counts ORDER BY timestamp DESC LIMIT 1"
    #     return self.execute_query(query)
    
        # def get_all_posts(self):
    #     query = "SELECT id, post_timestamp, media_product_type, trial_reel FROM post_metadata"
    #     return self.execute_query(query)
    
    # def get_post_by_id(self, post_id):
    #     query = "SELECT * FROM post_metadata WHERE id=%s"
    #     return self.execute_query(query, [post_id])

    def close(self):
        """Close cursor and connection"""
        self.cursor.close()
        self.connection.close()