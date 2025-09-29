from fastapi import APIRouter, Request, Response
from fastapi.responses import JSONResponse
import sqlite3
import secrets

router = APIRouter(prefix="/auth", tags=["auth"])

# --- Login ---
@router.post("/login")
async def login(request: Request, response: Response):
    data = await request.json()
    username = data.get("username")
    password = data.get("password")
    if not username or not password:
        return JSONResponse({"success": False, "message": "Benutzername und Passwort erforderlich."}, status_code=400)

    conn = sqlite3.connect("kasse.db")
    c = conn.cursor()
    c.execute("SELECT id FROM user WHERE username=? AND password=?", (username, password))
    user = c.fetchone()
    conn.close()

    if user:
        user_id = user[0]
        token = secrets.token_hex(32)
        conn = sqlite3.connect("kasse.db")
        c = conn.cursor()
        c.execute("INSERT INTO session (user_id, token) VALUES (?, ?)", (user_id, token))
        conn.commit()
        conn.close()
        response = JSONResponse({"success": True})
        response.set_cookie(
            key="session",
            value=token,
            httponly=True,
            samesite="lax",  # oder "strict"
            secure=True      # nur bei HTTPS!
        )
        return response
    else:
        return JSONResponse({"success": False, "message": "Falscher Benutzername oder Passwort."}, status_code=401)

# --- Session Check ---
@router.get("/check_session")
async def check_session(request: Request):
    session_token = request.cookies.get("session")
    if not session_token:
        return {"logged_in": False}
    conn = sqlite3.connect("kasse.db")
    c = conn.cursor()
    c.execute("SELECT user_id FROM session WHERE token=?", (session_token,))
    user = c.fetchone()
    conn.close()
    if user:
        return {"logged_in": True}
    return {"logged_in": False}

# --- Logout ---
@router.post("/logout")
async def logout(request: Request, response: Response):
    session_token = request.cookies.get("session")
    if session_token:
        conn = sqlite3.connect("kasse.db")
        c = conn.cursor()
        c.execute("DELETE FROM session WHERE token=?", (session_token,))
        conn.commit()
        conn.close()
    response = JSONResponse({"success": True})
    response.delete_cookie("session")
    return response

# --- Get Session User ---
@router.get("/session_user")
async def get_session_user(request: Request):
    session_token = request.cookies.get("session")
    if not session_token:
        return JSONResponse(content={"username": None, "id": None, "group": None})
    
    conn = sqlite3.connect("kasse.db")
    c = conn.cursor()
    c.execute("SELECT user_id FROM session WHERE token=?", (session_token,))
    row = c.fetchone()

    if not row:
        conn.close()
        return JSONResponse(content={"username": None, "id": None, "group": None})
    
    user_id = row[0]
    # Hole Username und alle Gruppennamen
    c.execute("""
        SELECT u.username, g.id, g.name
        FROM user u
        JOIN user_group ug ON u.id = ug.user_id
        JOIN "group" g ON ug.group_id = g.id
        WHERE u.id=?
        AND u.deleted=0 AND g.deleted=0 AND ug.deleted=0
    """, (user_id,))
    rows = c.fetchall()
    if not rows:
        conn.close()
        return JSONResponse(content={"username": None, "id": None, "groups": [], "categories": []})
    username = rows[0][0]
    group_ids = [row[1] for row in rows]
    groups = [row[2] for row in rows]
    # Hole alle Kategorien, auf die der User Zugriff hat (über Gruppen)
    c.execute(f"""
        SELECT DISTINCT c.display_name
        FROM category c
        JOIN category_group cg ON c.id = cg.category_id
        WHERE cg.group_id IN ({','.join(['?']*len(group_ids))}) AND c.deleted=0 AND cg.deleted=0
    """, group_ids)
    cat_rows = c.fetchall()
    conn.close()
    categories = [row[0] for row in cat_rows]
    return JSONResponse(content={"username": username, "id": user_id, "groups": groups, "categories": categories})