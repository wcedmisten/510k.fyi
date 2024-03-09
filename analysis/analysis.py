import matplotlib.pyplot as plt
import networkx as nx
import sqlite3

con = sqlite3.connect("../scripts/devices.db")
cur = con.cursor()

cur.execute("SELECT node_from, node_to FROM predicate_graph_edge;")
all_edges = cur.fetchall()

# detect a cycle
g = nx.DiGraph(all_edges)

degrees = [g.degree(n) for n in g.nodes()]
plt.hist(degrees)
# plt.show()

print("Calculating longest path...")
longest_dag = nx.dag_longest_path(g)
print(len(longest_dag))
