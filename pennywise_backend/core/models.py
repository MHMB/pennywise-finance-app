from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator
from decimal import Decimal


class User(AbstractUser):
    """Custom user model extending Django's AbstractUser"""
    email = models.EmailField(unique=True)
    telegram_chat_id = models.CharField(max_length=50, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.username


class Transaction(models.Model):
    """Model for storing financial transactions"""
    TRANSACTION_TYPES = [
        ('income', 'Income'),
        ('expense', 'Expense'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='transactions')
    date = models.DateField()
    amount = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))]
    )
    category = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    is_income = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-date', '-created_at']
        indexes = [
            models.Index(fields=['date']),
            models.Index(fields=['category']),
            models.Index(fields=['user', 'date']),
        ]

    def __str__(self):
        transaction_type = "Income" if self.is_income else "Expense"
        return f"{transaction_type}: {self.amount} - {self.category} ({self.date})"


class Budget(models.Model):
    """Model for storing budget limits by category"""
    PERIOD_CHOICES = [
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
        ('yearly', 'Yearly'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='budgets')
    category = models.CharField(max_length=100)
    limit = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))]
    )
    period = models.CharField(max_length=10, choices=PERIOD_CHOICES, default='monthly')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['user', 'category', 'period']
        indexes = [
            models.Index(fields=['user', 'category']),
        ]

    def __str__(self):
        return f"{self.category}: {self.limit} ({self.period})"

    @property
    def current_spending(self):
        """Calculate current spending for this budget category"""
        from django.utils import timezone
        from datetime import datetime, timedelta
        
        now = timezone.now().date()
        
        if self.period == 'weekly':
            start_date = now - timedelta(days=now.weekday())
        elif self.period == 'monthly':
            start_date = now.replace(day=1)
        elif self.period == 'yearly':
            start_date = now.replace(month=1, day=1)
        else:
            start_date = now.replace(day=1)  # Default to monthly
        
        expenses = Transaction.objects.filter(
            user=self.user,
            category=self.category,
            is_income=False,
            date__gte=start_date,
            date__lte=now
        )
        
        return sum(expense.amount for expense in expenses)

    @property
    def remaining_budget(self):
        """Calculate remaining budget"""
        return self.limit - self.current_spending

    @property
    def percentage_used(self):
        """Calculate percentage of budget used"""
        if self.limit == 0:
            return 0
        return (self.current_spending / self.limit) * 100


class AlertConfig(models.Model):
    """Model for storing alert configurations"""
    ALERT_TYPES = [
        ('threshold', 'Threshold Alert'),
        ('daily', 'Daily Summary'),
        ('weekly', 'Weekly Summary'),
        ('overspend', 'Overspend Alert'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='alert_configs')
    alert_type = models.CharField(max_length=20, choices=ALERT_TYPES)
    threshold = models.FloatField(default=75.0)  # Percentage threshold
    enabled = models.BooleanField(default=True)
    telegram_enabled = models.BooleanField(default=True)
    email_enabled = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['user', 'alert_type']
        indexes = [
            models.Index(fields=['user', 'alert_type']),
        ]

    def __str__(self):
        return f"{self.user.username} - {self.alert_type} ({self.threshold}%)"