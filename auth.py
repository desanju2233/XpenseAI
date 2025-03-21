import streamlit as st
import sqlite3

def check_credentials(username, password):
    """Verify user credentials against the database."""
    conn = sqlite3.connect("xpenseai.db")
    c = conn.cursor()
    c.execute("SELECT user_id FROM users WHERE username = ? AND password = ?", (username, password))
    user = c.fetchone()
    conn.close()
    return user[0] if user else None

def register_user(username, password, email):
    """Register a new user in the database."""
    conn = sqlite3.connect("xpenseai.db")
    c = conn.cursor()
    try:
        c.execute("INSERT INTO users (username, password, email) VALUES (?, ?, ?)",
                  (username, password, email))
        conn.commit()
        user_id = c.lastrowid  # Get the ID of the newly inserted user
        st.session_state["user_id"] = user_id  # Set user_id immediately
        st.success(f"User {username} registered successfully! Logging you in...")
        st.rerun()  # Re-run to switch to main interface
    except sqlite3.IntegrityError:
        st.error("Username already exists. Please choose a different username.")
    finally:
        conn.close()

def login():
    """Display login page and handle authentication."""
    st.title("XpenseAI Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        user_id = check_credentials(username, password)
        if user_id:
            st.session_state["user_id"] = user_id
            st.success("Logged in successfully!")
            st.rerun()  # Re-run to switch to main interface
        else:
            st.error("Invalid credentials")
    
    # Add register option
    st.write("Don't have an account? Register below:")
    with st.form("register_form"):
        new_username = st.text_input("New Username")
        new_password = st.text_input("New Password", type="password")
        new_email = st.text_input("Email (optional)", "")
        if st.form_submit_button("Register"):
            if new_username and new_password:
                register_user(new_username, new_password, new_email if new_email else None)
            else:
                st.error("Username and password are required!")

def get_users():
    """Retrieve list of user IDs from the database."""
    conn = sqlite3.connect("xpenseai.db")
    c = conn.cursor()
    c.execute("SELECT user_id FROM users")
    users = [row[0] for row in c.fetchall()]
    conn.close()
    return users