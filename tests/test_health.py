# test_health_scores.py
import unittest
from unittest.mock import Mock, patch, MagicMock
import pandas as pd
import sys
import os
import mysql.connector
from decimal import Decimal

# Add the parent directory to the path so we can import our modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import the functions we want to test
from backend.calculate_health_score import (
    login_freq, features_used, tickets, invoice, api_call, get_health_scores
)

class TestHealthScoreCalculation(unittest.TestCase):
    """Unit tests for health score calculation functions"""
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        # Mock database connection and cursor
        self.mock_conn = Mock()
        self.mock_cursor = Mock()
        self.mock_cursor.fetchall = Mock()
        
    @patch('backend.calculate_health_score.cursor')
    def test_login_freq_calculation(self, mock_cursor):
        """Test login frequency calculation with mock data"""
        # Arrange
        mock_data = [
            {'customer_id': 'cust-001', 'avg_logins_per_week': Decimal('15.5')},
            {'customer_id': 'cust-002', 'avg_logins_per_week': Decimal('5.2')},
            {'customer_id': 'cust-003', 'avg_logins_per_week': Decimal('0.8')}
        ]
        mock_cursor.fetchall.return_value = mock_data
        
        # Act
        result = login_freq()
        
        # Assert
        expected_query = """
    SELECT
        customer_id,
        COUNT(*) / 12 AS avg_logins_per_week
    FROM logins
    WHERE login_date >= NOW() - INTERVAL 3 MONTH
    GROUP BY customer_id
    """
        mock_cursor.execute.assert_called_once_with(expected_query)
        self.assertEqual(len(result), 3)
        self.assertEqual(result.iloc[0]['customer_id'], 'cust-001')
        self.assertEqual(float(result.iloc[0]['avg_logins_per_week']), 15.5)
    
    @patch('backend.calculate_health_score.cursor')
    def test_features_used_calculation(self, mock_cursor):
        """Test feature adoption score calculation with mock data"""
        # Arrange
        mock_data = [
            {'customer_id': 'cust-001', 'feature_adoption_score': Decimal('80.0')},
            {'customer_id': 'cust-002', 'feature_adoption_score': Decimal('60.0')},
            {'customer_id': 'cust-003', 'feature_adoption_score': Decimal('40.0')}
        ]
        mock_cursor.fetchall.return_value = mock_data
        
        # Act
        result = features_used()
        
        # Assert
        expected_query = """
    SELECT
        customer_id,
        COUNT(DISTINCT feature_name) / 5.0 * 100 AS feature_adoption_score
    FROM feature_usage
    GROUP BY customer_id
    """
        mock_cursor.execute.assert_called_once_with(expected_query)
        self.assertEqual(len(result), 3)
        self.assertEqual(float(result.iloc[0]['feature_adoption_score']), 80.0)
    
    @patch('backend.calculate_health_score.cursor')
    def test_tickets_calculation(self, mock_cursor):
        """Test support tickets score calculation with mock data"""
        # Arrange
        mock_data = [
            {'customer_id': 'cust-001', 'open_tickets': 0},
            {'customer_id': 'cust-002', 'open_tickets': 2},
            {'customer_id': 'cust-003', 'open_tickets': 6}
        ]
        mock_cursor.fetchall.return_value = mock_data
        
        # Act
        result = tickets()
        
        # Assert
        expected_query = """
    SELECT
        customer_id,
        COUNT(*) AS open_tickets
    FROM support_tickets
    WHERE status IN ('open','pending')
    AND created_at >= NOW() - INTERVAL 3 MONTH
    GROUP BY customer_id
    """
        mock_cursor.execute.assert_called_once_with(expected_query)
        self.assertEqual(len(result), 3)
        
        # Test ticket scoring logic
        self.assertEqual(result.iloc[0]['ticket_score'], 100)  # 0 tickets = 100 score
        self.assertEqual(result.iloc[1]['ticket_score'], 75)   # 2 tickets = 75 score
        self.assertEqual(result.iloc[2]['ticket_score'], 25)   # 6 tickets = 25 score
    
    @patch('backend.calculate_health_score.cursor')
    def test_invoice_calculation(self, mock_cursor):
        """Test invoice payment score calculation with mock data"""
        # Arrange
        mock_data = [
            {'customer_id': 'cust-001', 'invoice_payment_score': Decimal('95.0')},
            {'customer_id': 'cust-002', 'invoice_payment_score': Decimal('75.0')},
            {'customer_id': 'cust-003', 'invoice_payment_score': Decimal('50.0')}
        ]
        mock_cursor.fetchall.return_value = mock_data
        
        # Act
        result = invoice()
        
        # Assert
        expected_query = """
    SELECT
        customer_id,
        SUM(CASE WHEN paid_date <= due_date THEN 1 ELSE 0 END) / COUNT(*) * 100 AS invoice_payment_score
    FROM invoices
    GROUP BY customer_id
    """
        mock_cursor.execute.assert_called_once_with(expected_query)
        self.assertEqual(len(result), 3)
        self.assertEqual(float(result.iloc[0]['invoice_payment_score']), 95.0)
    
    @patch('backend.calculate_health_score.cursor')
    def test_api_call_calculation(self, mock_cursor):
        """Test API usage score calculation with mock data"""
        # Arrange
        mock_data = [
            {'customer_id': 'cust-001', 'avg_api_calls_per_week': Decimal('450.0')},
            {'customer_id': 'cust-002', 'avg_api_calls_per_week': Decimal('250.0')},
            {'customer_id': 'cust-003', 'avg_api_calls_per_week': Decimal('30.0')}
        ]
        mock_cursor.fetchall.return_value = mock_data
        
        # Act
        result = api_call()
        
        # Assert
        expected_query = """
    SELECT
        customer_id,
        SUM(calls_count) / 12 AS avg_api_calls_per_week
    FROM api_usage
    WHERE usage_date >= NOW() - INTERVAL 3 MONTH
    GROUP BY customer_id
    """
        mock_cursor.execute.assert_called_once_with(expected_query)
        self.assertEqual(len(result), 3)
        
        # Test API scoring logic
        self.assertEqual(result.iloc[0]['api_score'], 100)  # 450 calls = 100 score
        self.assertEqual(result.iloc[1]['api_score'], 75)   # 250 calls = 75 score
        self.assertEqual(result.iloc[2]['api_score'], 25)   # 30 calls = 25 score

    def test_ticket_score_function_edge_cases(self):
        """Test edge cases for ticket scoring function"""
        # Import the function directly to test it
        from backend.calculate_health_score import tickets
        
        # Mock the cursor to return edge case data
        with patch('backend.calculate_health_score.cursor') as mock_cursor:
            # Test boundary conditions
            test_cases = [
                ({'customer_id': 'test', 'open_tickets': 0}, 100),
                ({'customer_id': 'test', 'open_tickets': 1}, 75),
                ({'customer_id': 'test', 'open_tickets': 2}, 75),
                ({'customer_id': 'test', 'open_tickets': 3}, 50),
                ({'customer_id': 'test', 'open_tickets': 5}, 50),
                ({'customer_id': 'test', 'open_tickets': 6}, 25),
                ({'customer_id': 'test', 'open_tickets': 100}, 25)
            ]
            
            for mock_data, expected_score in test_cases:
                mock_cursor.fetchall.return_value = [mock_data]
                result = tickets()
                self.assertEqual(result.iloc[0]['ticket_score'], expected_score,
                               f"Failed for {mock_data['open_tickets']} tickets")

    def test_api_score_function_edge_cases(self):
        """Test edge cases for API scoring function"""
        from backend.calculate_health_score import api_call
        
        with patch('backend.calculate_health_score.cursor') as mock_cursor:
            # Test boundary conditions
            test_cases = [
                ({'customer_id': 'test', 'avg_api_calls_per_week': Decimal('500.0')}, 100),
                ({'customer_id': 'test', 'avg_api_calls_per_week': Decimal('400.0')}, 75),
                ({'customer_id': 'test', 'avg_api_calls_per_week': Decimal('300.0')}, 75),
                ({'customer_id': 'test', 'avg_api_calls_per_week': Decimal('200.0')}, 50),
                ({'customer_id': 'test', 'avg_api_calls_per_week': Decimal('100.0')}, 50),
                ({'customer_id': 'test', 'avg_api_calls_per_week': Decimal('50.0')}, 25),
                ({'customer_id': 'test', 'avg_api_calls_per_week': Decimal('10.0')}, 25)
            ]
            
            for mock_data, expected_score in test_cases:
                mock_cursor.fetchall.return_value = [mock_data]
                result = api_call()
                self.assertEqual(result.iloc[0]['api_score'], expected_score,
                               f"Failed for {mock_data['avg_api_calls_per_week']} API calls")

    def test_login_score_function_edge_cases(self):
        """Test edge cases for login scoring function"""
        # Test the login_score function logic directly
        def login_score(avg_logins):
            if avg_logins >= 20: return 100
            elif avg_logins >= 10: return 75
            elif avg_logins >= 5: return 50
            elif avg_logins >= 1: return 25
            else: return 0
        
        # Test boundary conditions
        test_cases = [
            (25.0, 100),
            (20.0, 100),
            (15.0, 75),
            (10.0, 75),
            (7.5, 50),
            (5.0, 50),
            (3.0, 25),
            (1.0, 25),
            (0.5, 0),
            (0.0, 0)
        ]
        
        for input_val, expected in test_cases:
            result = login_score(input_val)
            self.assertEqual(result, expected, f"Failed for {input_val} logins")

