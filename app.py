from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SelectMultipleField, SubmitField
from wtforms.validators import DataRequired, Email, Length
import mysql.connector
import bcrypt
from collections import defaultdict, deque
from functools import wraps
import os

app = Flask(__name__)
app.secret_key = os.urandom(24)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': 'mouse',
    'database': 'user_friends_db'
}

class User(UserMixin):
    def __init__(self, id, username, email, full_name):
        self.id = id
        self.username = username
        self.email = email
        self.full_name = full_name

def get_db():
    return mysql.connector.connect(**db_config)

@login_manager.user_loader
def load_user(user_id):
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
    user = cursor.fetchone()
    cursor.close()
    conn.close()
    
    if user:
        return User(user['id'], user['username'], user['email'], user['full_name'])
    return None

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

class RegisterForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=4, max=50)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    full_name = StringField('Full Name', validators=[DataRequired()])
    interests = SelectMultipleField('Interests', coerce=int)
    submit = SubmitField('Register')

def get_user_interests(user_id):
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT i.id, i.name
        FROM interests i
        JOIN user_interests ui ON i.id = ui.interest_id
        WHERE ui.user_id = %s
    """, (user_id,))
    interests = cursor.fetchall()
    cursor.close()
    conn.close()
    return interests

def get_friend_recommendations_bfs(user_id, max_depth=2, max_recommendations=10):
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    
    user_interests = set(i['id'] for i in get_user_interests(user_id))
    
    if not user_interests:
        cursor.close()
        conn.close()
        return []
    
    cursor.execute("""
        SELECT 
            CASE 
                WHEN user_id1 = %s THEN user_id2 
                WHEN user_id2 = %s THEN user_id1 
            END as friend_id
        FROM friendships 
        WHERE (user_id1 = %s OR user_id2 = %s)
        AND (status = 'accepted' OR status = 'pending')
    """, (user_id, user_id, user_id, user_id))
    
    excluded_users = set(row['friend_id'] for row in cursor.fetchall() if row['friend_id'] is not None)
    excluded_users.add(user_id)
    
    cursor.execute("""
        SELECT 
            u.id,
            u.username,
            u.full_name,
            u.profile_picture,
            COUNT(DISTINCT ui.interest_id) as common_interest_count
        FROM users u
        JOIN user_interests ui ON u.id = ui.user_id
        WHERE ui.interest_id IN (
            SELECT interest_id 
            FROM user_interests 
            WHERE user_id = %s
        )
        AND u.id NOT IN (
            SELECT user_id2 FROM friendships WHERE user_id1 = %s AND status IN ('accepted', 'pending')
            UNION
            SELECT user_id1 FROM friendships WHERE user_id2 = %s AND status IN ('accepted', 'pending')
        )
        AND u.id != %s
        GROUP BY u.id
        ORDER BY common_interest_count DESC
        LIMIT %s
    """, (user_id, user_id, user_id, user_id, max_recommendations * 2))
    
    interest_based_recommendations = cursor.fetchall()
    recommendations = []
    
    for friend in interest_based_recommendations:
        cursor.execute("""
            SELECT i.id, i.name
            FROM interests i
            JOIN user_interests ui ON i.id = ui.interest_id
            WHERE ui.user_id = %s
        """, (friend['id'],))
        
        friend_interests = set(row['id'] for row in cursor.fetchall())
        common_interests = len(user_interests & friend_interests)
        
        if common_interests > 0:
            recommendations.append({
                'id': friend['id'],
                'username': friend['username'],
                'full_name': friend['full_name'],
                'profile_picture': friend.get('profile_picture', 'default.jpg'),
                'common_interests': common_interests,
                'distance': 1,
                'score': common_interests * 2
            })
    
    if len(recommendations) < max_recommendations:
        queue = deque([(user_id, 0)])
        visited = {user_id: 0}
        
        while queue and len(recommendations) < max_recommendations * 2:
            current_id, depth = queue.popleft()
            
            if depth > max_depth:
                continue
            
            cursor.execute("""
                SELECT 
                    CASE 
                        WHEN f.user_id1 = %s THEN f.user_id2 
                        ELSE f.user_id1 
                    END as friend_id,
                    u.id,
                    u.username,
                    u.full_name,
                    u.profile_picture
                FROM friendships f
                JOIN users u ON u.id = CASE 
                    WHEN f.user_id1 = %s THEN f.user_id2 
                    ELSE f.user_id1 
                END
                WHERE (f.user_id1 = %s OR f.user_id2 = %s)
                AND f.status = 'accepted'
            """, (current_id, current_id, current_id, current_id))
            
            for friend in cursor.fetchall():
                friend_id = friend['friend_id']
                if friend_id not in visited and friend_id not in excluded_users:
                    visited[friend_id] = depth + 1
                    queue.append((friend_id, depth + 1))
                    
                    cursor.execute("""
                        SELECT i.id, i.name
                        FROM interests i
                        JOIN user_interests ui ON i.id = ui.interest_id
                        WHERE ui.user_id = %s
                    """, (friend_id,))
                    
                    friend_interests = set(row['id'] for row in cursor.fetchall())
                    common_interests = len(user_interests & friend_interests)
                    
                    if common_interests > 0:
                        recommendations.append({
                            'id': friend_id,
                            'username': friend['username'],
                            'full_name': friend['full_name'],
                            'profile_picture': friend.get('profile_picture', 'default.jpg'),
                            'common_interests': common_interests,
                            'distance': depth + 1,
                            'score': common_interests * (max_depth + 1 - (depth + 1))
                        })
    
    cursor.close()
    conn.close()
    
    recommendations.sort(key=lambda x: (-x['score'], -x['common_interests'], x['distance']))
    return recommendations[:max_recommendations]

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        conn = get_db()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users WHERE username = %s", (form.username.data,))
        user = cursor.fetchone()
        cursor.close()
        conn.close()
        
        if user and bcrypt.checkpw(form.password.data.encode('utf-8'), user['password_hash'].encode('utf-8')):
            user_obj = User(user['id'], user['username'], user['email'], user['full_name'])
            login_user(user_obj)
            return redirect(url_for('dashboard'))
        
        flash('Invalid username or password')
    return render_template('login.html', form=form)

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT id, name FROM interests")
    interests = cursor.fetchall()
    form.interests.choices = [(i['id'], i['name']) for i in interests]
    
    if form.validate_on_submit():
        password_hash = bcrypt.hashpw(form.password.data.encode('utf-8'), bcrypt.gensalt())
        
        try:
            cursor.execute("""
                INSERT INTO users (username, email, password_hash, full_name)
                VALUES (%s, %s, %s, %s)
            """, (form.username.data, form.email.data, password_hash, form.full_name.data))
            
            user_id = cursor.lastrowid
            
            for interest_id in form.interests.data:
                cursor.execute("""
                    INSERT INTO user_interests (user_id, interest_id)
                    VALUES (%s, %s)
                """, (user_id, interest_id))
            
            conn.commit()
            flash('Registration successful! Please login.')
            return redirect(url_for('login'))
            
        except mysql.connector.Error as err:
            flash(f'Registration failed: {err}')
        
    cursor.close()
    conn.close()
    return render_template('register.html', form=form)

@app.route('/dashboard')
@login_required
def dashboard():
    user_interests = get_user_interests(current_user.id)
    
    recommendations = get_friend_recommendations_bfs(current_user.id, max_depth=3, max_recommendations=10)
    
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    
    for rec in recommendations:
        cursor.execute("""
            SELECT i.name 
            FROM interests i 
            JOIN user_interests ui ON i.id = ui.interest_id 
            WHERE ui.user_id = %s
        """, (rec['id'],))
        rec['interests'] = [row['name'] for row in cursor.fetchall()]
    
    cursor.close()
    conn.close()
    
    return render_template('dashboard.html', 
                         recommendations=recommendations,
                         interests=user_interests)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))

@app.route('/api/send_friend_request', methods=['POST'])
@login_required
def send_friend_request():
    friend_id = request.json.get('friend_id')
    if not friend_id:
        return jsonify({'error': 'No friend_id provided'}), 400
        
    conn = get_db()
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            INSERT INTO friendships (user_id1, user_id2, status)
            VALUES (%s, %s, 'pending')
        """, (current_user.id, friend_id))
        conn.commit()
        return jsonify({'message': 'Friend request sent successfully'})
    except mysql.connector.Error as err:
        return jsonify({'error': str(err)}), 400
    finally:
        cursor.close()
        conn.close()

