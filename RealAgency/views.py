import datetime
import json

from django.contrib.auth import login
from django.core.exceptions import PermissionDenied
from django.core.paginator import Paginator
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.csrf import csrf_exempt

from RealAgency.forms import CustomAuthenticationForm
from RealAgency.models import ClientType
from .utils import generate_invoice_pdf


def login_view(request):
    if request.method == 'POST':
        form = CustomAuthenticationForm(request, data=request.POST)  # Use your custom form
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('/')  # Redirect to the homepage after login
        else:
            return render(request, 'login/login.html', {'form': form})
    else:
        form = CustomAuthenticationForm()
        return render(request, 'login/login.html', {'form': form})

def role_required(roles):
    def decorator(view_func):
        def _wrapped_view(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect('login')

            if not any(group.name in roles for group in request.user.groups.all()):
                raise PermissionDenied("You are not permitted to perform this action.")

            return view_func(request, *args, **kwargs)

        return _wrapped_view

    return decorator

@role_required(['Manager', 'Notary'])
def home(request):
    return render(request, 'main.html')

@role_required(['Manager', 'Notary'])
def clients(request):
    client_list = Client.objects.all().order_by('id')
    paginator = Paginator(client_list, 10)
    user_groups = request.user.groups.values_list('name', flat=True)

    client_types = ClientType.objects.all()

    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'clients/main.html', {'page_obj': page_obj, 'client_types': client_types, 'user_groups': user_groups })

@role_required(['Manager', 'Notary'])
def discounts(request):
    discount_list = Discount.objects.all().order_by('id')
    user_groups = request.user.groups.values_list('name', flat=True)

    return render(request, 'discounts/main.html', { 'discounts': discount_list, 'user_groups': user_groups })

@role_required(['Manager', 'Notary'])
def payments(request):
    payments_list = Invoice.objects.all().order_by('id')
    user_groups = request.user.groups.values_list('name', flat=True)

    # Pagination: 15 items per page
    paginator = Paginator(payments_list, 15)

    # Get the current page number from the request
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'invoices/main.html', {'invoices': page_obj, 'user_groups': user_groups})


@role_required(['Manager', 'Notary'])
def provided_services(request):
    provided_services_list = ProvidedService.objects.all().order_by('id')

    # Pagination: 15 items per page
    paginator = Paginator(provided_services_list, 15)

    # Get the current page number from the request
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'provided_services/main.html', {'provided_services': page_obj})

@role_required(['Manager', 'Notary'])
def services(request):
    search_query = request.GET.get('search', '')
    sort_option = request.GET.get('sort', '')
    user_groups = request.user.groups.values_list('name', flat=True)

    services_list = Service.objects.all()

    # Filter by search query if it's at least 2 characters
    if len(search_query) >= 2:
        services_list = services_list.filter(name__icontains=search_query)

    # Apply sorting
    if sort_option == 'name_asc':
        services_list = services_list.order_by('name')
    elif sort_option == 'name_desc':
        services_list = services_list.order_by('-name')
    elif sort_option == 'price_asc':
        services_list = services_list.order_by('price')
    elif sort_option == 'price_desc':
        services_list = services_list.order_by('-price')
    else:
        services_list = services_list.order_by('id')

    return render(request, 'services/main.html', {
        'services': services_list,
        'user_groups': user_groups,
        'search_query': search_query,
        'sort_option': sort_option,
    })


@role_required(['Manager'])
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

@role_required(['Manager', 'Notary'])
def add_or_edit_invoice(request, invoice_id=None):
    if request.method == 'POST':
        invoice_id = request.POST.get('invoice_id')
        client = Client.objects.get(id=request.POST.get('client'))
        date = request.POST.get('date')
        code = request.POST.get('code')
        invoice_file_path = request.POST.get('invoice_file_path')
        commission = request.POST.get('commission')
        discount = request.POST.get('discount')
        pdv = request.POST.get('pdv')
        commission_amount_no_pdv = request.POST.get('commission_amount_no_pdv')
        services_total_no_pdv = request.POST.get('services_total_no_pdv')
        total_no_pdv = request.POST.get('total_no_pdv')
        total_pdv = request.POST.get('total_pdv')

        if invoice_id:
            invoice = get_object_or_404(Invoice, id=invoice_id)
            invoice.client = client
            invoice.date = date
            invoice.code = code
            invoice.invoice_file_path = invoice_file_path
            invoice.commission = commission
            invoice.discount = discount
            invoice.pdv = pdv
            invoice.commission_amount_no_pdv = commission_amount_no_pdv
            invoice.services_total_no_pdv = services_total_no_pdv
            invoice.total_no_pdv = total_no_pdv
            invoice.total_pdv = total_pdv
            invoice.save()
        else:
            Invoice.objects.create(
                client=client,
                date=date,
                code=code,
                invoice_file_path=invoice_file_path,
                commission=commission,
                discount=discount,
                pdv=pdv,
                commission_amount_no_pdv=commission_amount_no_pdv,
                services_total_no_pdv=services_total_no_pdv,
                total_no_pdv=total_no_pdv,
                total_pdv=total_pdv)

        return redirect('invoices')

