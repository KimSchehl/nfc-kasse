import sqlite3

DB_PATH = "kasse.db"
conn = sqlite3.connect(DB_PATH)
c = conn.cursor()

# neuer Kunde anlegen
def create_customer(nfc_uid):
    c.execute("INSERT INTO customer (nfc_uid) VALUES (?)", (nfc_uid,))
    conn.commit()
    return c.lastrowid


create_customer("7");
#create_customer("Erika Musterfrau", "0047361875");
