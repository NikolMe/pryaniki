# from django.contrib import admin
from django.urls import path

from RealAgency.views import home, clients, discounts, payments, provided_services, services, \
    add_or_edit_client, delete_client

urlpatterns = [
    #    path('admin/', admin.site.urls),
    path('', home, name='home'),
    path('clients', clients, name='clients'),
    path('discounts', discounts, name='discounts'),
    path('payments', payments, name='payments'),
    path('clients', clients, name='clients'),
    path('provided_services', provided_services, name='provided_services'),
    path('services', services, name='services'),

    path('add_client/', add_or_edit_client, name='add_client'),
    path('edit_client/<int:client_id>/', add_or_edit_client, name='edit_client'),
    path('delete_client/<int:client_id>/', delete_client, name='delete_client'),
]
