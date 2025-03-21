import streamlit as st
import sqlite3
from PIL import Image
import pytesseract
import spacy
import pandas as pd
import subprocess

nlp = spacy.blank("en")

def categorize_expense(merchant):
    """Categorize an expense based on merchant name."""
    merchant = merchant.lower()
    if "restaurant" in merchant or "cafe" in merchant:
        return "Food"
    elif "gas" in merchant or "fuel" in merchant:
        return "Transportation"
    elif "movie" in merchant or "cinema" in merchant:
        return "Entertainment"
    return "Uncategorized"

def extract_expense_from_image(image):
    """Extract expense details from an image using OCR."""
    text = pytesseract.image_to_string(image)
    doc = nlp(text)
    amount, merchant, date = None, None, None
    for ent in doc.ents:
        if ent.label_ == "MONEY" and not amount:
            amount = float(ent.text.replace("$", "").replace(",", ""))
        elif ent.label_ == "ORG" and not merchant:
            merchant = ent.text
        elif ent.label_ == "DATE" and not date:
            date = ent.text
    return amount, merchant, date

def ocr_input(user_id):
    """Add expense via receipt image upload."""
    st.subheader("Add Expense via Receipt")
    uploaded_file = st.file_uploader("Upload Receipt", type=["png", "jpg"], key="ocr_upload")
    if uploaded_file:
        image = Image.open(uploaded_file)
        amount, merchant, date = extract_expense_from_image(image)
        suggested_category = categorize_expense(merchant or "")
        with st.form("ocr_form"):
            amount = st.number_input("Amount", value=amount or 0.0)
            merchant = st.text_input("Merchant", value=merchant or "")
            date = st.text_input("Date", value=date or "")
            category = st.selectbox("Category", ["Food", "Transportation", "Entertainment", "Uncategorized"],
                                    index=["Food", "Transportation", "Entertainment", "Uncategorized"].index(suggested_category))
            if st.form_submit_button("Save"):
                conn = sqlite3.connect("xpenseai.db")
                c = conn.cursor()
                c.execute("INSERT INTO expenses (payer_id, amount, merchant, date, category) VALUES (?, ?, ?, ?, ?)",
                          (user_id, amount, merchant, date, category))
                expense_id = c.lastrowid
                c.execute("INSERT INTO expense_splits (expense_id, user_id, share_amount) VALUES (?, ?, ?)",
                          (expense_id, user_id, amount))
                conn.commit()
                conn.close()
                st.success("Expense added!")

def text_input(user_id, get_users_func):
    """Add expense manually with split options."""
    st.subheader("Add Expense Manually")
    with st.form("text_form"):
        amount = st.number_input("Amount", min_value=0.0)
        merchant = st.text_input("Merchant")
        date = st.date_input("Date")
        split_users = st.multiselect("Split With", get_users_func(), default=[user_id])
        equal_split = st.checkbox("Split Equally", value=True)
        suggested_category = categorize_expense(merchant or "")
        category = st.selectbox("Category", ["Food", "Transportation", "Entertainment", "Uncategorized"],
                                index=["Food", "Transportation", "Entertainment", "Uncategorized"].index(suggested_category))
        if st.form_submit_button("Save"):
            conn = sqlite3.connect("xpenseai.db")
            c = conn.cursor()
            c.execute("INSERT INTO expenses (payer_id, amount, merchant, date, category) VALUES (?, ?, ?, ?, ?)",
                      (user_id, amount, merchant, str(date), category))
            expense_id = c.lastrowid
            share = amount / len(split_users) if equal_split else amount  # Unequal split logic TBD
            for uid in split_users:
                c.execute("INSERT INTO expense_splits (expense_id, user_id, share_amount) VALUES (?, ?, ?)",
                          (expense_id, uid, share))
            conn.commit()
            conn.close()
            st.success("Expense added!")

def csv_input(user_id):
    """Upload expenses via CSV."""
    st.subheader("Upload Expenses via CSV")
    uploaded_file = st.file_uploader("Upload CSV", type="csv", key="csv_upload")
    if uploaded_file:
        df = pd.read_csv(uploaded_file, names=["date", "merchant", "amount", "category"])
        conn = sqlite3.connect("xpenseai.db")
        c = conn.cursor()
        for _, row in df.iterrows():
            category = categorize_expense(row["merchant"]) if pd.isna(row["category"]) else row["category"]
            c.execute("INSERT INTO expenses (payer_id, amount, merchant, date, category) VALUES (?, ?, ?, ?, ?)",
                      (user_id, row["amount"], row["merchant"], row["date"], category))
            expense_id = c.lastrowid
            c.execute("INSERT INTO expense_splits (expense_id, user_id, share_amount) VALUES (?, ?, ?)",
                      (expense_id, user_id, row["amount"]))
        conn.commit()
        conn.close()
        st.success("Expenses imported!")
