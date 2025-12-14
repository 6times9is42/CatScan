import sqlite3
conn = sqlite3.connect("users.db")
c = conn.cursor()
c.execute("ALTER TABLE visits ADD COLUMN original_filename TEXT")
conn.commit()
conn.close()