@role_required(['Manager'])
def add_or_edit_service(request, service_id=None):
    if request.method == 'POST':
        service_id = request.POST.get('service_id')
        name = request.POST.get('name')
        description = request.POST.get('description')
        unit = request.POST.get('unit')
        price = request.POST.get('price')

        if service_id:
            service = get_object_or_404(Service, id=service_id)
            service.name = name
            service.description = description
            service.unit = unit
            service.price = price
            service.save()
        else:
            Service.objects.create(
                name=name,
                description=description,
                unit=unit,
                price=price)

        return redirect('services')

@role_required(['Manager', 'Notary'])
def add_or_edit_provided_service(request, provided_service_id=None):
    if request.method == 'POST':
        provided_service_id = request.POST.get('provided_service_id')
        invoice = Invoice.objects.get(id=request.POST.get('invoice'))
        service = Service.objects.get(id=request.POST.get('service'))
        amount = request.POST.get('amount')
        price = request.POST.get('price')
        pdv = request.POST.get('pdv')
        total_no_pdv = request.POST.get('total_no_pdv')
        total_pdv = request.POST.get('total_pdv')

        if provided_service_id:
            provided_service = get_object_or_404(ProvidedService, id=provided_service_id)
            provided_service.invoice = invoice
            provided_service.service = service
            provided_service.amount = amount
            provided_service.price = price
            provided_service.pdv = pdv
            provided_service.total_no_pdv = total_no_pdv
            provided_service.total_pdv = total_pdv
            provided_service.save()
        else:
            ProvidedService.objects.create(
                invoice=invoice,
                service=service,
                amount=amount,
                price=price,
                pdv=pdv,
                total_no_pdv=total_no_pdv,
                total_pdv=total_pdv)

        return redirect('provided_services')

@role_required(['Manager', 'Notary'])
def add_or_edit_discount(request, discount_id=None):
    if request.method == 'POST':
        discount_id = request.POST.get('discount_id')
        name = request.POST.get('name')
        rate = request.POST.get('rate')
        description = request.POST.get('description')

        if discount_id:
            discount = get_object_or_404(Discount, id=discount_id)
            discount.name = name
            discount.rate = rate
            discount.description = description
            discount.save()
        else:
            Discount.objects.create(
                name=name,
                rate=rate,
                description=description)

        return redirect('discounts')


@role_required(['Manager'])
def delete_client(request, client_id):
    client = get_object_or_404(Client, id=client_id)
    client.delete()
    return JsonResponse({"success": True})

@role_required(['Manager'])
def delete_discount(request, discount_id):
    discount = get_object_or_404(Discount, id=discount_id)
    discount.delete()
    return JsonResponse({"success": True})

@role_required(['Manager'])
def delete_payment(request, payment_id):
    payment = get_object_or_404(Invoice, id=payment_id)
    payment.delete()
    return JsonResponse({"success": True})

def delete_provided_service(request, provided_service_id):
    provided_service = get_object_or_404(ProvidedService, id=provided_service_id)
    provided_service.delete()
    return JsonResponse({"success": True})

@role_required(['Manager'])
@csrf_exempt
def add_discount(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        rate = request.POST.get('rate')
        description = request.POST.get('description')

        Discount.objects.create(
            name=name,
            rate=rate,
            description=description
        )
        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'error', 'message': 'Invalid request'}, status=400)


@role_required(['Manager'])
@csrf_exempt
def edit_discount(request, discount_id):
    discount = get_object_or_404(Discount, id=discount_id)

    if request.method == 'POST':
        discount.name = request.POST.get('name')
        discount.rate = request.POST.get('rate')
        discount.description = request.POST.get('description')
        discount.save()
        return JsonResponse({'status': 'success'})

    return JsonResponse({'status': 'error', 'message': 'Invalid request'}, status=400)


@role_required(['Manager'])
@csrf_exempt
def delete_discount(request, discount_id):
    if request.method == 'POST':
        discount = get_object_or_404(Discount, id=discount_id)
        discount.delete()
        return JsonResponse({'status': 'success'})

    return JsonResponse({'status': 'error', 'message': 'Invalid request'}, status=400)

