import mysql.connector

conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="mouse"
)

cursor = conn.cursor()

cursor.execute("CREATE DATABASE IF NOT EXISTS user_friends_db")
cursor.execute("USE user_friends_db")

cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INT AUTO_INCREMENT PRIMARY KEY,
        name VARCHAR(50) NOT NULL,
        friend1 VARCHAR(50) NOT NULL,
        friend2 VARCHAR(50) NOT NULL,
        friend3 VARCHAR(50) NOT NULL,
        friend4 VARCHAR(50) NOT NULL
    )
""")

sample_data = [
    ('John Smith', 'Emma Wilson', 'Oliver Brown', 'Sophia Davis', 'Lucas Miller'),
    ('Emma Wilson', 'John Smith', 'Ava Jones', 'William Taylor', 'Isabella Anderson'),
    ('Oliver Brown', 'Sophia Davis', 'John Smith', 'Mia Martin', 'James White'),
    ('Sophia Davis', 'Lucas Miller', 'Emma Wilson', 'Noah Thompson', 'Charlotte Garcia'),
    ('Lucas Miller', 'John Smith', 'Oliver Brown', 'Ava Jones', 'Mia Martin'),
    ('William Taylor', 'Emma Wilson', 'Isabella Anderson', 'Oliver Brown', 'Sophia Davis'),
    ('Ava Jones', 'Emma Wilson', 'Lucas Miller', 'Noah Thompson', 'Charlotte Garcia'),
    ('Noah Thompson', 'Sophia Davis', 'William Taylor', 'Isabella Anderson', 'James White'),
    ('Isabella Anderson', 'William Taylor', 'Emma Wilson', 'Lucas Miller', 'Mia Martin'),
    ('Mia Martin', 'Oliver Brown', 'Sophia Davis', 'John Smith', 'Noah Thompson')
]

cursor.execute("SELECT COUNT(*) FROM users")
count = cursor.fetchone()[0]

if count == 0:
    cursor.executemany("""
        INSERT INTO users (name, friend1, friend2, friend3, friend4)
        VALUES (%s, %s, %s, %s, %s)
    """, sample_data)

conn.commit()
print("Database setup completed successfully!")

cursor.close()
conn.close()