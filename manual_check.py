data = []
seen_files = set()

import re
import signal
import sqlite3
import subprocess
import os
import math

import argparse

con = sqlite3.connect("devices.db")
cur = con.cursor()


parser = argparse.ArgumentParser(
    prog="Manual PDF Check",
    description="Semi-automates predicate device data entry.",
    epilog="Stay cool kiddo",
)

parser.add_argument(
    "-l",
    "--local_pdfs",
    default=False,
    action=argparse.BooleanOptionalAction,
)
parser.add_argument(
    "-d",
    "--directory",
    default="/home/william/Downloads/fda-pdfs-ocr/scraper-combined",
    action="store",
)

parser.add_argument(
    "-r",
    "--reversed",
    default=False,
    action=argparse.BooleanOptionalAction,
)

args = parser.parse_args()

DOWNLOAD_PATH = args.directory

# read in the old data
with open("manually_added_links.csv", "r") as f:
    data = f.readlines()
    for line in data:
        target = line.split(",")[0]
        seen_files.add(target)


def good_input(input_str):
    return input_str == "F" or input_str == "S" or re.match("K\d{6}", input_str)


def process_pdf(k_number):
    filename = f"{DOWNLOAD_PATH}/{k_number}.pdf"
    if not os.path.isfile(filename) and args.local_pdfs:
        print("Could not find PDF, skipping.")
        data.append(f"{k_number},S\n")
        return

    if args.local_pdfs:
        process = subprocess.Popen(["evince", filename], shell=False)

    print("======================================")
    print(
        f"https://www.accessdata.fda.gov/scripts/cdrh/cfdocs/cfpmn/pmn.cfm?ID={k_number}"
    )
    print()

    res = cur.execute("SELECT * FROM device WHERE k_number = ?", [k_number])
    rows = res.fetchall()
    row = rows[0]

    print("Date received: ", row[1])
    print("Code: ",row[4])
    print("Name: ",row[3])

    print("======================================")

    prompt = f"Enter a predicate ID for {k_number}, or press F to finish inputting predicates for this device. Press S if no predicates can be found.\n"
    response = input(prompt)
    # F to finish entering predicates
    # S to skip entirely (no predicates found)
    while True:
        # fix bad OCR
        response = response.replace("O", "0").replace(" ", "")
        if good_input(response):
            if response == "F":
                if args.local_pdfs:
                    process.send_signal(signal.SIGTERM)
                    process.terminate()
                    process.kill()
                return
            if response == "S":
                data.append(f"{k_number},S\n")
                if args.local_pdfs:
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


with open("missing_predicates.txt", "r") as f:
    missing_edges = f.readlines()
    if args.reversed:
        missing_edges.reverse()

for edge in missing_edges:
    k_number = edge.strip()
    if k_number in seen_files:
        continue

    print(
        f"{len(seen_files)} / {len(missing_edges)} ({round(len(seen_files) / len(missing_edges) * 100, 5)}%) Completed"
    )
    nearest_tenth_percentage = (
        math.ceil(len(seen_files) / len(missing_edges) * 1000) / 10
    )
    to_nearest_tenth_percentage = len(missing_edges) * math.ceil(
        len(seen_files) / len(missing_edges) * 1000
    ) // 1000 - len(seen_files)
    print(f"{to_nearest_tenth_percentage} more files to {nearest_tenth_percentage}% 🎉")
    if to_nearest_tenth_percentage == 0:
        print("🎉🎉🎉🎉🎉🎉🎉🎉🎉")

    process_pdf(k_number)
    seen_files.add(k_number)

    with open("manually_added_links_new.csv", "w") as f:
        for line in data:
            f.write(line)
