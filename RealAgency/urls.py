# from django.contrib import admin
from django.urls import path

from RealAgency.views import home, clients, discounts, payments, provided_services, services, \
    add_or_edit_client, delete_client, add_discount, delete_discount, edit_discount, add_service, edit_service, \
    delete_service, add_invoice, search_services

urlpatterns = [
    #    path('admin/', admin.site.urls),
    path('', home, name='home'),
    path('clients', clients, name='clients'),
    path('discounts', discounts, name='discounts'),
    path('invoices', payments, name='invoices'),
    path('clients', clients, name='clients'),
    path('provided_services', provided_services, name='provided_services'),
    path('services', services, name='services'),

    path('add_client/', add_or_edit_client, name='add_client'),
    path('edit_client/<int:client_id>/', add_or_edit_client, name='edit_client'),
    path('delete_client/<int:client_id>/', delete_client, name='delete_client'),


    path('add_discount/', add_discount, name='add_discount'),
    path('edit_discount/<int:discount_id>/', edit_discount, name='edit_discount'),
    path('delete_discount/<int:discount_id>/', delete_discount, name='delete_discount'),

    path('add_service/', add_service, name='add_service'),
    path('edit_service/<int:service_id>/', edit_service, name='edit_service'),
    path('delete_service/<int:service_id>/', delete_service, name='delete_service'),

    path('add_invoice/', add_invoice, name='add_invoice'),

    path('search_services/', search_services, name='search_services'),
]

