from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
import sqlite3

router = APIRouter(prefix="/finances", tags=["finances"])

@router.get("/transactions")
async def get_transactions():
    try:
        conn = sqlite3.connect("kasse.db")
        c = conn.cursor()
        c.execute("""
            SELECT t.id, t.timestamp, c.nfc_uid, p.name
            FROM "transaction" t
            JOIN customer c ON t.customer_id = c.id
            JOIN product p ON t.product_id = p.id
            ORDER BY t.timestamp DESC
        """)
        rows = c.fetchall()
        conn.close()
        result = [
            {
                "id": r[0],
                "timestamp": r[1],
                "nfc_uid": r[2],
                "product_name": r[3]
            }
            for r in rows
        ]
        return result
    except Exception as e:
        return {"success": False, "message": str(e)}