@app.route('/api/friend_requests', methods=['GET'])
@login_required
def get_friend_requests():
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    
    cursor.execute("""
        SELECT 
            f.id as request_id,
            u.id as user_id,
            u.username,
            u.full_name,
            u.profile_picture,
            f.created_at
        FROM friendships f
        JOIN users u ON u.id = f.user_id1
        WHERE f.user_id2 = %s AND f.status = 'pending'
        ORDER BY f.created_at DESC
    """, (current_user.id,))
    
    requests = cursor.fetchall()
    cursor.close()
    conn.close()
    
    return jsonify(requests)

@app.route('/api/friend_requests/<int:request_id>', methods=['POST'])
@login_required
def handle_friend_request(request_id):
    action = request.json.get('action')
    if action not in ['accept', 'reject']:
        return jsonify({'error': 'Invalid action'}), 400
    
    conn = get_db()
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            UPDATE friendships 
            SET status = %s 
            WHERE id = %s AND user_id2 = %s
        """, (action, request_id, current_user.id))
        
        if cursor.rowcount == 0:
            return jsonify({'error': 'Friend request not found'}), 404
            
        conn.commit()
        return jsonify({'message': f'Friend request {action}ed successfully'})
        
    except mysql.connector.Error as err:
        return jsonify({'error': str(err)}), 400
        
    finally:
        cursor.close()
        conn.close()

if __name__ == '__main__':
    app.run(debug=True) 