from django.shortcuts import render, redirect
import matplotlib.pyplot as plt
import io
import base64
from django.views.generic import TemplateView
from rest_framework import viewsets
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from .models import Transaction, Category
from .forms import TransactionForm
from django.contrib.auth.forms import AuthenticationForm
from .serializers import TransactionSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework import serializers
from django.contrib.auth.models import User

from django.core.exceptions import ObjectDoesNotExist

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter, SearchFilter
import json
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.db.models import Q



# Signup view to create a new user
def signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)  # Automatically log the user in after registration
            return redirect('home')  # Redirect to the home page after login
    else:
        form = UserCreationForm()

    return render(request, 'signup.html', {'form': form})

# Home page view with login required
@login_required
def home(request):
    # Fetch transactions for the logged-in user only
    transactions = Transaction.objects.filter(user=request.user)

    # Calculate total income and total expenses for the user
    total_income = transactions.filter(type='Income').aggregate(total_income=Sum('amount'))['total_income'] or 0
    total_expense = transactions.filter(type='Expense').aggregate(total_expense=Sum('amount'))['total_expense'] or 0
    balance = total_income - total_expense

    context = {
        'balance': balance,
        'total_income': total_income,
        'total_expense': total_expense,
        'transactions': transactions
    }

    return render(request, 'index.html', context)

# Add income view with login required
@login_required
def add_income(request):
    if request.method == 'POST':
        amount = request.POST.get('amount')
        date = request.POST.get('date')
        description = request.POST.get('description')
        category = request.POST.get('category')

        # Automatically associate the logged-in user
        income = Transaction(
            user=request.user,
            type='Income',
            amount=amount,
            date=date,
            description=description,
            category=category,
        )
        income.save()

        return redirect('home')  # Redirect to the homepage after saving
    return render(request, 'add_income.html')  # Render the add income form


@login_required
def add_expense(request):
    if request.method == 'POST':
        amount = request.POST.get('amount')
        date = request.POST.get('date')
        description = request.POST.get('description')
        category = request.POST.get('category')

        # Automatically associate the logged-in user
        expense = Transaction(
            user=request.user,
            type='Expense',
            amount=amount,
            date=date,
            description=description,
            category=category,
        )
        expense.save()

        return redirect('home')  # Redirect to the homepage after saving
    return render(request, 'add_expense.html')  # Render the add expense form



# Transactions_list view with login required
@login_required
def transaction_list(request):
    # Fetch transactions for the logged-in user only
    transactions = Transaction.objects.filter(user=request.user)

    total_income = transactions.filter(type='Income').aggregate(total_income=Sum('amount'))['total_income'] or 0
    total_expense = transactions.filter(type='Expense').aggregate(total_expense=Sum('amount'))['total_expense'] or 0
    balance = total_income - total_expense

    context = {
        'transactions': transactions,
        'balance': balance
    }

    return render(request, 'transactions.html', context)




# Login view
def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('home')  # Redirect to home after login
    else:
        form = AuthenticationForm()

    return render(request, 'login.html', {'form': form})

class DashboardView(TemplateView):
    template_name = 'index.html'  # Your template file

    def get_context_data(self, **kwargs):

        context = super().get_context_data(**kwargs)

        # Filter transactions for the logged-in user
        transactions = Transaction.objects.filter(user=self.request.user)

        total_income = sum(t.amount for t in transactions if t.type == "Income")
        total_expense = sum(t.amount for t in transactions if t.type == "Expense")
        balance = total_income - total_expense

        # Initialize data containers for category and date-wise sums
        category_data = {}
        income_data = {}
        expense_data = {}

        for transaction in transactions:
            # Process by category
            category = transaction.category
            category_data[category] = category_data.get(category, 0) + transaction.amount

            # Process by date (for income/expense)
            date = transaction.date.strftime('%Y-%m-%d')
            if transaction.type == "Income":
                income_data[date] = income_data.get(date, 0) + transaction.amount
            elif transaction.type == "Expense":
                expense_data[date] = expense_data.get(date, 0) + transaction.amount

        # Prepare Bar Chart Data
        categories = list(category_data.keys())
        category_amounts = list(category_data.values())

        # Prepare Line Chart Data
        dates = sorted(set(income_data.keys()).union(expense_data.keys()))
        income_amounts = [income_data.get(date, 0) for date in dates]
        expense_amounts = [expense_data.get(date, 0) for date in dates]

        # Generate Charts and Convert to Base64
        category_chart = self.generate_category_chart(categories, category_amounts)
        line_chart = self.generate_line_chart(dates, income_amounts, expense_amounts)

        context.update({
            'category_chart': category_chart,
            'line_chart': line_chart,
            'total_income': total_income,
            'total_expense': total_expense,
            'balance': balance,
            'transactions': transactions,
        })

        return context

    def generate_category_chart(self, categories, category_amounts):
        # Create a BytesIO buffer to save the chart image
        buffer = io.BytesIO()

        # Create the Bar Chart
        plt.figure(figsize=(10, 6))
        plt.bar(categories, category_amounts, color='skyblue')
        plt.xlabel('Category')
        plt.ylabel('Amount')
        plt.title('Transactions by Category')
        plt.xticks(rotation=45)
        plt.tight_layout()

        # Save to buffer
        plt.savefig(buffer, format='png')
        buffer.seek(0)

        # Convert to base64 string for embedding in the HTML
        return base64.b64encode(buffer.getvalue()).decode('utf-8')

    def generate_line_chart(self, dates, income_amounts, expense_amounts):
        # Create the Line Chart
        buffer = io.BytesIO()
        plt.figure(figsize=(10, 6))
        plt.plot(dates, income_amounts, label='Income', color='green', marker='o')
        plt.plot(dates, expense_amounts, label='Expense', color='red', marker='o')
        plt.xlabel('Date')
        plt.ylabel('Amount')
        plt.title('Income and Expense Over Time')
        plt.legend()
        plt.xticks(rotation=45)
        plt.tight_layout()

        # Save to buffer
        plt.savefig(buffer, format='png')
        buffer.seek(0)

        # Convert to base64 string for embedding in the HTML
        return base64.b64encode(buffer.getvalue()).decode('utf-8')


