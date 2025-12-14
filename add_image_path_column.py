import sqlite3

conn = sqlite3.connect('users.db')
c = conn.cursor()
try:
    c.execute('ALTER TABLE visits ADD COLUMN image_path TEXT;')
    print('Column image_path added successfully.')
except Exception as e:
    print(f'Error or column may already exist: {e}')
conn.commit()
conn.close()
print('Done.')
