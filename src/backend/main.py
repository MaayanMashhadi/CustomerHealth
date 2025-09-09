from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.requests import Request
import mysql.connector
import pandas as pd
from pathlib import Path
import json
from src.backend.calculate_health_score import get_health_scores, get_health_details
from src.utils import config
db_config = config()
app = FastAPI()
BASE_DIR = Path(__file__).parent
# Construct the absolute path to the templates directory
templates = Jinja2Templates(directory=str(BASE_DIR.parent / "templates"))

@app.get("/api/customers", response_class=HTMLResponse)
def list_customers(request: Request):
    # Get health scores as DataFrame
    df = get_health_scores()
    
    # Convert to list of dicts for templating
    customers = df.to_dict(orient='records')
    
    # Render the HTML template
    return templates.TemplateResponse("customers.html", {"request": request, "customers": customers})

@app.get("/api/customers/{customer_id}/health", response_class=HTMLResponse)
def customer_health(request: Request, customer_id: int):
    # Get all health scores
    
    df = get_health_details()
    
    # Filter for the specific customer
    customer = df[df['customer_id'] == customer_id]
    if customer.empty:
        raise HTTPException(status_code=404, detail="Customer not found")
    
    # Convert to dict for templating
    customer_data = customer.to_dict(orient='records')[0]
    print(customer_data)
    # Render template
    return templates.TemplateResponse(
        "customer_detail.html",
        {"request": request, "customer": customer_data}
    )

from fastapi import HTTPException

@app.post("/api/customers/{customer_id}/events", response_class=HTMLResponse)
async def add_event_html(request: Request, customer_id: int, event: dict):
    event = await request.json()
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
        return templates.TemplateResponse(
        "event_result.html",
        {
            "request": request,
            "success": False,
            "message": f"Unknown event type: {event_type}",
            "event": event
        },
        status_code=400
    )

    # Validate required fields
    missing = [f for f in required_fields[event_type] if f not in details]
    if missing:
        return templates.TemplateResponse(
            "event_result.html",
            {"request": request, "success": False, "message": f"Missing required fields: {', '.join(missing)}", "event": event}
        )

    # Insert into database
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

    return templates.TemplateResponse(
        "event_result.html",
        {"request": request, "success": True, "message": "Event added successfully!", "event": event}
    )


@app.get("/api/dashboard", response_class=HTMLResponse)
def dashboard(request: Request):
    df = get_health_scores()
    customers = df.to_dict(orient='records')
    return templates.TemplateResponse("dashboard.html", {"request": request, "customers": customers})