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

@app.route('/savings', methods=['GET'])
def get_all_savings():
    """ Fetch the savings progress for all users. """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Get all users from the User table
    cursor.execute("SELECT * FROM User")
    all_users = cursor.fetchall()
    
    all_savings = []
    
    for user in all_users:
        username = user['username']
        
        # Get the contributions for the user
        cursor.execute("SELECT * FROM Contribution WHERE username = ?", (username,))
        contributions = cursor.fetchall()

        # Convert contributions to a list of dictionaries
        contrib_list = [{"username": contrib['username'], "amount": contrib['amount']} for contrib in contributions]

        # Calculate the total saved amount
        total_saved = sum(contrib['amount'] for contrib in contributions)

        # Get the user's goal amount (default to 0 if not set)
        goal_amount = user['goal_amount'] if 'goal_amount' in user.keys() else 0
        
        all_savings.append({
            "username": username,
            "goal_amount": goal_amount,
            "saved_amount": total_saved,
            "progress": (total_saved / goal_amount * 100) if goal_amount else 0,
            "contributions": contrib_list  # Include individual contributions
        })
    
    conn.close()
    return jsonify(all_savings), 200

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