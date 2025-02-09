from flask import Flask, render_template, jsonify, request, redirect, session
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash

# Initialize Flask app
app = Flask(__name__)
app.secret_key = "super_secret_key"  # Change this in production!

# Connect to SQLite database
def get_db_connection():
    conn = sqlite3.connect('savings.db')
    conn.row_factory = sqlite3.Row  # Enables dictionary-like row access
    return conn

@app.route('/')
def index():
    """ Serve the savings progress page (if logged in), else redirect to login. """
    if "user" not in session:
        return redirect("/login")
    return render_template('progress.html')

@app.route('/set_goal/', methods=['POST'])
def set_savings_goal():
    # Ensure the user is logged in
    if 'user' not in session:
        return jsonify({"error": "You must be logged in to set a goal."}), 400

    user_name = session['user']  # Assuming 'user' session holds username.

    # Connect to the database
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT id FROM User WHERE username = ?", (user_name,))
    user_id = cursor.fetchone()['id']
    print(user_id)

    # Get the new target amount from the request
    target_amount = request.form.get('target_amount')

    if not target_amount or float(target_amount) <= 0:
        return jsonify({"error": "Please provide a valid target amount."}), 400

    target_amount = float(target_amount)

    # Check if the user already has an associated goal
    cursor.execute("SELECT goal_id FROM User WHERE id = ?", (user_id,))
    existing_goal_id = cursor.fetchone()
    print(user_id)

    if existing_goal_id and existing_goal_id[0]:
        # If a goal already exists, update it
        cursor.execute("UPDATE SavingsGoal SET target_amount = ? WHERE id = ?", 
                       (target_amount, existing_goal_id[0]))
    else:
        return jsonify({"error": "Error goal does not exist."}), 400
    
        # If no goal exists, create a new one and associate with the user
        cursor.execute("INSERT INTO SavingsGoal (name, target_amount) VALUES (?, ?)",
                       ('Default Goal', target_amount))  # Adjust goal name as necessary
        goal_id = cursor.lastrowid
        cursor.execute("UPDATE User SET goal_id = ? WHERE id = ?", (goal_id, user_id))

    # Commit changes and close connection
    conn.commit()
    conn.close()

    return redirect("/")

@app.route('/savings/', methods=['GET'])
def get_savings_by_user():
    """ Fetch all users sharing the same savings goal as the given user. """
    conn = get_db_connection()
    cursor = conn.cursor()

    username = session["user"]

    # Fetch the user's savings goal
    cursor.execute("""
        SELECT SavingsGoal.id, SavingsGoal.name, SavingsGoal.target_amount
        FROM User 
        JOIN SavingsGoal ON User.goal_id = SavingsGoal.id
        WHERE User.username = ?
    """, (username,))
    
    goal = cursor.fetchone()

    if not goal:
        conn.close()
        return jsonify({"error": "User not found or no savings goal assigned"}), 404

    goal_id, goal_name, target_amount = goal

    # Fetch all users who share this goal
    cursor.execute("""
        SELECT id, username FROM User WHERE goal_id = ?
    """, (goal_id,))
    
    users = cursor.fetchall()

    # Fetch total contributions for each user
    user_savings = []
    for user in users:
        user_id, user_name = user

        cursor.execute("""
            SELECT COALESCE(SUM(amount), 0) AS total_saved 
            FROM Contribution 
            WHERE user_id = ?
        """, (user_id,))
        
        total_saved = cursor.fetchone()["total_saved"]

        cursor.execute("""
            SELECT *
            FROM Contribution, User
            WHERE user_id = ? AND Contribution.user_id = User.id
        """, (user_id,))

        contributions = list(map(dict, cursor.fetchall()))

        user_savings.append({
            "username": user_name,
            "saved_amount": total_saved,
            "progress": (total_saved / target_amount * 100) if target_amount else 0,
            "contributions": contributions,
        })

    conn.close()

    return jsonify({
        "goal": {
            "id": goal_id,
            "name": goal_name,
            "target_amount": target_amount
        },
        "users": user_savings
    }), 200

### --- Authentication Routes --- ###

@app.route('/register', methods=['POST'])
def register():
    """ Register a new user with a hashed password. """
    data = request.json
    username = data.get("username")
    email = data.get("email")
    password = data.get("password")

    if not username or not email or not password:
        return jsonify({"error": "Missing fields"}), 400

    password_hash = generate_password_hash(password)

    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO User (username, email, name, password_hash) VALUES (?, ?, ?, ?)",
                       (username, email, username, password_hash))
        conn.commit()
        return jsonify({"message": "User registered successfully"}), 201
    except sqlite3.IntegrityError:
        return jsonify({"error": "Username already exists"}), 400
    finally:
        conn.close()

@app.route('/login', methods=['GET', 'POST'])
def login():
    """ Login route - validates user and starts session. """
    if request.method == 'GET':
        return render_template("login.html")  # Serve login form

    data = request.json
    username = data.get("username")
    password = data.get("password")

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM User WHERE username = ?", (username,))
    user = cursor.fetchone()
    conn.close()

    print(dict(user))

    if user and check_password_hash(user["password_hash"], password):
        session["user"] = username
        return jsonify({"message": "Login successful"}), 200
    else:
        return jsonify({"error": "Invalid username or password"}), 401

@app.route('/logout', methods=['GET'])
def logout():
    """ Logout the user and clear the session. """
    session.pop("user", None)
    return redirect("/login")

if __name__ == '__main__':
    app.run(debug=True)