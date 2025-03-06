from io import BytesIO

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

def generate_invoice_pdf(client, services, discounts):
    original_pdf_path = 'RealAgency/media/invoice.pdf'
    original_pdf = PdfReader(original_pdf_path)

    total_price = sum(service.price for service in services)
    total_discount_rate = sum(discount.rate for discount in discounts)

    # Create overlay PDF with dynamic data
    overlay_buffer = BytesIO()
    c = canvas.Canvas(overlay_buffer, pagesize=letter)
    c.setFont("DejaVuSans", 12)

    PDV_RATE = 20  # example 20%
    services_data = [["Назва", "Ціна без ПДВ", "Ціна з ПДВ"]]
    for service in services:
        price_without_pdv = service.price
        services_data.append([
            service.name,
            f"{price_without_pdv:.2f} UAH",
        ])

    c.setFont("DejaVuSans", 12)

    c.drawString(100, 700, f"Client: {client.name}")
    c.drawString(100, 680, f"Total Price: {total_price:.2f} UAH")

    table = Table(services_data, colWidths=[80 * mm, 40 * mm, 40 * mm])
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
    table.drawOn(c, 100, 500)

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