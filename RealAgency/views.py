from django.shortcuts import render

def home(request):
    return render(request, 'main.html')

def clients(request):
    return render(request, 'clients/main.html')

def discounts(request):
    return render(request, 'discounts/main.html')

def payments(request):
    return render(request, 'payments/main.html')

def provided_services(request):
    return render(request, 'provided_services/main.html')

def services(request):
    return render(request, 'services/main.html')
