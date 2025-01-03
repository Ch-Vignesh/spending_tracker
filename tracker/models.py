from django.db import models
from django.contrib.auth.models import User


class Category(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

    @classmethod
    def create_default_categories(cls):
        # Create default categories if they don't exist
        default_categories = ['Food', 'Transportation', 'Utilities']
        for category_name in default_categories:
            if not cls.objects.filter(name=category_name).exists():
                cls.objects.create(name=category_name)



class Transaction(models.Model):

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    type = models.CharField(max_length=10)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateField()
    description = models.TextField()
    category = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.type} - {self.amount}"

    @property
    def get_balance(self):
        balance = Transaction.objects.filter(type=Transaction.INCOME).aggregate(
            total_income=models.Sum('amount')
        )['total_income'] or 0
        expenses = Transaction.objects.filter(type=Transaction.EXPENSE).aggregate(
            total_expenses=models.Sum('amount')
        )['total_expenses'] or 0
        return balance - expenses
