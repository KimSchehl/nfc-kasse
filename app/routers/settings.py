from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
import sqlite3

router = APIRouter(prefix="/settings", tags=["settings"])


@router.post("/grid_columns/{user_id}")
async def set_setting(user_id: int, request: Request):
    data = await request.json()
    type_ = data.get("type")
    value = data.get("value")
    if not type_ or value is None:
        return JSONResponse({"success": False, "message": "Typ und Wert erforderlich."}, status_code=400)
    conn = sqlite3.connect("kasse.db")
    c = conn.cursor()
    # Upsert
    c.execute("SELECT id FROM settings WHERE user_id=? AND type=?", (user_id, type_))
    row = c.fetchone()
    if row:
        c.execute("UPDATE settings SET value=? WHERE id=?", (value, row[0]))
    else:
        c.execute("INSERT INTO settings (user_id, type, value) VALUES (?, ?, ?)", (user_id, type_, value))
    conn.commit()
    conn.close()
    return {"success": True}

@router.get("/grid_columns/{user_id}")
async def get_grid_columns(user_id: int = 1):
    conn = sqlite3.connect("kasse.db")
    c = conn.cursor()
    c.execute("SELECT value FROM settings WHERE user_id=? AND type='spalten'", (user_id,))
    row = c.fetchone()
    conn.close()
    try:
        columns = int(row[0]) if row else 2
    except Exception:
        columns = 2
    return {"columns": columns}