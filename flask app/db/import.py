import sqlite3
import pandas as pd

# Step 1: Read the CSV file using pandas
csv_file = 'constituency_data.csv'  # Your scraped CSV file path
df = pd.read_csv(csv_file)

# Strip any extra spaces from column names
df.columns = df.columns.str.strip()

# Check the column names to verify the expected structure
print(df.columns)  # Ensure columns like 'Constituency Name', 'Constituency ID', 'State ID' exist

# Step 2: Connect to SQLite database (constituency.db)
conn = sqlite3.connect('constituency.db')
cursor = conn.cursor()

# Step 3: Ensure the table exists in the database
cursor.execute('''
CREATE TABLE IF NOT EXISTS constituency (
    id INTEGER PRIMARY KEY,  -- Constituency ID
    name TEXT NOT NULL,       -- Constituency Name
    state_code INTEGER NOT NULL  -- State ID
)
''')

# Step 4: Insert data into SQLite table
for index, row in df.iterrows():
    try:
        cursor.execute('''
        INSERT INTO constituency (id, name, state_code)
        VALUES (?, ?, ?)
        ''', (row['Constituency ID'], row['Constituency Name'], row['State ID']))
    except KeyError as e:
        print(f"KeyError: Missing column {e} in the DataFrame.")
    except sqlite3.Error as e:
        print(f"SQLite Error: {e}")

# Step 5: Commit the transaction to save changes
conn.commit()

# Step 6: Close the connection
conn.close()

print("Data inserted successfully.")
