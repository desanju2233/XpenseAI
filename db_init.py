import sqlite3

def init_db():
    """Initialize the SQLite database with required tables."""
    conn = sqlite3.connect("xpenseai.db")
    c = conn.cursor()

    # Create users table
    c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            email TEXT
        )
    """)

    # Create expenses table
    c.execute("""
        CREATE TABLE IF NOT EXISTS expenses (
            expense_id INTEGER PRIMARY KEY AUTOINCREMENT,
            payer_id INTEGER,
            amount REAL NOT NULL,
            merchant TEXT,
            date TEXT,
            category TEXT,
            FOREIGN KEY (payer_id) REFERENCES users(user_id)
        )
    """)

    # Create expense_splits table
    c.execute("""
        CREATE TABLE IF NOT EXISTS expense_splits (
            expense_id INTEGER,
            user_id INTEGER,
            share_amount REAL NOT NULL,
            PRIMARY KEY (expense_id, user_id),
            FOREIGN KEY (expense_id) REFERENCES expenses(expense_id),
            FOREIGN KEY (user_id) REFERENCES users(user_id)
        )
    """)

    # Create payments table
    c.execute("""
        CREATE TABLE IF NOT EXISTS payments (
            payment_id INTEGER PRIMARY KEY AUTOINCREMENT,
            from_user_id INTEGER,
            to_user_id INTEGER,
            amount REAL NOT NULL,
            date TEXT,
            FOREIGN KEY (from_user_id) REFERENCES users(user_id),
            FOREIGN KEY (to_user_id) REFERENCES users(user_id)
        )
    """)

    # Create categories table
    c.execute("""
        CREATE TABLE IF NOT EXISTS categories (
            category_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL
        )
    """)

    # Insert default categories if not already present
    c.execute("INSERT OR IGNORE INTO categories (name) VALUES ('Food'), ('Transportation'), ('Entertainment')")

    conn.commit()
    conn.close()

if __name__ == "__main__":
    init_db()