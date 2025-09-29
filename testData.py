import sqlite3

DB_PATH = "kasse.db"
conn = sqlite3.connect(DB_PATH)
c = conn.cursor()

# --- Gruppen anlegen ---
groups = ["Admin", "Bonkasse", "Essen", "Bar", "Finanzbuchhaltung", "Bierwagen"]
for g in groups:
    c.execute("INSERT OR IGNORE INTO 'group' (name) VALUES (?)", (g,))

# --- Gruppen IDs auslesen ---
def get_group_id(name):
    c.execute("SELECT id FROM 'group' WHERE name=?", (name,))
    return c.fetchone()[0]

admin_group_id = get_group_id("Admin")
bonkasse_group_id = get_group_id("Bonkasse")
essen_group_id = get_group_id("Essen")
bar_group_id = get_group_id("Bar")
fibu_group_id = get_group_id("Finanzbuchhaltung")
bierwagen_group_id = get_group_id("Bierwagen")

# --- Kategorien anlegen (dynamisch, keine festen IDs) ---
categories = [
    ("Essen",),
    ("Getränke",),
    ("Bar",),
    ("BonKasse",),
]
for cat in categories:
    c.execute("INSERT OR IGNORE INTO category (display_name) VALUES (?)", cat)

def get_category_id(name):
    c.execute("SELECT id FROM category WHERE display_name=?", (name,))
    return c.fetchone()[0]

essen_cat_id = get_category_id("Essen")
getraenke_cat_id = get_category_id("Getränke")
bar_cat_id = get_category_id("Bar")
bonkasse_cat_id = get_category_id("BonKasse")

# --- User anlegen ---
users = [
    ("admin", "test123"),
    ("bonkasse_1", "test123"),
    ("bonkasse_2", "test123"),
    ("bar_1", "test123"),
    ("bar_2", "test123"),
    ("bierwagen_1", "test123"),
    ("bierwagen_2", "test123"),
    ("bierwagen_3", "test123"),
    ("fibu_1", "test123"),
    ("fibu_2", "test123"),
    ("essen_1", "test123"),
    ("essen_2", "test123"),
]
for username, password in users:
    c.execute("INSERT INTO user (username, password) VALUES (?, ?)", (username, password))

# --- User zu Gruppen zuordnen ---
user_group_map = {
    "admin": [admin_group_id, fibu_group_id],
    "bonkasse_1": [bonkasse_group_id],
    "bonkasse_2": [bonkasse_group_id],
    "bar_1": [bar_group_id],
    "bar_2": [bar_group_id],
    "bierwagen_1": [bierwagen_group_id],
    "bierwagen_2": [bierwagen_group_id],
    "bierwagen_3": [bierwagen_group_id],
    "fibu_1": [fibu_group_id],
    "fibu_2": [fibu_group_id],
    "essen_1": [essen_group_id],
    "essen_2": [essen_group_id],
}

for username, groups in user_group_map.items():
    c.execute("SELECT id FROM user WHERE username=?", (username,))
    user_id = c.fetchone()[0]
    for group_id in groups:
        c.execute("INSERT INTO user_group (user_id, group_id) VALUES (?, ?)", (user_id, group_id))

# --- Beispielkunde ---
c.execute("INSERT OR IGNORE INTO customer (nfc_uid, balance) VALUES (?, ?)", ("1", 50.00))

# --- Kategorien zu Gruppen zuordnen (dynamisch) ---
# Stand Essen darf auf Essen zugreifen
c.execute("INSERT OR IGNORE INTO category_group (category_id, group_id) VALUES (?, ?)", (essen_cat_id, essen_group_id))
# Stand Bar darf auf Bar zugreifen
c.execute("INSERT OR IGNORE INTO category_group (category_id, group_id) VALUES (?, ?)", (bar_cat_id, bar_group_id))
# Stand Bierwagen darf auf Getränke zugreifen
c.execute("INSERT OR IGNORE INTO category_group (category_id, group_id) VALUES (?, ?)", (getraenke_cat_id, bierwagen_group_id))
# Bonkasse darf auf BonKasse zugreifen
c.execute("INSERT OR IGNORE INTO category_group (category_id, group_id) VALUES (?, ?)", (bonkasse_cat_id, bonkasse_group_id))
# Admin darf auf alle Kategorien zugreifen
for cat_id in [essen_cat_id, getraenke_cat_id, bar_cat_id, bonkasse_cat_id]:
    c.execute("INSERT OR IGNORE INTO category_group (category_id, group_id) VALUES (?, ?)", (cat_id, admin_group_id))

# --- Produkte anlegen ---
# Getränke (category_id = getraenke_cat_id)
getraenke_produkte = [
    ("Bier 0,5L", 4),
    ("Fanta 0,33L", 3),
    ("Cola 0,33L", 3),
    ("Wasser 0,33L", 2),
    ("Wasser 0,7L", 3.5),
    ("+ Glas Pfand", 3),
    ("+ Flaschen Pfand", 1),
    ("+ Stein Pfand", 5),
    ("- Glas Pfand", -3),
    ("- Flaschen Pfand", -1),
    ("- Stein Pfand", -5),
]
for name, price in getraenke_produkte:
    c.execute("INSERT INTO product (name, price, category_id) VALUES (?, ?, ?)", (name, price, getraenke_cat_id))

# Essen (category_id = essen_cat_id)
essen_produkte = [
    ("Pommes", 4.5),
    ("Currywurst + Brötchen", 6),
    ("Currywurst + Pommes", 8),
    ("Wurstsalat + Pommes", 8),
    ("Pizza", 6),
    ("Flammkuchen", 7),
]
for name, price in essen_produkte:
    c.execute("INSERT INTO product (name, price, category_id) VALUES (?, ?, ?)", (name, price, essen_cat_id))

# Bar (category_id = bar_cat_id)
bar_produkte = [
    ("Hugo", 6.5),
    ("Aperol Spritz", 6),
    ("Jägermeister 2cl", 2.5),
    ("Sierra Tequila 2cl", 2.5),
    ("Vodka 2cl", 2.5),
    ("Rum 2cl", 2.5),
    ("Gin 2cl", 2.5),
    ("Whiskey 2cl", 2.5),
    ("Campari 2cl", 2.5),
    ("Martini 2cl", 2.5),
    ("Sekt", 4),
    ("Champagner", 10),
]
for name, price in bar_produkte:
    c.execute("INSERT INTO product (name, price, category_id) VALUES (?, ?, ?)", (name, price, bar_cat_id))

# BonKasse (category_id = bonkasse_cat_id)
BonKasse_products = [
    ("5€", -5),
    ("10€", -10),
    ("20€", -20),
    ("50€", -50),
    ("100€", -100),
]
for name, price in BonKasse_products:
    c.execute("INSERT INTO product (name, price, category_id) VALUES (?, ?, ?)", (name, price, bonkasse_cat_id))

conn.commit()
conn.close()

print("Testdaten erfolgreich eingefügt.")