from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
import sqlite3

router = APIRouter(prefix="/categories", tags=["categories"])

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
async def get_categories(request: Request):
    user_id = get_user_id_from_session(request)
    if not user_id:
        return JSONResponse({"success": False, "message": "Nicht eingeloggt."}, status_code=401)
    group_ids = get_user_group_ids(user_id)
    # Admin sieht alle Kategorien
    conn = sqlite3.connect("kasse.db")
    c = conn.cursor()
    c.execute("SELECT id FROM 'group' WHERE name='Admin'")
    admin_group_id = c.fetchone()
    if admin_group_id and admin_group_id[0] in group_ids:
        c.execute("SELECT id, display_name FROM category")
        categories = [{"id": row[0], "display_name": row[1]} for row in c.fetchall()]
    else:
        # Nur Kategorien, auf die die Gruppen Zugriff haben
        q = """
        SELECT DISTINCT c.id, c.display_name
        FROM category c
        JOIN category_group cg ON c.id = cg.category_id
        WHERE cg.group_id IN ({seq})
        """.format(seq=','.join(['?']*len(group_ids)))
        c.execute(q, group_ids)
        categories = [{"id": row[0], "display_name": row[1]} for row in c.fetchall()]
    conn.close()
    return categories

@router.post("/")
async def add_category(request: Request):
    user_id = get_user_id_from_session(request)
    if not user_id:
        return JSONResponse({"success": False, "message": "Nicht eingeloggt."}, status_code=401)
    group_ids = get_user_group_ids(user_id)
    # Nur Admin darf Kategorien anlegen
    conn = sqlite3.connect("kasse.db")
    c = conn.cursor()
    c.execute("SELECT id FROM 'group' WHERE name='Admin'")
    admin_group_id = c.fetchone()
    if not (admin_group_id and admin_group_id[0] in group_ids):
        conn.close()
        return JSONResponse({"success": False, "message": "Keine Berechtigung."}, status_code=403)
    data = await request.json()
    display_name = data.get("display_name")
    if not display_name:
        conn.close()
        return JSONResponse({"success": False, "message": "Anzeigename erforderlich."}, status_code=400)
    try:
        c.execute("INSERT INTO category (display_name) VALUES (?)", (display_name,))
        conn.commit()
        return {"success": True}
    except sqlite3.IntegrityError:
        return JSONResponse({"success": False, "message": "Kategorie existiert bereits."}, status_code=409)
    finally:
        conn.close()

@router.put("/{category_id}")
async def update_category(category_id: int, request: Request):
    user_id = get_user_id_from_session(request)
    if not user_id:
        return JSONResponse({"success": False, "message": "Nicht eingeloggt."}, status_code=401)
    group_ids = get_user_group_ids(user_id)
    conn = sqlite3.connect("kasse.db")
    c = conn.cursor()
    c.execute("SELECT id FROM 'group' WHERE name='Admin'")
    admin_group_id = c.fetchone()
    if not (admin_group_id and admin_group_id[0] in group_ids):
        conn.close()
        return JSONResponse({"success": False, "message": "Keine Berechtigung."}, status_code=403)
    data = await request.json()
    display_name = data.get("display_name")
    if not display_name:
        conn.close()
        return JSONResponse({"success": False, "message": "Anzeigename erforderlich."}, status_code=400)
    c.execute("UPDATE category SET display_name=? WHERE id=?", (display_name, category_id))
    conn.commit()
    conn.close()
    return {"success": True}

@router.delete("/{category_id}")
async def delete_category(category_id: int, request: Request):
    user_id = get_user_id_from_session(request)
    if not user_id:
        return JSONResponse({"success": False, "message": "Nicht eingeloggt."}, status_code=401)
    group_ids = get_user_group_ids(user_id)
    conn = sqlite3.connect("kasse.db")
    c = conn.cursor()
    c.execute("SELECT id FROM 'group' WHERE name='Admin'")
    admin_group_id = c.fetchone()
    if not (admin_group_id and admin_group_id[0] in group_ids):
        conn.close()
        return JSONResponse({"success": False, "message": "Keine Berechtigung."}, status_code=403)
    c.execute("DELETE FROM category WHERE id=?", (category_id,))
    conn.commit()
    conn.close()
    return {"success": True}