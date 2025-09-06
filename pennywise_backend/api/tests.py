from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from rest_framework.authtoken.models import Token
from decimal import Decimal
from datetime import date
from core.models import Transaction, Budget, AlertConfig

User = get_user_model()


class UserRegistrationAPITest(APITestCase):
    def test_user_registration(self):
        url = reverse('user-register')
        data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'testpass123',
            'password_confirm': 'testpass123'
        }
        
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('token', response.data)
        self.assertIn('user', response.data)

    def test_user_registration_password_mismatch(self):
        url = reverse('user-register')
        data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'testpass123',
            'password_confirm': 'differentpass'
        }
        
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class AuthenticationAPITest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )

    def test_login(self):
        url = reverse('api_token_auth')
        data = {
            'username': 'testuser',
            'password': 'testpass123'
        }
        
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('token', response.data)

    def test_login_invalid_credentials(self):
        url = reverse('api_token_auth')
        data = {
            'username': 'testuser',
            'password': 'wrongpassword'
        }
        
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class TransactionAPITest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.token = Token.objects.create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)

    def test_create_transaction(self):
        url = reverse('transaction-list')
        data = {
            'date': date.today(),
            'amount': '100.50',
            'category': 'Food',
            'description': 'Grocery shopping',
            'is_income': False
        }
        
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Transaction.objects.count(), 1)

    def test_get_transactions(self):
        Transaction.objects.create(
            user=self.user,
            date=date.today(),
            amount=Decimal('100.00'),
            category='Food',
            is_income=False
        )
        
        url = reverse('transaction-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)

    def test_transaction_summary(self):
        Transaction.objects.create(
            user=self.user,
            date=date.today(),
            amount=Decimal('100.00'),
            category='Food',
            is_income=False
        )
        Transaction.objects.create(
            user=self.user,
            date=date.today(),
            amount=Decimal('2000.00'),
            category='Salary',
            is_income=True
        )
        
        url = reverse('transaction-summary')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['total_income'], '2000.00')
        self.assertEqual(response.data['total_expenses'], '100.00')
        self.assertEqual(response.data['net_amount'], '1900.00')


class BudgetAPITest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.token = Token.objects.create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)

    def test_create_budget(self):
        url = reverse('budget-list')
        data = {
            'category': 'Food',
            'limit': '500.00',
            'period': 'monthly'
        }
        
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Budget.objects.count(), 1)

    def test_budget_status(self):
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
            is_income=False
        )
        
        url = reverse('budget-status')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['current_spending'], '100.00')