import locale
from datetime import datetime
from io import BytesIO

from num2words import num2words
from reportlab.lib import colors
from reportlab.lib.fonts import addMapping
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from PyPDF2 import PdfReader, PdfWriter
from reportlab.platypus import Table, TableStyle

pdfmetrics.registerFont(TTFont('DejaVuSans', 'RealAgency/media/dejavu-fonts-ttf-2.37/ttf/DejaVuSans.ttf'))
addMapping('DejaVuSans', 0, 0, 'DejaVuSans')

def generate_preview_invoice(client, services, discounts):
    original_pdf_path = 'RealAgency/media/invoice.pdf'
    original_pdf = PdfReader(original_pdf_path)

    # Create overlay PDF with dynamic data
    overlay_buffer = BytesIO()
    c = canvas.Canvas(overlay_buffer, pagesize=letter)

    PDV_RATE = 20  # example 20%

    services_data = [["№", "Код", "Назва", "Ціна без ПДВ", "Ціна з ПДВ"]]
    num = 0
    for service in services:
        num += 1

        price = float(service.price)
        price_without_pdv = price * ((100 - PDV_RATE) / 100)

        services_data.append([
            num,
            service.id,
            service.name,
            f"{price_without_pdv:.2f} UAH",
            f"{service.price:.2f} UAH",
        ])


    c.setFont("DejaVuSans", 8)

    locale.setlocale(locale.LC_TIME, 'uk_UA.UTF-8')
    now = datetime.now()
    formatted_date = now.strftime('%d %B %Y')


    total_discount_rate = float(sum([discount.rate for discount in discounts]))
    total_price = float(sum([service.price for service in services]))
    total_pdv = total_price * ((100 - total_discount_rate) / 100)
    pdv_amount = total_pdv * (PDV_RATE / 100)

    c.drawString(177, 724, f"{formatted_date}")
    c.drawString(241, 616, f"{formatted_date}")
    c.drawString(114, 642, f"{client.name}")
    c.drawString(150, 167, f"{num}")
    c.drawString(101, 158, f"{total_pdv:.2f}, {format_currency(total_pdv)}")
    c.drawString(105, 148, f"{pdv_amount:.2f}")

    table = Table(services_data, colWidths=[7 * mm, 13 * mm, 100 * mm, 40 * mm, 40 * mm])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, -1), 'DejaVuSans'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]))

    # Draw table on canvas
    table.wrapOn(c, 100, 500)
    table.drawOn(c, 30, 500)

    c.save()
    overlay_buffer.seek(0)

    overlay_pdf = PdfReader(overlay_buffer)

    # Merge overlay onto first page
    output_pdf = PdfWriter()
    original_page = original_pdf.pages[0]
    overlay_page = overlay_pdf.pages[0]
    original_page.merge_page(overlay_page)
    output_pdf.add_page(original_page)

    # Add remaining pages if necessary
    for page in original_pdf.pages[1:]:
        output_pdf.add_page(page)

    final_pdf_buffer = BytesIO()
    output_pdf.write(final_pdf_buffer)
    final_pdf_buffer.seek(0)

    return final_pdf_buffer


def generate_invoice_pdf(invoice, provided_services):
    original_pdf_path = 'RealAgency/media/invoice.pdf'
    original_pdf = PdfReader(original_pdf_path)

    # Create overlay PDF with dynamic data
    overlay_buffer = BytesIO()
    c = canvas.Canvas(overlay_buffer, pagesize=letter)

    PDV_RATE = 20  # example 20%

    services_data = [["№", "Код", "Назва", "Ціна без ПДВ", "Ціна з ПДВ"]]
    num = 0
    for service in provided_services:
        num += 1

        price = float(service.price)
        price_without_pdv = price * ((100 - PDV_RATE) / 100)

        services_data.append([
            num,
            service.id,
            service.service.name,
            f"{price_without_pdv:.2f} UAH",
            f"{service.price:.2f} UAH",
        ])


    c.setFont("DejaVuSans", 8)

    locale.setlocale(locale.LC_TIME, 'uk_UA.UTF-8')
    formatted_date = invoice.date.strftime('%d %B %Y')


    total_discount_rate = float(invoice.discount)
    total_price = float(sum([service.price for service in provided_services]))
    total_pdv = total_price * ((100 - total_discount_rate) / 100)
    pdv_amount = total_pdv * (PDV_RATE / 100)

    c.drawString(177, 724, f"{formatted_date} №{invoice.code}")
    c.drawString(241, 616, f"{formatted_date} №{invoice.code}")
    c.drawString(114, 642, f"{invoice.client.name}")
    c.drawString(150, 167, f"{num}")
    c.drawString(101, 158, f"{total_pdv:.2f}, {format_currency(total_pdv)}")
    c.drawString(105, 148, f"{pdv_amount:.2f}")

    table = Table(services_data, colWidths=[7 * mm, 13 * mm, 100 * mm, 40 * mm, 40 * mm])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, -1), 'DejaVuSans'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]))

    # Draw table on canvas
    table.wrapOn(c, 100, 500)
    table.drawOn(c, 30, 500)

    c.save()
    overlay_buffer.seek(0)

    overlay_pdf = PdfReader(overlay_buffer)

    # Merge overlay onto first page
    output_pdf = PdfWriter()
    original_page = original_pdf.pages[0]
    overlay_page = overlay_pdf.pages[0]
    original_page.merge_page(overlay_page)
    output_pdf.add_page(original_page)

    # Add remaining pages if necessary
    for page in original_pdf.pages[1:]:
        output_pdf.add_page(page)

    final_pdf_buffer = BytesIO()
    output_pdf.write(final_pdf_buffer)
    final_pdf_buffer.seek(0)

    return final_pdf_buffer


def format_currency(total_pdv):
    # Total is divided into the integer and fractional parts
    integer_part = int(total_pdv)
    fractional_part = round((total_pdv - integer_part) * 100)

    # Get words for the integer part (in Ukrainian)
    integer_words = num2words(integer_part, lang='uk', to='cardinal')

    # Determine the correct plural form for "гривня"
    integer_part_ost = integer_part % 10
    if integer_part_ost == 1:
        integer_words += " гривня"
    elif 2 <= integer_part_ost <= 4:
        integer_words += " гривні"
    else:
        integer_words += " гривень"

    # Get words for the fractional part (kopecks)
    if fractional_part == 1:
        fractional_words = f"{num2words(fractional_part, lang='uk', to='cardinal')} копійка"
    elif 2 <= fractional_part <= 4:
        fractional_words = f"{num2words(fractional_part, lang='uk', to='cardinal')} копійки"
    else:
        fractional_words = f"{num2words(fractional_part, lang='uk', to='cardinal')} копійок"

    # Combine both parts into the final formatted string
    return f"{integer_words} {fractional_words}"