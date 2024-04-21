import re
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.pdfpage import PDFPage
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from io import StringIO

resource_manager = PDFResourceManager()
fake_file_handle = StringIO()
converter = TextConverter(resource_manager, fake_file_handle, laparams=LAParams())
page_interpreter = PDFPageInterpreter(resource_manager, converter)

with open("pdf/sample.pdf", "rb") as fh:
    for page in PDFPage.get_pages(fh, caching=True, check_extractable=True):
        page_interpreter.process_page(page)

    text = fake_file_handle.getvalue()

# print(text)

# Define regular expressions for invoice value, sender information, and invoice number
invoice_value_pattern = re.compile(r"Amount Paid\s*\n\s*\$([0-9,]+(?:\.\d{1,2})?)", re.MULTILINE)
sender_pattern = re.compile(r"Plan Partners Pty Ltd[\s\S]+?SAWAYA TRANSPORT SERVICES PTY[\s\S]+?Email:\s*([^@]+@[^@]+\.[^@]+)", re.MULTILINE)
invoice_number_pattern = re.compile(r"Invoice Number\s*\n\s*([^ ]+)")

# Search for patterns in the extracted text
invoice_value_match = invoice_value_pattern.search(text)
sender_match = sender_pattern.search(text)
invoice_number_match = invoice_number_pattern.search(text)

# Extract information
invoice_value = invoice_value_match.group(1) if invoice_value_match else "Not found"
sender = sender_match.group(1) if sender_match else "Not found"
invoice_number = invoice_number_match.group(1) if invoice_number_match else "Not found"

# Print extracted information
print("Invoice Value:", invoice_value)
print("Sender:", sender)
print("Invoice Number:", invoice_number)