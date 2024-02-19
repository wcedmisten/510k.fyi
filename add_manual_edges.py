data = []
seen_files = set()

import sqlite3

con = sqlite3.connect("devices.db")
cur = con.cursor()

# read in the old data
with open("manually_added_links.csv", "r") as f:
    data = f.readlines()
    for line in data:
        (device, predicate) = line.strip().split(",")
        
        if (predicate != "S" and predicate != "predicate"):
            print(device, predicate)
            try:
                cur.execute("INSERT INTO predicate_graph_edge VALUES(?, ?)", (predicate, device))
                con.commit()
            except sqlite3.IntegrityError as e:
                print(e)
                continue
