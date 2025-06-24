from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from .models import Product, Sale, User
from .forms import SaleForm, ProductForm, UserCreationForm

def is_owner(user):
    return user.is_owner

def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('dashboard')
    else:
        form = UserCreationForm()
    return render(request, 'crm/register.html', {'form': form})

@login_required
def dashboard(request):
    total_products = Product.objects.count()
    total_sales = Sale.objects.count()
    revenue = sum(sale.sale_price * sale.quantity for sale in Sale.objects.all())
    latest_products = Product.objects.order_by('-created_at')[:5]
    
    context = {
        'total_products': total_products,
        'total_sales': total_sales,
        'revenue': revenue,
        'latest_products': latest_products
    }
    return render(request, 'crm/dashboard.html', context)

class ProductListView(LoginRequiredMixin, ListView):
    model = Product
    template_name = 'crm/product_list.html'
    context_object_name = 'products'
    paginate_by = 10

class ProductCreateView(LoginRequiredMixin, CreateView):
    model = Product
    form_class = ProductForm
    template_name = 'crm/product_form.html'
    success_url = reverse_lazy('product-list')

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        return super().form_valid(form)

class ProductUpdateView(LoginRequiredMixin, UpdateView):
    model = Product
    form_class = ProductForm
    template_name = 'crm/product_form.html'
    success_url = reverse_lazy('product-list')

class ProductDeleteView(LoginRequiredMixin, DeleteView):
    model = Product
    template_name = 'crm/product_confirm_delete.html'
    success_url = reverse_lazy('product-list')

@login_required
@user_passes_test(is_owner)
def sales_report(request):
    sales = Sale.objects.all().order_by('-created_at')
    total_revenue = sum(sale.sale_price * sale.quantity for sale in sales)
    
    context = {
        'sales': sales,
        'total_revenue': total_revenue
    }
    return render(request, 'crm/sales_report.html', context)


@login_required
def registrar_venda(request):
    if request.method == 'POST':
        form = SaleForm(request.POST)
        if form.is_valid():
            venda = form.save(commit=False)
            venda.created_by = request.user
            venda.save()
            return redirect('dashboard')
    else:
        form = SaleForm()
    return render(request, 'crm/sale_form.html', {'form': form, 'titulo': 'Registrar Venda'})
