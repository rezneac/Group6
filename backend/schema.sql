-- Create SavingsGoal table
CREATE TABLE IF NOT EXISTS SavingsGoal (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    target_amount NUMERIC(8, 2) NOT NULL
);

-- Create User table
CREATE TABLE IF NOT EXISTS User (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    email TEXT NOT NULL,
    name TEXT NOT NULL,
    password_hash TEXT NOT NULL,
    goal_id INTEGER,  -- Each user is linked to ONE goal
    FOREIGN KEY (goal_id) REFERENCES SavingsGoal(id) ON DELETE SET NULL
);

-- Create Contribution table
CREATE TABLE IF NOT EXISTS Contribution (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    amount REAL NOT NULL,
    date TEXT NOT NULL,
    FOREIGN KEY (user_id) REFERENCES User(id) ON DELETE CASCADE
);