@role_required(['Manager'])
def add_service(request):
    if request.method == 'POST':
        Service.objects.create(
            name=request.POST['name'],
            description=request.POST['description'],
            price=request.POST['price']
        )
        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'error'}, status=400)

@role_required(['Manager'])
def edit_service(request, service_id):
    if request.method == 'POST':
        service = get_object_or_404(Service, id=service_id)
        service.name = request.POST['name']
        service.description = request.POST['description']
        service.price = request.POST['price']
        service.save()
        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'error'}, status=400)

@role_required(['Manager'])
def delete_service(request, service_id):
    if request.method == 'POST':
        service = get_object_or_404(Service, id=service_id)
        service.delete()
        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'error'}, status=400)

@role_required(['Notary'])
def add_invoice(request):
    discount_list = Discount.objects.all().order_by('id')
    return render(request, 'invoices/add_invoice.html', {'discounts': discount_list})

@role_required(['Manager', 'Notary'])
def search_services(request):
    query = request.GET.get('q', '').strip()
    services = []
    if len(query) >= 2:
        services = list(Service.objects.filter(name__icontains=query).values('id', 'name', 'description', 'price')[:5])
    return JsonResponse(services, safe=False)


@role_required(['Manager', 'Notary'])
def search_clients(request):
    query = request.GET.get('q', '')
    clients = Client.objects.filter(name__icontains=query)[:5]
    client_data = [{'id': client.id, 'name': client.name, 'iin': client.iin} for client in clients]
    return JsonResponse(client_data, safe=False)


import random
from datetime import datetime
from django.http import JsonResponse
from .models import Invoice, Client, Service, Discount, ProvidedService

def create_invoice(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        client_id = data.get('client_id')
        service_ids = data.get('service_ids', [])
        discount_ids = data.get('discount_ids', [])

        client = Client.objects.get(id=client_id)
        services = Service.objects.filter(id__in=service_ids)
        discounts = Discount.objects.filter(id__in=discount_ids)

        invoice_code = ''.join([str(random.randint(0, 9)) for _ in range(5)])

        current_date = datetime.now().date()

        invoice_file_path = f"{client.name}_invoice_{current_date.day}_{current_date.strftime('%b').lower()}_{str(current_date.year)[2:]}.pdf"

        pdv = 20  # PDV is 20%
        commission = 10  # Commission is 10% (static)

        total_discount_rate = sum([discount.rate for discount in discounts])
        total_price = sum([service.price for service in services])
        total_price = float(total_price)
        total_discount_rate = float(total_discount_rate)
        total_pdv = total_price * ((100 - total_discount_rate) / 100)
        total_no_pdv = total_pdv * ((100 - pdv) / 100)
        commission_amount_no_pdv = total_no_pdv * commission

        invoice = Invoice.objects.create(
            client=client,
            date=current_date,
            code=invoice_code,
            invoice_file_path=invoice_file_path,
            commission=commission,
            discount=total_discount_rate,
            pdv=pdv,
            commission_amount_no_pdv=commission_amount_no_pdv,
            services_total_no_pdv=0,
            total_no_pdv=total_no_pdv,
            total_pdv=total_pdv
        )

        for service in services:
            price = service.price

            total_service_pdv = float(price) * ((100 - total_discount_rate) / 100)
            total_service_no_pdv= total_service_pdv * ((100 - pdv) / 100)

            provided_service = ProvidedService.objects.create(
                invoice=invoice,
                service=service,
                amount=1,
                price=price,
                pdv=pdv,
                total_no_pdv=total_service_no_pdv,
                total_pdv=total_service_pdv
            )

        invoice.save()

        return JsonResponse({'success': True, 'invoice_id': invoice.id})

    else:
        return JsonResponse({'success': False, 'message': 'Invalid request method.'}, status=400)


def generate_invoice_preview(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        client_id = data.get('client_id')
        service_ids = data.get('service_ids', [])
        discount_ids = data.get('discount_ids', [])

        try:
            client = Client.objects.get(id=client_id)
            services = Service.objects.filter(id__in=service_ids)
            discounts = Discount.objects.filter(id__in=discount_ids)
        except Client.DoesNotExist:
            return JsonResponse({'error': 'Client not found'}, status=404)

        final_pdf_buffer = generate_invoice_pdf(client, services, discounts)

        response = HttpResponse(final_pdf_buffer, content_type='application/pdf')
        response['Content-Disposition'] = 'inline; filename="invoice_preview.pdf"'
        return response

    return HttpResponse(status=400)


