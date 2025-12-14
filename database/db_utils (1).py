import sqlite3

def init_db():
    conn = sqlite3.connect("users.db")
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users (
                    aadhaar TEXT PRIMARY KEY,
                    name TEXT,
                    dob TEXT,
                    sex TEXT,
                    phone TEXT
                )''')
    
    c.execute("""
        CREATE TABLE IF NOT EXISTS visits (
            visit_id INTEGER PRIMARY KEY AUTOINCREMENT,
            aadhaar TEXT,
            date TEXT,
            prediction TEXT,
            image_path TEXT,
            notes TEXT,
            original_filename TEXT,
            FOREIGN KEY(aadhaar) REFERENCES users(aadhaar)
        )
    """)
    conn.commit()
    conn.close()