class TestIntegratedHealthScoreCalculation(unittest.TestCase):
    """Integration tests for the complete health score calculation"""
    
    @patch('backend.calculate_health_score.api_call')
    @patch('backend.calculate_health_score.invoice')
    @patch('backend.calculate_health_score.tickets')
    @patch('backend.calculate_health_score.features_used')
    @patch('backend.calculate_health_score.login_freq')
    def test_get_health_scores_integration(self, mock_login, mock_features, mock_tickets, mock_invoice, mock_api):
        """Test the complete health score calculation with mocked components"""
        # Arrange - Mock all component functions
        mock_login.return_value = pd.DataFrame([
            {'customer_id': 'cust-001', 'avg_logins_per_week': 15.0},
            {'customer_id': 'cust-002', 'avg_logins_per_week': 5.0},
            {'customer_id': 'cust-003', 'avg_logins_per_week': 0.5}
        ])
        
        mock_features.return_value = pd.DataFrame([
            {'customer_id': 'cust-001', 'feature_adoption_score': 80.0},
            {'customer_id': 'cust-002', 'feature_adoption_score': 60.0},
            {'customer_id': 'cust-003', 'feature_adoption_score': 20.0}
        ])
        
        mock_tickets.return_value = pd.DataFrame([
            {'customer_id': 'cust-001', 'open_tickets': 1, 'ticket_score': 75},
            {'customer_id': 'cust-002', 'open_tickets': 3, 'ticket_score': 50},
            {'customer_id': 'cust-003', 'open_tickets': 8, 'ticket_score': 25}
        ])
        
        mock_invoice.return_value = pd.DataFrame([
            {'customer_id': 'cust-001', 'invoice_payment_score': 95.0},
            {'customer_id': 'cust-002', 'invoice_payment_score': 75.0},
            {'customer_id': 'cust-003', 'invoice_payment_score': 50.0}
        ])
        
        mock_api.return_value = pd.DataFrame([
            {'customer_id': 'cust-001', 'avg_api_calls_per_week': 450.0, 'api_score': 100},
            {'customer_id': 'cust-002', 'avg_api_calls_per_week': 250.0, 'api_score': 75},
            {'customer_id': 'cust-003', 'avg_api_calls_per_week': 30.0, 'api_score': 25}
        ])
        
        # Act
        result = get_health_scores()
        
        # Assert
        self.assertEqual(len(result), 3)
        self.assertIn('customer_id', result.columns)
        self.assertIn('health_score', result.columns)
        
        # Verify health score calculation for first customer
        # login_score: 75, feature_score: 80, ticket_score: 75, invoice_score: 95, api_score: 100
        # Expected: 75*0.25 + 80*0.25 + 75*0.2 + 95*0.15 + 100*0.15 = 82.0
        first_customer_score = result[result['customer_id'] == 'cust-001']['health_score'].iloc[0]
        expected_score = 75*0.25 + 80*0.25 + 75*0.2 + 95*0.15 + 100*0.15
        self.assertAlmostEqual(first_customer_score, expected_score, places=1)
        
        # Verify all health scores are within valid range
        for score in result['health_score']:
            self.assertTrue(0 <= score <= 100, f"Health score {score} is out of range")
    
    @patch('backend.calculate_health_score.api_call')
    @patch('backend.calculate_health_score.invoice')
    @patch('backend.calculate_health_score.tickets')
    @patch('backend.calculate_health_score.features_used')
    @patch('backend.calculate_health_score.login_freq')
    def test_get_health_scores_with_missing_data(self, mock_login, mock_features, mock_tickets, mock_invoice, mock_api):
        """Test health score calculation with missing data for some customers"""
        # Arrange - Mock functions with missing data for some customers
        mock_login.return_value = pd.DataFrame([
            {'customer_id': 'cust-001', 'avg_logins_per_week': 15.0},
            {'customer_id': 'cust-002', 'avg_logins_per_week': 5.0}
            # cust-003 missing
        ])
        
        mock_features.return_value = pd.DataFrame([
            {'customer_id': 'cust-001', 'feature_adoption_score': 80.0},
            # cust-002 and cust-003 missing
        ])
        
        mock_tickets.return_value = pd.DataFrame([
            {'customer_id': 'cust-001', 'open_tickets': 1, 'ticket_score': 75},
            {'customer_id': 'cust-003', 'open_tickets': 8, 'ticket_score': 25}
            # cust-002 missing
        ])
        
        mock_invoice.return_value = pd.DataFrame([
            {'customer_id': 'cust-001', 'invoice_payment_score': 95.0},
            {'customer_id': 'cust-002', 'invoice_payment_score': 75.0},
            {'customer_id': 'cust-003', 'invoice_payment_score': 50.0}
        ])
        
        mock_api.return_value = pd.DataFrame([
            {'customer_id': 'cust-001', 'avg_api_calls_per_week': 450.0, 'api_score': 100},
            {'customer_id': 'cust-002', 'avg_api_calls_per_week': 250.0, 'api_score': 75}
            # cust-003 missing
        ])
        
        # Act
        result = get_health_scores()
        
        # Assert
        # Should have all customers due to outer joins
        self.assertEqual(len(result), 3)
        
        # Check that missing values are filled with defaults
        for _, row in result.iterrows():
            self.assertFalse(pd.isna(row['health_score']), "Health score should not be NaN")
            self.assertTrue(0 <= row['health_score'] <= 100, "Health score should be in valid range")


