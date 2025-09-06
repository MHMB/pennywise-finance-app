from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser
from django.contrib.auth import authenticate
from django.db.models import Sum, Q
from django.http import HttpResponse, FileResponse
from datetime import datetime, timedelta, date
from decimal import Decimal
import tempfile
import os

from core.models import User, Transaction, Budget, AlertConfig
from core.utils.csv_processor import process_csv_file
from core.utils.data_utils import (
    get_financial_summary, get_category_breakdown, get_monthly_trends,
    get_top_categories, clean_transaction_data, detect_duplicate_transactions
)
from core.utils.budget_utils import (
    get_budget_status, get_budget_alerts, create_budget_recommendations,
    get_budget_performance_history, optimize_budget_allocation
)
from core.visuals.charts import (
    create_pie_chart, create_bar_chart, create_line_chart,
    create_budget_status_chart, create_dashboard_chart, save_chart_to_file
)
from .serializers import (
    UserSerializer, UserRegistrationSerializer, TransactionSerializer,
    TransactionImportSerializer, TransactionBulkCreateSerializer,
    BudgetSerializer, BudgetStatusSerializer, AlertConfigSerializer,
    FinancialSummarySerializer, CategoryBreakdownSerializer,
    MonthlyTrendSerializer, ReportSerializer, ChartSerializer
)


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=['get'])
    def me(self, request):
        """Get current user profile"""
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)

    @action(detail=False, methods=['post'], permission_classes=[AllowAny])
    def register(self, request):
        """Register a new user"""
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            token, created = Token.objects.get_or_create(user=user)
            return Response({
                'token': token.key,
                'user': UserSerializer(user).data
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CustomAuthToken(ObtainAuthToken):
    """Custom token authentication view"""
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data,
                                         context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        return Response({
            'token': token.key,
            'user': UserSerializer(user).data
        })


class TransactionViewSet(viewsets.ModelViewSet):
    queryset = Transaction.objects.all()
    serializer_class = TransactionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = Transaction.objects.filter(user=self.request.user)
        
        # Filter by date range
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')
        
        if start_date:
            queryset = queryset.filter(date__gte=start_date)
        if end_date:
            queryset = queryset.filter(date__lte=end_date)
        
        # Filter by category
        category = self.request.query_params.get('category')
        if category:
            queryset = queryset.filter(category__icontains=category)
        
        # Filter by transaction type
        is_income = self.request.query_params.get('is_income')
        if is_income is not None:
            queryset = queryset.filter(is_income=is_income.lower() == 'true')
        
        return queryset.order_by('-date', '-created_at')

    @action(detail=False, methods=['get'])
    def summary(self, request):
        """Get transaction summary for current user"""
        period = request.query_params.get('period', 'monthly')
        start_date = request.query_params.get('start_date')
        
        if start_date:
            start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
        
        summary = get_financial_summary(request.user, period, start_date)
        serializer = FinancialSummarySerializer(summary)
        return Response(serializer.data)

    @action(detail=False, methods=['post'])
    def bulk_create(self, request):
        """Create multiple transactions from CSV data"""
        serializer = TransactionBulkCreateSerializer(data=request.data)
        if serializer.is_valid():
            result = serializer.save()
            return Response({
                'message': f'Successfully created {len(result["transactions"])} transactions',
                'transactions': TransactionSerializer(result['transactions'], many=True).data
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'], parser_classes=[MultiPartParser, FormParser])
    def import_csv(self, request):
        """Import transactions from CSV file"""
        serializer = TransactionImportSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        csv_file = serializer.validated_data['file']
        
        try:
            # Read CSV content
            csv_content = csv_file.read().decode('utf-8')
            
            # Process CSV
            result = process_csv_file(csv_content, request.user.id)
            
            if not result['success']:
                return Response({
                    'success': False,
                    'error': result['error']
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Create transactions
            created_transactions = []
            errors = []
            
            for transaction_data in result['transactions']:
                try:
                    # Check for duplicates
                    duplicates = detect_duplicate_transactions(request.user, transaction_data)
                    if duplicates:
                        errors.append(f"Duplicate transaction detected: {transaction_data['description']}")
                        continue
                    
                    # Clean and create transaction
                    cleaned_data = clean_transaction_data(transaction_data)
                    transaction = Transaction.objects.create(**cleaned_data)
                    created_transactions.append(transaction)
                    
                except Exception as e:
                    errors.append(f"Error creating transaction: {str(e)}")
                    continue
            
            return Response({
                'success': True,
                'message': f'Successfully imported {len(created_transactions)} transactions',
                'total_rows': result['total_rows'],
                'processed_rows': len(created_transactions),
                'errors': errors,
                'transactions': TransactionSerializer(created_transactions, many=True).data
            }, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            return Response({
                'success': False,
                'error': f'Error processing CSV file: {str(e)}'
            }, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get'])
    def categories(self, request):
        """Get all unique categories for the user"""
        categories = Transaction.objects.filter(user=request.user).values_list('category', flat=True).distinct()
        return Response({'categories': list(categories)})

    @action(detail=False, methods=['get'])
    def duplicates(self, request):
        """Detect potential duplicate transactions"""
        transactions = Transaction.objects.filter(user=request.user).order_by('-date')
        duplicates = []
        
        for transaction in transactions:
            potential_duplicates = detect_duplicate_transactions(
                request.user, 
                {
                    'amount': transaction.amount,
                    'description': transaction.description,
                    'date': transaction.date
                }
            )
            
            if potential_duplicates:
                duplicates.append({
                    'transaction': TransactionSerializer(transaction).data,
                    'duplicates': TransactionSerializer(potential_duplicates, many=True).data
                })
        
        return Response({'duplicates': duplicates})


class BudgetViewSet(viewsets.ModelViewSet):
    queryset = Budget.objects.all()
    serializer_class = BudgetSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Budget.objects.filter(user=self.request.user)

    @action(detail=False, methods=['get'])
    def status(self, request):
        """Get budget status for all categories"""
        period = request.query_params.get('period', 'monthly')
        budgets = self.get_queryset().filter(period=period)
        
        budget_status = []
        for budget in budgets:
            status = get_budget_status(budget)
            budget_status.append(status)
        
        serializer = BudgetStatusSerializer(budget_status, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def alerts(self, request):
        """Get budget alerts"""
        alerts = get_budget_alerts(request.user)
        return Response({'alerts': alerts})

    @action(detail=False, methods=['get'])
    def recommendations(self, request):
        """Get budget recommendations"""
        period = request.query_params.get('period', 'monthly')
        recommendations = create_budget_recommendations(request.user, period)
        return Response({'recommendations': recommendations})

    @action(detail=True, methods=['get'])
    def history(self, request, pk=None):
        """Get budget performance history"""
        budget = self.get_object()
        months = int(request.query_params.get('months', 6))
        history = get_budget_performance_history(request.user, budget.category, months)
        return Response({'history': history})

    @action(detail=False, methods=['post'])
    def optimize(self, request):
        """Get optimized budget allocation"""
        total_budget = Decimal(request.data.get('total_budget', 0))
        period = request.data.get('period', 'monthly')
        
        if total_budget <= 0:
            return Response({'error': 'Total budget must be greater than 0'}, 
                           status=status.HTTP_400_BAD_REQUEST)
        
        allocations = optimize_budget_allocation(request.user, total_budget, period)
        return Response({'allocations': allocations})


class AlertConfigViewSet(viewsets.ModelViewSet):
    queryset = AlertConfig.objects.all()
    serializer_class = AlertConfigSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return AlertConfig.objects.filter(user=self.request.user)


class ReportViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=['get'])
    def summary(self, request):
        """Get financial summary report"""
        serializer = ReportSerializer(data=request.query_params)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        data = serializer.validated_data
        summary = get_financial_summary(
            request.user, 
            data['period'], 
            data.get('start_date')
        )
        
        response_serializer = FinancialSummarySerializer(summary)
        return Response(response_serializer.data)

    @action(detail=False, methods=['get'])
    def category(self, request):
        """Get category breakdown report"""
        serializer = ReportSerializer(data=request.query_params)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        data = serializer.validated_data
        breakdown = get_category_breakdown(
            request.user, 
            data['period'], 
            data.get('start_date')
        )
        
        serializer = CategoryBreakdownSerializer(breakdown, many=True)
        return Response({'breakdown': serializer.data})

    @action(detail=False, methods=['get'])
    def trends(self, request):
        """Get monthly trends report"""
        months = int(request.query_params.get('months', 12))
        trends = get_monthly_trends(request.user, months)
        
        serializer = MonthlyTrendSerializer(trends, many=True)
        return Response({'trends': serializer.data})

    @action(detail=False, methods=['get'])
    def budget(self, request):
        """Get budget performance report"""
        period = request.query_params.get('period', 'monthly')
        budgets = Budget.objects.filter(user=request.user, period=period)
        
        performance = []
        for budget in budgets:
            status = get_budget_status(budget)
            performance.append(status)
        
        return Response({'performance': performance})


class ChartViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=['get'])
    def pie(self, request):
        """Generate pie chart"""
        serializer = ChartSerializer(data=request.query_params)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        data = serializer.validated_data
        chart_base64 = create_pie_chart(
            request.user, 
            data['period'], 
            data.get('start_date')
        )
        
        if not chart_base64:
            return Response({'error': 'No data available for chart'}, 
                           status=status.HTTP_400_BAD_REQUEST)
        
        return Response({'chart': chart_base64, 'data_url': f"data:image/png;base64,{chart_base64}"})

    @action(detail=False, methods=['get'])
    def bar(self, request):
        """Generate bar chart"""
        serializer = ChartSerializer(data=request.query_params)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        data = serializer.validated_data
        chart_type = request.query_params.get('chart_type', 'category')
        
        chart_base64 = create_bar_chart(
            request.user, 
            data['period'], 
            data.get('start_date'),
            chart_type
        )
        
        if not chart_base64:
            return Response({'error': 'No data available for chart'}, 
                           status=status.HTTP_400_BAD_REQUEST)
        
        return Response({'chart': chart_base64, 'data_url': f"data:image/png;base64,{chart_base64}"})

    @action(detail=False, methods=['get'])
    def line(self, request):
        """Generate line chart"""
        months = int(request.query_params.get('months', 12))
        chart_base64 = create_line_chart(request.user, months)
        
        if not chart_base64:
            return Response({'error': 'No data available for chart'}, 
                           status=status.HTTP_400_BAD_REQUEST)
        
        return Response({'chart': chart_base64, 'data_url': f"data:image/png;base64,{chart_base64}"})

    @action(detail=False, methods=['get'])
    def dashboard(self, request):
        """Generate dashboard chart"""
        chart_base64 = create_dashboard_chart(request.user)
        
        if not chart_base64:
            return Response({'error': 'No data available for chart'}, 
                           status=status.HTTP_400_BAD_REQUEST)
        
        return Response({'chart': chart_base64, 'data_url': f"data:image/png;base64,{chart_base64}"})

    @action(detail=False, methods=['get'])
    def budget(self, request):
        """Generate budget status chart"""
        period = request.query_params.get('period', 'monthly')
        chart_base64 = create_budget_status_chart(request.user, period)
        
        if not chart_base64:
            return Response({'error': 'No data available for chart'}, 
                           status=status.HTTP_400_BAD_REQUEST)
        
        return Response({'chart': chart_base64, 'data_url': f"data:image/png;base64,{chart_base64}"})

    @action(detail=False, methods=['get'])
    def download(self, request):
        """Download chart as PNG file"""
        chart_type = request.query_params.get('type', 'pie')
        period = request.query_params.get('period', 'monthly')
        
        chart_base64 = None
        filename = f"{chart_type}_chart_{period}.png"
        
        if chart_type == 'pie':
            chart_base64 = create_pie_chart(request.user, period)
        elif chart_type == 'bar':
            chart_base64 = create_bar_chart(request.user, period)
        elif chart_type == 'line':
            months = int(request.query_params.get('months', 12))
            chart_base64 = create_line_chart(request.user, months)
        elif chart_type == 'dashboard':
            chart_base64 = create_dashboard_chart(request.user)
        elif chart_type == 'budget':
            chart_base64 = create_budget_status_chart(request.user, period)
        
        if not chart_base64:
            return Response({'error': 'No data available for chart'}, 
                           status=status.HTTP_400_BAD_REQUEST)
        
        # Save to temporary file
        temp_file_path = save_chart_to_file(chart_base64, filename)
        
        # Return file response
        response = FileResponse(
            open(temp_file_path, 'rb'),
            content_type='image/png',
            filename=filename
        )
        
        # Clean up temporary file after response
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        
        return response