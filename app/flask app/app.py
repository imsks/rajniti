from flask import Flask, jsonify, request
import sqlite3

app = Flask(__name__)


def get_db_connection():
    conn = sqlite3.connect('partywise.db')
    conn.row_factory = sqlite3.Row 
    return conn


@app.route('/scrape', methods=['GET'])
def get_all_parties():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM partywise') 
    rows = cursor.fetchall()

    parties = [{'id': row['id'], 'name': row['Party Name'], 'symbol': row['Symbol']} for row in rows]

    conn.close()
    return jsonify(parties)

@app.route('/verify', methods=['GET'])
def verify():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
       
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='partywise';")
        table = cursor.fetchone()
        
        if table:
            message = {'status': 'success', 'message': 'Database and table are accessible.'}
        else:
            message = {'status': 'error', 'message': 'Table `partywise` does not exist in the database.'}
        
        conn.close()
    except Exception as e:
        message = {'status': 'error', 'message': f'Database connection failed: {str(e)}'}

    return jsonify(message)

@app.route('/insert', methods=['POST'])
def insert_party():
   
    if not request.is_json:
        return jsonify({'status': 'error', 'message': 'Content-Type must be application/json'}), 415

    data = request.get_json() 
    name = data.get('name')
    symbol = data.get('symbol')

    if not name or not symbol:
        return jsonify({'status': 'error', 'message': 'Both `name` and `symbol` fields are required.'}), 400

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute('INSERT INTO partywise ("Party Name", "Symbol") VALUES (?, ?)', (name, symbol))
        conn.commit()
        conn.close()

        return jsonify({'status': 'success', 'message': 'Party inserted successfully.'}), 201

    except Exception as e:
        return jsonify({'status': 'error', 'message': f'Failed to insert data: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(debug=True)
