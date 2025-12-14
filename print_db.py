import sqlite3

print('--- USERS TABLE ---')
conn = sqlite3.connect('users.db')
c = conn.cursor()

try:
    c.execute('SELECT * FROM users')
    users = c.fetchall()
    for user in users:
        print(user)
except Exception as e:
    print('Error reading users table:', e)

print('\n--- VISITS TABLE ---')
try:
    c.execute('SELECT * FROM visits')
    visits = c.fetchall()
    for visit in visits:
        print(visit)
except Exception as e:
    print('Error reading visits table:', e)

conn.close()
