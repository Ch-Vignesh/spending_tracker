from rest_framework import serializers
from .models import Transaction, Category

class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = '__all__'
        
    # Optionally, you can add custom validation or methods if needed
