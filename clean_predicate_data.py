data = []
seen_files = set()

import sqlite3

con = sqlite3.connect("devices.db")
cur = con.cursor()

# find all the links where the device is older than the predicate
cur.execute("SELECT node_from, node_to FROM predicate_graph_edge JOIN device AS child_device ON child_device.k_number = node_to JOIN device AS parent_device ON parent_device.k_number = node_from WHERE parent_device.date_received > child_device.date_received;")
bad_edges = cur.fetchall()

print(bad_edges)
for edge in bad_edges:
    cur.execute("DELETE FROM predicate_graph_edge WHERE node_from = ? AND node_to = ?;", edge)

con.commit()

# cur.commit()
