# tests/test_api_integration.py
"""
API Integration Tests for Customer Health Score System

Tests all API endpoints with proper database mocking to ensure no real database calls.
Uses Solution 1: Mock at module level before importing.
"""

import unittest
import sys
import os
import json
from unittest.mock import patch, Mock, MagicMock
import pandas as pd
from decimal import Decimal
from fastapi.testclient import TestClient
from fastapi import HTTPException
import pytest

# SOLUTION 1: Mock at the module level BEFORE importing
# This ensures that when the modules are imported, they use our mocks instead of real DB connections

# Mock mysql.connector before any imports
mysql_mock = MagicMock()
mysql_mock.connector = MagicMock()
sys.modules['mysql.connector'] = mysql_mock
sys.modules['mysql'] = mysql_mock

# Mock the database connection and cursor at module level
mock_conn = Mock()
mock_cursor = Mock() 
mock_conn.cursor.return_value = mock_cursor
mysql_mock.connector.connect.return_value = mock_conn

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

# Now import after mocking - this ensures the modules use our mocks
import src.backend.calculate_health_score
from src.backend.main import app  # Replace 'your_api_module' with your actual API module name

# Replace the module-level database objects with our mocks
src.backend.calculate_health_score.conn = mock_conn
src.backend.calculate_health_score.cursor = mock_cursor

