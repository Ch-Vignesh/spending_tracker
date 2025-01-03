from django import forms
from .models import Transaction, Category

class TransactionForm(forms.ModelForm):
    new_category = forms.CharField(max_length=100, required=False, label="New Category", help_text="Optional: Enter a new category if needed")

    class Meta:
        model = Transaction
        fields = ['amount', 'description', 'category']
        widgets = {
            'amount': forms.NumberInput(attrs={'required': True}),
        }

    def clean(self):
        cleaned_data = super().clean()
        new_category = cleaned_data.get('new_category')

        if new_category:
            # If a new category is provided, create a new Category instance
            category, created = Category.objects.get_or_create(name=new_category)
            cleaned_data['category'] = category  # Assign the new category to the transaction
        return cleaned_data
