from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
import sqlite3

router = APIRouter(prefix="/user", tags=["user"])

def get_db_connection():
    conn = sqlite3.connect("kasse.db")
    conn.row_factory = sqlite3.Row
    return conn

def get_session_user(request: Request):
    # Example: Get user from session (adjust according to authentication)
    return request.cookies.get("session_user")

@router.get("/all/")
async def get_all_user():
    conn = get_db_connection()
    users = conn.execute("SELECT id, username, password FROM user WHERE deleted = 0").fetchall()
    categories = conn.execute("SELECT id, display_name FROM category WHERE deleted = 0").fetchall()
    # Get the group assignment for each user
    user_list = []
    for user in users:
        # Get all groups of the user
        groups = conn.execute("SELECT group_id FROM user_group WHERE user_id = ? AND deleted = 0", (user["id"],)).fetchall()
        group_ids = [g["group_id"] for g in groups]
        # Get all categories belonging to these groups
        cat_ids = set()
        for gid in group_ids:
            cats = conn.execute("SELECT category_id FROM category_group WHERE group_id = ? AND deleted = 0", (gid,)).fetchall()
            cat_ids.update([c["category_id"] for c in cats])
        # Get the display_names of the categories
        user_categories = [cat["display_name"] for cat in categories if cat["id"] in cat_ids]
        user_list.append({
            "id": user["id"],
            "username": user["username"],
            "password": user["password"],
            "categories": user_categories
        })
    conn.close()
    return JSONResponse(content=user_list)

@router.post("/add/")
async def add_user(request: Request):
    data = await request.json()
    username = data.get("username")
    password = data.get("password")
    conn = get_db_connection()
    conn.execute("INSERT INTO user (username, password) VALUES (?, ?)", (username, password))
    conn.commit()
    conn.close()
    return JSONResponse(content={"success": True, "message": "User created."})

@router.post("/update_permission/")
async def update_permission(request: Request):
    data = await request.json()
    user_id = data.get("user_id")
    category_display_name = data.get("category")
    allowed = data.get("allowed")  # True/False

    conn = get_db_connection()
    # Get the category ID
    cat = conn.execute("SELECT id FROM category WHERE display_name = ?", (category_display_name,)).fetchone()
    if not cat:
        conn.close()
        return JSONResponse(content={"success": False, "message": "Category not found"}, status_code=400)
    category_id = cat["id"]

    # Get all groups of the user
    groups = conn.execute("SELECT group_id FROM user_group WHERE user_id = ?", (user_id,)).fetchall()
    group_ids = [g["group_id"] for g in groups]

    # Get all groups that have assigned this category
    cat_groups = conn.execute("SELECT group_id FROM category_group WHERE category_id = ?", (category_id,)).fetchall()
    cat_group_ids = [g["group_id"] for g in cat_groups]

    # Set/remove permission
    if allowed:
        # Add the category to a group of the user (if not already present)
        # Take the first group of the user, if available
        if group_ids:
            if not cat_group_ids or group_ids[0] not in cat_group_ids:
                conn.execute("INSERT INTO category_group (group_id, category_id) VALUES (?, ?)", (group_ids[0], category_id))
                conn.commit()
    else:
        # Remove the category from all groups of the user
        for gid in group_ids:
            conn.execute("DELETE FROM category_group WHERE group_id = ? AND category_id = ?", (gid, category_id))
        conn.commit()

    conn.close()
    return JSONResponse(content={"success": True})

@router.post("/update/")
async def update_user(request: Request):
    data = await request.json()
    user_id = data.get("user_id")
    username = data.get("username")
    password = data.get("password")
    conn = get_db_connection()
    conn.execute("UPDATE user SET username = ?, password = ? WHERE id = ?", (username, password, user_id))
    conn.commit()
    conn.close()
    return JSONResponse(content={"success": True, "message": "User data updated."})

@router.post("/delete/")
async def delete_user(request: Request):
    data = await request.json()
    user_id = data.get("user_id")
    conn = get_db_connection()
    conn.execute("UPDATE user SET deleted = 1 WHERE id = ?", (user_id,))
    conn.execute("UPDATE user_group SET deleted = 1 WHERE user_id = ?", (user_id,))
    conn.commit()
    conn.close()
    return JSONResponse(content={"success": True, "message": "User deleted."})

