import os
import subprocess
import platform
from datetime import datetime, date, timedelta
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.units import inch, cm
from reportlab.lib.colors import HexColor
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image as RLImage
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.lib import colors
from PIL import Image
import io
import qrcode
import json

class PDFGenerator:
    """PDF generation utilities for the application"""
    
    def __init__(self, db):
        """Initialize with database connection"""
        self.db = db
    
    def generate_invoice_pdf(self, invoice_id, file_path=None):
        """Generate PDF for an invoice"""
        try:
            # Get invoice details
            invoice = self.db.get_invoice_by_id(invoice_id)
            items = self.db.get_invoice_items(invoice_id)
            
            if not invoice:
                return None
            
            # Generate file path if not provided
            if not file_path:
                if not os.path.exists("invoices"):
                    os.makedirs("invoices")
                file_path = os.path.join("invoices", f"Invoice_{invoice['invoice_number']}.pdf")
            
            # Generate PDF using the new method
            return self.generate_invoice_pdf_from_data(invoice, items, file_path)
        except Exception as e:
            print(f"Error generating invoice PDF: {e}")
            return None
    
    def generate_invoice_pdf_from_data(self, invoice, items, file_path):
        """Generate PDF for an invoice from data"""
        try:
            # Create PDF
            doc = SimpleDocTemplate(file_path, pagesize=A4)
            elements = []
            
            # Get styles
            styles = getSampleStyleSheet()
            
            # Add custom style for modern look
            styles.add(ParagraphStyle(
                name='CustomTitle',
                parent=styles['Heading1'],
                fontSize=18,
                spaceAfter=30,
                textColor=colors.darkblue,
                alignment=TA_CENTER
            ))
            
            styles.add(ParagraphStyle(
                name='CustomHeading',
                parent=styles['Heading2'],
                fontSize=14,
                spaceAfter=12,
                textColor=colors.darkblue
            ))
            
            styles.add(ParagraphStyle(
                name='ButtonStyle',
                parent=styles['Normal'],
                fontSize=12,
                textColor=colors.white,
                alignment=TA_CENTER,
                backColor=colors.green,
                borderColor=colors.darkgreen,
                borderWidth=1,
                borderPadding=5,
                spaceBefore=10,
                spaceAfter=10
            ))
            
            # Company details and logo in a table for better layout
            company_data = []
            company_name = self.db.get_setting("company_name") or "GANESH TOUGHENED INDUSTRY"
            company_address = self.db.get_setting("company_address") or "Plot no:B13, Industrial Estate, Madanapalli"
            company_phone = self.db.get_setting("company_phone") or "9398530499, 7013374872"
            company_gst = self.db.get_setting("company_gst") or "37EXFPK2395CIZE"
            
            # Add logo if available
            logo_path = "assets/images/logo.png"
            if not os.path.exists(logo_path):
                logo_path = "ganesh_toughened_industry/assets/images/logo.png"
            
            logo_cell = None
            if os.path.exists(logo_path):
                logo = RLImage(logo_path, width=1.5*inch, height=1*inch)
                logo_cell = logo
            
            # Company details
            company_details = [
                [Paragraph(f"<b>{company_name}</b>", styles["CustomTitle"])],
                [Paragraph(company_address, styles["Normal"])],
                [Paragraph(f"Phone: {company_phone}", styles["Normal"])],
                [Paragraph(f"GST: {company_gst}", styles["Normal"])]
            ]
            
            company_table = Table(company_details, colWidths=[10*cm])
            company_table.setStyle(TableStyle([
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ]))
            
            # Create table with logo and company details
            if logo_cell:
                company_layout_data = [[logo_cell, company_table]]
                company_layout_table = Table(company_layout_data, colWidths=[2*inch, 10*cm])
            else:
                company_layout_table = company_table
            
            company_layout_table.setStyle(TableStyle([
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ]))
            
            elements.append(company_layout_table)
            elements.append(Spacer(1, 0.3*inch))
            
            # Invoice title
            invoice_title = Paragraph("INVOICE", styles["CustomHeading"])
            elements.append(invoice_title)
            elements.append(Spacer(1, 0.3*cm))
            
            # Invoice details
            invoice_data = [
                ["Invoice #:", invoice["invoice_number"]],
                ["Date:", invoice["date"].strftime("%d/%m/%Y")],
                ["Customer:", invoice["customer_name"]],
                ["Place:", invoice["customer_place"] or ""],
                ["Phone:", invoice["customer_phone"] or ""],
                ["GST:", invoice["customer_gst"] or ""]
            ]
            
            invoice_table = Table(invoice_data, colWidths=[4*cm, 12*cm])
            invoice_table.setStyle(TableStyle([
                ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
                ('ALIGN', (1, 0), (1, -1), 'LEFT'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
            ]))
            
            elements.append(invoice_table)
            elements.append(Spacer(1, 0.5*cm))
            
            # Items table with better formatting
            items_data = [["S.No", "Product", "Actual Size", "Chargeable Size", "SQ.FT", "Rounded SQ.FT", "Rate", "Qty", "Amount"]]
            
            for i, item in enumerate(items, 1):
                actual_size = f"{item['actual_height']}\" x {item['actual_width']}\""
                chargeable_size = f"{item['chargeable_height']}\" x {item['chargeable_width']}\""
                
                items_data.append([
                    str(i),
                    item["product_name"],
                    actual_size,
                    chargeable_size,
                    f"{item['sqft']:.2f}",
                    f"{item['rounded_sqft']:.1f}",
                    f"{item['rate']:.2f}",
                    str(item["quantity"]),
                    f"{item['amount']:.2f}"
                ])
            
            items_table = Table(items_data, colWidths=[1.5*cm, 4*cm, 2.5*cm, 2.5*cm, 1.5*cm, 1.5*cm, 1.5*cm, 1*cm, 2*cm])
            items_table.setStyle(TableStyle([
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('FONTSIZE', (0, 1), (-1, -1), 9),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('TOPPADDING', (0, 1), (-1, -1), 8),
                ('BOTTOMPADDING', (0, 1), (-1, -1), 8),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ]))
            
            elements.append(items_table)
            elements.append(Spacer(1, 0.5*cm))
            
            # Extra charges section
            if 'extra_charges_breakdown' in invoice and invoice['extra_charges_breakdown']:
                try:
                    extra_charges = json.loads(invoice['extra_charges_breakdown'])
                    
                    extra_charges_data = [["Description", "Amount"]]
                    
                    if float(extra_charges.get('cutout', 0)) > 0:
                        extra_charges_data.append(["Cut Out Charges", f"{float(extra_charges.get('cutout', 0)):.2f}"])
                    
                    if float(extra_charges.get('hole', 0)) > 0:
                        extra_charges_data.append(["Hole Charges", f"{float(extra_charges.get('hole', 0)):.2f}"])
                    
                    if float(extra_charges.get('handle', 0)) > 0:
                        extra_charges_data.append(["Door Handle Hole Charges", f"{float(extra_charges.get('handle', 0)):.2f}"])
                    
                    if float(extra_charges.get('jumbo', 0)) > 0:
                        extra_charges_data.append(["Jumbo Size Charges", f"{float(extra_charges.get('jumbo', 0)):.2f}"])
                    
                    if len(extra_charges_data) > 1:  # More than just the header
                        extra_charges_table = Table(extra_charges_data, colWidths=[8*cm, 4*cm])
                        extra_charges_table.setStyle(TableStyle([
                            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
                            ('ALIGN', (0, 1), (0, -1), 'LEFT'),
                            ('ALIGN', (1, 1), (1, -1), 'RIGHT'),
                            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                            ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
                            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                            ('GRID', (0, 0), (-1, -1), 1, colors.darkblue),
                            ('FONTSIZE', (0, 0), (-1, 0), 10),
                            ('FONTSIZE', (0, 1), (-1, -1), 9),
                            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                            ('TOPPADDING', (0, 1), (-1, -1), 8),
                            ('BOTTOMPADDING', (0, 1), (-1, -1), 8),
                            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                        ]))
                        
                        elements.append(extra_charges_table)
                        elements.append(Spacer(1, 0.3*inch))
                except:
                    pass  # Skip if there's an error parsing the extra charges
            
            # Summary
            summary_data = [
                ["Subtotal:", f"{invoice['subtotal']:.2f}"],
                ["Extra Charges:", f"{invoice['extra_charges']:.2f}"],
                ["Gross Total:", f"{invoice['total']:.2f}"]
            ]
            
            summary_table = Table(summary_data, colWidths=[10*cm, 6*cm])
            summary_table.setStyle(TableStyle([
                ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
                ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                ('TEXTCOLOR', (0, 2), (1, 2), colors.darkblue),  # Make total row text blue
                ('FONTNAME', (0, 2), (1, 2), 'Helvetica-Bold'),  # Make total row text bold
            ]))
            
            elements.append(summary_table)
            elements.append(Spacer(1, 0.5*cm))
            
            # Payment details
            payment_data = [
                ["Payment Mode:", invoice["payment_mode"] or ""],
                ["P-PAY No.:", invoice["p_pay_no"] or ""]
            ]
            
            payment_table = Table(payment_data, colWidths=[4*cm, 12*cm])
            payment_table.setStyle(TableStyle([
                ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
                ('ALIGN', (1, 0), (1, -1), 'LEFT'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
            ]))
            
            elements.append(payment_table)
            elements.append(Spacer(1, 0.5*cm))
            
            # Create a table for bank details and UPI QR code side by side for better layout
            bank_upi_data = []
            
            # Bank details
            bank_name = self.db.get_setting("bank_name") or ""
            bank_account = self.db.get_setting("bank_account") or ""
            bank_ifsc = self.db.get_setting("bank_ifsc") or ""
            bank_branch = self.db.get_setting("bank_branch") or ""
            
            bank_details = [
                [Paragraph("Bank Details", styles["CustomHeading"])],
                [Paragraph(f"Bank: {bank_name}", styles["Normal"])],
                [Paragraph(f"Account: {bank_account}", styles["Normal"])],
                [Paragraph(f"IFSC: {bank_ifsc}", styles["Normal"])],
                [Paragraph(f"Branch: {bank_branch}", styles["Normal"])]
            ]
            
            bank_table = Table(bank_details, colWidths=[8*cm])
            bank_table.setStyle(TableStyle([
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ]))
            
            # UPI details
            upi_id = self.db.get_setting("upi_id") or ""
            upi_name = self.db.get_setting("upi_name") or ""
            
            # Generate QR code
            upi_string = f"upi://pay?pa={upi_id}&pn={upi_name}&am={invoice['total']:.2f}&cu=INR"
            
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=4,
            )
            qr.add_data(upi_string)
            qr.make(fit=True)
            
            qr_img = qr.make_image(fill_color="black", back_color="white")
            qr_buffer = io.BytesIO()
            qr_img.save(qr_buffer, format="PNG")
            qr_buffer.seek(0)
            
            qr_image = RLImage(qr_buffer, width=3*cm, height=3*cm)
            
            # Create UPI details without the "Click to Pay via UPI" text
            upi_details = [
                [Paragraph("UPI Payment", styles["CustomHeading"])],
                [qr_image],
                [Paragraph(f"UPI ID: {upi_id}", styles["Normal"])],
                [Paragraph(f"Name: {upi_name}", styles["Normal"])],
                [Paragraph(f"Amount: {invoice['total']:.2f}", styles["Normal"])]
            ]
            
            upi_table = Table(upi_details, colWidths=[8*cm])
            upi_table.setStyle(TableStyle([
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ]))
            
            # Add both tables to the main table
            bank_upi_data.append([bank_table, upi_table])
            
            bank_upi_table = Table(bank_upi_data, colWidths=[8*cm, 8*cm])
            bank_upi_table.setStyle(TableStyle([
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ]))
            
            elements.append(bank_upi_table)
            
            # Build PDF
            doc.build(elements)
            
            return file_path
        except Exception as e:
            print(f"Error generating invoice PDF: {e}")
            return None
    
    def generate_customer_ledger_pdf(self, customer_id, start_date, end_date, file_path=None):
        """Generate PDF for customer ledger"""
        try:
            # Get customer details
            customer = self.db.get_customer_by_id(customer_id)
            if not customer:
                return None
            
            # Get ledger entries
            entries = self.db.get_customer_ledger(customer_id, start_date, end_date)
            
            # Generate file path if not provided
            if not file_path:
                if not os.path.exists("ledgers"):
                    os.makedirs("ledgers")
                file_path = os.path.join("ledgers", f"Ledger_{customer['name']}_{start_date}_{end_date}.pdf")
            
            # Create PDF
            doc = SimpleDocTemplate(file_path, pagesize=A4)
            elements = []
            
            # Styles
            styles = getSampleStyleSheet()
            
            # Title
            title = Paragraph(f"Customer Ledger: {customer['name']}", styles['Heading1'])
            elements.append(title)
            elements.append(Spacer(1, 0.2*inch))
            
            # Period
            period = Paragraph(f"Period: {start_date} to {end_date}", styles['Normal'])
            elements.append(period)
            elements.append(Spacer(1, 0.3*inch))
            
            # Ledger table
            data = [["Date", "Description", "Debit", "Credit", "Balance"]]
            
            balance = 0
            for entry in entries:
                date = entry['date'].strftime("%d/%m/%Y")
                description = entry['description']
                debit = entry['debit'] if entry['debit'] > 0 else ""
                credit = entry['credit'] if entry['credit'] > 0 else ""
                balance += entry['debit'] - entry['credit']
                data.append([date, description, f"{debit:.2f}", f"{credit:.2f}", f"{balance:.2f}"])
            
            table = Table(data, colWidths=[3*cm, 8*cm, 3*cm, 3*cm, 3*cm])
            table.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (-1,0), colors.grey),
                ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
                ('ALIGN', (0,0), (-1,-1), 'CENTER'),
                ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
                ('FONTSIZE', (0,0), (-1,0), 14),
                ('BOTTOMPADDING', (0,0), (-1,0), 12),
                ('BACKGROUND', (0,1), (-1,-1), colors.beige),
                ('GRID', (0,0), (-1,-1), 1, colors.black)
            ]))
            
            elements.append(table)
            
            # Build PDF
            doc.build(elements)
            
            return file_path
        except Exception as e:
            print(f"Error generating customer ledger PDF: {e}")
            return None
    
    def generate_daily_ledger_pdf(self, date, file_path=None):
        """Generate PDF for daily ledger"""
        try:
            # Get daily data
            daily_data = self.db.get_daily_ledger(date)
            
            # Generate file path if not provided
            if not file_path:
                if not os.path.exists("daily_ledgers"):
                    os.makedirs("daily_ledgers")
                file_path = os.path.join("daily_ledgers", f"Daily_Ledger_{date}.pdf")
            
            # Create PDF
            doc = SimpleDocTemplate(file_path, pagesize=A4)
            elements = []
            
            # Styles
            styles = getSampleStyleSheet()
            
            # Title
            formatted_date = date.strftime("%d %B %Y")
            title = Paragraph(f"Daily Ledger - {formatted_date}", styles['Heading1'])
            elements.append(title)
            elements.append(Spacer(1, 0.2*inch))
            
            # Table
            data = [["S.No", "Customer", "Product", "Size", "SQ.FT", "Rate", "Amount"]]
            
            total_sqft = 0
            total_amount = 0
            s_no = 1
            for item in daily_data:
                customer = item['customer_name']
                product = item['product_name']
                size = f"{item['chargeable_height']}\" x {item['chargeable_width']}\""
                sqft = item['sqft']
                rate = item['rate']
                amount = item['amount']
                
                data.append([str(s_no), customer, product, size, f"{sqft:.2f}", f"{rate:.2f}", f"{amount:.2f}"])
                total_sqft += sqft
                total_amount += amount
                s_no += 1
            
            # Add total row
            data.append(["", "", "", "Total", f"{total_sqft:.2f}", "", f"{total_amount:.2f}"])
            
            table = Table(data, colWidths=[1.5*cm, 4*cm, 4*cm, 3*cm, 2*cm, 2*cm, 3*cm])
            table.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (-1,0), colors.grey),
                ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
                ('ALIGN', (0,0), (-1,-1), 'CENTER'),
                ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
                ('FONTSIZE', (0,0), (-1,0), 14),
                ('BOTTOMPADDING', (0,0), (-1,0), 12),
                ('BACKGROUND', (0,1), (-1,-2), colors.beige),
                ('GRID', (0,0), (-1,-1), 1, colors.black),
                ('BACKGROUND', (0,-1), (-1,-1), colors.lightgrey),
                ('FONTNAME', (0,-1), (-1,-1), 'Helvetica-Bold'),
            ]))
            
            elements.append(table)
            
            # Build PDF
            doc.build(elements)
            
            return file_path
        except Exception as e:
            print(f"Error generating daily ledger PDF: {e}")
            return None
    
    def generate_daily_ledger_pdf_by_date_range(self, start_date, end_date, file_path=None):
        """Generate PDF for daily ledger by date range"""
        try:
            # Get daily data
            daily_data = self.db.get_daily_ledger_by_date_range(start_date, end_date)
            
            # Generate file path if not provided
            if not file_path:
                if not os.path.exists("daily_ledgers"):
                    os.makedirs("daily_ledgers")
                file_path = os.path.join("daily_ledgers", f"Daily_Ledger_{start_date}_to_{end_date}.pdf")
            
            # Create PDF
            doc = SimpleDocTemplate(file_path, pagesize=A4)
            elements = []
            
            # Styles
            styles = getSampleStyleSheet()
            
            # Title
            title = Paragraph(f"Daily Ledger - {start_date} to {end_date}", styles['Heading1'])
            elements.append(title)
            elements.append(Spacer(1, 0.2*inch))
            
            # Create table for each date
            for date_str in sorted(daily_data.keys()):
                # Parse date
                year, month, day = date_str.split('-')
                date_obj = date(int(year), int(month), int(day))
                formatted_date = date_obj.strftime("%d %B %Y")
                
                # Date heading
                date_heading = Paragraph(f"Date: {formatted_date}", styles["Heading2"])
                elements.append(date_heading)
                elements.append(Spacer(1, 0.3*cm))
                
                # Table data
                table_data = [["S.No", "Height", "Width", "SQ.FT"]]
                
                total_sqft = 0
                for i, item in enumerate(daily_data[date_str], 1):
                    height = f"{item['actual_height']}\"" 
                    width = f"{item['actual_width']}\"" 
                    sqft = item["sqft"]
                    total_sqft += sqft
                    
                    table_data.append([
                        str(i),
                        height,
                        width,
                        f"{sqft:.2f}"
                    ])
                
                # Add total row
                table_data.append(["", "", "Total:", f"{total_sqft:.2f}"])
                
                # Create table
                table = Table(table_data, colWidths=[1.5*cm, 3*cm, 3*cm, 3*cm])
                table.setStyle(TableStyle([
                    ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
                    ('ALIGN', (0, 1), (-2, -2), 'CENTER'),
                    ('ALIGN', (-1, -1), (-1, -1), 'RIGHT'),
                    ('ALIGN', (0, -1), (-2, -1), 'RIGHT'),
                    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                    ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black)
                ]))
                
                elements.append(table)
                elements.append(Spacer(1, 0.5*cm))
            
            # Build PDF
            doc.build(elements)
            
            return file_path
            
        except Exception as e:
            print(f"Error generating ledger PDF: {e}")
            return None
    
    def open_pdf(self, file_path):
        """Open PDF file with default application"""
        try:
            if platform.system() == "Windows":
                os.startfile(file_path)
            elif platform.system() == "Darwin":  # macOS
                subprocess.call(["open", file_path])
            else:  # Linux
                subprocess.call(["xdg-open", file_path])
            return True
        except Exception as e:
            print(f"Error opening PDF: {e}")
            return False