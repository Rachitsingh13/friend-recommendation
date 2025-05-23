-- Create the database
CREATE DATABASE IF NOT EXISTS user_friends_db;
USE user_friends_db;

-- Create the users table
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(50) NOT NULL,
    friend1 VARCHAR(50) NOT NULL,
    friend2 VARCHAR(50) NOT NULL,
    friend3 VARCHAR(50) NOT NULL,
    friend4 VARCHAR(50) NOT NULL
);

-- Insert 100 users with their friends
INSERT INTO users (name, friend1, friend2, friend3, friend4) VALUES
('John Smith', 'Emma Wilson', 'Oliver Brown', 'Sophia Davis', 'Lucas Miller'),
('Emma Wilson', 'John Smith', 'Ava Jones', 'William Taylor', 'Isabella Anderson'),
('Oliver Brown', 'Sophia Davis', 'John Smith', 'Mia Martin', 'James White'),
('Sophia Davis', 'Lucas Miller', 'Emma Wilson', 'Noah Thompson', 'Charlotte Garcia'),
('Lucas Miller', 'John Smith', 'Oliver Brown', 'Ava Jones', 'Mia Martin'),
('William Taylor', 'Emma Wilson', 'Isabella Anderson', 'Oliver Brown', 'Sophia Davis'),
('Ava Jones', 'Emma Wilson', 'Lucas Miller', 'Noah Thompson', 'Charlotte Garcia'),
('Noah Thompson', 'Sophia Davis', 'William Taylor', 'Isabella Anderson', 'James White'),
('Isabella Anderson', 'William Taylor', 'Emma Wilson', 'Lucas Miller', 'Mia Martin'),
('Mia Martin', 'Oliver Brown', 'Sophia Davis', 'John Smith', 'Noah Thompson'),
('James White', 'Noah Thompson', 'Isabella Anderson', 'William Taylor', 'Emma Wilson'),
('Charlotte Garcia', 'Ava Jones', 'Sophia Davis', 'Lucas Miller', 'Oliver Brown'),
('Daniel Lee', 'Sophie Clark', 'Henry Wilson', 'Luna Park', 'Grace Kim'),
('Sophie Clark', 'Daniel Lee', 'Oliver Young', 'Emma Lee', 'Noah Park'),
('Henry Wilson', 'Luna Park', 'Daniel Lee', 'Zoe Chen', 'Liam Wang'),
('Luna Park', 'Grace Kim', 'Sophie Clark', 'Ethan Lee', 'Aria Kim'),
('Grace Kim', 'Daniel Lee', 'Henry Wilson', 'Sophie Clark', 'Zoe Chen'),
('Oliver Young', 'Sophie Clark', 'Emma Lee', 'Henry Wilson', 'Luna Park'),
('Emma Lee', 'Sophie Clark', 'Grace Kim', 'Ethan Lee', 'Aria Kim'),
('Ethan Lee', 'Luna Park', 'Oliver Young', 'Emma Lee', 'Liam Wang');

-- Generate remaining 80 users programmatically
INSERT INTO users (name, friend1, friend2, friend3, friend4)
SELECT 
    CONCAT('User', number),
    CONCAT('Friend', number, 'A'),
    CONCAT('Friend', number, 'B'),
    CONCAT('Friend', number, 'C'),
    CONCAT('Friend', number, 'D')
FROM (
    SELECT n.number
    FROM (
        SELECT @row := @row + 1 as number
        FROM (SELECT 0 UNION ALL SELECT 1 UNION ALL SELECT 2 UNION ALL SELECT 3 UNION ALL SELECT 4 UNION ALL SELECT 5 UNION ALL SELECT 6 UNION ALL SELECT 7 UNION ALL SELECT 8 UNION ALL SELECT 9) t1,
             (SELECT 0 UNION ALL SELECT 1 UNION ALL SELECT 2 UNION ALL SELECT 3 UNION ALL SELECT 4 UNION ALL SELECT 5 UNION ALL SELECT 6 UNION ALL SELECT 7 UNION ALL SELECT 8 UNION ALL SELECT 9) t2,
        (SELECT @row:=20) t3
    ) n
    WHERE n.number <= 100
) numbers; 