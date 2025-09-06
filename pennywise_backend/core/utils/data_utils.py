from decimal import Decimal
from datetime import datetime, date, timedelta
from django.db.models import Sum, Q, Count
from django.utils import timezone
from typing import Dict, List, Optional
import pandas as pd

from core.models import Transaction, Budget, User


def get_date_range(period: str, start_date: Optional[date] = None) -> tuple[date, date]:
    """
    Get date range based on period
    """
    now = timezone.now().date()
    
    if start_date:
        base_date = start_date
    else:
        base_date = now
    
    if period == 'daily':
        return base_date, base_date
    elif period == 'weekly':
        start = base_date - timedelta(days=base_date.weekday())
        end = start + timedelta(days=6)
        return start, end
    elif period == 'monthly':
        start = base_date.replace(day=1)
        if base_date.month == 12:
            end = base_date.replace(year=base_date.year + 1, month=1, day=1) - timedelta(days=1)
        else:
            end = base_date.replace(month=base_date.month + 1, day=1) - timedelta(days=1)
        return start, end
    elif period == 'yearly':
        start = base_date.replace(month=1, day=1)
        end = base_date.replace(month=12, day=31)
        return start, end
    else:
        # Default to monthly
        start = base_date.replace(day=1)
        if base_date.month == 12:
            end = base_date.replace(year=base_date.year + 1, month=1, day=1) - timedelta(days=1)
        else:
            end = base_date.replace(month=base_date.month + 1, day=1) - timedelta(days=1)
        return start, end


def calculate_category_spending(user: User, category: str, period: str = 'monthly', 
                               start_date: Optional[date] = None) -> Decimal:
    """
    Calculate total spending for a category in a given period
    """
    start, end = get_date_range(period, start_date)
    
    expenses = Transaction.objects.filter(
        user=user,
        category=category,
        is_income=False,
        date__gte=start,
        date__lte=end
    ).aggregate(total=Sum('amount'))
    
    return expenses['total'] or Decimal('0')


def calculate_total_income(user: User, period: str = 'monthly', 
                         start_date: Optional[date] = None) -> Decimal:
    """
    Calculate total income for a period
    """
    start, end = get_date_range(period, start_date)
    
    income = Transaction.objects.filter(
        user=user,
        is_income=True,
        date__gte=start,
        date__lte=end
    ).aggregate(total=Sum('amount'))
    
    return income['total'] or Decimal('0')


def calculate_total_expenses(user: User, period: str = 'monthly', 
                           start_date: Optional[date] = None) -> Decimal:
    """
    Calculate total expenses for a period
    """
    start, end = get_date_range(period, start_date)
    
    expenses = Transaction.objects.filter(
        user=user,
        is_income=False,
        date__gte=start,
        date__lte=end
    ).aggregate(total=Sum('amount'))
    
    return expenses['total'] or Decimal('0')


def get_category_breakdown(user: User, period: str = 'monthly', 
                          start_date: Optional[date] = None) -> List[Dict]:
    """
    Get spending breakdown by category
    """
    start, end = get_date_range(period, start_date)
    
    breakdown = Transaction.objects.filter(
        user=user,
        is_income=False,
        date__gte=start,
        date__lte=end
    ).values('category').annotate(
        total=Sum('amount'),
        count=Count('id')
    ).order_by('-total')
    
    return list(breakdown)


def get_monthly_trends(user: User, months: int = 12) -> List[Dict]:
    """
    Get monthly income/expense trends
    """
    trends = []
    now = timezone.now().date()
    
    for i in range(months):
        month_start = (now.replace(day=1) - timedelta(days=1)).replace(day=1)
        month_start = month_start - timedelta(days=30 * i)
        
        if month_start.month == 12:
            month_end = month_start.replace(year=month_start.year + 1, month=1, day=1) - timedelta(days=1)
        else:
            month_end = month_start.replace(month=month_start.month + 1, day=1) - timedelta(days=1)
        
        income = calculate_total_income(user, 'monthly', month_start)
        expenses = calculate_total_expenses(user, 'monthly', month_start)
        
        trends.append({
            'month': month_start.strftime('%Y-%m'),
            'month_name': month_start.strftime('%B %Y'),
            'income': income,
            'expenses': expenses,
            'net': income - expenses
        })
    
    return list(reversed(trends))


