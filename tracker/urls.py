from django.urls import path, include
from . import views
from django.contrib.auth import views as auth_views
from django.contrib.auth.views import LogoutView
from .views import (
    signup, login_view, home, add_income, add_expense, 
    transaction_list, DashboardView, TransactionsViewSet, transactions_view
)
from rest_framework.routers import DefaultRouter
from .views import TransactionsListAPIView

router = DefaultRouter()
router.register(r'transactions', TransactionsViewSet, basename='transactions')
# router.register(r'admin/transactions', views.AdminTransactionsViewSet, basename='admin-transactions') # Add this line

from rest_framework_simplejwt import views as jwt_views



urlpatterns = [
    path('', DashboardView.as_view(), name='home'),  # Home page
    path('signup/', views.signup, name='signup'),  # Signup page
    path('login/', auth_views.LoginView.as_view(), name='login'),  # Login page
    path('logout/', LogoutView.as_view(next_page='/'), name='logout'),
    path('add_income/', views.add_income, name='add_income'),  # Add Income page
    path('add_expense/', views.add_expense, name='add_expense'),  # Add Expense page
    path('transactions/', views.transaction_list, name='transaction_list'),  # Transactions page
    path('logout/', LogoutView.as_view(), name='logout'),  # Add logout URL
    # path('charts/', views.generate_chart, name='generate_charts'),
    path('api/', include(router.urls)),
    path('api/token/', jwt_views.TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', jwt_views.TokenRefreshView.as_view(), name='token_refresh'),
    path('transactions/filter/', views.transactions_view, name='transactions_view'),  # Transactions filtering view
    path('api/transactions/', TransactionsListAPIView.as_view(), name='api_transactions_list'),

]
