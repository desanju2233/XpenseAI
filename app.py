import streamlit as st
from db_init import init_db
from auth import login, get_users
from expense_input import ocr_input, text_input, csv_input
from dashboard import dashboard
from user_actions import savings_goals, record_payment
from savings_prediction import savings_prediction

def main():
    """Main application logic with navigation."""
    init_db()

    if "user_id" not in st.session_state:
        login()
    else:
        st.sidebar.title("Navigation")
        page = st.sidebar.radio("Go to", ["Dashboard", "Add Expense", "Record Payment", "Savings Goals", "Savings Prediction"])
        user_id = st.session_state["user_id"]
        st.write(f"Welcome, User {user_id}!")

        if st.sidebar.button("Logout"):
            del st.session_state["user_id"]
            st.rerun()

        if page == "Dashboard":
            dashboard(user_id)
        elif page == "Add Expense":
            ocr_input(user_id)
            text_input(user_id, get_users)
            csv_input(user_id)
        elif page == "Record Payment":
            record_payment(user_id)
        elif page == "Savings Goals":
            savings_goals(user_id)
        elif page == "Savings Prediction":
            savings_prediction(user_id)

if __name__ == "__main__":
    main()