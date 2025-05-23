import mysql.connector

def get_db():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="mouse",
        database="user_friends_db"
    )

def show_users():
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    
    # Get users with their interests
    cursor.execute("""
        SELECT 
            u.id,
            u.username,
            u.email,
            u.full_name,
            GROUP_CONCAT(i.name) as interests
        FROM users u
        LEFT JOIN user_interests ui ON u.id = ui.user_id
        LEFT JOIN interests i ON ui.interest_id = i.id
        GROUP BY u.id
        ORDER BY u.id
        LIMIT 20
    """)
    
    users = cursor.fetchall()
    
    # Get friend count for each user
    for user in users:
        cursor.execute("""
            SELECT COUNT(*) as friend_count
            FROM friendships
            WHERE (user_id1 = %s OR user_id2 = %s)
            AND status = 'accepted'
        """, (user['id'], user['id']))
        friend_count = cursor.fetchone()['friend_count']
        user['friend_count'] = friend_count
    
    print("\n=== Sample Users from Database ===\n")
    for user in users:
        print(f"ID: {user['id']}")
        print(f"Username: {user['username']}")
        print(f"Name: {user['full_name']}")
        print(f"Email: {user['email']}")
        print(f"Friends: {user['friend_count']}")
        print(f"Interests: {user['interests'] if user['interests'] else 'None'}")
        print("-" * 50)
    
    # Show some statistics
    cursor.execute("SELECT COUNT(*) as total FROM users")
    total_users = cursor.fetchone()['total']
    
    cursor.execute("SELECT COUNT(*) as total FROM friendships WHERE status = 'accepted'")
    total_friendships = cursor.fetchone()['total']
    
    cursor.execute("SELECT COUNT(*) as total FROM friendships WHERE status = 'pending'")
    pending_requests = cursor.fetchone()['total']
    
    print("\n=== Database Statistics ===")
    print(f"Total Users: {total_users}")
    print(f"Total Friendships: {total_friendships}")
    print(f"Pending Friend Requests: {pending_requests}")
    
    cursor.close()
    conn.close()

if __name__ == "__main__":
    show_users() 