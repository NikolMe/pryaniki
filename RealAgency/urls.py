# from django.contrib import admin
from django.urls import path

from RealAgency.views import home, clients, discounts, payments, provided_services, services

urlpatterns = [
    #    path('admin/', admin.site.urls),
    path('', home, name='home'),
    path('clients', clients, name='clients'),
    path('discounts', discounts, name='discounts'),
    path('payments', payments, name='payments'),
    path('clients', clients, name='clients'),
    path('provided_services', provided_services, name='provided_services'),
    path('services', services, name='services'),
]
