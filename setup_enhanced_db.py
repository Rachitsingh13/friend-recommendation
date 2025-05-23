import mysql.connector
from mysql.connector import Error
import bcrypt
from faker import Faker
import random

fake = Faker()

INTERESTS = [
    'Reading', 'Gaming', 'Cooking', 'Travel', 'Music', 'Sports', 
    'Photography', 'Art', 'Technology', 'Movies', 'Fitness', 'Dancing',
    'Writing', 'Hiking', 'Programming', 'Fashion', 'Food', 'Science',
    'History', 'Animals'
]

def create_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="mouse",
        database="user_friends_db"
    )

def setup_database():
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="mouse"
    )
    cursor = conn.cursor()

    cursor.execute("DROP DATABASE IF EXISTS user_friends_db")
    cursor.execute("CREATE DATABASE user_friends_db")
    cursor.execute("USE user_friends_db")

    cursor.execute("""
        CREATE TABLE users (
            id INT AUTO_INCREMENT PRIMARY KEY,
            username VARCHAR(50) UNIQUE NOT NULL,
            email VARCHAR(100) UNIQUE NOT NULL,
            password_hash VARCHAR(255) NOT NULL,
            full_name VARCHAR(100) NOT NULL,
            profile_picture VARCHAR(255) DEFAULT 'default.jpg',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    cursor.execute("""
        CREATE TABLE interests (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(50) UNIQUE NOT NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE user_interests (
            user_id INT,
            interest_id INT,
            PRIMARY KEY (user_id, interest_id),
            FOREIGN KEY (user_id) REFERENCES users(id),
            FOREIGN KEY (interest_id) REFERENCES interests(id)
        )
    """)

    cursor.execute("""
        CREATE TABLE friendships (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_id1 INT,
            user_id2 INT,
            status ENUM('pending', 'accepted', 'rejected') DEFAULT 'pending',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id1) REFERENCES users(id),
            FOREIGN KEY (user_id2) REFERENCES users(id)
        )
    """)

    for interest in INTERESTS:
        cursor.execute("INSERT INTO interests (name) VALUES (%s)", (interest,))

    print("Generating sample users...")
    for i in range(500):
        username = fake.user_name() + str(random.randint(100, 999))
        email = fake.email()
        password = "password123"
        full_name = fake.name()
        
        password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        
        try:
            cursor.execute("""
                INSERT INTO users (username, email, password_hash, full_name)
                VALUES (%s, %s, %s, %s)
            """, (username, email, password_hash, full_name))
            
            user_id = cursor.lastrowid
            
            num_interests = random.randint(3, 6)
            interest_ids = random.sample(range(1, len(INTERESTS) + 1), num_interests)
            
            for interest_id in interest_ids:
                cursor.execute("""
                    INSERT INTO user_interests (user_id, interest_id)
                    VALUES (%s, %s)
                """, (user_id, interest_id))
                
            for other_id in range(1, user_id):
                if random.random() < 0.3:
                    cursor.execute("""
                        INSERT INTO friendships (user_id1, user_id2, status)
                        VALUES (%s, %s, 'accepted')
                    """, (user_id, other_id))
            
            if (i + 1) % 50 == 0:
                print(f"Added {i + 1} users...")
                
        except Error as e:
            print(f"Error adding user {username}: {e}")
            continue

    conn.commit()
    print("\nDatabase setup completed successfully!")
    
    print("\nSample users and their interests:")
    cursor.execute("""
        SELECT u.username, u.full_name, GROUP_CONCAT(i.name) as interests
        FROM users u
        JOIN user_interests ui ON u.id = ui.user_id
        JOIN interests i ON ui.interest_id = i.id
        GROUP BY u.id
        LIMIT 5
    """)
    
    samples = cursor.fetchall()
    for sample in samples:
        print(f"\nUser: {sample[1]} (@{sample[0]})")
        print(f"Interests: {sample[2]}")

    cursor.close()
    conn.close()

if __name__ == "__main__":
    setup_database()