from django.contrib import admin
from .models import User, Transaction, Budget, AlertConfig


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ['username', 'email', 'telegram_chat_id', 'created_at']
    list_filter = ['created_at', 'is_active']
    search_fields = ['username', 'email']


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ['user', 'date', 'amount', 'category', 'is_income', 'created_at']
    list_filter = ['is_income', 'category', 'date', 'created_at']
    search_fields = ['description', 'category']
    date_hierarchy = 'date'


@admin.register(Budget)
class BudgetAdmin(admin.ModelAdmin):
    list_display = ['user', 'category', 'limit', 'period', 'current_spending', 'remaining_budget']
    list_filter = ['period', 'category']
    search_fields = ['category']


@admin.register(AlertConfig)
class AlertConfigAdmin(admin.ModelAdmin):
    list_display = ['user', 'alert_type', 'threshold', 'enabled', 'telegram_enabled']
    list_filter = ['alert_type', 'enabled', 'telegram_enabled']