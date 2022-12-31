import graphviz

import json

import sqlite3

import matplotlib as plt
import numpy as np

con = sqlite3.connect("devices.db")
cur = con.cursor()

with open("tree.json") as f:
    tree = json.load(f)

g = graphviz.Digraph("G", filename="510k.gv")

product_codes = set()
seen = set()

for child, parents in tree.items():
    for parent in parents:
        if child not in seen:
            res = cur.execute("SELECT * FROM device WHERE k_number = ?", (child,))
            row = res.fetchone()

            product_code = row[4]
            product_codes.add(product_code)
            seen.add(child)

        if parent not in seen:
            res = cur.execute("SELECT * FROM device WHERE k_number = ?", (parent,))
            row = res.fetchone()

            product_code = row[4]
            product_codes.add(product_code)
            seen.add(parent)

print(product_codes)


cmap = plt.colormaps["Pastel1"]  # PiYG
colors = [plt.colors.rgb2hex(c) for c in cmap.colors]

color_mapping = {}


def get_color(product_code: str):
    if not product_code in color_mapping:
        new_color = colors[len(color_mapping)]
        color_mapping[product_code] = new_color

    return color_mapping[product_code]


def add_node(node):
    res = cur.execute("SELECT * FROM device WHERE k_number = ?", (node,))
    row = res.fetchone()

    product_code = row[4]
    date = row[1]

    g.node(
        node,
        label=f"{node}\n{date}",
        style="filled",
        fillcolor=get_color(product_code),
    )


seen = set()

for child, parents in tree.items():
    for parent in parents:
        if child not in seen:
            add_node(child)
            seen.add(child)

        if parent not in seen:
            add_node(parent)
            seen.add(parent)
        g.edge(parent, child)

for key, val in color_mapping.items():
    res = cur.execute("SELECT * FROM device WHERE product_code = ?", (key,))
    row = res.fetchone()
    generic_name = row[2].replace(",", ",\n")
    label = f"{key}\n{generic_name}"
    g.node(key, label=label, style="filled", fillcolor=val)

g.view()
