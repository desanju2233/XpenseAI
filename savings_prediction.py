import streamlit as st
import sqlite3
import pandas as pd
import tensorflow as tf
import numpy as np
from datetime import datetime, timedelta
import joblib

# Load model and preprocessing objects
@st.cache_resource
def load_model_and_preprocessors():
    model = tf.keras.models.load_model("savings_model.h5")
    scaler = joblib.load("scaler.pkl")
    encoder = joblib.load("encoder.pkl")
    return model, scaler, encoder

def get_previous_month_data(user_id):
    """Fetch average monthly data for the previous month from the database."""
    conn = sqlite3.connect("xpenseai.db")
    today = datetime.today()
    first_of_current_month = today.replace(day=1)
    last_of_previous_month = first_of_current_month - timedelta(days=1)
    previous_month = last_of_previous_month.strftime("%Y-%m")

    query = """
        SELECT category, AVG(amount) as avg_amount
        FROM expenses
        WHERE payer_id = ? AND date LIKE ?
        GROUP BY category
    """
    df = pd.read_sql_query(query, conn, params=(user_id, f"{previous_month}%"))
    conn.close()

    input_data = {
        "Income": 20000.0,
        "Age": 30,
        "Dependents": 1,
        "Disposable_Income": 15000.0,
        "Desired_Savings": 5000.0,
        "Groceries": 0.0,
        "Transport": 0.0,
        "Eating_Out": 0.0,
        "Entertainment": 0.0,
        "Utilities": 0.0,
        "Healthcare": 0.0,
        "Education": 0.0,
        "Miscellaneous": 0.0,
        "Occupation": "Professional",  # Adjust if needed
        "City_Tier": "Tier_1"         # Updated default to a common alternative
    }

    for _, row in df.iterrows():
        if row["category"] == "Food":
            input_data["Groceries"] = row["avg_amount"]
            input_data["Eating_Out"] = row["avg_amount"] * 0.5
        elif row["category"] == "Transportation":
            input_data["Transport"] = row["avg_amount"]
        elif row["category"] == "Entertainment":
            input_data["Entertainment"] = row["avg_amount"]

    return input_data

def preprocess_input(input_data, scaler, encoder):
    """Preprocess input data to match training format (17 features)."""
    numerical_features = [
        'Income', 'Age', 'Dependents', 'Disposable_Income', 'Desired_Savings',
        'Groceries', 'Transport', 'Eating_Out', 'Entertainment', 'Utilities',
        'Healthcare', 'Education', 'Miscellaneous'
    ]
    categorical_features = ['Occupation', 'City_Tier']

    # Numerical data
    numerical_df = pd.DataFrame([[
        input_data[feat] for feat in numerical_features
    ]], columns=numerical_features)
    scaled_numerical = scaler.transform(numerical_df)
    numerical_array = scaled_numerical[0]

    # Categorical data with error handling
    categorical_df = pd.DataFrame([[input_data["Occupation"], input_data["City_Tier"]]], columns=categorical_features)
    try:
        encoded_cats = encoder.transform(categorical_df).flatten()
    except ValueError as e:
        st.error(f"Error in categorical encoding: {e}")
        st.write("Expected categories for 'Occupation':", encoder.categories_[0])
        st.write("Expected categories for 'City_Tier':", encoder.categories_[1])
        return None

    # Combine
    return np.concatenate([numerical_array, encoded_cats]).reshape(1, 18)

def savings_prediction(user_id):
    """Display savings prediction section."""
    st.subheader("Savings Prediction")
    model, scaler, encoder = load_model_and_preprocessors()

    today = datetime.today()
    if today.day == 1:
        st.write("Fetching data for the previous month...")
        input_data = get_previous_month_data(user_id)
        preprocessed_input = preprocess_input(input_data, scaler, encoder)
        if preprocessed_input is not None:
            prediction = model.predict(preprocessed_input)[0]
            target_columns = [
                "Potential_Savings_Groceries", "Potential_Savings_Transport",
                "Potential_Savings_Eating_Out", "Potential_Savings_Entertainment",
                "Potential_Savings_Utilities", "Potential_Savings_Healthcare",
                "Potential_Savings_Education", "Potential_Savings_Miscellaneous"
            ]
            for i, output in enumerate(target_columns):
                st.write(f"{output}: ${prediction[i]:.2f}")
    else:
        st.write("Month not completed yet.")
        
        if st.checkbox("Enter data manually for prediction"):
            with st.form("manual_prediction_form"):
                input_data = {
                    "Income": st.number_input("Income", min_value=0.0, value=20000.0),
                    "Age": st.number_input("Age", min_value=0, value=30),
                    "Dependents": st.number_input("Dependents", min_value=0, value=1),
                    "Disposable_Income": st.number_input("Disposable Income", min_value=0.0, value=15000.0),
                    "Desired_Savings": st.number_input("Desired Savings", min_value=0.0, value=5000.0),
                    "Groceries": st.number_input("Groceries", min_value=0.0, value=0.0),
                    "Transport": st.number_input("Transport", min_value=0.0, value=0.0),
                    "Eating_Out": st.number_input("Eating Out", min_value=0.0, value=0.0),
                    "Entertainment": st.number_input("Entertainment", min_value=0.0, value=0.0),
                    "Utilities": st.number_input("Utilities", min_value=0.0, value=0.0),
                    "Healthcare": st.number_input("Healthcare", min_value=0.0, value=0.0),
                    "Education": st.number_input("Education", min_value=0.0, value=0.0),
                    "Miscellaneous": st.number_input("Miscellaneous", min_value=0.0, value=0.0),
                    # Adjust these based on training data categories (example placeholders)
                    "Occupation": st.selectbox("Occupation", ["Professional", "Student", "Other"]),
                    "City_Tier": st.selectbox("City Tier", ["Tier_1", "Tier_2", "Tier_3"])  # Updated options
                }
                if st.form_submit_button("Predict"):
                    preprocessed_input = preprocess_input(input_data, scaler, encoder)
                    if preprocessed_input is not None:
                        prediction = model.predict(preprocessed_input)[0]
                        target_columns = [
                            "Potential_Savings_Groceries", "Potential_Savings_Transport",
                            "Potential_Savings_Eating_Out", "Potential_Savings_Entertainment",
                            "Potential_Savings_Utilities", "Potential_Savings_Healthcare",
                            "Potential_Savings_Education", "Potential_Savings_Miscellaneous"
                        ]
                        for i, output in enumerate(target_columns):
                            st.write(f"{output}: {prediction[i]:.2f}")