import sqlite3

con = sqlite3.connect("devices.db")
cur = con.cursor()

res = cur.execute(
    "SELECT k_number FROM device WHERE statement_or_summary = 'Summary' AND k_number NOT IN (SELECT k_number FROM device JOIN predicate_graph_edge ON device.k_number = predicate_graph_edge.node_to) ORDER BY date_received DESC;"
)

missing_edges = res.fetchall()
with open("missing_predicates.txt", "w") as f:
    for device in missing_edges:
        k_number = device[0]
        f.write(k_number + "\n")
