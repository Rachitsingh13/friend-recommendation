import mysql.connector
from mysql.connector import Error
import sys
import os

def check_database_connection():
    try:
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="mouse"
        )
        print("✓ Successfully connected to MySQL server")
        return conn
    except Error as e:
        print("✗ Error connecting to MySQL server:", e)
        return None

def setup_database(conn):
    try:
        cursor = conn.cursor()
        
        cursor.execute("CREATE DATABASE IF NOT EXISTS user_friends_db")
        cursor.execute("USE user_friends_db")
        print("✓ Database 'user_friends_db' created/selected successfully")
        
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
        print("✓ Table 'users' created successfully")
        
        cursor.execute("SELECT COUNT(*) FROM users")
        count = cursor.fetchone()[0]
        
        if count == 0:
            sample_data = [
                ('John Smith', 'Emma Wilson', 'Oliver Brown', 'Sophia Davis', 'Lucas Miller'),
                ('Emma Wilson', 'John Smith', 'Ava Jones', 'William Taylor', 'Isabella Anderson'),
                ('Oliver Brown', 'Sophia Davis', 'John Smith', 'Mia Martin', 'James White'),
                ('Sophia Davis', 'Lucas Miller', 'Emma Wilson', 'Noah Thompson', 'Charlotte Garcia'),
                ('Lucas Miller', 'John Smith', 'Oliver Brown', 'Ava Jones', 'Mia Martin')
            ]
            
            cursor.executemany("""
                INSERT INTO users (name, friend1, friend2, friend3, friend4)
                VALUES (%s, %s, %s, %s, %s)
            """, sample_data)
            
            for i in range(6, 11):
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
            print("✓ Sample data inserted successfully")
        else:
            print("✓ Data already exists in the database")
        
        return True
    except Error as e:
        print("✗ Error setting up database:", e)
        return False

def check_files():
    required_files = {
        'app.py': False,
        'static/style.css': False,
        'static/script.js': False,
        'templates/index.html': False
    }
    
    for file_path in required_files.keys():
        if os.path.exists(file_path):
            required_files[file_path] = True
            print(f"✓ Found {file_path}")
        else:
            print(f"✗ Missing {file_path}")
    
    return all(required_files.values())

def main():
    print("\n=== Checking System Setup ===\n")
    
    print("Checking required files...")
    files_ok = check_files()
    print()
    
    print("Checking database connection...")
    conn = check_database_connection()
    if conn:
        print("\nSetting up database...")
        database_ok = setup_database(conn)
        conn.close()
    else:
        database_ok = False
    
    print("\n=== Setup Summary ===")
    print("Files status:", "✓ OK" if files_ok else "✗ Missing files")
    print("Database status:", "✓ OK" if database_ok else "✗ Setup failed")
    print("\nNext steps:")
    if files_ok and database_ok:
        print("1. Run 'python app.py'")
        print("2. Open http://127.0.0.1:5000 in your web browser")
    else:
        if not database_ok:
            print("- Please check your MySQL installation and credentials")
        if not files_ok:
            print("- Please ensure all required files are in place")

if __name__ == "__main__":
    main()