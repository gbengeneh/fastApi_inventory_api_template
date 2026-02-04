import win32print
import win32api
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.units import inch
import os
from typing import Dict, Any
import json

def get_installed_printers():
    """Get list of installed printers on the system."""
    printers = []
    try:
        printer_list = win32print.EnumPrinters(2)  # PRINTER_ENUM_LOCAL
        print(f"Raw printer list length: {len(printer_list)}")
        for i, printer in enumerate(printer_list):
            print(f"Printer {i}: {printer}")
            if len(printer) >= 3:
                printers.append({
                    'name': printer[2],  # pPrinterName
                    'description': printer[1] if len(printer) > 1 else '',  # pDescription
                    'status': printer[4] if len(printer) > 4 else 0,  # Status
                    'location': printer[5] if len(printer) > 5 else '',  # pLocation
                    'comment': printer[6] if len(printer) > 6 else ''  # pComment
                })
        print(f"Processed printers: {len(printers)}")
    except Exception as e:
        print(f"Error getting printers: {e}")
        import traceback
        traceback.print_exc()
    return printers

def print_receipt(printer_name: str, receipt_data: Dict[str, Any], printer_settings: Dict[str, Any] = None):
    """Print receipt using Windows printer."""
    try:
        # Set default printer if specified
        if printer_name:
            win32print.SetDefaultPrinter(printer_name)

        # Get printer handle
        hprinter = win32print.OpenPrinter(printer_name)
        try:
            # Start print job
            job_info = ("Receipt", None, "RAW")
            hjob = win32print.StartDocPrinter(hprinter, 1, job_info)
            try:
                win32print.StartPagePrinter(hprinter)

                # Format receipt text
                receipt_text = format_receipt_text(receipt_data, printer_settings or {})

                # Send to printer
                win32print.WritePrinter(hprinter, receipt_text.encode('utf-8'))

                win32print.EndPagePrinter(hprinter)
            finally:
                win32print.EndDocPrinter(hprinter)
        finally:
            win32print.ClosePrinter(hprinter)

        return {"success": True, "message": f"Receipt printed to {printer_name}"}
    except Exception as e:
        return {"success": False, "message": f"Printing failed: {str(e)}"}

def print_invoice_pdf(printer_name: str, invoice_data: Dict[str, Any], template_data: str = None):
    """Generate and print PDF invoice."""
    try:
        # Parse template_data if it's a string
        if isinstance(template_data, str):
            try:
                template_data = json.loads(template_data) if template_data else {}
            except json.JSONDecodeError:
                template_data = {}
        elif template_data is None:
            template_data = {}

        # Generate PDF
        pdf_path = generate_invoice_pdf(invoice_data, template_data)

        # Print PDF using default PDF viewer or direct print
        win32api.ShellExecute(0, "print", pdf_path, None, ".", 0)

        # Clean up PDF file after printing (optional)
        # os.remove(pdf_path)

        return {"success": True, "message": f"Invoice PDF sent to printer", "pdf_path": pdf_path}
    except Exception as e:
        return {"success": False, "message": f"PDF printing failed: {str(e)}"}

def format_receipt_text(receipt_data: Dict[str, Any], settings: Dict[str, Any]) -> str:
    """Format receipt data as text for thermal printer."""
    lines = []

    # Header
    header_text = receipt_data.get('template', {}).get('header_text', 'RECEIPT')
    lines.append(f"{'='*32}")
    lines.append(f"{header_text.center(32)}")
    lines.append(f"{'='*32}")

    # Outlet info
    outlet = receipt_data.get('outlet', {})
    if isinstance(outlet, dict):
        lines.append(f"{outlet.get('name', 'Store')}")
        if outlet.get('address'):
            lines.append(f"{outlet['address']}")
        if outlet.get('phone'):
            lines.append(f"Phone: {outlet['phone']}")
        if outlet.get('email'):
            lines.append(f"Email: {outlet['email']}")
    else:
        lines.append(f"Outlet: {outlet}")
    lines.append("")

    # Items
    lines.append("Items:")
    lines.append("-" * 32)
    for item in receipt_data.get('items', []):
        name = item['product_name'][:20]  # Truncate long names
        qty = str(item['quantity'])
        price = f"{item['selling_price']:.2f}"
        total = f"{item['total']:.2f}"
        lines.append(f"{name:<20} {qty:>3} x {price:>6}")
        lines.append(f"{'':<20} {'':>3}   {total:>6}")

    lines.append("-" * 32)

    # Totals
    total = f"{receipt_data.get('total_amount', 0):.2f}"
    discount = f"{receipt_data.get('discount', 0):.2f}"
    tax = f"{receipt_data.get('tax', 0):.2f}"
    net = f"{receipt_data.get('net_total', 0):.2f}"

    lines.append(f"Subtotal: {total:>18}")
    if discount != "0.00":
        lines.append(f"Discount: {discount:>18}")
    if tax != "0.00":
        lines.append(f"Tax: {tax:>18}")
    lines.append(f"Total: {net:>20}")
    lines.append("")

    # Footer
    footer_text = receipt_data.get('template', {}).get('footer_text', 'Thank you!')
    lines.append(footer_text.center(32))
    lines.append(f"{'='*32}")

    return "\n".join(lines) + "\n\n\n"