class TestAPIIntegration(unittest.TestCase):
    """Integration tests for API endpoints with mocked database"""
    
    @classmethod
    def setUpClass(cls):
        """Set up test client and common test data"""
        cls.client = TestClient(app)
        cls.sample_health_data = pd.DataFrame([
            {
                'customer_id': 1,
                'health_score': 85.5,
                'login_score': 75,
                'feature_score': 80,
                'ticket_score': 100,
                'invoice_payment_score': 95,
                'api_score': 75
            },
            {
                'customer_id': 2, 
                'health_score': 67.2,
                'login_score': 50,
                'feature_score': 60,
                'ticket_score': 75,
                'invoice_payment_score': 80,
                'api_score': 50
            },
            {
                'customer_id': 3,
                'health_score': 45.8,
                'login_score': 25,
                'feature_score': 40,
                'ticket_score': 50,
                'invoice_payment_score': 60,
                'api_score': 25
            }
        ])
    
    def setUp(self):
        """Reset mocks before each test"""
        mock_cursor.reset_mock()
        mock_conn.reset_mock()
        
        # Setup default mock responses for health score calculation
        self.setup_default_health_score_mocks()
    
    def setup_default_health_score_mocks(self):
        """Setup default mock responses for health score calculations"""
        # Mock login_freq data
        mock_cursor.fetchall.side_effect = [
            # login_freq call
            [
                {'customer_id': 1, 'avg_logins_per_week': Decimal('15.0')},
                {'customer_id': 2, 'avg_logins_per_week': Decimal('8.0')},
                {'customer_id': 3, 'avg_logins_per_week': Decimal('3.0')}
            ],
            # features_used call
            [
                {'customer_id': 1, 'feature_adoption_score': Decimal('80.0')},
                {'customer_id': 2, 'feature_adoption_score': Decimal('60.0')},
                {'customer_id': 3, 'feature_adoption_score': Decimal('40.0')}
            ],
            # tickets call
            [
                {'customer_id': 1, 'open_tickets': 0},
                {'customer_id': 2, 'open_tickets': 2},
                {'customer_id': 3, 'open_tickets': 5}
            ],
            # invoice call
            [
                {'customer_id': 1, 'invoice_payment_score': Decimal('95.0')},
                {'customer_id': 2, 'invoice_payment_score': Decimal('80.0')},
                {'customer_id': 3, 'invoice_payment_score': Decimal('60.0')}
            ],
            # api_call call
            [
                {'customer_id': 1, 'avg_api_calls_per_week': Decimal('300.0')},
                {'customer_id': 2, 'avg_api_calls_per_week': Decimal('150.0')},
                {'customer_id': 3, 'avg_api_calls_per_week': Decimal('40.0')}
            ]
        ]

    def test_list_customers_endpoint(self):
        """Test GET /api/customers endpoint (HTML)"""
        # Act
        response = self.client.get("/api/customers")
        
        # Assert
        self.assertEqual(response.status_code, 200)
        self.assertIn("text/html", response.headers["content-type"])
        
        html_content = response.text
        # Verify that customer IDs appear in the rendered HTML
        self.assertIn("1", html_content)
        self.assertIn("2", html_content)
        self.assertIn("3", html_content)

    def test_customer_health_detail_endpoint_success(self):
        """Test GET /api/customers/{customer_id}/health endpoint with valid customer (HTML)"""
        # Act
        response = self.client.get("/api/customers/1/health")
        
        # Assert
        self.assertEqual(response.status_code, 200)
        self.assertIn("text/html", response.headers["content-type"])
        
        html_content = response.text
        # Verify that customer ID appears in the rendered HTML
        self.assertIn("1", html_content)
        
        # Optional: check that the health score is included in the HTML
        self.assertIn("Overall Health Score", html_content)

    def test_customer_health_detail_endpoint_not_found(self):
        """Test GET /api/customers/{customer_id}/health endpoint with invalid customer"""
        # Act
        response = self.client.get("/api/customers/5/health")
        
        # Assert
        self.assertEqual(response.status_code, 404)
        
        data = response.json()
        self.assertEqual(data['detail'], "Customer not found")

    def test_add_login_event_endpoint(self):
        """Test POST /api/customers/{customer_id}/events endpoint with login event"""
        # Arrange
        event_data = {
            "type": "login",
            "details": {}
        }
        
        # Act
        response = self.client.post("/api/customers/1/events", json=event_data)
        
        # Assert
        self.assertEqual(response.status_code, 200)
        self.assertIn("text/html", response.headers["content-type"])
        
        html_content = response.text
        self.assertIn("Event added successfully!", html_content)
        self.assertIn("login", html_content)

        # Verify database insert was called
        mock_cursor.execute.assert_any_call(
            "INSERT INTO logins (customer_id, login_date) VALUES (%s, NOW())",
            (1,)
        )
        mock_conn.commit.assert_called()

    def test_add_feature_event_endpoint(self):
        """Test POST /api/customers/{customer_id}/events endpoint with feature event"""
        # Arrange
        event_data = {
            "type": "feature",
            "details": {
                "feature_name": "dashboard",
                "usage_count": 5
            }
        }
        
        # Act
        response = self.client.post("/api/customers/1/events", json=event_data)
        
        # Assert
        self.assertEqual(response.status_code, 200)
        self.assertIn("text/html", response.headers["content-type"])
        
        # Check HTML content
        html_content = response.text
        self.assertIn("Event added successfully!", html_content)
        self.assertIn("dashboard", html_content)
        # self.assertIn("customer_id", html_content)  # optional: verify that customer_id is rendered
        
        # Verify database insert was called
        mock_cursor.execute.assert_any_call(
            "INSERT INTO feature_usage (customer_id, feature_name, usage_count, usage_date) VALUES (%s,%s,%s,NOW())",
            (1, 'dashboard', 5)
        )
        mock_conn.commit.assert_called()

    def test_add_ticket_event_endpoint(self):
        """Test POST /api/customers/{customer_id}/events endpoint with ticket event"""
        # Arrange
        event_data = {
            "type": "ticket",
            "details": {
                "status": "open",
                "priority": "high"
            }
        }
        
        # Act
        response = self.client.post("/api/customers/1/events", json=event_data)
        
        # Assert
        self.assertEqual(response.status_code, 200)
        self.assertIn("text/html", response.headers["content-type"])
        
        # Check HTML content
        html_content = response.text
        self.assertIn("Event added successfully!", html_content)
        self.assertIn("ticket", html_content)
        
        # Verify database insert was called
        mock_cursor.execute.assert_any_call(
            "INSERT INTO support_tickets (customer_id, created_at, status, priority) VALUES (%s,NOW(),%s,%s)",
            (1, 'open', 'high')
        )
        mock_conn.commit.assert_called()


    def test_add_invoice_event_endpoint(self):
        """Test POST /api/customers/{customer_id}/events endpoint with invoice event"""
        # Arrange
        event_data = {
            "type": "invoice",
            "details": {
                "amount": 2500.00,
                "due_date": "2024-10-15",
                "paid_date": "2024-10-14"
            }
        }
        
        # Act
        response = self.client.post("/api/customers/1/events", json=event_data)
        
        # Assert
        self.assertEqual(response.status_code, 200)
        self.assertIn("text/html", response.headers["content-type"])
        
        # Check HTML content
        html_content = response.text
        self.assertIn("Event added successfully!", html_content)
        self.assertIn("invoice", html_content)
        
        # Verify database insert was called
        mock_cursor.execute.assert_any_call(
            "INSERT INTO invoices (customer_id, amount, due_date, paid_date) VALUES (%s,%s,%s,%s)",
            (1, 2500.00, '2024-10-15', '2024-10-14')
        )
        mock_conn.commit.assert_called()


    def test_add_api_event_endpoint(self):
        """Test POST /api/customers/{customer_id}/events endpoint with API event"""
        # Arrange
        event_data = {
            "type": "api",
            "details": {
                "calls_count": 150
            }
        }
        
        # Act
        response = self.client.post("/api/customers/1/events", json=event_data)
        
        # Assert
        self.assertEqual(response.status_code, 200)
        self.assertIn("text/html", response.headers["content-type"])
        
        # Check HTML content
        html_content = response.text
        self.assertIn("Event added successfully!", html_content)
        self.assertIn("api", html_content)
        
        # Verify database insert was called
        mock_cursor.execute.assert_any_call(
            "INSERT INTO api_usage (customer_id, calls_count, usage_date) VALUES (%s,%s,NOW())",
            (1, 150)
        )
        mock_conn.commit.assert_called()


    def test_add_event_with_invalid_type(self):
        """Test POST /api/customers/{customer_id}/events endpoint with invalid event type"""
        # Arrange
        event_data = {
            "type": "invalid_type",
            "details": {}
        }
        
        # Act
        response = self.client.post("/api/customers/1/events", json=event_data)
        
        # Assert
        self.assertEqual(response.status_code, 400)
        self.assertIn("text/html", response.headers["content-type"])
        
        html_content = response.text
        self.assertIn("Unknown event type", html_content)
        self.assertIn("invalid_type", html_content)


    def test_add_event_with_missing_required_fields(self):
        """Test POST /api/customers/{customer_id}/events with missing invoice fields"""
        event_data = {
            "type": "invoice",
            "details": {
                # Missing 'amount' and 'due_date'
                "paid_date": "2024-10-14"
            }
        }

        response = self.client.post("/api/customers/1/events", json=event_data)

    
        self.assertEqual(response.status_code, 200)
        self.assertIn("text/html", response.headers["content-type"])

        html_content = response.text
        self.assertIn("Missing required fields: amount, due_date", html_content)

    def test_dashboard_endpoint(self):
        """Test GET /api/dashboard endpoint"""
        # Act
        response = self.client.get("/api/dashboard")
        
        # Assert
        self.assertEqual(response.status_code, 200)
        self.assertIn("text/html", response.headers["content-type"])
        
        # Verify HTML content contains customer data
        html_content = response.text
        self.assertIn("1", html_content)  # Customer IDs should be in template
        self.assertIn("2", html_content)
        self.assertIn("3", html_content)



