from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.requests import Request
import mysql.connector
import pandas as pd
from pathlib import Path
import json
from src.backend.calculate_health_score import get_health_scores
from src.utils import config
db_config = config()
app = FastAPI()
BASE_DIR = Path(__file__).parent
# Construct the absolute path to the templates directory
templates = Jinja2Templates(directory=str(BASE_DIR.parent / "templates"))

@app.get("/api/customers")
def list_customers():
    df = get_health_scores()
    return df.to_dict(orient='records')

@app.get("/api/customers/{customer_id}/health")
def customer_health(customer_id: int):
    df = get_health_scores()
    customer = df[df['customer_id']==customer_id]
    if customer.empty:
        raise HTTPException(status_code=404, detail="Customer not found")
    return customer.to_dict(orient='records')[0]

from fastapi import HTTPException

@app.post("/api/customers/{customer_id}/events")
def add_event(customer_id: int, event: dict):
    event_type = event.get("type")
    details = event.get("details", {})

    required_fields = {
        "login": [],
        "feature": ["feature_name"],
        "ticket": [],
        "invoice": ["amount", "due_date"],
        "api": []
    }

    if event_type not in required_fields:
        raise HTTPException(status_code=400, detail="Unknown event type")

    # Validate required fields
    missing = [f for f in required_fields[event_type] if f not in details]
    if missing:
        raise HTTPException(
            status_code=400,
            detail=f"Missing required fields: {', '.join(missing)}"
        )

    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()
    try:
        if event_type == "login":
            cursor.execute(
                "INSERT INTO logins (customer_id, login_date) VALUES (%s, NOW())",
                (customer_id,)
            )
        elif event_type == "feature":
            cursor.execute(
                "INSERT INTO feature_usage (customer_id, feature_name, usage_count, usage_date) VALUES (%s,%s,%s,NOW())",
                (customer_id, details['feature_name'], details.get('usage_count', 1))
            )
        elif event_type == "ticket":
            cursor.execute(
                "INSERT INTO support_tickets (customer_id, created_at, status, priority) VALUES (%s,NOW(),%s,%s)",
                (customer_id, details.get('status', 'open'), details.get('priority', 'medium'))
            )
        elif event_type == "invoice":
            cursor.execute(
                "INSERT INTO invoices (customer_id, amount, due_date, paid_date) VALUES (%s,%s,%s,%s)",
                (customer_id, details['amount'], details['due_date'], details.get('paid_date'))
            )
        elif event_type == "api":
            cursor.execute(
                "INSERT INTO api_usage (customer_id, calls_count, usage_date) VALUES (%s,%s,NOW())",
                (customer_id, details.get('calls_count', 1))
            )

        conn.commit()
    finally:
        cursor.close()
        conn.close()

    return {"status": "success", "event": event}


@app.get("/api/dashboard", response_class=HTMLResponse)
def dashboard(request: Request):
    df = get_health_scores()
    customers = df.to_dict(orient='records')
    return templates.TemplateResponse("dashboard.html", {"request": request, "customers": customers})