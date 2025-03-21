import streamlit as st
import sqlite3
import pandas as pd
import plotly.express as px
from analysis import personal_finance, calculate_debts

def dashboard(user_id):
    """Display the user's financial dashboard."""
    st.title("XpenseAI Dashboard")
    monthly, predicted_budget = personal_finance(user_id)

    # Pie Chart: Spending by Category
    conn = sqlite3.connect("xpenseai.db")
    df = pd.read_sql_query("SELECT category, SUM(amount) as total FROM expenses WHERE payer_id = ? GROUP BY category",
                           conn, params=(user_id,))
    conn.close()
    fig = px.pie(df, values="total", names="category", title="Spending Distribution")
    st.plotly_chart(fig)

    # Line Chart: Budget vs. Actual
    fig = px.line(monthly, y="amount", title=f"Monthly Spending (Predicted Next: ${predicted_budget:.2f})")
    st.plotly_chart(fig)

    # Group Debts
    simplified_debts = calculate_debts()
    if simplified_debts:
        st.subheader("Debt Settlements")
        for from_id, to_id, amount in simplified_debts:
            st.write(f"User {from_id} owes User {to_id} {amount:.2f}")

    # Alerts
    if not monthly.empty and monthly["amount"].iloc[-1] > predicted_budget * 1.2:
        st.warning("You’ve exceeded your predicted budget this month!")