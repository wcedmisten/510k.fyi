from time import sleep
from fastapi import FastAPI
import psycopg2
from pydantic import BaseModel
import os

import sqlite3

POSTGRES_PASSWORD = os.environ["POSTGRES_PASSWORD"]

con = psycopg2.connect(
    dbname="postgres",
    user="postgres",
    password=POSTGRES_PASSWORD,
    host="database",
    port="5432",
)

cur = con.cursor()

def get_ancestors(device_id):
    with sqlite3.connect("./devices.db") as con:
        cur = con.cursor()
        return cur.execute(
            """WITH RECURSIVE ancestor(n)
            AS (
                VALUES(?)
                UNION ALL
                SELECT node_from FROM predicate_graph_edge, ancestor
                WHERE predicate_graph_edge.node_to=ancestor.n
            )
            SELECT k_number, date_received, generic_name, device_name, product_code, node_to, node_from
            FROM predicate_graph_edge
            JOIN device ON node_from = device.k_number
            WHERE predicate_graph_edge.node_to IN ancestor;""",
            [device_id],
        ).fetchall()


def get_device(device_id):
    with sqlite3.connect("./devices.db") as con:
        cur = con.cursor()
        return cur.execute(
            """SELECT k_number, date_received, device_name, product_code FROM device WHERE k_number = ?""",
            [device_id],
        ).fetchall()[0]


def format_row(row):
    return {
        "k_number": row[0],
        "date_received": row[1],
        "generic_name": row[2],
        "device_name": row[3],
        "product_code": row[4],
        "node_to": row[5],
        "node_from": row[6],
    }


def format_node(row):
    return {
        "id": row["k_number"],
        "date": row["date_received"],
        "product_code": row["product_code"],
        "name": row["device_name"],
    }


def format_edge(row):
    return {"source": row["node_from"], "target": row["node_to"]}

async def get_ancestry_graph(device_id):
    ancestors = get_ancestors(device_id)
    device = get_device(device_id)
    res = list(map(format_row, ancestors))

    edges = list(map(format_edge, res))
    nodes = list(map(format_node, res))

    unique_nodes = []
    seen_nodes = set()

    all_nodes = set(map(lambda x: x["id"], nodes))

    names = {}

    # assert names are the same for the same ID
    for node in res:
        if node["k_number"] in names:
            assert node["device_name"] == names[node["k_number"]]
        names[node["k_number"]] = node["device_name"]

        assert node["k_number"] == node["node_from"]

    for node in nodes:
        if not node["id"] in seen_nodes:
            unique_nodes.append(node)

        seen_nodes.add(node["id"])

    unique_nodes.append({
        # k_number, date_received, device_name, product_code
        "id": device[0],
        "date": device[1],
        "name": device[2],
        "product_code": device[3]
    })

    product_descriptions = {}

    for row in res:
        product_descriptions[row["product_code"]] = row["generic_name"]

    return {
        "nodes": unique_nodes,
        "links": edges,
        "product_descriptions": product_descriptions,
    }

def format_row_search(row):
    return {
        "k_number": row[0],
        "date_received": row[1],
        "device_name": row[2],
        "product_code": row[3],
    }

async def device_search(query):
    rows = []
    with sqlite3.connect("./devices.db") as con:
        cur = con.cursor()
        rows = cur.execute(
            """SELECT k_number, date_received, device_name, product_code FROM device WHERE k_number LIKE ? OR device_name LIKE ? ORDER BY date_received DESC""",
            ["%" + query + "%", "%" + query + "%"],
        ).fetchall()

    return list(map(format_node, map(format_row_search, rows)))

# DB model
class Test(BaseModel):
    field_1: str

app = FastAPI()

@app.get("/ancestry/{device_number}") # , response_model=list[Test]
async def read_user_details(device_number):
    return await get_ancestry_graph(device_number)

@app.get("/search")
async def put_user_details(query):
    return await device_search(query)
