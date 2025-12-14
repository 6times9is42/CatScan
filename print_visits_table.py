import sqlite3
from tabulate import tabulate

# Path to your database
DB_PATH = 'users.db'

# Connect to the database
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# Fetch all rows from visits table
cursor.execute('SELECT * FROM visits')
rows = cursor.fetchall()

# Fetch column names
col_names = [description[0] for description in cursor.description]

# Print as a formatted table
print(tabulate(rows, headers=col_names, tablefmt='grid'))

conn.close()
