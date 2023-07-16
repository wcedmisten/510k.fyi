data = []
seen_files = set()

import re
import signal
import sqlite3
import subprocess
import os
from PyPDF2 import PdfReader

con = sqlite3.connect("devices.db")
cur = con.cursor()

with open("manually_added_links.csv", "r") as f:
    data = f.readlines()
    for line in data:
        target = line.split(",")[0]
        seen_files.add(target)


res = cur.execute("SELECT k_number FROM device WHERE statement_or_summary = 'Summary' AND k_number NOT IN (SELECT k_number FROM device JOIN predicate_graph_edge ON device.k_number = predicate_graph_edge.node_to);")
missing_edges = res.fetchall()

DOWNLOAD_PATH = "/home/wcedmisten/Downloads/fda-pdfs-ocr/scraper-combined"

def good_input(input_str):
    return input_str == "F" or input_str == "S" or re.match("K\d{6}", input_str)

def check_for_predicate_description(filename):
    if os.path.isfile(filename + ".txt"):
        print(f"cat {filename}.txt | grep -i -e equivalent -e predicate -e equivalence -e equivalency -A 5")
        with open (filename + ".txt", "r") as f:
            lines = f.read()
            if "equivalent" in lines or "predicate" in lines or "equivalence" in lines or "equivalency" in lines:
                print("✅ Found predicate description")
                return
    else:
        print(f"cat {filename} | grep -i -e equivalent -e predicate -e equivalence -e equivalency -A 5")

        try:
            with open(filename, "rb") as f:
                pdf = PdfReader(f)

                for p in range(len(pdf.pages)):
                    page = pdf.pages[p]
                    try:
                        lines= page.extract_text()
                        if "equivalent" in lines or "predicate" in lines or "equivalence" in lines or "equivalency" in lines:
                            return
                    except Exception as e:
                        print("Could not parse PDF page")
                        print(e)

        except Exception as e:
            print("Could not open PDF file")

def process_pdf(k_number):
    filename = f"{DOWNLOAD_PATH}/{k_number}.pdf"
    if not os.path.isfile(filename):
        print("Could not find PDF, skipping.")
        data.append(f"{k_number},S\n")
        return

    process = subprocess.Popen(["evince", filename], shell=False)

    check_for_predicate_description(filename)

    print(f"https://www.accessdata.fda.gov/scripts/cdrh/cfdocs/cfpmn/pmn.cfm?ID={k_number}")
    print()

    prompt = f"Enter a predicate ID for {k_number}, or press F to finish inputting predicates for this device. Press S if no predicates can be found.\n"
    response = input(prompt)
    # F to finish entering predicates
    # S to skip entirely (no predicates found)
    while True:
        # fix bad OCR
        response = response.replace("O", "0").replace(" ", "")
        if good_input(response):
            if response == "F":
                process.send_signal(signal.SIGTERM)
                process.terminate()
                process.kill()
                return
            if response == "S":
                data.append(f"{k_number},S\n")
                process.send_signal(signal.SIGTERM)
                process.terminate()
                process.kill()
                return
            elif re.match("K\d{6}", response):
                data.append(f"{k_number},{response}\n")
                response = input(prompt)
        else:
            print("Unexpected response, try again.")
            response = input(prompt)

for edge in missing_edges:
    k_number = edge[0]
    if k_number in seen_files:
        continue
    process_pdf(k_number)
    seen_files.add(k_number)

    print(f"{len(seen_files)} / {len(missing_edges)} Completed")

    with open("manually_added_links_new.csv", "w") as f:
        for line in data:
            f.write(line)
