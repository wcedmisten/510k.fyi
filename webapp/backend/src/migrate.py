import os
import psycopg2

POSTGRES_PASSWORD = os.environ["POSTGRES_PASSWORD"]

con = psycopg2.connect(
    dbname="postgres",
    user="postgres",
    password=POSTGRES_PASSWORD,
    host="database",
    port="5432",
)

cur = con.cursor()


# home grown DB migrations these should be IDEMPOTENT statements
# these statements will be run before the database starts up
migrations = [
    "CREATE TABLE IF NOT EXISTS device("
    "k_number TEXT PRIMARY KEY,"
    "date_received TEXT,"
    "generic_name TEXT,"
    "device_name TEXT,"
    "product_code TEXT,"
    "statement_or_summary TEXT);",
    "CREATE TABLE IF NOT EXISTS recall("
    "id TEXT PRIMARY KEY,"
    "product_code TEXT,"
    "event_date_initiated TEXT,"
    "recall_status TEXT,"
    "reason_for_recall TEXT);",
    "CREATE TABLE IF NOT EXISTS device_recall("
    "recall_id TEXT,"
    "k_number TEXT,"
    "FOREIGN KEY(recall_id) REFERENCES recall(id),"
    "FOREIGN KEY(k_number) REFERENCES device(k_number));",
    "CREATE TABLE IF NOT EXISTS predicate_graph_edge("
    "node_from TEXT,"
    "node_to TEXT,"
    "FOREIGN KEY(node_from) REFERENCES device(k_number),"
    "FOREIGN KEY(node_to) REFERENCES device(k_number),"
    "PRIMARY KEY(node_from, node_to));",
    "CREATE EXTENSION IF NOT EXISTS pg_trgm;",
    "CREATE INDEX IF NOT EXISTS device_name_trgm_idx ON device USING gin (device_name gin_trgm_ops);",
    "CREATE TABLE IF NOT EXISTS feedback(id uuid DEFAULT gen_random_uuid(), name TEXT, email TEXT, message TEXT)",
]


for script in migrations:
    cur.execute(script)
con.commit()

print("Executed ", len(migrations), " migrations")
