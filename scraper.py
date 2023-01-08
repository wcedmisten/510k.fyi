import datetime
from time import sleep
from bs4 import BeautifulSoup
import re
import urllib3
import os
from PyPDF2 import PdfReader
import shutil
import sqlite3

http = urllib3.PoolManager()

con = sqlite3.connect("devices.db")
cur = con.cursor()

seen_con = sqlite3.connect("seen.db")
seen_cursor = seen_con.cursor()

seen_cursor.execute(
    "CREATE TABLE IF NOT EXISTS missing_summaries("
    "k_number TEXT PRIMARY KEY);"
)

if not os.path.exists("pdfs"):
    os.makedirs("pdfs")

min_scrape_time = 5
prev_time = datetime.datetime.now()

def find_summary_pdf(device_id):
    pdf_filename = f"pdfs/{device_id}.pdf"
    if not os.path.isfile(pdf_filename):
        print("Checking database")
        res = cur.execute("SELECT * FROM device WHERE k_number = ?", (device_id,))
        row = res.fetchone()
        if not row:
            print("No device found in the database")
            return None

        if row[5] != "Summary":
            print(row[5])
            print("No summary is available")
            return None

        res = seen_cursor.execute("SELECT * FROM missing_summaries WHERE k_number = ?", (device_id,))
        seen_row = res.fetchone()

        # track the missing summaries
        if seen_row:
            print("Previously known to have no summary")
            return None

        global prev_time, min_scrape_time

        time = datetime.datetime.now()
        diff = (time - prev_time).total_seconds()

        if diff < min_scrape_time:
            print("sleeping ", min_scrape_time - diff)
            sleep(min_scrape_time - diff)

        url = f"https://www.accessdata.fda.gov/scripts/cdrh/cfdocs/cfpmn/pmn.cfm?ID={device_id}"
        response = http.request("GET", url)
        soup = BeautifulSoup(response.data, features="html.parser")

        prev_time = datetime.datetime.now()

        summary = soup.find("a", string="Summary")

        if not summary:
            print("Could not find a summary PDF:")
            seen_cursor.execute("INSERT INTO missing_summaries VALUES(?)", (device_id,))
            seen_con.commit()
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
    # Path of the Input pdf
    PDF_file = Path(pdf_filename)

    text_filename = f"{pdf_filename}.txt"
    if os.path.isfile(text_filename):
        print("File already exists, skipping OCR")
        with open(text_filename, "r", encoding="utf-8") as f:
            return f.read()

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

    with open(text_filename, "w", encoding="utf-8") as f:
        f.write(pdf_text)

    return pdf_text


def find_predicate_ids(device_id):
    pdf_filename = download_device_pdf(device_id)

    if not pdf_filename:
        return []

    pdf_text = get_pdf_text(pdf_filename)

    # match = re.findall("[Pp]redicate [Dd]evice.*\n{0,5}.*[k|K|DEN]\d+", pdf_text)
    # print(match)
    match = re.findall("((?:k|K|DEN)\d{6})", pdf_text)
    if not match:
        print("No predicates found in ", pdf_filename)

        print("Running OCR")
        pdf_text = get_ocr_text(pdf_filename)

        match = re.findall("((?:k|K|DEN)\d{6})", pdf_text)
        print(match)
        if not match:
            return []

    # match = re.search("[Pp]redicate [Dd]evice.*\n{0,5}.*([k|K|DEN]\d+).*", pdf_text)
    predicates = list(set(match) - set([device_id]))

    print("predicates: ", predicates)
    return predicates


seen = set()

tree = {}

res = cur.execute("SELECT k_number FROM device WHERE k_number NOT LIKE 'DEN%' LIMIT 10 OFFSET 10000;")
rows = res.fetchall()

for row in rows:
    prev_time = datetime.datetime.now()
    
    id = row[0]
    print(id)

    # skip for now
    if "DEN" in id:
        continue

    predicates = find_predicate_ids(id)
    tree[id] = predicates

    for predicate in predicates:
        # from, to
        vals = (predicate, id)
        try:
            cur.execute("INSERT INTO predicate_graph_edge VALUES(?, ?)", vals)
        except sqlite3.IntegrityError:
            None

con.commit()
