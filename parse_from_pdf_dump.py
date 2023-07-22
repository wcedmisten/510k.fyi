from time import sleep
import re
import urllib3
import os
from PyPDF2 import PdfReader
import sqlite3


PATH_TO_PDFS = "/home/wcedmisten/Downloads/fda-pdfs-ocr/scraper-combined"
# PATH_TO_PDFS = "/home/wcedmisten/Downloads/test-pdfs"


http = urllib3.PoolManager()

con = sqlite3.connect("devices.db")
cur = con.cursor()

def get_pdf_path(device_id):
    pdf_filename = f"{PATH_TO_PDFS}/{device_id}.pdf"
    if not os.path.isfile(pdf_filename):
        return None

    return pdf_filename


def get_pdf_text(pdf_filename):
    pdf_text = ""

    with open(pdf_filename, "rb") as f:
        try:
            pdf = PdfReader(f)

            for p in range(len(pdf.pages)):
                page = pdf.pages[p]
                try:
                    pdf_text += page.extract_text()
                except Exception as e:
                    print("Could not parse PDF page")
                    print(e)
        except Exception as e:
            print("Could not open PDF file")
            print(e)

    return pdf_text


# Import libraries
from tempfile import TemporaryDirectory
from pathlib import Path

import pytesseract
from pdf2image import convert_from_path
from PIL import Image


# https://www.geeksforgeeks.org/python-reading-contents-of-pdf-using-ocr-optical-character-recognition/
def get_ocr_text(pdf_filename):
    # Path of the Input pdf
    PDF_file = Path(pdf_filename)

    text_filename = f"{pdf_filename}.txt"
    if os.path.isfile(text_filename):
        print("File already exists, skipping OCR")
        with open(text_filename, "r", encoding="utf-8") as f:
            return f.read()

    # Store all the pages of the PDF in a variable
    image_file_list = []

    pdf_text = ""

    with TemporaryDirectory() as tempdir:
        # Create a temporary directory to hold our temporary images.

        try:
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

            with open(text_filename, "w", encoding="utf-8") as f:
                f.write(pdf_text)
        except Exception as e:
            print("Could not OCR file")
            print(e)

    return pdf_text


needs_ocr = []

# allow the two most common OCR fails: subbing 0 for O and random spaces in the ID
k_number_regex = "((?:k|K|DEN)[0-9O]\s?[0-9O]\s?[0-9O]\s?[0-9O]\s?[0-9O]\s?[0-9O])"

def find_predicate_ids(device_id):
    pdf_filename = get_pdf_path(device_id)

    if not pdf_filename:
        return []

    pdf_text = get_pdf_text(pdf_filename)

    # match = re.findall("[Pp]redicate [Dd]evice.*\n{0,5}.*[k|K|DEN]\d+", pdf_text)
    # print(match)
    match = re.findall(k_number_regex, pdf_text)
    if not match:
        # hack for running on droplet where OCR doesn't work
        print("No predicates found in ", pdf_filename)
        pdf_text = get_ocr_text(pdf_filename) # TODO: remove this once OCR is tested
        needs_ocr.append(device_id)

    # clean up the bad OCR
    match = [k.replace(" ", "").replace("O", "0").upper() for k in match]
    predicates = list(set(match) - set([device_id]))

    print("predicates: ", predicates)
    return predicates

res = cur.execute("SELECT k_number FROM device WHERE k_number NOT LIKE 'DEN%' AND statement_or_summary = 'Summary' ORDER BY date_received DESC;")
rows = res.fetchall()
count = 0
for device_id in [row[0] for row in rows]:
    print(device_id)
    # skip the non-OCR files
    if not os.path.isfile(f"{PATH_TO_PDFS}/{device_id}.pdf.txt"):
        continue
    count += 1

    # print(count, " / ", len(rows))

    predicates = find_predicate_ids(device_id)

    # add the predicate links to the database
    for predicate in predicates:
        # from, to
        vals = (predicate, device_id)
        try:
            cur.execute("INSERT INTO predicate_graph_edge VALUES(?, ?)", vals)
            con.commit()
        except Exception as e:
            None

print(f"Running OCR for {len(needs_ocr)} files")
count = 0
for device_id in needs_ocr:
    print(count, " / ", len(needs_ocr))
    count += 1
    pdf_filename = get_pdf_path(device_id)

    if not pdf_filename:
        continue
    
    print("Running OCR")
    pdf_text = get_ocr_text(pdf_filename)

    match = re.findall(k_number_regex, pdf_text)
    # clean up the bad OCR
    match = [k.replace(" ", "").replace("O", "0").upper() for k in match]
    print(match)
    if not match:
        continue

    predicates = list(set(match) - set([device_id]))

    print("predicates: ", predicates)
    # add the predicate links to the database
    for predicate in predicates:
        # from, to
        vals = (predicate, device_id)
        try:
            cur.execute("INSERT INTO predicate_graph_edge VALUES(?, ?)", vals)
            con.commit()
        except Exception as e:
            print(e)

con.commit()
