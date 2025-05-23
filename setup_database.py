import mysql.connector
import getpass

def setup_database():
    password = getpass.getpass("Enter MySQL password: ")
    
    try:
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password=password
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
            ('Lucas Miller', 'John Smith', 'Oliver Brown', 'Ava Jones', 'Mia Martin')
        ]
        
        cursor.execute("SELECT COUNT(*) FROM users")
        count = cursor.fetchone()[0]
        
        if count == 0:
            cursor.executemany("""
                INSERT INTO users (name, friend1, friend2, friend3, friend4)
                VALUES (%s, %s, %s, %s, %s)
            """, sample_data)
            
            for i in range(6, 101):
                cursor.execute("""
                    INSERT INTO users (name, friend1, friend2, friend3, friend4)
                    VALUES (%s, %s, %s, %s, %s)
                """, (
                    f"User{i}",
                    f"Friend{i}A",
                    f"Friend{i}B",
                    f"Friend{i}C",
                    f"Friend{i}D"
                ))
        
        conn.commit()
        print("Database setup completed successfully!")
        
    except mysql.connector.Error as err:
        print(f"Error: {err}")
    finally:
        if 'conn' in locals() and conn.is_connected():
            cursor.close()
            conn.close()

if __name__ == "__main__":
    setup_database()