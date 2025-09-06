from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    UserViewSet, TransactionViewSet, BudgetViewSet, AlertConfigViewSet,
    CustomAuthToken, ReportViewSet, ChartViewSet
)

router = DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'transactions', TransactionViewSet)
router.register(r'budgets', BudgetViewSet)
router.register(r'alert-configs', AlertConfigViewSet)
router.register(r'reports', ReportViewSet, basename='reports')
router.register(r'charts', ChartViewSet, basename='charts')

urlpatterns = [
    path('auth/login/', CustomAuthToken.as_view(), name='api_token_auth'),
    path('', include(router.urls)),
]