import mysql.connector
from collections import Counter
import sys

def connect_to_database():
    try:
        connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password="mouse",
            database="user_friends_db"
        )
        return connection
    except mysql.connector.Error as err:
        print(f"Error connecting to database: {err}")
        sys.exit(1)

def get_all_users():
    conn = connect_to_database()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT id, name FROM users")
    users = cursor.fetchall()
    cursor.close()
    conn.close()
    return users

def get_user_friends(user_id):
    conn = connect_to_database()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT friend1, friend2, friend3, friend4 
        FROM users 
        WHERE id = %s
    """, (user_id,))
    friends = cursor.fetchone()
    cursor.close()
    conn.close()
    return list(friends.values()) if friends else []

def get_recommendations(user_id):
    current_friends = set(get_user_friends(user_id))
    
    conn = connect_to_database()
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM users WHERE id = %s", (user_id,))
    user_name = cursor.fetchone()[0]
    
    recommendations = []
    for friend in current_friends:
        cursor.execute("""
            SELECT friend1, friend2, friend3, friend4 
            FROM users 
            WHERE name = %s
        """, (friend,))
        friend_of_friend = cursor.fetchone()
        if friend_of_friend:
            recommendations.extend(friend_of_friend)
    
    cursor.close()
    conn.close()
    
    recommendation_counts = Counter(recommendations)
    
    recommendation_counts.pop(user_name, None)
    for friend in current_friends:
        recommendation_counts.pop(friend, None)
    
    return recommendation_counts.most_common(5)

def main():
    print("\n=== Friend Recommendation System ===\n")
    
    users = get_all_users()
    
    print("Available Users:")
    for user in users:
        print(f"{user['id']}: {user['name']}")
    
    while True:
        try:
            user_id = input("\nEnter user ID to get recommendations (or 'q' to quit): ")
            
            if user_id.lower() == 'q':
                break
                
            user_id = int(user_id)
            
            print("\nCurrent Friends:")
            friends = get_user_friends(user_id)
            for friend in friends:
                print(f"- {friend}")
            
            print("\nRecommended Friends:")
            recommendations = get_recommendations(user_id)
            if recommendations:
                for name, common_friends in recommendations:
                    print(f"- {name} ({common_friends} mutual friends)")
            else:
                print("No recommendations found.")
                
        except ValueError:
            print("Please enter a valid user ID.")
        except Exception as e:
            print(f"An error occurred: {e}")
        
        print("\n" + "="*40 + "\n")

if __name__ == "__main__":
    main() 