def generate_invoice_pdf(invoice_data: Dict[str, Any], template_data: Dict[str, Any]) -> str:
    """Generate PDF invoice using ReportLab."""
    # Create PDF filename
    pdf_filename = f"invoice_{invoice_data['sale_id']}.pdf"
    pdf_path = os.path.join(os.getcwd(), pdf_filename)

    # Create PDF document
    doc = SimpleDocTemplate(pdf_path, pagesize=A4)
    styles = getSampleStyleSheet()
    story = []

    # Custom styles
    title_style = ParagraphStyle(
        'Title',
        parent=styles['Heading1'],
        fontSize=18,
        spaceAfter=30,
        alignment=1  # Center
    )

    header_style = ParagraphStyle(
        'Header',
        parent=styles['Normal'],
        fontSize=12,
        spaceAfter=10
    )

    # Title
    story.append(Paragraph("INVOICE", title_style))
    story.append(Spacer(1, 12))

    # Header info
    header_text = template_data.get('header_text', 'Invoice Header')
    story.append(Paragraph(header_text, header_style))
    story.append(Spacer(1, 12))

    # Outlet and sale info
    outlet = invoice_data.get('outlet', {})
    sale_id = invoice_data.get('sale_id', 'N/A')

    if isinstance(outlet, dict):
        outlet_info = f"{outlet.get('name', 'Store')}"
        if outlet.get('address'):
            outlet_info += f"\n{outlet['address']}"
        if outlet.get('phone'):
            outlet_info += f"\nPhone: {outlet['phone']}"
        if outlet.get('email'):
            outlet_info += f"\nEmail: {outlet['email']}"
    else:
        outlet_info = outlet

    info_data = [
        ['Outlet:', outlet_info],
        ['Sale ID:', str(sale_id)],
        ['Date:', invoice_data.get('created_at', 'N/A')]
    ]

    info_table = Table(info_data, colWidths=[2*inch, 4*inch])
    info_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ]))
    story.append(info_table)
    story.append(Spacer(1, 20))

    # Items table
    items_data = [['Product', 'Qty', 'Price', 'Total']]
    for item in invoice_data.get('items', []):
        items_data.append([
            item['product_name'],
            str(item['quantity']),
            f"{item['selling_price']:.2f}",
            f"{item['total']:.2f}"
        ])

    items_table = Table(items_data, colWidths=[3*inch, 1*inch, 1.5*inch, 1.5*inch])
    items_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    story.append(items_table)
    story.append(Spacer(1, 20))

    # Totals
    total = invoice_data.get('total_amount', 0)
    discount = invoice_data.get('discount', 0)
    tax = invoice_data.get('tax', 0)
    net_total = invoice_data.get('net_total', total + tax - discount)

    totals_data = [
        ['Subtotal:', f"{total:.2f}"],
        ['Discount:', f"{discount:.2f}"],
        ['Tax:', f"{tax:.2f}"],
        ['Total:', f"{net_total:.2f}"]
    ]

    totals_table = Table(totals_data, colWidths=[4*inch, 2*inch])
    totals_table.setStyle(TableStyle([
        ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
        ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 12),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ]))
    story.append(totals_table)
    story.append(Spacer(1, 20))

    # Footer
    footer_text = template_data.get('footer_text', 'Thank you for your business!')
    story.append(Paragraph(footer_text, header_style))

    # Build PDF
    doc.build(story)
    return pdf_path
