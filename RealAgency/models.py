from django.db import models

class ClientType(models.Model):
    name = models.CharField(max_length=255)

class Client(models.Model):
    client_type = models.ForeignKey(ClientType, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    address = models.CharField(max_length=255)
    phone = models.CharField(max_length=255)
    email = models.CharField(max_length=255)
    passport_id = models.CharField(max_length=255, null=True, blank=True)
    iin = models.CharField(max_length=255, null=True, blank=True)
    edrpou = models.CharField(max_length=255, null=True, blank=True)

class Invoice(models.Model):
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    date = models.DateField()
    code = models.CharField(max_length=255)
    invoice_file_path = models.CharField(max_length=255)
    commission = models.IntegerField()
    discount = models.IntegerField()
    pdv = models.IntegerField()
    commission_amount_no_pdv = models.DecimalField(max_digits=19, decimal_places=2)
    services_total_no_pdv = models.DecimalField(max_digits=19, decimal_places=2)
    total_no_pdv = models.DecimalField(max_digits=19, decimal_places=2)
    total_pdv = models.DecimalField(max_digits=19, decimal_places=2)

class Service(models.Model):
    name = models.CharField(max_length=255)
    description = models.CharField(max_length=255)
    unit = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=19, decimal_places=2)

class ProvidedService(models.Model):
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE)
    service = models.ForeignKey(Service, on_delete=models.CASCADE)
    amount = models.IntegerField()
    price = models.DecimalField(max_digits=19, decimal_places=2)
    pdv = models.IntegerField()
    total_no_pdv = models.DecimalField(max_digits=19, decimal_places=2)
    total_pdv = models.DecimalField(max_digits=19, decimal_places=2)

class Discount(models.Model):
    name = models.CharField(max_length=255)
    rate = models.IntegerField()
    description = models.CharField(max_length=255)

class InvoiceDiscount(models.Model):
    discount = models.ForeignKey(Discount, on_delete=models.CASCADE)
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE)
