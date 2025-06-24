from django.urls import path
from .views import (
    dashboard, 
    ProductListView, 
    ProductCreateView, 
    ProductUpdateView, 
    ProductDeleteView,
    sales_report
)
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('login/', auth_views.LoginView.as_view(template_name='crm/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('register/', views.register, name='register'),
    path('', dashboard, name='dashboard'),
    path('products/', ProductListView.as_view(), name='product-list'),
    path('products/new/', ProductCreateView.as_view(), name='product-create'),
    path('products/<int:pk>/edit/', ProductUpdateView.as_view(), name='product-update'),
    path('products/<int:pk>/delete/', ProductDeleteView.as_view(), name='product-delete'),
    path('vendas/nova/', views.registrar_venda, name='registrar_venda'),
    path('sales-report/', sales_report, name='sales-report'),
]