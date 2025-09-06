from decimal import Decimal
from datetime import datetime, date, timedelta
from django.db.models import Sum, Q
from django.utils import timezone
from typing import Dict, List, Optional, Tuple
import pandas as pd

from core.models import Transaction, Budget, User
from core.utils.data_utils import get_date_range, calculate_category_spending


def calculate_budget_spending(budget: Budget, start_date: Optional[date] = None) -> Decimal:
    """
    Calculate current spending for a budget category
    """
    return calculate_category_spending(
        budget.user, 
        budget.category, 
        budget.period, 
        start_date
    )


def get_budget_status(budget: Budget) -> Dict:
    """
    Get comprehensive budget status
    """
    spent = calculate_budget_spending(budget)
    remaining = budget.limit - spent
    percentage_used = (spent / budget.limit * 100) if budget.limit > 0 else 0
    
    # Determine status
    if percentage_used > 100:
        status = 'over'
        status_message = 'Over budget'
    elif percentage_used > 90:
        status = 'critical'
        status_message = 'Critical - 90%+ used'
    elif percentage_used > 75:
        status = 'warning'
        status_message = 'Warning - 75%+ used'
    else:
        status = 'good'
        status_message = 'On track'
    
    return {
        'budget_id': budget.id,
        'category': budget.category,
        'period': budget.period,
        'limit': budget.limit,
        'spent': spent,
        'remaining': remaining,
        'percentage_used': percentage_used,
        'status': status,
        'status_message': status_message,
        'days_remaining': get_days_remaining_in_period(budget.period),
        'daily_budget': get_daily_budget_allowance(budget),
        'projected_spending': get_projected_spending(budget)
    }


def get_days_remaining_in_period(period: str) -> int:
    """
    Get days remaining in current period
    """
    now = timezone.now().date()
    
    if period == 'daily':
        return 0
    elif period == 'weekly':
        days_until_sunday = (6 - now.weekday()) % 7
        return days_until_sunday
    elif period == 'monthly':
        if now.month == 12:
            next_month = now.replace(year=now.year + 1, month=1, day=1)
        else:
            next_month = now.replace(month=now.month + 1, day=1)
        return (next_month - now).days
    elif period == 'yearly':
        next_year = now.replace(year=now.year + 1, month=1, day=1)
        return (next_year - now).days
    else:
        return 0


def get_daily_budget_allowance(budget: Budget) -> Decimal:
    """
    Calculate daily budget allowance
    """
    days_remaining = get_days_remaining_in_period(budget.period)
    if days_remaining <= 0:
        return Decimal('0')
    
    spent = calculate_budget_spending(budget)
    remaining_budget = budget.limit - spent
    
    if remaining_budget <= 0:
        return Decimal('0')
    
    return remaining_budget / days_remaining


def get_projected_spending(budget: Budget) -> Decimal:
    """
    Project spending for the entire period based on current rate
    """
    start, end = get_date_range(budget.period)
    now = timezone.now().date()
    
    # Calculate days elapsed
    days_elapsed = (now - start).days + 1
    total_days = (end - start).days + 1
    
    if days_elapsed <= 0:
        return Decimal('0')
    
    spent = calculate_budget_spending(budget)
    daily_rate = spent / days_elapsed
    
    return daily_rate * total_days


def get_budget_alerts(user: User, threshold_percentages: List[float] = [75, 90, 100]) -> List[Dict]:
    """
    Get budget alerts for user
    """
    budgets = Budget.objects.filter(user=user)
    alerts = []
    
    for budget in budgets:
        status = get_budget_status(budget)
        
        for threshold in threshold_percentages:
            if status['percentage_used'] >= threshold:
                alert_type = 'critical' if threshold >= 100 else 'warning'
                
                alerts.append({
                    'budget_id': budget.id,
                    'category': budget.category,
                    'alert_type': alert_type,
                    'threshold': threshold,
                    'percentage_used': status['percentage_used'],
                    'spent': status['spent'],
                    'limit': status['limit'],
                    'remaining': status['remaining'],
                    'message': f"{budget.category} budget is {status['percentage_used']:.1f}% used ({threshold}% threshold)"
                })
                break  # Only show the highest threshold reached
    
    return alerts


