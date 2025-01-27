from flask import Flask, jsonify
import sqlite3

app = Flask(__name__)

# Function to connect to the SQLite database
def get_db_connection():
    conn = sqlite3.connect('constituency.db')
    conn.row_factory = sqlite3.Row  # To return rows as dictionaries
    return conn

# Route to get all constituency data
@app.route('/api/constituencies', methods=['GET'])
def get_all_constituencies():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM constituency')  # Query to fetch all data
    rows = cursor.fetchall()

    # Convert rows to list of dictionaries
    constituencies = [{'id': row['id'], 'name': row['name'], 'state_code': row['state_code']} for row in rows]

    conn.close()
    return jsonify(constituencies)

# Main entry point
if __name__ == '__main__':
    app.run(debug=True)
