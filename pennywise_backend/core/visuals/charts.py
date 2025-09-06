import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
from datetime import datetime, date, timedelta
from decimal import Decimal
from typing import List, Dict, Optional
import io
import base64
import tempfile
import os

from core.models import Transaction, Budget, User
from core.utils.data_utils import get_category_breakdown, get_monthly_trends, get_financial_summary


def create_pie_chart(user: User, period: str = 'monthly', 
                    start_date: Optional[date] = None, 
                    chart_type: str = 'expenses') -> str:
    """
    Create pie chart for category breakdown
    """
    if chart_type == 'expenses':
        breakdown = get_category_breakdown(user, period, start_date)
        title = f'Expense Categories - {period.title()}'
    else:
        # For income categories
        breakdown = Transaction.objects.filter(
            user=user,
            is_income=True,
            date__gte=start_date or date.today().replace(day=1)
        ).values('category').annotate(total=Sum('amount')).order_by('-total')
        title = f'Income Categories - {period.title()}'
    
    if not breakdown:
        return None
    
    # Prepare data
    categories = [item['category'] for item in breakdown]
    amounts = [float(item['total']) for item in breakdown]
    
    # Create plotly pie chart
    fig = go.Figure(data=[go.Pie(
        labels=categories,
        values=amounts,
        hole=0.3,
        textinfo='label+percent',
        textposition='outside'
    )])
    
    fig.update_layout(
        title=title,
        font_size=12,
        showlegend=True,
        height=500,
        width=600
    )
    
    # Convert to base64 string
    img_bytes = fig.to_image(format="png", width=600, height=500)
    img_base64 = base64.b64encode(img_bytes).decode()
    
    return img_base64


def create_bar_chart(user: User, period: str = 'monthly', 
                    start_date: Optional[date] = None,
                    chart_type: str = 'category') -> str:
    """
    Create bar chart for spending analysis
    """
    if chart_type == 'category':
        breakdown = get_category_breakdown(user, period, start_date)
        title = f'Spending by Category - {period.title()}'
        x_data = [item['category'] for item in breakdown]
        y_data = [float(item['total']) for item in breakdown]
    else:
        # Monthly trends
        trends = get_monthly_trends(user, 6)
        title = 'Monthly Income vs Expenses'
        x_data = [item['month_name'] for item in trends]
        y_data_income = [float(item['income']) for item in trends]
        y_data_expenses = [float(item['expenses']) for item in trends]
    
    if chart_type == 'category':
        fig = go.Figure(data=[
            go.Bar(
                x=x_data,
                y=y_data,
                marker_color='lightblue',
                text=[f'${amount:.2f}' for amount in y_data],
                textposition='auto'
            )
        ])
    else:
        fig = go.Figure()
        fig.add_trace(go.Bar(
            name='Income',
            x=x_data,
            y=y_data_income,
            marker_color='green',
            text=[f'${amount:.2f}' for amount in y_data_income],
            textposition='auto'
        ))
        fig.add_trace(go.Bar(
            name='Expenses',
            x=x_data,
            y=y_data_expenses,
            marker_color='red',
            text=[f'${amount:.2f}' for amount in y_data_expenses],
            textposition='auto'
        ))
    
    fig.update_layout(
        title=title,
        xaxis_title='Category' if chart_type == 'category' else 'Month',
        yaxis_title='Amount ($)',
        font_size=12,
        height=500,
        width=800,
        barmode='group' if chart_type != 'category' else 'group'
    )
    
    # Convert to base64 string
    img_bytes = fig.to_image(format="png", width=800, height=500)
    img_base64 = base64.b64encode(img_bytes).decode()
    
    return img_base64


def create_line_chart(user: User, months: int = 12) -> str:
    """
    Create line chart for spending trends
    """
    trends = get_monthly_trends(user, months)
    
    if not trends:
        return None
    
    months_data = [item['month_name'] for item in trends]
    income_data = [float(item['income']) for item in trends]
    expense_data = [float(item['expenses']) for item in trends]
    net_data = [float(item['net']) for item in trends]
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=months_data,
        y=income_data,
        mode='lines+markers',
        name='Income',
        line=dict(color='green', width=3),
        marker=dict(size=8)
    ))
    
    fig.add_trace(go.Scatter(
        x=months_data,
        y=expense_data,
        mode='lines+markers',
        name='Expenses',
        line=dict(color='red', width=3),
        marker=dict(size=8)
    ))
    
    fig.add_trace(go.Scatter(
        x=months_data,
        y=net_data,
        mode='lines+markers',
        name='Net Amount',
        line=dict(color='blue', width=3),
        marker=dict(size=8)
    ))
    
    fig.update_layout(
        title='Monthly Financial Trends',
        xaxis_title='Month',
        yaxis_title='Amount ($)',
        font_size=12,
        height=500,
        width=800,
        hovermode='x unified'
    )
    
    # Convert to base64 string
    img_bytes = fig.to_image(format="png", width=800, height=500)
    img_base64 = base64.b64encode(img_bytes).decode()
    
    return img_base64


