import mysql.connector
import random
from faker import Faker

fake = Faker()

conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="mouse",
    database="user_friends_db"
)

cursor = conn.cursor()

cursor.execute("TRUNCATE TABLE users")

all_names = []
while len(all_names) < 500:
    name = fake.name()
    if name not in all_names:
        all_names.append(name)

for i in range(500):
    possible_friends = [name for name in all_names if name != all_names[i]]
    friends = random.sample(possible_friends, 4)
    
    cursor.execute("""
        INSERT INTO users (name, friend1, friend2, friend3, friend4)
        VALUES (%s, %s, %s, %s, %s)
    """, (all_names[i], friends[0], friends[1], friends[2], friends[3]))
    
    if (i + 1) % 50 == 0:
        print(f"Added {i + 1} users...")

conn.commit()
print("\nSuccessfully added 500 users with friends!")

cursor.execute("SELECT COUNT(*) FROM users")
count = cursor.fetchone()[0]
print(f"\nTotal users in database: {count}")

print("\nSample users and their friends:")
cursor.execute("SELECT * FROM users LIMIT 5")
samples = cursor.fetchall()
for sample in samples:
    print(f"\nUser: {sample[1]}")
    print(f"Friends: {sample[2]}, {sample[3]}, {sample[4]}, {sample[5]}")

cursor.close()
conn.close()