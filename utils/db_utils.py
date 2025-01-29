import sqlite3

def get_db_connection():
    """Establish and return a connection to the SQLite database."""
    try:
        conn = sqlite3.connect('partywise.db')
        conn.row_factory = sqlite3.Row  # Return rows as dictionaries
        return conn
    except sqlite3.Error as e:
        raise Exception(f"Database connection failed: {str(e)}")
