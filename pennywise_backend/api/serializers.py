from rest_framework import serializers
from core.models import User, Transaction, Budget, AlertConfig


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'telegram_chat_id', 'created_at']
        read_only_fields = ['id', 'created_at']


class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'password_confirm', 'telegram_chat_id']

    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError("Passwords don't match")
        return attrs

    def create(self, validated_data):
        validated_data.pop('password_confirm')
        user = User.objects.create_user(**validated_data)
        return user


class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = ['id', 'date', 'amount', 'category', 'description', 'is_income', 'created_at']
        read_only_fields = ['id', 'created_at']

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


class TransactionImportSerializer(serializers.Serializer):
    file = serializers.FileField()
    
    def validate_file(self, value):
        if not value.name.endswith('.csv'):
            raise serializers.ValidationError("File must be a CSV file")
        return value


class TransactionBulkCreateSerializer(serializers.Serializer):
    transactions = TransactionSerializer(many=True)
    
    def create(self, validated_data):
        transactions_data = validated_data['transactions']
        user = self.context['request'].user
        created_transactions = []
        
        for transaction_data in transactions_data:
            transaction_data['user'] = user
            transaction = Transaction.objects.create(**transaction_data)
            created_transactions.append(transaction)
        
        return {'transactions': created_transactions}


class BudgetSerializer(serializers.ModelSerializer):
    current_spending = serializers.ReadOnlyField()
    remaining_budget = serializers.ReadOnlyField()
    percentage_used = serializers.ReadOnlyField()

    class Meta:
        model = Budget
        fields = ['id', 'category', 'limit', 'period', 'current_spending', 
                 'remaining_budget', 'percentage_used', 'created_at']
        read_only_fields = ['id', 'created_at']

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


class BudgetStatusSerializer(serializers.Serializer):
    budget_id = serializers.IntegerField()
    category = serializers.CharField()
    limit = serializers.DecimalField(max_digits=10, decimal_places=2)
    current_spending = serializers.DecimalField(max_digits=10, decimal_places=2)
    remaining_budget = serializers.DecimalField(max_digits=10, decimal_places=2)
    percentage_used = serializers.FloatField()
    status = serializers.CharField()


class AlertConfigSerializer(serializers.ModelSerializer):
    class Meta:
        model = AlertConfig
        fields = ['id', 'alert_type', 'threshold', 'enabled', 'telegram_enabled', 
                 'email_enabled', 'created_at']
        read_only_fields = ['id', 'created_at']

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


class FinancialSummarySerializer(serializers.Serializer):
    period = serializers.CharField()
    date_range = serializers.DictField()
    totals = serializers.DictField()
    transaction_counts = serializers.DictField()
    category_breakdown = serializers.ListField()
    budget_performance = serializers.ListField()
    top_categories = serializers.ListField()


class CategoryBreakdownSerializer(serializers.Serializer):
    category = serializers.CharField()
    total = serializers.DecimalField(max_digits=10, decimal_places=2)
    count = serializers.IntegerField()


class MonthlyTrendSerializer(serializers.Serializer):
    month = serializers.CharField()
    month_name = serializers.CharField()
    income = serializers.DecimalField(max_digits=10, decimal_places=2)
    expenses = serializers.DecimalField(max_digits=10, decimal_places=2)
    net = serializers.DecimalField(max_digits=10, decimal_places=2)


class ReportSerializer(serializers.Serializer):
    report_type = serializers.ChoiceField(choices=['summary', 'category', 'time', 'budget'])
    period = serializers.ChoiceField(choices=['daily', 'weekly', 'monthly', 'yearly'], default='monthly')
    start_date = serializers.DateField(required=False)
    end_date = serializers.DateField(required=False)
    category = serializers.CharField(required=False)


class ChartSerializer(serializers.Serializer):
    chart_type = serializers.ChoiceField(choices=['pie', 'bar', 'line', 'dashboard', 'budget'])
    period = serializers.ChoiceField(choices=['daily', 'weekly', 'monthly', 'yearly'], default='monthly')
    start_date = serializers.DateField(required=False)
    category = serializers.CharField(required=False)
    months = serializers.IntegerField(min_value=1, max_value=24, default=12)