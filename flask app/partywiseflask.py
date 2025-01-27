from flask import Flask, jsonify
import sqlite3

app = Flask(__name__)

# Function to connect to the SQLite database
def get_db_connection():
    conn = sqlite3.connect('partywise.db')
    conn.row_factory = sqlite3.Row  # To return rows as dictionaries
    return conn

# Simplified Route to get all party data
@app.route('/api/parties', methods=['GET'])
def get_all_parties():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM partywise')  # Query to fetch all data
    rows = cursor.fetchall()

    # Convert rows to list of dictionaries
    parties = [{'id': row['id'], 'name': row['Party Name'], 'symbol': row['Symbol']} for row in rows]

    conn.close()
    return jsonify(parties)

# Main entry point
if __name__ == '__main__':
    app.run(debug=True)
