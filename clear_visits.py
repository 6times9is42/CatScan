import sqlite3

def clear_visits_table():
    conn = sqlite3.connect("users.db")
    c = conn.cursor()
    c.execute("DELETE FROM visits")
    conn.commit()
    conn.close()

if __name__ == "__main__":
    clear_visits_table()
    print("All records from 'visits' table have been deleted.")
