import sqlite3
import os
from werkzeug.security import generate_password_hash

def load_schema(cursor, schema_file):
    """Load and execute SQL schema from a file."""
    with open(schema_file, "r") as f:
        sql_script = f.read()
    cursor.executescript(sql_script)

def create_database():
    if os.path.exists("savings.db"):
        os.remove("savings.db")
    
    conn = sqlite3.connect("savings.db")
    cursor = conn.cursor()

    # Load schema from file
    load_schema(cursor, "schema.sql")

    # Insert savings goals
    goals = [
        (1, "Holiday Fund", 1000.00),
        (2, "New Car Fund", 5000.00)
    ]
    cursor.executemany("INSERT OR IGNORE INTO SavingsGoal (id, name, target_amount) VALUES (?, ?, ?)", goals)

    # Test users with hashed passwords, linked to different goals
    users = [
        ("john_doe", "john@example.com", "John Doe", generate_password_hash("password123"), 1),  # Holiday Fund
        ("jane_smith", "jane@example.com", "Jane Smith", generate_password_hash("securepass"), 1),  # Holiday Fund
        ("alice_wonder", "alice@example.com", "Alice Wonder", generate_password_hash("alice123"), 2)  # New Car Fund
    ]
    
    cursor.executemany("INSERT OR IGNORE INTO User (username, email, name, password_hash, goal_id) VALUES (?, ?, ?, ?, ?)", users)

    # Get user IDs
    cursor.execute("SELECT id, username FROM User")
    user_ids = {row[1]: row[0] for row in cursor.fetchall()}

    # Test contributions
    contributions = [
        (user_ids["john_doe"], 100, "2025-02-08"),
        (user_ids["jane_smith"], 200, "2025-02-08"),
        (user_ids["alice_wonder"], 150, "2025-02-07"),
        (user_ids["john_doe"], 50, "2025-02-07")
    ]

    cursor.executemany("INSERT INTO Contribution (user_id, amount, date) VALUES (?, ?, ?)", contributions)

    # Commit and close
    conn.commit()
    conn.close()

    print("Database created successfully with test users, shared goals, and contributions.")

if __name__ == "__main__":
    create_database()