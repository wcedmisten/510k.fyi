import datetime
from time import sleep
from bs4 import BeautifulSoup
import urllib3
import os
import shutil
import sqlite3
import pytz

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

min_scrape_time = 30
prev_time = datetime.datetime.now() - datetime.timedelta(seconds=30)

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
        if response.status == 403:
            print("Blocked from scraping!!!!")
            exit(1)

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
        global prev_time

        time = datetime.datetime.now()
        diff = (time - prev_time).total_seconds()

        if diff < min_scrape_time:
            print("sleeping ", min_scrape_time - diff)
            sleep(min_scrape_time - diff)

        if url:
            with http.request("GET", url, preload_content=False) as resp, open(
                pdf_filename, "wb"
            ) as out_file:
                prev_time = datetime.datetime.now()
                shutil.copyfileobj(resp, out_file)
            return pdf_filename
        else:
            return None

    return pdf_filename

seen = set()

tree = {}

res = cur.execute("SELECT k_number FROM device WHERE k_number NOT LIKE 'DEN%' AND statement_or_summary = 'Summary' AND date_received > '2022-12-06' ORDER BY date_received DESC LIMIT 1;")
rows = res.fetchall()

# from https://www.accessdata.fda.gov/robots.txt
visiting_hours_start = 23
visiting_hours_end = 5

for device in rows:
    current_hour = datetime.datetime.now(pytz.timezone('US/Eastern')).time().hour
    counter = 0
    
    while current_hour < visiting_hours_start and current_hour > visiting_hours_end:
        # sleep for 1 minute
        sleep(60)

        # print every hour
        if counter == 0:
            print(datetime.datetime.now(pytz.timezone('US/Eastern')).time(), "Still sleeping")
        counter = (counter + 1) % 60

        current_hour = datetime.datetime.now(pytz.timezone('US/Eastern')).time().hour

    print("Downloading " + device[0])
    download_device_pdf(device[0])

con.commit()
