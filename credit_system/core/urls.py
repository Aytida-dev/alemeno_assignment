from django.urls import path
from .import views

urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.create_customer, name='create customers'),
    path('check-eligiblity/', views.check_eligiblity, name='check eligibility'),
    path('create-loan/', views.create_loan, name='apply loan'),
    path('view-loan/<int:loan_id>' , views.get_loan_by_loan_id, name='view loan'),
    path('view-loans/<int:customer_id>' , views.view_loan_by_customer, name='view loan'),
]