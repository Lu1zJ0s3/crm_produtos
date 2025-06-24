from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import Product, Sale, User

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'description', 'price', 'stock']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'price': forms.NumberInput(attrs={'class': 'form-control'}),
            'stock': forms.NumberInput(attrs={'class': 'form-control'}),
        }
        labels = {
            'name': 'Nome do Produto',
            'description': 'Descrição',
            'price': 'Preço (R$)',
            'stock': 'Quantidade em Estoque'
        }

class UserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2', 'is_owner']
        widgets = {
            'is_owner': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
        

class SaleForm(forms.ModelForm):
    class Meta:
        model = Sale
        fields = ['product', 'quantity', 'sale_price']