def create_budget_status_chart(user: User, period: str = 'monthly') -> str:
    """
    Create chart showing budget status
    """
    from core.utils.budget_utils import get_budget_status
    
    budgets = Budget.objects.filter(user=user, period=period)
    
    if not budgets:
        return None
    
    categories = []
    limits = []
    spent = []
    percentages = []
    
    for budget in budgets:
        status = get_budget_status(budget)
        categories.append(budget.category)
        limits.append(float(budget.limit))
        spent.append(float(status['spent']))
        percentages.append(status['percentage_used'])
    
    # Create subplot with two y-axes
    fig = make_subplots(
        rows=1, cols=1,
        specs=[[{"secondary_y": True}]]
    )
    
    # Add bars for budget limits and spent amounts
    fig.add_trace(
        go.Bar(
            name='Budget Limit',
            x=categories,
            y=limits,
            marker_color='lightblue',
            opacity=0.7
        ),
        secondary_y=False
    )
    
    fig.add_trace(
        go.Bar(
            name='Amount Spent',
            x=categories,
            y=spent,
            marker_color='red',
            opacity=0.8
        ),
        secondary_y=False
    )
    
    # Add line for percentage
    fig.add_trace(
        go.Scatter(
            name='Percentage Used',
            x=categories,
            y=percentages,
            mode='lines+markers',
            line=dict(color='orange', width=3),
            marker=dict(size=8)
        ),
        secondary_y=True
    )
    
    fig.update_xaxes(title_text="Category")
    fig.update_yaxes(title_text="Amount ($)", secondary_y=False)
    fig.update_yaxes(title_text="Percentage (%)", secondary_y=True)
    
    fig.update_layout(
        title=f'Budget Status - {period.title()}',
        font_size=12,
        height=500,
        width=800,
        barmode='group'
    )
    
    # Convert to base64 string
    img_bytes = fig.to_image(format="png", width=800, height=500)
    img_base64 = base64.b64encode(img_bytes).decode()
    
    return img_base64


def create_dashboard_chart(user: User) -> str:
    """
    Create comprehensive dashboard chart
    """
    summary = get_financial_summary(user)
    
    # Create subplots
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=('Monthly Income vs Expenses', 'Category Breakdown', 
                       'Budget Performance', 'Net Amount Trend'),
        specs=[[{"type": "bar"}, {"type": "pie"}],
               [{"type": "bar"}, {"type": "scatter"}]]
    )
    
    # 1. Monthly trends (top left)
    trends = get_monthly_trends(user, 6)
    if trends:
        months = [item['month_name'] for item in trends]
        income = [float(item['income']) for item in trends]
        expenses = [float(item['expenses']) for item in trends]
        
        fig.add_trace(
            go.Bar(name='Income', x=months, y=income, marker_color='green'),
            row=1, col=1
        )
        fig.add_trace(
            go.Bar(name='Expenses', x=months, y=expenses, marker_color='red'),
            row=1, col=1
        )
    
    # 2. Category breakdown (top right)
    breakdown = summary['category_breakdown'][:5]  # Top 5 categories
    if breakdown:
        categories = [item['category'] for item in breakdown]
        amounts = [float(item['total']) for item in breakdown]
        
        fig.add_trace(
            go.Pie(labels=categories, values=amounts, hole=0.3),
            row=1, col=2
        )
    
    # 3. Budget performance (bottom left)
    budget_perf = summary['budget_performance']
    if budget_perf:
        budget_categories = [item['category'] for item in budget_perf]
        budget_percentages = [item['percentage_used'] for item in budget_perf]
        
        fig.add_trace(
            go.Bar(x=budget_categories, y=budget_percentages, 
                  marker_color='orange'),
            row=2, col=1
        )
    
    # 4. Net amount trend (bottom right)
    if trends:
        net_amounts = [float(item['net']) for item in trends]
        fig.add_trace(
            go.Scatter(x=months, y=net_amounts, mode='lines+markers',
                      line=dict(color='blue', width=3)),
            row=2, col=2
        )
    
    fig.update_layout(
        title='Financial Dashboard',
        font_size=10,
        height=800,
        width=1000,
        showlegend=True
    )
    
    # Convert to base64 string
    img_bytes = fig.to_image(format="png", width=1000, height=800)
    img_base64 = base64.b64encode(img_bytes).decode()
    
    return img_base64


def save_chart_to_file(chart_base64: str, filename: str) -> str:
    """
    Save chart to temporary file and return file path
    """
    if not chart_base64:
        return None
    
    # Decode base64 image
    img_data = base64.b64decode(chart_base64)
    
    # Create temporary file
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.png')
    temp_file.write(img_data)
    temp_file.close()
    
    return temp_file.name


def get_chart_data_url(chart_base64: str) -> str:
    """
    Get data URL for embedding chart in HTML
    """
    if not chart_base64:
        return None
    
    return f"data:image/png;base64,{chart_base64}"