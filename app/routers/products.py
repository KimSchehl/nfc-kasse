from fastapi import APIRouter, Query, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import sqlite3

router = APIRouter(prefix="/products", tags=["products"])

def get_user_id_from_session(request: Request):
    session_token = request.cookies.get("session")
    if not session_token:
        return None
    conn = sqlite3.connect("kasse.db")
    c = conn.cursor()
    c.execute("SELECT user_id FROM session WHERE token=?", (session_token,))
    row = c.fetchone()
    conn.close()
    return row[0] if row else None

def get_user_group_ids(user_id):
    conn = sqlite3.connect("kasse.db")
    c = conn.cursor()
    c.execute("SELECT group_id FROM user_group WHERE user_id=?", (user_id,))
    group_ids = [row[0] for row in c.fetchall()]
    conn.close()
    return group_ids

@router.get("/")
async def get_products(request: Request, category_id: int = Query(...)):
    user_id = get_user_id_from_session(request)
    if not user_id:
        return JSONResponse({"success": False, "message": "Nicht eingeloggt."}, status_code=401)
    group_ids = get_user_group_ids(user_id)
    # Prüfen, ob User Zugriff auf die Kategorie hat
    conn = sqlite3.connect("kasse.db")
    c = conn.cursor()
    c.execute("SELECT group_id FROM category_group WHERE category_id=?", (category_id,))
    allowed_groups = [row[0] for row in c.fetchall()]
    if not set(group_ids).intersection(allowed_groups):
        conn.close()
        return JSONResponse({"success": False, "message": "Keine Berechtigung für diese Kategorie."}, status_code=403)
    c.execute("SELECT id, name, price FROM product WHERE category_id=?", (category_id,))
    products = [{"id": row[0], "name": row[1], "price": row[2]} for row in c.fetchall()]
    conn.close()
    return products

class ProductCreate(BaseModel):
    name: str
    price: float
    category_id: int

# Neues Produkt anlegen
@router.post("/")
async def add_product(product: ProductCreate):
    conn = sqlite3.connect("kasse.db")
    c = conn.cursor()
    try:
        c.execute(
            "INSERT INTO product (name, price, category_id) VALUES (?, ?, ?)",
            (product.name, product.price, product.category_id)
        )
        conn.commit()
        return {"success": True}
    except Exception as e:
        return JSONResponse({"success": False, "message": str(e)}, status_code=500)
    finally:
        conn.close()