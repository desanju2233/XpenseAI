import streamlit as st
import sqlite3
from auth import get_users

def savings_goals(user_id):
    """Set and display savings goals."""
    st.subheader("Set Savings Goal")
    goal = st.number_input("Monthly Savings Goal", min_value=0.0)
    if st.button("Save Goal"):
        st.session_state["savings_goal"] = goal
        st.success("Goal saved!")
    if "savings_goal" in st.session_state:
        st.write(f"Current Savings Goal: ${st.session_state['savings_goal']:.2f}")

def record_payment(user_id):
    """Record a payment between users."""
    st.subheader("Record Payment")
    with st.form("payment_form"):
        to_user = st.selectbox("Paid To", get_users())
        amount = st.number_input("Amount", min_value=0.0)
        date = st.date_input("Date")
        if st.form_submit_button("Record"):
            conn = sqlite3.connect("xpenseai.db")
            c = conn.cursor()
            c.execute("INSERT INTO payments (from_user_id, to_user_id, amount, date) VALUES (?, ?, ?, ?)",
                      (user_id, to_user, amount, str(date)))
            conn.commit()
            conn.close()
            st.success("Payment recorded!")