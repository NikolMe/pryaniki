from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.core.paginator import Paginator

from RealAgency.models import Client, ClientType


def home(request):
    return render(request, 'main.html')

def clients(request):
    client_list = Client.objects.all().order_by('id')
    paginator = Paginator(client_list, 10)

    client_types = ClientType.objects.all()

    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'clients/main.html', {'page_obj': page_obj, 'client_types': client_types })

def discounts(request):
    return render(request, 'discounts/main.html')

def payments(request):
    return render(request, 'payments/main.html')

def provided_services(request):
    return render(request, 'provided_services/main.html')

def services(request):
    return render(request, 'services/main.html')

def add_or_edit_client(request, client_id=None):
    if request.method == 'POST':
        client_id = request.POST.get('client_id')
        client_type = ClientType.objects.get(id=request.POST.get('client_type'))
        name = request.POST.get('name')
        address = request.POST.get('address')
        phone = request.POST.get('phone')
        email = request.POST.get('email')
        passport_id = request.POST.get('passport_id')
        iin = request.POST.get('iin')
        edrpou = request.POST.get('edrpou')

        if client_id:
            client = get_object_or_404(Client, id=client_id)
            client.client_type = client_type
            client.name = name
            client.address = address
            client.phone = phone
            client.email = email
            client.passport_id = passport_id
            client.iin = iin
            client.edrpou = edrpou
            client.save()
        else:
            Client.objects.create(
                client_type=client_type,
                name=name,
                address=address,
                phone=phone,
                email=email,
                passport_id=passport_id,
                iin=iin,
                edrpou=edrpou)

        return redirect('clients')

def delete_client(request, client_id):
    client = get_object_or_404(Client, id=client_id)
    client.delete()
    return JsonResponse({"success": True})

