import networkx as nx
import sqlite3
from Levenshtein import distance
import itertools

con = sqlite3.connect("devices.db")
cur = con.cursor()


def clean_extra_characters():
    """Remove extra newlines or # that may be in the data"""
    cur.execute("SELECT node_from, node_to FROM predicate_graph_edge;")
    all_edges = cur.fetchall()

    num_cleaned_chars = 0
    for edge in all_edges:
        new_node_from = edge[0].replace("\n", "").replace("#", "")
        new_node_to = edge[1].replace("\n", "").replace("#", "")
        if new_node_from != edge[0] or new_node_to != edge[1]:
            try:
                cur.execute(
                    "DELETE FROM predicate_graph_edge WHERE node_from = ? AND node_to = ?;",
                    edge,
                )
                cur.execute(
                    "INSERT INTO predicate_graph_edge VALUES(?, ?)",
                    [new_node_from, new_node_to],
                )
                num_cleaned_chars += 1
            except Exception:
                continue
    print(f"{num_cleaned_chars} edge characters cleaned")
    con.commit()


def delete_date_wrong_edges():
    """Deletes edges where the device is older than the predicate"""
    # find all the links where the device is older than the predicate
    cur.execute(
        "SELECT node_from, node_to FROM predicate_graph_edge JOIN device AS child_device ON child_device.k_number = node_to JOIN device AS parent_device ON parent_device.k_number = node_from WHERE parent_device.date_received > child_device.date_received;"
    )
    bad_edges = cur.fetchall()

    for edge in bad_edges:
        cur.execute(
            "DELETE FROM predicate_graph_edge WHERE node_from = ? AND node_to = ?;",
            edge,
        )

    print(f"Deleted {len(bad_edges)} bad date edges")
    con.commit()


def delete_cycle_edges():
    """Deletes all edges that are in a cycle"""
    cur.execute("SELECT node_from, node_to FROM predicate_graph_edge;")
    all_edges = cur.fetchall()

    # detect a cycle
    g = nx.DiGraph(all_edges)
    cycles = list(nx.simple_cycles(g))

    def flatten(matrix):
        return [item for row in matrix for item in row]

    cycle_edges_to_delete = flatten(
        map(lambda cycle: list(itertools.combinations(cycle, 2)), cycles)
    )

    # for cycle in cycles:
    #     print(list(itertools.combinations(cycle, 2)))

    # A lot of these cycles are caused by the FDA response letter
    # containing multiple K numbers, even though the application doesn't
    #
    # Can we detect the FDA response letter format to remove
    # these automatically?

    print(f"{len(cycle_edges_to_delete)} cycles found")

    for edge in cycle_edges_to_delete:
        cur.execute(
            "DELETE FROM predicate_graph_edge WHERE node_from = ? AND node_to = ?;",
            edge,
        )

    con.commit()


def delete_suspiciously_close_edges():
    """Deletes devices that are probably OCR mistakes
    TODO: actually delete them"""
    cur.execute("SELECT node_from, node_to FROM predicate_graph_edge;")
    all_edges = cur.fetchall()

    suspiciously_close_edges = [
        edge for edge in all_edges if distance(edge[0], edge[1]) == 1
    ]

    print(f"{len(suspiciously_close_edges)} edges with levenstein distance = 1")


def delete_nonexistent():
    """Deletes predicates that aren't in the database."""
    cur.execute(
        "SELECT node_from FROM predicate_graph_edge WHERE node_from NOT IN (SELECT k_number FROM device);"
    )
    nonexistent_devices = cur.fetchall()

    for edge in nonexistent_devices:
        cur.execute("DELETE FROM predicate_graph_edge WHERE node_from = ?;", [edge[0]])
    con.commit()

    print(f"{len(nonexistent_devices)} nonexistant devices deleted")


clean_extra_characters()
delete_date_wrong_edges()
delete_cycle_edges()
delete_nonexistent()
delete_suspiciously_close_edges()
