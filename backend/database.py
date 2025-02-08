import sqlite3
from werkzeug.security import generate_password_hash

def create_database():
    # Connect to SQLite3 database (or create it if it doesn't exist)
    conn = sqlite3.connect("savings.db")
    cursor = conn.cursor()
    
    # Create User table with password hash
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS User (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        email TEXT NOT NULL,
        name TEXT NOT NULL,
        password_hash TEXT NOT NULL
    )
    """)
    
    # Create Contribution table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Contribution (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL,
        amount REAL NOT NULL,
        date TEXT NOT NULL,
        FOREIGN KEY (username) REFERENCES User(username)
    )
    """)
    
    # Test users with hashed passwords
    users = [
        ("john_doe", "john@example.com", "John Doe", generate_password_hash("password123")),
        ("jane_smith", "jane@example.com", "Jane Smith", generate_password_hash("securepass")),
        ("alice_wonder", "alice@example.com", "Alice Wonder", generate_password_hash("alice123"))
    ]
    
    # Insert users into the User table
    cursor.executemany("""
    INSERT OR IGNORE INTO User (username, email, name, password_hash)
    VALUES (?, ?, ?, ?)
    """, users)
    
    # Test data for contributions
    contributions = [
        ("john_doe", 100, "2025-02-08"),
        ("jane_smith", 200, "2025-02-08"),
        ("alice_wonder", 150, "2025-02-07"),
        ("john_doe", 50, "2025-02-07")
    ]
    
    # Insert contributions into the Contribution table
    cursor.executemany("""
    INSERT INTO Contribution (username, amount, date)
    VALUES (?, ?, ?)
    """, contributions)
    
    # Commit changes and close the connection
    conn.commit()
    conn.close()
    
    print("Database and tables created successfully with test users and test data.")

if __name__ == "__main__":
    create_database()