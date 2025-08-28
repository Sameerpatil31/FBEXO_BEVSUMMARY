
# from src.BEV_Details.sql_db_connection import connection_
# import logging

# # --- Setup logging ---
# logger = logging.getLogger(__name__)
# logger.setLevel(logging.INFO)

# # Optional: Log to file
# file_handler = logging.FileHandler("sql_operations.log")
# file_handler.setLevel(logging.ERROR)
# formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
# file_handler.setFormatter(formatter)
# logger.addHandler(file_handler)

# def execute_query(query, params=None):
#     """
#     Execute INSERT, UPDATE, DELETE, etc.
#     """
#     try:
#         with connection_() as conn:
#             with conn.begin():  # Ensures COMMIT
#                 if params:
#                     conn.execute(query, params)
#                 else:
#                     conn.execute(query)
#     except Exception as e:
#         logger.error(f"❌ Query failed: {query}\nParams: {params}\nError: {e}")
#         raise e


# def fetch_query(query, params=None):
#     """
#     Execute SELECT queries and return result as list of dicts.
#     """
#     try:
#         with connection_() as conn:
#             if params:
#                 if isinstance(params, list):
#                     raise ValueError("❌ SELECT query parameters must be a tuple or dict, not a list.")
#                 result = conn.execute(query, params)
#             else:
#                 result = conn.execute(query)

#             rows = result.fetchall()
#             columns = result.keys()
#             return [dict(zip(columns, row)) for row in rows]

#     except Exception as e:
#         logger.error(f"❌ SELECT query failed: {query}\nParams: {params}\nError: {e}")
#         raise e


from src.BEV_Details.sql_db_connection import connection_
from sqlalchemy import text
import logging

# --- Setup logging ---
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Optional: Log to file
file_handler = logging.FileHandler("sql_operations.log")
file_handler.setLevel(logging.ERROR)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

def execute_query(query, params=None):
    """
    Execute INSERT, UPDATE, DELETE, etc.
    """
    try:
        # Wrap raw SQL string with text() for SQLAlchemy 2.x compatibility
        if isinstance(query, str):
            query = text(query)
            
        with connection_() as conn:
            with conn.begin():  # Ensures COMMIT
                if params:
                    conn.execute(query, params)
                else:
                    conn.execute(query)
    except Exception as e:
        # Remove emoji to avoid encoding issues
        logger.error(f"Query failed: {query}. Params: {params}. Error: {e}")
        raise e


def fetch_query(query, params=None):
    """
    Execute SELECT queries and return result as list of dicts.
    """
    try:
        # Wrap raw SQL string with text() for SQLAlchemy 2.x compatibility
        if isinstance(query, str):
            query = text(query)
            
        with connection_() as conn:
            if params:
                if isinstance(params, list):
                    raise ValueError("SELECT query parameters must be a tuple or dict, not a list.")
                result = conn.execute(query, params)
            else:
                result = conn.execute(query)

            rows = result.fetchall()
            columns = result.keys()
            return [dict(zip(columns, row)) for row in rows]

    except Exception as e:
        # Remove emoji to avoid encoding issues
        logger.error(f"SELECT query failed: {query}. Params: {params}. Error: {e}")


        raise e
    

def fetch_query_one(query, params=None):
    """
    Execute SELECT queries and return result as list of dicts.
    """
    try:
        # Wrap raw SQL string with text() for SQLAlchemy 2.x compatibility
        if isinstance(query, str):
            query = text(query)
            
        with connection_() as conn:
            if params:
                if isinstance(params, list):
                    raise ValueError("SELECT query parameters must be a tuple or dict, not a list.")
                result = conn.execute(query, params)
            else:
                result = conn.execute(query)

            row = result.fetchone()
            columns = result.keys()
            return dict(zip(columns, row)) if row else None

    except Exception as e:
        # Remove emoji to avoid encoding issues
        logger.error(f"SELECT query failed: {query}. Params: {params}. Error: {e}")