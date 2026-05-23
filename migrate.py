import sqlite3
import re

def migrate_mysql_to_sqlite():
    # Connect to the SQLite database file
    conn = sqlite3.connect('inventory.db')
    cursor = conn.cursor()

    print("Cleaning up old structural mismatches...")
    # Clean up old mismatched table names if any exist
    cursor.execute("DROP TABLE IF EXISTS item;")
    cursor.execute("DROP TABLE IF EXISTS ITEM;")

    print("Creating 'item' table explicitly for Flask-SQLAlchemy...")
    # Create the correct lowercase table name
    cursor.execute('''
        CREATE TABLE item (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            category TEXT,
            price REAL,
            quantity INTEGER,
            status TEXT
        );
    ''')

    # Read and parse your SQL dump file
    print("Reading stock_item.sql and extracting rows...")
    with open('stock_item.sql', 'r', encoding='utf-8') as f:
        sql_content = f.read()

    # Find the INSERT statements
    insert_matches = re.findall(r"INSERT INTO `item` VALUES\s+(.*?);", sql_content, re.DOTALL)

    if insert_matches:
        values_block = insert_matches[0].strip()
        rows = re.findall(r"\(([^)]+)\)", values_block)
        
        inserted_count = 0
        for row in rows:
            # Insert explicitly into our lowercase table
            query = f"INSERT INTO item VALUES ({row});"
            try:
                cursor.execute(query)
                inserted_count += 1
            except Exception as e:
                print(f"Skipping row due to error: {e}")

        conn.commit()
        print(f"Successfully migrated {inserted_count} items into inventory.db!")
    else:
        print("Error: Could not find any data lines inside stock_item.sql.")

    conn.close()

if __name__ == "__main__":
    migrate_mysql_to_sqlite()