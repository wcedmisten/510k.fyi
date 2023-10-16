import json

import sqlite3

con = sqlite3.connect("devices.db")
cur = con.cursor()

product_codes = set()
seen = set()

res = cur.execute("SELECT * FROM predicate_graph_edge")
edges = res.fetchall()

for parent, child in edges:
    if child not in seen:
        seen.add(child)

        res = cur.execute("SELECT * FROM device WHERE k_number = ?", (child,))
        row = res.fetchone()

        if not row:
            continue

        product_code = row[4]
        product_codes.add(product_code)


    if parent not in seen:
        seen.add(parent)

        res = cur.execute("SELECT * FROM device WHERE k_number = ?", (parent,))
        row = res.fetchone()

        if not row:
            continue

        product_code = row[4]
        product_codes.add(product_code)


d3_data = {"nodes": [], "links": []}

def get_predicates(k_number):
    res = cur.execute("SELECT * FROM predicate_graph_edge WHERE node_to = ?", (k_number,))
    edges = res.fetchall()

    return edges

product_descriptions = {}

def add_node(node):
    res = cur.execute("SELECT * FROM device WHERE k_number = ?", (node,))
    row = res.fetchone()

    if not row:
        raise Exception("Device not found.")

    product_code = row[4]
    generic_name = row[2]
    name = row[3]
    product_descriptions[product_code] = generic_name
    date = row[1]

    d3_data["nodes"].append({"id": node, "date": date, "product_code": product_code, "name": name})


seen = set()

for parent, child in edges:
    if child not in seen:
        add_node(child)
        seen.add(child)

    if parent not in seen:
        try:
            add_node(parent)
            seen.add(parent)
        except Exception as e:
            continue
    d3_data["links"].append({"source": parent, "target": child})

d3_data["product_descriptions"] = product_descriptions

with open("d3_fda_510k_graph.json", "w") as f:
    json.dump(d3_data, f)

