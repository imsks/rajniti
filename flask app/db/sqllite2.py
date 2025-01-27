import sqlite3

# Connect to SQLite database
conn = sqlite3.connect('constituency.db')
cursor = conn.cursor()

# Create the table with auto-increment for the id
cursor.execute('''
CREATE TABLE IF NOT EXISTS partywise (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    state_code INTEGER NOT NULL
)
''')

# Commit and close the connection
conn.commit()
conn.close()

print("Table created successfully.")
