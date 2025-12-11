from flask import jsonify
from functools import wraps

def with_db_connection(db_service):
    """
    Decorator to handle database connection management automatically.
    
    Usage:
        @app.route('/data')
        @token_required
        @with_db_connection(db_service)
        def get_data(conn):
            data = db_service.get_data(conn)
            return jsonify(data)
    """
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            conn = None
            try:
                # Acquire connection
                conn = db_service.get_db_connection()
                
                # Pass connection to the route function
                result = f(conn, *args, **kwargs)
                
                # Commit if needed (though SELECTs don't require it)
                conn.commit()
                
                return result
                
            except Exception as e:
                print(f"Database error: {e}")
                if conn:
                    conn.rollback()
                raise
                
            finally:
                # Always close the connection
                if conn:
                    conn.close()
        
        return decorated
    return decorator