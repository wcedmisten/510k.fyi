import json

import sqlite3

con = sqlite3.connect("devices.db")
cur = con.cursor()

res = cur.execute("SELECT * FROM predicate_graph_edge ORDER BY node_to DESC")
edges = res.fetchall()

with open("predicates.csv", "w") as f:
    f.write("device,predicate\n")

    for edge in edges:
        # node_from,node_to
        node_from, node_to = edge

        f.write(node_to + "," + node_from + "\n")
