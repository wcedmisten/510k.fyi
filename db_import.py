import ujson as json
import sqlite3

con = sqlite3.connect("devices.db")

cur = con.cursor()
cur.execute(
    "CREATE TABLE device(k_number TEXT, date_received TEXT, generic_name TEXT, device_name TEXT, product_code TEXT);"
)

from progress.bar import Bar


print("Reading JSON file")
with open("device-510k-0001-of-0001.json") as f:
    data = json.load(f)

    bar = Bar("Importing data to sqlite", max=len(data["results"]))

    for device in data["results"]:
        bar.next()
        vals = (
            device.get("k_number"),
            device.get("date_received"),
            device["openfda"].get("device_name"),
            device.get("device_name"),
            device.get("product_code"),
        )

        cur.execute("INSERT INTO device VALUES(?, ?, ?, ?, ?)", vals)

    con.commit()

print()
