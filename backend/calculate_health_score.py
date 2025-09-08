import mysql.connector
import pandas as pd
import os
import json
with open("db_config.json") as f:
    db_config = json.load(f)
    db_config['password'] = os.environ.get('sql_pass')
    
conn = mysql.connector.connect(**db_config)
cursor = conn.cursor(dictionary=True)
def login_freq():
    query = """
    SELECT
        customer_id,
        COUNT(*) / 12 AS avg_logins_per_week
    FROM logins
    WHERE login_date >= NOW() - INTERVAL 3 MONTH
    GROUP BY customer_id
    """
    cursor.execute(query)
    login_freq = cursor.fetchall()

    df_login = pd.DataFrame(login_freq)
    return df_login

def features_used():
    query = """
    SELECT
        customer_id,
        COUNT(DISTINCT feature_name) / 5.0 * 100 AS feature_adoption_score
    FROM feature_usage
    GROUP BY customer_id
    """
    cursor.execute(query)
    feature_adoption = cursor.fetchall()

    df_feature = pd.DataFrame(feature_adoption)
    return df_feature

def tickets():
    # Count of open/pending tickets in last 3 months
    query = """
    SELECT
        customer_id,
        COUNT(*) AS open_tickets
    FROM support_tickets
    WHERE status IN ('open','pending')
    AND created_at >= NOW() - INTERVAL 3 MONTH
    GROUP BY customer_id
    """
    cursor.execute(query)
    tickets = cursor.fetchall()

    df_tickets = pd.DataFrame(tickets)

    # Convert to score (inverse: more tickets = lower score)
    def ticket_score(open_tickets):
        if open_tickets == 0: return 100
        elif open_tickets <= 2: return 75
        elif open_tickets <= 5: return 50
        else: return 25

    df_tickets['ticket_score'] = df_tickets['open_tickets'].apply(ticket_score)
    return df_tickets

def invoice():
    query = """
    SELECT
        customer_id,
        SUM(CASE WHEN paid_date <= due_date THEN 1 ELSE 0 END) / COUNT(*) * 100 AS invoice_payment_score
    FROM invoices
    GROUP BY customer_id
    """
    cursor.execute(query)
    invoices = cursor.fetchall()

    df_invoice = pd.DataFrame(invoices)
    return df_invoice

def api_call():
     # Average API calls per week in last 3 months
    query = """
    SELECT
        customer_id,
        SUM(calls_count) / 12 AS avg_api_calls_per_week
    FROM api_usage
    WHERE usage_date >= NOW() - INTERVAL 3 MONTH
    GROUP BY customer_id
    """
    cursor.execute(query)
    api_usage = cursor.fetchall()

    df_api = pd.DataFrame(api_usage)
    def api_score(calls):
        if calls > 400: return 100
        elif calls > 200: return 75
        elif calls > 50: return 50
        else: return 25

    df_api['api_score'] = df_api['avg_api_calls_per_week'].apply(api_score)
    return df_api



def get_health_scores():
    df_login = login_freq()
    df_feature = features_used()
    df_tickets = tickets()
    df_invoice = invoice()
    df_api = api_call()


    # Merge all dataframes on customer_id
    df = df_login.merge(df_feature, on='customer_id', how='outer') \
                .merge(df_tickets[['customer_id','ticket_score']], on='customer_id', how='outer') \
                .merge(df_invoice, on='customer_id', how='outer') \
                .merge(df_api[['customer_id','api_score']], on='customer_id', how='outer')

    # Optional: convert login and API metrics to 0–100 using thresholds
    # Example for login frequency
    def login_score(avg_logins):
        if avg_logins >= 20: return 100
        elif avg_logins >= 10: return 75
        elif avg_logins >= 5: return 50
        elif avg_logins >= 1: return 25
        else: return 0



    df['login_score'] = df['avg_logins_per_week'].apply(login_score)

    # Example for feature adoption
    df['feature_score'] = df['feature_adoption_score']  # already 0–100

    # Calculate overall health score using weights
    weights = {'login_score':0.25, 'feature_score':0.25, 'ticket_score':0.2,
            'invoice_payment_score':0.15, 'api_score':0.15}

    # Columns that are decimal from MySQL
    decimal_cols = ['login_score', 'feature_score', 'ticket_score', 'invoice_payment_score', 'api_score']

    for col in decimal_cols:
        df[col] = df[col].astype(float)

    df['login_score'] = df['login_score'].fillna(0)
    df['feature_score'] = df['feature_score'].fillna(0)
    df['ticket_score'] = df['ticket_score'].fillna(100)
    df['invoice_payment_score'] = df['invoice_payment_score'].fillna(100)
    df['api_score'] = df['api_score'].fillna(25)

    df['health_score'] = (
        df['login_score']*weights['login_score'] +
        df['feature_score']*weights['feature_score'] +
        df['ticket_score']*weights['ticket_score'] +
        df['invoice_payment_score']*weights['invoice_payment_score'] +
        df['api_score']*weights['api_score']
    )

    return df[['customer_id','health_score']]

# print(get_health_scores())
