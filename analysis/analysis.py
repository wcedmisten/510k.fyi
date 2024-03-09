import seaborn as sns
import networkx as nx
import sqlite3
import pandas as pd
import matplotlib.pyplot as plt

import statistics

con = sqlite3.connect("../scripts/devices.db")
cur = con.cursor()

cur.execute("SELECT node_from, node_to FROM predicate_graph_edge;")
all_edges = cur.fetchall()

g = nx.DiGraph(all_edges)

# avg degree
print("Average degree:")
print(sum(map(lambda x: x[1], g.in_degree())) / len(g))

# longest path

print("Calculating longest path:")
longest_dag = nx.dag_longest_path(g)
print(len(longest_dag))

# median 
print("Median degree")
print(statistics.median(map(lambda x: x[1], g.in_degree())))

# degree histogram

degrees = [g.in_degree(n) for n in g.nodes()]

data = pd.DataFrame(degrees)

fig, ax1 = plt.subplots()

hist = sns.histplot(data=data, log_scale=True, legend=None)

ax1.set_title("Histogram of Node Degrees", fontsize=18)
ax1.set_xlabel("Degree", fontsize=18)
ax1.set_ylabel("Count", fontsize=18)

plt.show()