class TransactionsListAPIView(generics.ListAPIView):
    queryset = Transaction.objects.all()
    serializer_class = TransactionSerializer
    filter_backends = [DjangoFilterBackend, OrderingFilter, SearchFilter]
    filterset_fields = ['type', 'category']
    ordering_fields = ['amount', 'date']
    ordering = ['date']
    search_fields = ['description']

    # def get_queryset(self):
    #     transactions = Transaction.objects.all()
    #     filters = self.request.query_params

    #     # Apply filters using the same logic from the previous function
    #     transactions = TransactionsViewSet.apply_filters(transactions, filters)

    #     return transactions

    def get_queryset(self):
        # Filter transactions for the logged-in user
        return Transaction.objects.filter(user=self.request.user)

    def list(self, request, *args, **kwargs):
        transactions = self.get_queryset()
        serializer = self.get_serializer(transactions, many=True)
        return Response(serializer.data)



class TransactionSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)  # Make sure to include the username field

    class Meta:
        model = Transaction
        fields = ['id', 'type', 'amount', 'date', 'description', 'category', 'username', 'user']  # Include 'user' here

    def validate(self, data):
        """
        This will ensure that all required fields are validated properly.
        """
        if not data.get('type'):
            raise serializers.ValidationError("Type is required.")
        if not data.get('amount'):
            raise serializers.ValidationError("Amount is required.")
        if not data.get('description'):
            raise serializers.ValidationError("Description is required.")
        if not data.get('category'):
            raise serializers.ValidationError("Category is required.")
        
        return data
    

@api_view(['GET', 'POST'])
def transactions_view(request):
    if request.method == 'GET':
        # Extract the user from the request
        user_id = request.query_params.get('user', None)  # Get user from query params
        
        # If no user ID is provided, return an error
        if not user_id:
            return Response({'error': 'User ID is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            # Try to find the user by ID
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            # If the user does not exist, return an error
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

        # Filter transactions based on the user
        transactions = Transaction.objects.filter(user=user)
        
        # Serialize the transactions
        serializer = TransactionSerializer(transactions, many=True)
        return Response({'transactions': serializer.data})
    
    elif request.method == 'POST':
        # Handle POST request here as previously outlined
        # You can also add user validation here if needed
        pass

class TransactionsViewSet(ModelViewSet):
    queryset = Transaction.objects.all()
    serializer_class = TransactionSerializer
    filter_backends = [DjangoFilterBackend, OrderingFilter, SearchFilter]
    filterset_fields = ['type', 'category']
    ordering_fields = ['amount', 'date']
    ordering = ['date']  # Default ordering
    search_fields = ['description']  # Add fields for searching

    def apply_filters(self, filters): # i renamed the transactions to self, check for error.
        """Applies filters to the transaction queryset."""
        q_objects = Q()  # Initialize Q object for OR conditions

        for key, value in filters.items():
            if value:
                if key == 'search':
                    q_objects |= Q(description__icontains=value) | Q(notes__icontains=value)
                elif key == 'start_date':
                    transactions = transactions.filter(date__gte=value)
                elif key == 'end_date':
                    transactions = transactions.filter(date__lte=value)
                else:
                    transactions = transactions.filter(**{key: value})  # Use dictionary unpacking for other filters
        
        if q_objects:
            transactions = transactions.filter(q_objects)

        return transactions
    

@csrf_exempt
def transactions_view(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)

        # Get or create the 'web' user
        web_user, created = User.objects.get_or_create(username='web')

        # Get the data for creating a new transaction
        transaction_type = data.get('type')
        amount = data.get('amount')
        description = data.get('description')
        category_id = data.get('category')

        # Create the transaction with the default user 'web'
        transaction = Transaction.objects.create(
            user=web_user,  # Assign the default user if not provided
            type=transaction_type,
            amount=amount,
            description=description,
            category_id=category_id
        )

        # Return a success response
        return JsonResponse({'message': 'Transaction created successfully'}, status=201)

    # If it's a GET request, show all transactions
    transactions = Transaction.objects.all()
    transaction_list = list(transactions.values())
    return JsonResponse({'transactions': transaction_list}, safe=False)