def get_top_categories(user: User, period: str = 'monthly', 
                      start_date: Optional[date] = None, limit: int = 10) -> List[Dict]:
    """
    Get top spending categories
    """
    breakdown = get_category_breakdown(user, period, start_date)
    return breakdown[:limit]


def calculate_budget_performance(user: User, period: str = 'monthly') -> List[Dict]:
    """
    Calculate budget performance for all categories
    """
    budgets = Budget.objects.filter(user=user, period=period)
    performance = []
    
    for budget in budgets:
        spent = calculate_category_spending(user, budget.category, period)
        remaining = budget.limit - spent
        percentage_used = (spent / budget.limit * 100) if budget.limit > 0 else 0
        
        status = 'good'
        if percentage_used > 100:
            status = 'over'
        elif percentage_used > 75:
            status = 'warning'
        
        performance.append({
            'budget_id': budget.id,
            'category': budget.category,
            'limit': budget.limit,
            'spent': spent,
            'remaining': remaining,
            'percentage_used': percentage_used,
            'status': status,
            'period': period
        })
    
    return performance


def get_financial_summary(user: User, period: str = 'monthly', 
                         start_date: Optional[date] = None) -> Dict:
    """
    Get comprehensive financial summary
    """
    start, end = get_date_range(period, start_date)
    
    # Basic calculations
    total_income = calculate_total_income(user, period, start_date)
    total_expenses = calculate_total_expenses(user, period, start_date)
    net_amount = total_income - total_expenses
    
    # Category breakdown
    category_breakdown = get_category_breakdown(user, period, start_date)
    
    # Transaction counts
    transaction_counts = Transaction.objects.filter(
        user=user,
        date__gte=start,
        date__lte=end
    ).aggregate(
        total_count=Count('id'),
        income_count=Count('id', filter=Q(is_income=True)),
        expense_count=Count('id', filter=Q(is_income=False))
    )
    
    # Budget performance
    budget_performance = calculate_budget_performance(user, period)
    
    return {
        'period': period,
        'date_range': {
            'start': start,
            'end': end
        },
        'totals': {
            'income': total_income,
            'expenses': total_expenses,
            'net': net_amount
        },
        'transaction_counts': transaction_counts,
        'category_breakdown': category_breakdown,
        'budget_performance': budget_performance,
        'top_categories': get_top_categories(user, period, start_date, 5)
    }


def clean_transaction_data(transaction_data: Dict) -> Dict:
    """
    Clean and normalize transaction data
    """
    cleaned = transaction_data.copy()
    
    # Clean description
    if 'description' in cleaned:
        cleaned['description'] = str(cleaned['description']).strip()
    
    # Clean category
    if 'category' in cleaned:
        cleaned['category'] = str(cleaned['category']).strip().title()
    
    # Ensure amount is positive
    if 'amount' in cleaned and cleaned['amount'] < 0:
        cleaned['amount'] = abs(cleaned['amount'])
    
    return cleaned


def detect_duplicate_transactions(user: User, transaction_data: Dict, 
                                 tolerance_days: int = 1) -> List[Transaction]:
    """
    Detect potential duplicate transactions
    """
    amount = transaction_data['amount']
    description = transaction_data['description']
    transaction_date = transaction_data['date']
    
    # Look for transactions with similar amount and description within tolerance
    start_date = transaction_date - timedelta(days=tolerance_days)
    end_date = transaction_date + timedelta(days=tolerance_days)
    
    # Allow for small amount differences (e.g., rounding)
    amount_tolerance = amount * Decimal('0.01')  # 1% tolerance
    
    potential_duplicates = Transaction.objects.filter(
        user=user,
        amount__gte=amount - amount_tolerance,
        amount__lte=amount + amount_tolerance,
        description__icontains=description[:20],  # First 20 chars
        date__gte=start_date,
        date__lte=end_date
    )
    
    return list(potential_duplicates)