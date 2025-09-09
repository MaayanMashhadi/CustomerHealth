import mysql.connector
from faker import Faker
import random
from datetime import datetime, timedelta
import os
import json
from pathlib import Path
BASE_DIR = Path(__file__).parent
# --- Database Connection ---
print(f"using base dir {BASE_DIR}")
with open(str(BASE_DIR.parent / "src/db_config.json")) as f:
    db_config = json.load(f)
db_config["host"] = os.getenv("DB_HOST", db_config["host"])
conn = mysql.connector.connect(**db_config)
cursor = conn.cursor()
faker = Faker()
# --- Idempotency Check ---
try:
    cursor.execute("SELECT COUNT(*) FROM customers")
    result = cursor.fetchone()
    if result[0] > 0:
        print("Data already exists. Skipping data generation.")
        cursor.close()
        conn.close()
        # Exit the script
        exit()
except mysql.connector.Error as err:
    print(f"Error checking for existing data: {err}")
    cursor.close()
    conn.close()
    exit()
# --- Parameters ---
NUM_CUSTOMERS = 60
NUM_MONTHS = 3
START_DATE = datetime.now() - timedelta(days=NUM_MONTHS * 30)

# --- Helper function ---
def random_date(start, end):
    delta = end - start
    return start + timedelta(days=random.randint(0, delta.days))

# --- Insert Customers ---
segments = ['Enterprise', 'SMB', 'Startup']
customers = []
for _ in range(NUM_CUSTOMERS):
    name = faker.company()
    email = faker.company_email()
    segment = random.choice(segments)
    created_at = random_date(START_DATE, datetime.now())
    cursor.execute(
        "INSERT INTO customers (name, email, segment, created_at) VALUES (%s, %s, %s, %s)",
        (name, email, segment, created_at)
    )
    customers.append(cursor.lastrowid)

conn.commit()

# --- Insert Login Activity ---
for customer_id in customers:
    for _ in range(random.randint(10, 100)):
        login_date = random_date(START_DATE, datetime.now())
        cursor.execute(
            "INSERT INTO logins (customer_id, login_date) VALUES (%s, %s)",
            (customer_id, login_date)
        )

conn.commit()

# --- Insert Feature Usage ---
features = ['Feature_A', 'Feature_B', 'Feature_C', 'Feature_D', 'Feature_E']
for customer_id in customers:
    for _ in range(random.randint(5, 20)):
        feature = random.choice(features)
        usage_count = random.randint(1, 15)
        usage_date = random_date(START_DATE, datetime.now())
        cursor.execute(
            "INSERT INTO feature_usage (customer_id, feature_name, usage_count, usage_date) VALUES (%s, %s, %s, %s)",
            (customer_id, feature, usage_count, usage_date)
        )

conn.commit()

# --- Insert Support Tickets ---
ticket_statuses = ['open', 'closed', 'pending']
priorities = ['low', 'medium', 'high']
for customer_id in customers:
    for _ in range(random.randint(0, 5)):  # some customers may have no tickets
        created_at = random_date(START_DATE, datetime.now())
        status = random.choice(ticket_statuses)
        priority = random.choice(priorities)
        cursor.execute(
            "INSERT INTO support_tickets (customer_id, created_at, status, priority) VALUES (%s, %s, %s, %s)",
            (customer_id, created_at, status, priority)
        )

conn.commit()

# --- Insert Invoices ---
for customer_id in customers:
    for _ in range(random.randint(1, 5)):  # 1–5 invoices per customer
        amount = round(random.uniform(100, 1000), 2)
        due_date = random_date(START_DATE, datetime.now())
        paid_date = None if random.random() < 0.2 else random_date(due_date, datetime.now())
        cursor.execute(
            "INSERT INTO invoices (customer_id, amount, due_date, paid_date) VALUES (%s, %s, %s, %s)",
            (customer_id, amount, due_date, paid_date)
        )

conn.commit()

# --- Insert API Usage ---
for customer_id in customers:
    for _ in range(random.randint(10, 30)):  # 10–30 API usage records
        calls_count = random.randint(10, 500)
        usage_date = random_date(START_DATE, datetime.now())
        cursor.execute(
            "INSERT INTO api_usage (customer_id, calls_count, usage_date) VALUES (%s, %s, %s)",
            (customer_id, calls_count, usage_date)
        )

conn.commit()

cursor.close()
conn.close()
print("Sample data generation completed successfully!")
