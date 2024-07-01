import sqlite3
import random
import os

def fetch_random_data(table_name, cursor):
    cursor.execute(f'SELECT * FROM {table_name}')
    rows = cursor.fetchall()
    if rows:
        return random.choice(rows)
    return None

def print_random_data_from_table(table_name, cursor):
    random_data = fetch_random_data(table_name, cursor)
    if random_data:
        print(f"Random data from {table_name}:")
        for col, data in zip([desc[0] for desc in cursor.description], random_data):
            print(f"{col}: {data}")
    else:
        print(f"No data found in table {table_name}")

def main():
    db_path = os.path.join(os.path.dirname(__file__), '..', 'thing.db')
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    tables = ['thingmenn', 'malaskra', 'thingskjal', 'dagskra', 'raedur', 'flutningsmadur']
    for table in tables:
        try:
            print_random_data_from_table(table, cursor)
        except sqlite3.OperationalError as e:
            print(f"Table {table} does not exist. Error: {e}")
        print("\n" + "-"*50 + "\n")

    conn.close()

if __name__ == '__main__':
    main()
