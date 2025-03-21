import sqlite3
import pandas as pd

def personal_finance(user_id):
    """Analyze personal spending patterns."""
    conn = sqlite3.connect("xpenseai.db")
    df = pd.read_sql_query(
        "SELECT date, amount, category FROM expenses WHERE payer_id = ?",
        conn, params=(user_id,))
    conn.close()
    monthly = df.groupby(df["date"].str[:7]).agg({"amount": "sum"})
    moving_avg = monthly["amount"].rolling(window=3, min_periods=1).mean()
    predicted_budget = moving_avg.iloc[-1] if not moving_avg.empty else 0
    return monthly, predicted_budget

def calculate_debts():
    """Calculate and simplify group debts."""
    conn = sqlite3.connect("xpenseai.db")
    splits = pd.read_sql_query("SELECT expense_id, user_id, share_amount FROM expense_splits", conn)
    expenses = pd.read_sql_query("SELECT expense_id, payer_id FROM expenses", conn)
    payments = pd.read_sql_query("SELECT from_user_id, to_user_id, amount FROM payments", conn)
    conn.close()

    debts = {}
    for _, exp in expenses.iterrows():
        splits_for_exp = splits[splits["expense_id"] == exp["expense_id"]]
        for _, split in splits_for_exp.iterrows():
            if split["user_id"] != exp["payer_id"]:
                pair = (split["user_id"], exp["payer_id"])
                debts[pair] = debts.get(pair, 0) + split["share_amount"]

    for _, pay in payments.iterrows():
        pair = (pay["from_user_id"], pay["to_user_id"])
        debts[pair] = debts.get(pair, 0) - pay["amount"]

    net_debts = {k: v for k, v in debts.items() if v > 0}

    simplified = []
    while net_debts:
        max_debtor = max(net_debts.items(), key=lambda x: x[1])[0]
        max_creditor = min(net_debts.items(), key=lambda x: x[1] if x[1] < 0 else float('inf'))[0]
        amount = min(net_debts[max_debtor], abs(net_debts[max_creditor]))
        simplified.append((max_debtor[0], max_creditor[1], amount))
        net_debts[max_debtor] -= amount
        net_debts[max_creditor] += amount
        if net_debts[max_debtor] == 0:
            del net_debts[max_debtor]
        if net_debts[max_creditor] == 0:
            del net_debts[max_creditor]
    return simplified