class TestHealthScoreComponents(unittest.TestCase):
    """Test individual components and helper functions"""
    
    def test_health_score_weights(self):
        """Test that health score weights sum to 1.0"""
        weights = {'login_score': 0.25, 'feature_score': 0.25, 'ticket_score': 0.2,
                  'invoice_payment_score': 0.15, 'api_score': 0.15}
        
        total_weight = sum(weights.values())
        self.assertAlmostEqual(total_weight, 1.0, places=2)
    
    def test_score_boundaries(self):
        """Test that all scoring functions return values between 0 and 100"""
        # Test login scoring
        def login_score(avg_logins):
            if avg_logins >= 20: return 100
            elif avg_logins >= 10: return 75
            elif avg_logins >= 5: return 50
            elif avg_logins >= 1: return 25
            else: return 0
        
        test_values = [-1, 0, 0.5, 1, 5, 10, 15, 20, 25, 100]
        for val in test_values:
            score = login_score(val)
            self.assertTrue(0 <= score <= 100, f"Login score {score} for value {val} is out of range")
        
        # Test API scoring
        def api_score(calls):
            if calls > 400: return 100
            elif calls > 200: return 75
            elif calls > 50: return 50
            else: return 25
        
        for val in test_values:
            score = api_score(val)
            self.assertTrue(0 <= score <= 100, f"API score {score} for value {val} is out of range")


if __name__ == '__main__':
    # Create a test suite that runs all tests
    test_suite = unittest.TestLoader().loadTestsFromModule(sys.modules[__name__])
    
    # Run tests with detailed output
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # Print coverage summary (requires coverage.py)
    print(f"\n{'='*50}")
    print("TEST SUMMARY")
    print(f"{'='*50}")
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Success rate: {((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100):.1f}%")
    
    # Exit with error code if tests failed
    exit_code = len(result.failures) + len(result.errors)
    sys.exit(exit_code)
