import sqlite3
import os

# Database path
DB_PATH = "kasse.db"

# Delete the database file if it exists (development only!)
if os.path.exists(DB_PATH):
    os.remove(DB_PATH)

# Connection and cursor
conn = sqlite3.connect(DB_PATH)
c = conn.cursor()

# Create tables
c.execute("""
CREATE TABLE user (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL,
    password TEXT NOT NULL,
    deleted BOOLEAN NOT NULL DEFAULT 0
)
""")

c.execute("""
CREATE TABLE "group" (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    deleted BOOLEAN NOT NULL DEFAULT 0
)
""")

c.execute("""
CREATE TABLE user_group (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    group_id INTEGER NOT NULL,
    deleted BOOLEAN NOT NULL DEFAULT 0,
    FOREIGN KEY (user_id) REFERENCES user(id),
    FOREIGN KEY (group_id) REFERENCES "group"(id)
)
""")

c.execute("""
CREATE TABLE customer (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nfc_uid TEXT NOT NULL UNIQUE,
    balance REAL NOT NULL DEFAULT 0
)
""")

c.execute("""
CREATE TABLE category (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    display_name TEXT NOT NULL,
    deleted BOOLEAN NOT NULL DEFAULT 0
)
""")

c.execute("""
CREATE TABLE category_group (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    category_id INTEGER NOT NULL,
    group_id INTEGER NOT NULL,
    deleted BOOLEAN NOT NULL DEFAULT 0,
    FOREIGN KEY (category_id) REFERENCES category(id),
    FOREIGN KEY (group_id) REFERENCES "group"(id)
)
""")

c.execute("""
CREATE TABLE product (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    price REAL NOT NULL,
    category_id INTEGER NOT NULL,
    deleted BOOLEAN NOT NULL DEFAULT 0,
    FOREIGN KEY (category_id) REFERENCES category(id)
)
""")

c.execute("""
CREATE TABLE "transaction" (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_id INTEGER,
    product_id INTEGER,
    timestamp TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (customer_id) REFERENCES customer(id),
    FOREIGN KEY (product_id) REFERENCES product(id)
)
""")

c.execute("""
CREATE TABLE session (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    token TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES user(id)
)
""")

c.execute("""
CREATE TABLE settings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    type TEXT NOT NULL,
    value TEXT NOT NULL,
    FOREIGN KEY (user_id) REFERENCES user(id)
)
""")

# Commit and close
conn.commit()
conn.close()

print("SQLite database created and populated successfully.")
