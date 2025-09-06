from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from rest_framework.authtoken.models import Token
from decimal import Decimal
from datetime import date, timedelta
import json
import tempfile
import os

from core.models import Transaction, Budget, AlertConfig
from core.utils.csv_processor import process_csv_file, detect_csv_format, parse_amount, parse_date, categorize_transaction
from core.utils.data_utils import (
    get_financial_summary, get_category_breakdown, get_monthly_trends,
    calculate_total_income, calculate_total_expenses, get_date_range
)
from core.utils.budget_utils import (
    get_budget_status, get_budget_alerts, create_budget_recommendations,
    calculate_budget_spending, get_daily_budget_allowance
)
from core.visuals.charts import create_pie_chart, create_bar_chart, create_line_chart

User = get_user_model()


class CSVProcessorTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )

    def test_detect_csv_format(self):
        """Test CSV format detection"""
        csv_content = "date,amount,description\n2023-01-01,100.50,Grocery shopping"
        format_info = detect_csv_format(csv_content)
        
        self.assertIn('delimiter', format_info)
        self.assertIn('columns', format_info)
        self.assertEqual(format_info['delimiter'], ',')
        self.assertIn('date', format_info['columns'])
        self.assertIn('amount', format_info['columns'])
        self.assertIn('description', format_info['columns'])

    def test_parse_amount(self):
        """Test amount parsing"""
        self.assertEqual(parse_amount('100.50'), Decimal('100.50'))
        self.assertEqual(parse_amount('$100.50'), Decimal('100.50'))
        self.assertEqual(parse_amount('1,234.56'), Decimal('1234.56'))
        self.assertEqual(parse_amount('1.234,56'), Decimal('1234.56'))
        self.assertIsNone(parse_amount('invalid'))
        self.assertIsNone(parse_amount(''))

    def test_parse_date(self):
        """Test date parsing"""
        self.assertEqual(parse_date('2023-01-01').date(), date(2023, 1, 1))
        self.assertEqual(parse_date('01/01/2023').date(), date(2023, 1, 1))
        self.assertEqual(parse_date('01-01-2023').date(), date(2023, 1, 1))
        self.assertIsNone(parse_date('invalid'))
        self.assertIsNone(parse_date(''))

    def test_categorize_transaction(self):
        """Test transaction categorization"""
        self.assertEqual(categorize_transaction('Grocery shopping', Decimal('50')), 'Food')
        self.assertEqual(categorize_transaction('Gas station', Decimal('30')), 'Transportation')
        self.assertEqual(categorize_transaction('Salary deposit', Decimal('2000')), 'Income')
        self.assertEqual(categorize_transaction('Unknown expense', Decimal('25')), 'Uncategorized')

    def test_process_csv_file(self):
        """Test CSV file processing"""
        csv_content = """date,amount,description
2023-01-01,100.50,Grocery shopping
2023-01-02,-50.00,Gas station
2023-01-03,2000.00,Salary deposit"""
        
        result = process_csv_file(csv_content, self.user.id)
        
        self.assertTrue(result['success'])
        self.assertEqual(len(result['transactions']), 3)
        self.assertEqual(result['total_rows'], 3)
        self.assertEqual(result['processed_rows'], 3)
        
        # Check first transaction
        transaction = result['transactions'][0]
        self.assertEqual(transaction['user_id'], self.user.id)
        self.assertEqual(transaction['date'], date(2023, 1, 1))
        self.assertEqual(transaction['amount'], Decimal('100.50'))
        self.assertEqual(transaction['description'], 'Grocery shopping')
        self.assertFalse(transaction['is_income'])


class DataUtilsTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )

    def test_get_date_range(self):
        """Test date range calculation"""
        start, end = get_date_range('monthly')
        self.assertIsInstance(start, date)
        self.assertIsInstance(end, date)
        self.assertLessEqual(start, end)

    def test_calculate_total_income(self):
        """Test income calculation"""
        Transaction.objects.create(
            user=self.user,
            date=date.today(),
            amount=Decimal('2000.00'),
            category='Salary',
            description='Monthly salary',
            is_income=True
        )
        
        income = calculate_total_income(self.user, 'monthly')
        self.assertEqual(income, Decimal('2000.00'))

    def test_calculate_total_expenses(self):
        """Test expense calculation"""
        Transaction.objects.create(
            user=self.user,
            date=date.today(),
            amount=Decimal('100.00'),
            category='Food',
            description='Grocery shopping',
            is_income=False
        )
        
        expenses = calculate_total_expenses(self.user, 'monthly')
        self.assertEqual(expenses, Decimal('100.00'))

    def test_get_category_breakdown(self):
        """Test category breakdown"""
        Transaction.objects.create(
            user=self.user,
            date=date.today(),
            amount=Decimal('100.00'),
            category='Food',
            description='Grocery shopping',
            is_income=False
        )
        Transaction.objects.create(
            user=self.user,
            date=date.today(),
            amount=Decimal('50.00'),
            category='Transportation',
            description='Gas',
            is_income=False
        )
        
        breakdown = get_category_breakdown(self.user, 'monthly')
        self.assertEqual(len(breakdown), 2)
        
        food_total = next(item['total'] for item in breakdown if item['category'] == 'Food')
        self.assertEqual(food_total, Decimal('100.00'))

    def test_get_financial_summary(self):
        """Test financial summary"""
        Transaction.objects.create(
            user=self.user,
            date=date.today(),
            amount=Decimal('2000.00'),
            category='Salary',
            description='Monthly salary',
            is_income=True
        )
        Transaction.objects.create(
            user=self.user,
            date=date.today(),
            amount=Decimal('100.00'),
            category='Food',
            description='Grocery shopping',
            is_income=False
        )
        
        summary = get_financial_summary(self.user, 'monthly')
        
        self.assertEqual(summary['totals']['income'], Decimal('2000.00'))
        self.assertEqual(summary['totals']['expenses'], Decimal('100.00'))
        self.assertEqual(summary['totals']['net'], Decimal('1900.00'))
        self.assertIn('category_breakdown', summary)
        self.assertIn('budget_performance', summary)


class BudgetUtilsTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.budget = Budget.objects.create(
            user=self.user,
            category='Food',
            limit=Decimal('500.00'),
            period='monthly'
        )

    def test_calculate_budget_spending(self):
        """Test budget spending calculation"""
        Transaction.objects.create(
            user=self.user,
            date=date.today(),
            amount=Decimal('100.00'),
            category='Food',
            description='Grocery shopping',
            is_income=False
        )
        
        spending = calculate_budget_spending(self.budget)
        self.assertEqual(spending, Decimal('100.00'))

    def test_get_budget_status(self):
        """Test budget status calculation"""
        Transaction.objects.create(
            user=self.user,
            date=date.today(),
            amount=Decimal('100.00'),
            category='Food',
            description='Grocery shopping',
            is_income=False
        )
        
        status = get_budget_status(self.budget)
        
        self.assertEqual(status['category'], 'Food')
        self.assertEqual(status['limit'], Decimal('500.00'))
        self.assertEqual(status['spent'], Decimal('100.00'))
        self.assertEqual(status['remaining'], Decimal('400.00'))
        self.assertEqual(status['percentage_used'], 20.0)
        self.assertEqual(status['status'], 'good')

    def test_get_budget_alerts(self):
        """Test budget alerts"""
        # Create a budget that's over limit
        over_budget = Budget.objects.create(
            user=self.user,
            category='Entertainment',
            limit=Decimal('100.00'),
            period='monthly'
        )
        
        Transaction.objects.create(
            user=self.user,
            date=date.today(),
            amount=Decimal('150.00'),
            category='Entertainment',
            description='Movie tickets',
            is_income=False
        )
        
        alerts = get_budget_alerts(self.user)
        self.assertGreater(len(alerts), 0)
        
        entertainment_alert = next((alert for alert in alerts if alert['category'] == 'Entertainment'), None)
        self.assertIsNotNone(entertainment_alert)
        self.assertEqual(entertainment_alert['alert_type'], 'critical')

    def test_get_daily_budget_allowance(self):
        """Test daily budget allowance calculation"""
        allowance = get_daily_budget_allowance(self.budget)
        self.assertGreaterEqual(allowance, Decimal('0'))


class ChartTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        # Create some test data
        Transaction.objects.create(
            user=self.user,
            date=date.today(),
            amount=Decimal('100.00'),
            category='Food',
            description='Grocery shopping',
            is_income=False
        )
        Transaction.objects.create(
            user=self.user,
            date=date.today(),
            amount=Decimal('50.00'),
            category='Transportation',
            description='Gas',
            is_income=False
        )

    def test_create_pie_chart(self):
        """Test pie chart creation"""
        chart_base64 = create_pie_chart(self.user, 'monthly')
        self.assertIsNotNone(chart_base64)
        self.assertIsInstance(chart_base64, str)

    def test_create_bar_chart(self):
        """Test bar chart creation"""
        chart_base64 = create_bar_chart(self.user, 'monthly')
        self.assertIsNotNone(chart_base64)
        self.assertIsInstance(chart_base64, str)

    def test_create_line_chart(self):
        """Test line chart creation"""
        chart_base64 = create_line_chart(self.user, 6)
        self.assertIsNotNone(chart_base64)
        self.assertIsInstance(chart_base64, str)


class TransactionAPITest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.token = Token.objects.create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)

    def test_transaction_filtering(self):
        """Test transaction filtering by date and category"""
        Transaction.objects.create(
            user=self.user,
            date=date.today(),
            amount=Decimal('100.00'),
            category='Food',
            description='Grocery shopping',
            is_income=False
        )
        Transaction.objects.create(
            user=self.user,
            date=date.today() - timedelta(days=1),
            amount=Decimal('50.00'),
            category='Transportation',
            description='Gas',
            is_income=False
        )
        
        # Test category filter
        response = self.client.get('/api/transactions/?category=Food')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        
        # Test date filter
        start_date = (date.today() - timedelta(days=1)).strftime('%Y-%m-%d')
        response = self.client.get(f'/api/transactions/?start_date={start_date}')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2)

    def test_transaction_summary(self):
        """Test transaction summary endpoint"""
        Transaction.objects.create(
            user=self.user,
            date=date.today(),
            amount=Decimal('2000.00'),
            category='Salary',
            description='Monthly salary',
            is_income=True
        )
        Transaction.objects.create(
            user=self.user,
            date=date.today(),
            amount=Decimal('100.00'),
            category='Food',
            description='Grocery shopping',
            is_income=False
        )
        
        response = self.client.get('/api/transactions/summary/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['totals']['income'], '2000.00')
        self.assertEqual(response.data['totals']['expenses'], '100.00')
        self.assertEqual(response.data['totals']['net'], '1900.00')

    def test_csv_import(self):
        """Test CSV import functionality"""
        csv_content = """date,amount,description
2023-01-01,100.50,Grocery shopping
2023-01-02,-50.00,Gas station"""
        
        # Create temporary CSV file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write(csv_content)
            temp_file_path = f.name
        
        try:
            with open(temp_file_path, 'rb') as f:
                response = self.client.post('/api/transactions/import_csv/', {
                    'file': f
                }, format='multipart')
            
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)
            self.assertTrue(response.data['success'])
            self.assertEqual(response.data['processed_rows'], 2)
            
        finally:
            os.unlink(temp_file_path)

    def test_categories_endpoint(self):
        """Test categories endpoint"""
        Transaction.objects.create(
            user=self.user,
            date=date.today(),
            amount=Decimal('100.00'),
            category='Food',
            description='Grocery shopping',
            is_income=False
        )
        
        response = self.client.get('/api/transactions/categories/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('Food', response.data['categories'])


class BudgetAPITest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.token = Token.objects.create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)

    def test_budget_status(self):
        """Test budget status endpoint"""
        budget = Budget.objects.create(
            user=self.user,
            category='Food',
            limit=Decimal('500.00'),
            period='monthly'
        )
        
        Transaction.objects.create(
            user=self.user,
            date=date.today(),
            amount=Decimal('100.00'),
            category='Food',
            description='Grocery shopping',
            is_income=False
        )
        
        response = self.client.get('/api/budgets/status/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        
        budget_status = response.data[0]
        self.assertEqual(budget_status['category'], 'Food')
        self.assertEqual(budget_status['limit'], '500.00')
        self.assertEqual(budget_status['current_spending'], '100.00')

    def test_budget_alerts(self):
        """Test budget alerts endpoint"""
        budget = Budget.objects.create(
            user=self.user,
            category='Entertainment',
            limit=Decimal('100.00'),
            period='monthly'
        )
        
        Transaction.objects.create(
            user=self.user,
            date=date.today(),
            amount=Decimal('150.00'),
            category='Entertainment',
            description='Movie tickets',
            is_income=False
        )
        
        response = self.client.get('/api/budgets/alerts/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreater(len(response.data['alerts']), 0)

    def test_budget_recommendations(self):
        """Test budget recommendations endpoint"""
        # Create some spending history
        for i in range(3):
            Transaction.objects.create(
                user=self.user,
                date=date.today() - timedelta(days=30 * i),
                amount=Decimal('200.00'),
                category='Food',
                description='Grocery shopping',
                is_income=False
            )
        
        response = self.client.get('/api/budgets/recommendations/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('recommendations', response.data)


class ReportAPITest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.token = Token.objects.create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)

    def test_summary_report(self):
        """Test summary report endpoint"""
        Transaction.objects.create(
            user=self.user,
            date=date.today(),
            amount=Decimal('2000.00'),
            category='Salary',
            description='Monthly salary',
            is_income=True
        )
        Transaction.objects.create(
            user=self.user,
            date=date.today(),
            amount=Decimal('100.00'),
            category='Food',
            description='Grocery shopping',
            is_income=False
        )
        
        response = self.client.get('/api/reports/summary/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('totals', response.data)
        self.assertIn('category_breakdown', response.data)

    def test_category_report(self):
        """Test category report endpoint"""
        Transaction.objects.create(
            user=self.user,
            date=date.today(),
            amount=Decimal('100.00'),
            category='Food',
            description='Grocery shopping',
            is_income=False
        )
        
        response = self.client.get('/api/reports/category/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('breakdown', response.data)

    def test_trends_report(self):
        """Test trends report endpoint"""
        response = self.client.get('/api/reports/trends/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('trends', response.data)


class ChartAPITest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.token = Token.objects.create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
        
        # Create some test data
        Transaction.objects.create(
            user=self.user,
            date=date.today(),
            amount=Decimal('100.00'),
            category='Food',
            description='Grocery shopping',
            is_income=False
        )

    def test_pie_chart(self):
        """Test pie chart endpoint"""
        response = self.client.get('/api/charts/pie/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('chart', response.data)
        self.assertIn('data_url', response.data)

    def test_bar_chart(self):
        """Test bar chart endpoint"""
        response = self.client.get('/api/charts/bar/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('chart', response.data)
        self.assertIn('data_url', response.data)

    def test_line_chart(self):
        """Test line chart endpoint"""
        response = self.client.get('/api/charts/line/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('chart', response.data)
        self.assertIn('data_url', response.data)

    def test_dashboard_chart(self):
        """Test dashboard chart endpoint"""
        response = self.client.get('/api/charts/dashboard/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('chart', response.data)
        self.assertIn('data_url', response.data)