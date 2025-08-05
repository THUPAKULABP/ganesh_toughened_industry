import os
import subprocess
import platform
from datetime import datetime, date, timedelta
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.units import inch, cm
from reportlab.lib.colors import HexColor
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.lib import colors
from PIL import Image
import io
import qrcode

class PDFGenerator:
    """PDF generation utilities for the application"""
    
    def __init__(self, db):
        """Initialize with database connection"""
        self.db = db
    
    def generate_invoice_pdf(self, invoice_id, file_path=None):
        """Generate PDF for an invoice"""
        try:
            # Get invoice details
            invoice, items = self.db.get_invoice_by_id(invoice_id)
            
            if not invoice:
                return None
            
            # Generate file path if not provided
            if not file_path:
                file_path = f"Invoice_{invoice['invoice_number']}.pdf"
            
            # Create PDF
            doc = SimpleDocTemplate(file_path, pagesize=A4)
            elements = []
            
            # Get styles
            styles = getSampleStyleSheet()
            
            # Company details
            company_name = self.db.get_setting("company_name") or "GANESH TOUGHENED INDUSTRY"
            company_address = self.db.get_setting("company_address") or "Plot no:B13, Industrial Estate, Madanapalli"
            company_phone = self.db.get_setting("company_phone") or "9398530499, 7013374872"
            company_gst = self.db.get_setting("company_gst") or "37EXFPK2395CIZE"
            
            # Company header
            company_data = [
                [Paragraph(f"<b>{company_name}</b>", styles["Heading1"])],
                [Paragraph(company_address, styles["Normal"])],
                [Paragraph(f"Phone: {company_phone}", styles["Normal"])],
                [Paragraph(f"GST: {company_gst}", styles["Normal"])]
            ]
            
            company_table = Table(company_data, colWidths=[16*cm])
            company_table.setStyle(TableStyle([
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
            ]))
            
            elements.append(company_table)
            elements.append(Spacer(1, 0.5*cm))
            
            # Invoice title
            invoice_title = Paragraph("<b>INVOICE</b>", styles["Heading2"])
            elements.append(invoice_title)
            elements.append(Spacer(1, 0.3*cm))
            
            # Invoice details
            invoice_data = [
                ["Invoice #:", invoice["invoice_number"]],
                ["Date:", invoice["date"]],
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
                ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ]))
            
            elements.append(invoice_table)
            elements.append(Spacer(1, 0.5*cm))
            
            # Items table
            items_data = [["S.No", "Product", "Actual Size", "Chargeable Size", "SQ.FT", "Rate", "Qty", "Amount"]]
            
            for i, item in enumerate(items, 1):
                actual_size = f"{item['actual_height']}\" x {item['actual_width']}\""
                chargeable_size = f"{item['chargeable_height']}\" x {item['chargeable_width']}\""
                
                items_data.append([
                    str(i),
                    item["product_name"],
                    actual_size,
                    chargeable_size,
                    f"{item['sqft']:.2f}",
                    f"{item['rate']:.2f}",
                    str(item["quantity"]),
                    f"{item['amount']:.2f}"
                ])
            
            items_table = Table(items_data, colWidths=[1*cm, 4*cm, 2.5*cm, 2.5*cm, 1.5*cm, 1.5*cm, 1*cm, 2*cm])
            items_table.setStyle(TableStyle([
                ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
                ('ALIGN', (0, 1), (-1, -1), 'CENTER'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            
            elements.append(items_table)
            elements.append(Spacer(1, 0.5*cm))
            
            # Summary table
            subtotal = invoice["subtotal"]
            extra_charges = invoice["extra_charges"]
            round_off = invoice["round_off"]
            total = invoice["total"]
            
            summary_data = [
                ["Subtotal:", f"{subtotal:.2f}"],
                ["Extra Charges:", f"{extra_charges:.2f}"],
                ["Round Off:", f"{round_off:.2f}"],
                ["<b>Gross Total:</b>", f"<b>{total:.2f}</b>"]
            ]
            
            summary_table = Table(summary_data, colWidths=[13*cm, 3*cm])
            summary_table.setStyle(TableStyle([
                ('ALIGN', (0, 0), (-2, -2), 'RIGHT'),
                ('ALIGN', (1, 0), (-1, -2), 'RIGHT'),
                ('ALIGN', (0, -1), (-1, -1), 'RIGHT'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                ('LINEBELOW', (0, -1), (-1, -1), 1, colors.black),
                ('FONT', (0, -1), (-1, -1), 'Helvetica-Bold'),
            ]))
            
            elements.append(summary_table)
            elements.append(Spacer(1, 0.5*cm))
            
            # Payment details
            payment_mode = invoice["payment_mode"] or ""
            ppay_no = invoice["p_pay_no"] or ""
            
            payment_data = [
                ["Payment Mode:", payment_mode],
                ["P-PAY No.:", ppay_no]
            ]
            
            payment_table = Table(payment_data, colWidths=[4*cm, 12*cm])
            payment_table.setStyle(TableStyle([
                ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
                ('ALIGN', (1, 0), (1, -1), 'LEFT'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ]))
            
            elements.append(payment_table)
            elements.append(Spacer(1, 0.5*cm))
            
            # Bank details
            bank_name = self.db.get_setting("bank_name") or ""
            bank_account = self.db.get_setting("bank_account") or ""
            bank_ifsc = self.db.get_setting("bank_ifsc") or ""
            bank_branch = self.db.get_setting("bank_branch") or ""
            
            bank_data = [
                ["Bank Details:"],
                [f"Bank: {bank_name}"],
                [f"Account: {bank_account}"],
                [f"IFSC: {bank_ifsc}"],
                [f"Branch: {bank_branch}"]
            ]
            
            bank_table = Table(bank_data, colWidths=[16*cm])
            bank_table.setStyle(TableStyle([
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ]))
            
            elements.append(bank_table)
            elements.append(Spacer(1, 0.5*cm))
            
            # UPI details
            upi_id = self.db.get_setting("upi_id") or ""
            upi_name = self.db.get_setting("upi_name") or ""
            
            # Generate UPI QR code
            try:
                qr_img = self.generate_upi_qr(upi_id, upi_name, total)
                elements.append(qr_img)
            except Exception as e:
                print(f"Error generating UPI QR: {e}")
            
            # Build PDF
            doc.build(elements)
            
            return file_path
            
        except Exception as e:
            print(f"Error generating invoice PDF: {e}")
            return None
    
    def generate_upi_qr(self, upi_id, upi_name, amount):
        """Generate UPI QR code for payment"""
        try:
            # Create UPI payment string
            upi_string = f"upi://pay?pa={upi_id}&pn={upi_name}&am={amount}&cu=INR"
            
            # Generate QR code
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=4,
            )
            qr.add_data(upi_string)
            qr.make(fit=True)
            
            # Create an image from the QR Code
            img = qr.make_image(fill_color="black", back_color="white")
            
            # Convert to ReportLab Image
            img_byte_arr = io.BytesIO()
            img.save(img_byte_arr, format='PNG')
            img_byte_arr = img_byte_arr.getvalue()
            
            # Create ReportLab Image
            from reportlab.lib.utils import ImageReader
            qr_image = ImageReader(io.BytesIO(img_byte_arr))
            
            # Create a table with the QR code
            qr_table = Table([[qr_image]], colWidths=[3*cm])
            qr_table.setStyle(TableStyle([
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ]))
            
            return qr_table
            
        except Exception as e:
            print(f"Error generating UPI QR: {e}")
            return None
    
    def generate_ledger_pdf(self, from_date, to_date, file_path=None):
        """Generate PDF for daily ledger"""
        try:
            # Get ledger data
            ledger_data = self.db.get_daily_ledger(from_date, to_date)
            
            if not ledger_data:
                return None
            
            # Generate file path if not provided
            if not file_path:
                file_path = f"Daily_Ledger_{from_date.strftime('%d_%m_%Y')}_to_{to_date.strftime('%d_%m_%Y')}.pdf"
            
            # Create PDF
            doc = SimpleDocTemplate(file_path, pagesize=A4)
            elements = []
            
            # Get styles
            styles = getSampleStyleSheet()
            
            # Title
            title = Paragraph("<b>DAILY LEDGER</b>", styles["Heading1"])
            elements.append(title)
            elements.append(Spacer(1, 0.5*cm))
            
            # Date range
            date_range = f"From: {from_date.strftime('%d/%m/%Y')} To: {to_date.strftime('%d/%m/%Y')}"
            date_para = Paragraph(date_range, styles["Normal"])
            elements.append(date_para)
            elements.append(Spacer(1, 0.5*cm))
            
            # Group by date
            daily_data = {}
            for item in ledger_data:
                date_str = item["date"]
                if date_str not in daily_data:
                    daily_data[date_str] = []
                daily_data[date_str].append(item)
            
            # Create table for each date
            for date_str in sorted(daily_data.keys()):
                # Parse date
                day, month, year = date_str.split('-')
                date_obj = date(int(year), int(month), int(day))
                formatted_date = date_obj.strftime("%d %B %Y")
                
                # Date heading
                date_heading = Paragraph(f"<b>Date: {formatted_date}</b>", styles["Heading2"])
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
                    ('BACKGROUND', (0, 1), (-1, -2), colors.beige),
                    ('BACKGROUND', (0, -1), (-1, -1), colors.lightgrey),
                    ('FONT', (0, -1), (-1, -1), 'Helvetica-Bold'),
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