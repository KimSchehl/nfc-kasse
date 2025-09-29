from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
import sqlite3

router = APIRouter(prefix="/transactions", tags=["transactions"])

@router.post("/book")
async def book_transaction(request: Request):
    data = await request.json()
    nfc_uid = data.get("nfc_uid")
    products = data.get("products")  # Liste von Produkt-IDs

    if not nfc_uid or not products or not isinstance(products, list):
        return JSONResponse({"success": False, "message": "Ungültige Anfrage."}, status_code=400)

    conn = sqlite3.connect("kasse.db")
    conn.isolation_level = "EXCLUSIVE"  # Für Transaktionssicherheit
    c = conn.cursor()
    try:
        c.execute("BEGIN EXCLUSIVE")
        # Customer und Guthaben holen
        c.execute("SELECT id, balance FROM customer WHERE nfc_uid=?", (nfc_uid,))
        row = c.fetchone()
        if not row:
            # Neuen Kunden anlegen
            c.execute("INSERT INTO customer (nfc_uid, balance) VALUES (?, ?)", (nfc_uid, 0))
            customer_id = c.lastrowid
            balance = 0
        else:
            customer_id, balance = row

        # Produkte und Gesamtpreis berechnen
        prices = []
        for pid in products:
            c.execute("SELECT price FROM product WHERE id=?", (pid,))
            row = c.fetchone()
            if not row:
                return JSONResponse({"success": False, "message": f"Produkt mit ID {pid} nicht gefunden."}, status_code=404)
            prices.append(row[0])
        total = sum(prices)

        # Guthaben prüfen
        if balance < total:
            return JSONResponse({"success": False, "message": "Nicht genügend Guthaben."}, status_code=400)

        # Transaktionen eintragen
        for pid in products:
            c.execute('INSERT INTO "transaction" (customer_id, product_id) VALUES (?, ?)', (customer_id, pid))

        # Guthaben abziehen
        c.execute("UPDATE customer SET balance = balance - ? WHERE id = ?", (total, customer_id))

        conn.commit()
        return {"success": True, "new_balance": balance - total}
    except Exception as e:
        conn.rollback()
        return JSONResponse({"success": False, "message": "Fehler: " + str(e)}, status_code=500)
    finally:
        conn.close()

@router.get("/balance/{nfc_uid}")
async def get_balance(nfc_uid: str):
    conn = sqlite3.connect("kasse.db")
    c = conn.cursor()
    c.execute("SELECT balance FROM customer WHERE nfc_uid=?", (nfc_uid,))
    row = c.fetchone()
    conn.close()
    if row:
        return {"success": True, "balance": row[0]}
    return {"success": False, "message": "Kunde nicht gefunden."}

@router.post("/payout")
async def payout_balance(request: Request):
    data = await request.json()
    nfc_uid = data.get("nfc_uid")
    if not nfc_uid:
        return {"success": False, "message": "NFC UID fehlt."}
    conn = sqlite3.connect("kasse.db")
    c = conn.cursor()
    c.execute("UPDATE customer SET balance = 0 WHERE nfc_uid=?", (nfc_uid,))
    conn.commit()
    conn.close()
    return {"success": True}

