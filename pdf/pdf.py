import os
print("Current Working Directory:", os.getcwd())
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

with open("sample.pdf", "rb") as fh:
    for page in PDFPage.get_pages(fh, caching=True, check_extractable=True):
        page_interpreter.process_page(page)

    text = fake_file_handle.getvalue()

# Now you can process the extracted text
print(text)


# text = extract_text("sample.pdf")
# print(text)

# pattern = re.compile(r"[a-zA-Z]+,{1}\s{1}")
# matches = pattern.findall(text)
# names = [n[:-2] for n in matches]
# print(names)