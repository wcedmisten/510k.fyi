import ujson as json
import ijson
import uuid
import os

import psycopg2

POSTGRES_PASSWORD = os.environ["POSTGRES_PASSWORD"]

con = psycopg2.connect(
    dbname="postgres",
    user="postgres",
    password=POSTGRES_PASSWORD,
    host="database",
    port="5432",
)

cur = con.cursor()


def import_devices():
    print("Reading 510(k) JSON file")
    with open("/import_data/device-510k-0001-of-0001.json") as f:
        results = ijson.items(f, "results.item")

        print(f"Importing 510k data to database.")

        for device in results:
            # skip the DE NOVO devices
            if "DEN" not in device.get("k_number"):
                vals = (
                    device.get("k_number"),
                    device.get("date_received"),
                    device["openfda"].get("device_name"),
                    device.get("device_name"),
                    device.get("product_code"),
                    device.get("statement_or_summary"),
                )

                try:
                    cur.execute(
                        "INSERT INTO device VALUES(%s, %s, %s, %s, %s, %s) ON CONFLICT DO NOTHING",
                        vals,
                    )
                    con.commit()
                except Exception as e:
                    print(e)
                    print(vals)
                    con.rollback()
                    continue

        con.commit()


def import_recalls():
    print("Reading recalls JSON file")
    with open("/import_data/device-recall-0001-of-0001.json") as f:
        results = ijson.items(f, "results.item")

        print(f"Importing recall data to database.")

        for recall in results:
            id = recall.get("cfres_id")
            if not id:
                id = str(uuid.uuid4())

            vals = (
                id,
                recall.get("product_code"),
                recall.get("event_date_initiated"),
                recall.get("recall_status"),
                recall.get("reason_for_recall"),
            )

            try:
                cur.execute(
                    "INSERT INTO recall VALUES(%s, %s, %s, %s, %s) ON CONFLICT DO NOTHING",
                    vals,
                )

                for k_number in recall.get("k_numbers", []):
                    cur.execute(
                        "INSERT INTO device_recall VALUES(%s, %s) ON CONFLICT DO NOTHING",
                        (id, k_number),
                    )

                con.commit()
            except Exception as e:
                print(e)
                print(vals)
                con.rollback()
                continue

        con.commit()


def import_predicates():
    print("Importing predicates")
    with open("/import_data/predicates.csv") as f:
        for idx, line in enumerate(f.readlines()):
            # skip the header
            if idx == 0:
                continue

            # device,predicate
            device, predicate = line.split(",")
            device = device.strip()
            predicate = predicate.strip()

            try:
                cur.execute(
                    "INSERT INTO predicate_graph_edge VALUES(%s, %s)",
                    (predicate, device),
                )
                con.commit()
            except Exception as e:
                print(e)
                print((predicate, device))
                con.rollback()
