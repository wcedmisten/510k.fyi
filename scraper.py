from time import sleep
from bs4 import BeautifulSoup
import re
import urllib3
import os.path
from PyPDF2 import PdfReader
import shutil

http = urllib3.PoolManager()


def find_summary_pdf(device_id):
    pdf_filename = f"pdfs/{device_id}.pdf"
    if not os.path.isfile(pdf_filename):
        print("Checking website")
        url = f"https://www.accessdata.fda.gov/scripts/cdrh/cfdocs/cfpmn/pmn.cfm?ID={device_id}"
        response = http.request("GET", url)
        soup = BeautifulSoup(response.data, features="lxml")

        summary = soup.find("a", string="Summary")

        if not summary:
            print("Could not find a summary PDF:")
            print(url)
            return None
        else:
            return summary.attrs.get("href")

    return None


def download_device_pdf(device_id):
    pdf_filename = f"pdfs/{device_id}.pdf"
    if not os.path.isfile(pdf_filename):
        url = find_summary_pdf(device_id)
        if url:
            with http.request("GET", url, preload_content=False) as resp, open(
                pdf_filename, "wb"
            ) as out_file:
                shutil.copyfileobj(resp, out_file)
            return pdf_filename
        else:
            return None

    return pdf_filename


def get_pdf_text(pdf_filename):
    pdf_text = ""

    with open(pdf_filename, "rb") as f:
        pdf = PdfReader(f)

        for p in range(len(pdf.pages)):
            page = pdf.pages[p]
            pdf_text += page.extract_text()

    return pdf_text


# Import libraries
from tempfile import TemporaryDirectory
from pathlib import Path

import pytesseract
from pdf2image import convert_from_path
from PIL import Image


# https://www.geeksforgeeks.org/python-reading-contents-of-pdf-using-ocr-optical-character-recognition/
def get_ocr_text(pdf_filename):
    # Requires Python 3.6 or higher due to f-strings
    out_directory = Path("~").expanduser()

    # Path of the Input pdf
    PDF_file = Path(pdf_filename)

    # Store all the pages of the PDF in a variable
    image_file_list = []

    with TemporaryDirectory() as tempdir:
        # Create a temporary directory to hold our temporary images.

        pdf_pages = convert_from_path(PDF_file, 500)
        # Read in the PDF file at 500 DPI

        # Iterate through all the pages stored above
        for page_enumeration, page in enumerate(pdf_pages, start=1):
            # enumerate() "counts" the pages for us.

            # Create a file name to store the image
            filename = f"{tempdir}\page_{page_enumeration:03}.jpg"

            # Declaring filename for each page of PDF as JPG
            # For each page, filename will be:
            # PDF page 1 -> page_001.jpg
            # PDF page 2 -> page_002.jpg
            # PDF page 3 -> page_003.jpg
            # ....
            # PDF page n -> page_00n.jpg

            # Save the image of the page in system
            page.save(filename, "JPEG")
            image_file_list.append(filename)

        pdf_text = ""
        # Open the file in append mode so that
        # All contents of all images are added to the same file

        # Iterate from 1 to total number of pages
        for image_file in image_file_list:

            # Set filename to recognize text from
            # Again, these files will be:
            # page_1.jpg
            # page_2.jpg
            # ....
            # page_n.jpg

            # Recognize the text as string in image using pytesserct
            text = str(((pytesseract.image_to_string(Image.open(image_file)))))

            # The recognized text is stored in variable text
            # Any string processing may be applied on text
            # Here, basic formatting has been done:
            # In many PDFs, at line ending, if a word can't
            # be written fully, a 'hyphen' is added.
            # The rest of the word is written in the next line
            # Eg: This is a sample text this word here GeeksF-
            # orGeeks is half on first line, remaining on next.
            # To remove this, we replace every '-\n' to ''.
            text = text.replace("-\n", "")

            pdf_text += text

    return pdf_text


def find_predicate_ids(device_id):
    pdf_filename = download_device_pdf(device_id)

    if not pdf_filename:
        return []

    pdf_text = get_pdf_text(pdf_filename)

    if len(pdf_text) < 50:
        print("Scanned PDF found, using OCR instead")
        pdf_text = get_ocr_text(pdf_filename)

    # match = re.findall("[Pp]redicate [Dd]evice.*\n{0,5}.*[k|K|DEN]\d+", pdf_text)
    # print(match)
    match = re.findall("((?:k|K|DEN)\d{6})", pdf_text)
    print(match)
    if not match:
        print("No predicates found in ", pdf_filename)
        return []

    # match = re.search("[Pp]redicate [Dd]evice.*\n{0,5}.*([k|K|DEN]\d+).*", pdf_text)
    predicates = list(set(match) - set([device_id]))

    print("predicates: ", predicates)
    return predicates


seen = set()
device_ids = ["K211954"]

tree = {}

while device_ids:
    id = device_ids.pop()
    if id not in seen:
        seen.add(id)
        print(id)

        predicates = find_predicate_ids(id)
        tree[id] = predicates
        device_ids.extend(predicates)
        sleep(0.3)

import json

with open("tree.json", "w") as f:
    json.dump(tree, f)