def create_budget_recommendations(user: User, period: str = 'monthly') -> List[Dict]:
    """
    Create budget recommendations based on spending patterns
    """
    # Get spending patterns for the last 3 months
    now = timezone.now().date()
    recommendations = []
    
    # Calculate average spending by category
    category_spending = {}
    for i in range(3):  # Last 3 months
        month_start = (now.replace(day=1) - timedelta(days=30 * i)).replace(day=1)
        start, end = get_date_range('monthly', month_start)
        
        breakdown = Transaction.objects.filter(
            user=user,
            is_income=False,
            date__gte=start,
            date__lte=end
        ).values('category').annotate(total=Sum('amount'))
        
        for item in breakdown:
            category = item['category']
            if category not in category_spending:
                category_spending[category] = []
            category_spending[category].append(item['total'])
    
    # Calculate averages and create recommendations
    for category, amounts in category_spending.items():
        if len(amounts) >= 2:  # Need at least 2 months of data
            avg_spending = sum(amounts) / len(amounts)
            
            # Check if user has a budget for this category
            existing_budget = Budget.objects.filter(
                user=user,
                category=category,
                period=period
            ).first()
            
            if existing_budget:
                # Compare with existing budget
                if avg_spending > existing_budget.limit * Decimal('1.1'):  # 10% over
                    recommendations.append({
                        'category': category,
                        'type': 'increase',
                        'current_limit': existing_budget.limit,
                        'recommended_limit': avg_spending * Decimal('1.2'),  # 20% buffer
                        'reason': f'Average spending (${avg_spending:.2f}) exceeds current budget'
                    })
                elif avg_spending < existing_budget.limit * Decimal('0.8'):  # 20% under
                    recommendations.append({
                        'category': category,
                        'type': 'decrease',
                        'current_limit': existing_budget.limit,
                        'recommended_limit': avg_spending * Decimal('1.1'),  # 10% buffer
                        'reason': f'Average spending (${avg_spending:.2f}) is well below current budget'
                    })
            else:
                # Suggest new budget
                if avg_spending > Decimal('50'):  # Only suggest for significant spending
                    recommendations.append({
                        'category': category,
                        'type': 'create',
                        'recommended_limit': avg_spending * Decimal('1.2'),  # 20% buffer
                        'reason': f'Regular spending of ${avg_spending:.2f} per month detected'
                    })
    
    return recommendations


def get_budget_performance_history(user: User, category: str, months: int = 6) -> List[Dict]:
    """
    Get budget performance history for a category
    """
    history = []
    now = timezone.now().date()
    
    for i in range(months):
        month_start = (now.replace(day=1) - timedelta(days=30 * i)).replace(day=1)
        
        # Get budget for this month
        budget = Budget.objects.filter(
            user=user,
            category=category,
            period='monthly'
        ).first()
        
        if budget:
            start, end = get_date_range('monthly', month_start)
            spent = calculate_category_spending(user, category, 'monthly', month_start)
            
            history.append({
                'month': month_start.strftime('%Y-%m'),
                'month_name': month_start.strftime('%B %Y'),
                'limit': budget.limit,
                'spent': spent,
                'remaining': budget.limit - spent,
                'percentage_used': (spent / budget.limit * 100) if budget.limit > 0 else 0
            })
    
    return list(reversed(history))


def optimize_budget_allocation(user: User, total_budget: Decimal, 
                              period: str = 'monthly') -> List[Dict]:
    """
    Suggest optimal budget allocation based on spending patterns
    """
    # Get spending patterns
    category_spending = {}
    now = timezone.now().date()
    
    for i in range(3):  # Last 3 months
        month_start = (now.replace(day=1) - timedelta(days=30 * i)).replace(day=1)
        start, end = get_date_range('monthly', month_start)
        
        breakdown = Transaction.objects.filter(
            user=user,
            is_income=False,
            date__gte=start,
            date__lte=end
        ).values('category').annotate(total=Sum('amount'))
        
        for item in breakdown:
            category = item['category']
            if category not in category_spending:
                category_spending[category] = []
            category_spending[category].append(item['total'])
    
    # Calculate average spending percentages
    total_spending = sum(sum(amounts) / len(amounts) for amounts in category_spending.values())
    allocations = []
    
    for category, amounts in category_spending.items():
        if len(amounts) >= 2:
            avg_spending = sum(amounts) / len(amounts)
            percentage = (avg_spending / total_spending * 100) if total_spending > 0 else 0
            
            allocations.append({
                'category': category,
                'current_avg': avg_spending,
                'percentage': percentage,
                'suggested_allocation': total_budget * Decimal(str(percentage / 100)),
                'priority': 'high' if percentage > 20 else 'medium' if percentage > 10 else 'low'
            })
    
    # Sort by percentage
    allocations.sort(key=lambda x: x['percentage'], reverse=True)
    
    return allocations