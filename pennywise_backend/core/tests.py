from django.test import TestCase
from django.contrib.auth import get_user_model
from decimal import Decimal
from datetime import date, timedelta
from core.models import Transaction, Budget, AlertConfig

User = get_user_model()


class UserModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )

    def test_user_creation(self):
        self.assertEqual(self.user.username, 'testuser')
        self.assertEqual(self.user.email, 'test@example.com')
        self.assertTrue(self.user.check_password('testpass123'))

    def test_user_str(self):
        self.assertEqual(str(self.user), 'testuser')


class TransactionModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )

    def test_transaction_creation(self):
        transaction = Transaction.objects.create(
            user=self.user,
            date=date.today(),
            amount=Decimal('100.50'),
            category='Food',
            description='Grocery shopping',
            is_income=False
        )
        
        self.assertEqual(transaction.user, self.user)
        self.assertEqual(transaction.amount, Decimal('100.50'))
        self.assertEqual(transaction.category, 'Food')
        self.assertFalse(transaction.is_income)

    def test_transaction_str(self):
        transaction = Transaction.objects.create(
            user=self.user,
            date=date.today(),
            amount=Decimal('50.00'),
            category='Salary',
            is_income=True
        )
        
        expected_str = f"Income: 50.00 - Salary ({date.today()})"
        self.assertEqual(str(transaction), expected_str)


class BudgetModelTest(TestCase):
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

    def test_budget_creation(self):
        self.assertEqual(self.budget.user, self.user)
        self.assertEqual(self.budget.category, 'Food')
        self.assertEqual(self.budget.limit, Decimal('500.00'))
        self.assertEqual(self.budget.period, 'monthly')

    def test_budget_str(self):
        expected_str = "Food: 500.00 (monthly)"
        self.assertEqual(str(self.budget), expected_str)

    def test_current_spending_calculation(self):
        # Create some transactions
        Transaction.objects.create(
            user=self.user,
            date=date.today(),
            amount=Decimal('100.00'),
            category='Food',
            is_income=False
        )
        Transaction.objects.create(
            user=self.user,
            date=date.today() - timedelta(days=1),
            amount=Decimal('50.00'),
            category='Food',
            is_income=False
        )
        
        self.assertEqual(self.budget.current_spending, Decimal('150.00'))
        self.assertEqual(self.budget.remaining_budget, Decimal('350.00'))
        self.assertEqual(self.budget.percentage_used, 30.0)


class AlertConfigModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )

    def test_alert_config_creation(self):
        alert_config = AlertConfig.objects.create(
            user=self.user,
            alert_type='threshold',
            threshold=75.0,
            enabled=True
        )
        
        self.assertEqual(alert_config.user, self.user)
        self.assertEqual(alert_config.alert_type, 'threshold')
        self.assertEqual(alert_config.threshold, 75.0)
        self.assertTrue(alert_config.enabled)

    def test_alert_config_str(self):
        alert_config = AlertConfig.objects.create(
            user=self.user,
            alert_type='daily',
            threshold=90.0
        )
        
        expected_str = "testuser - daily (90.0%)"
        self.assertEqual(str(alert_config), expected_str)