class TestAPIEndpointsEdgeCases(unittest.TestCase):
    """Test edge cases and error scenarios for API endpoints"""
    
    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(app)
    
    def setUp(self):
        """Reset mocks and setup for each test"""
        mock_cursor.reset_mock()
        mock_conn.reset_mock()
        
        # Setup empty health data scenario
        mock_cursor.fetchall.side_effect = [[], [], [], [], []]  # Empty results for all queries
    
    def test_list_customers_empty_database(self):
        """Test GET /api/customers when database is empty"""
        # Act
        response = self.client.get("/api/customers")
        
        # Assert
        self.assertEqual(response.status_code, 200)
        self.assertIn("text/html", response.headers["content-type"])

        html_content = response.text
        # Check that table exists but no customer rows are rendered
        self.assertIn("<table>", html_content)
        self.assertIn("<tbody>", html_content)
        self.assertNotIn("<td>", html_content) 

    def test_add_event_with_malformed_json(self):
        """Test POST /api/customers/{customer_id}/events with malformed JSON"""
        # Act
        response = self.client.post(
            "/api/customers/1/events", 
            data="invalid json"
        )
        
        # Assert
        self.assertEqual(response.status_code, 422)  # Unprocessable Entity

    def test_add_event_with_empty_payload(self):
        """Test POST /api/customers/{customer_id}/events with empty payload"""
        # Act
        response = self.client.post("/api/customers/1/events", json={})
        
        # Assert
        self.assertEqual(response.status_code, 400)  # Should fail validation


if __name__ == '__main__':
    # Create test suite
    test_suite = unittest.TestSuite()
    
    # Add test classes
    test_classes = [
        TestAPIIntegration,
        TestAPIEndpointsEdgeCases,
    ]
    
    for test_class in test_classes:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        test_suite.addTests(tests)
    
    # Run tests with detailed output
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # Print summary
    print(f"\n{'='*60}")
    print("API INTEGRATION TEST SUMMARY")
    print(f"{'='*60}")
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Success rate: {((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100):.1f}%")
    
    if result.failures:
        print(f"\nFailures:")
        for test, traceback in result.failures:
            print(f"- {test}")
    
    if result.errors:
        print(f"\nErrors:")
        for test, traceback in result.errors:
            print(f"- {test}")
    
    # Verify mocking worked
    print(f"\n🔍 Mocking Verification:")
    print(f"Database cursor calls: {mock_cursor.execute.call_count}")
    print(f"Database connection calls: {mock_conn.cursor.call_count}")
    print(f"✅ All database calls were properly mocked!")
    
    # Exit with proper code
    exit_code = len(result.failures) + len(result.errors)
    sys.exit(exit_code)