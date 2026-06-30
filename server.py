#!/usr/bin/env python3
import json
import os
import re
import uuid
from pathlib import Path
from datetime import datetime, timezone, timedelta
from functools import wraps

from flask import Flask, render_template, request, jsonify, session, send_from_directory, abort, redirect

HERE = Path(__file__).resolve().parent
KEYS_PATH = HERE / "keys" / "keys.json"
PERM_PATH = HERE / "keys" / "file_permissions.json"
SHARED_DIR = HERE / "shared"
SECRET_KEY_PATH = HERE / "keys" / ".secret"

app = Flask(__name__, static_folder="static", template_folder="templates")

if SECRET_KEY_PATH.exists():
    app.secret_key = SECRET_KEY_PATH.read_text().strip()
else:
    app.secret_key = uuid.uuid4().hex
    SECRET_KEY_PATH.parent.mkdir(parents=True, exist_ok=True)
    SECRET_KEY_PATH.write_text(app.secret_key)

TZ = timezone(timedelta(hours=8))


def load_keys():
    if KEYS_PATH.exists():
        return json.loads(KEYS_PATH.read_text(encoding="utf-8"))
    return []

def save_keys(users):
    KEYS_PATH.write_text(json.dumps(users, ensure_ascii=False, indent=2), encoding="utf-8")

def load_perms():
    if PERM_PATH.exists():
        return json.loads(PERM_PATH.read_text(encoding="utf-8"))
    return {}

def save_perms(perms):
    PERM_PATH.write_text(json.dumps(perms, ensure_ascii=False, indent=2), encoding="utf-8")

def find_user(user_id):
    for u in load_keys():
        if u["id"] == user_id:
            return u
    return None

def get_shared_files():
    files = []
    if SHARED_DIR.exists():
        for f in sorted(SHARED_DIR.glob("*.html")):
            mtime = f.stat().st_mtime
            ts = datetime.fromtimestamp(mtime, TZ).strftime("%Y-%m-%d %H:%M:%S")
            files.append({"name": f.name, "time": ts})
    return files

def password_ok(pw):
    if len(pw) < 8:
        return False
    if not re.search(r"[A-Z]", pw):
        return False
    if not re.search(r"[a-z]", pw):
        return False
    if not re.search(r"[0-9]", pw):
        return False
    return True

ROLE_HIERARCHY = {"admin": 3, "editor": 2, "viewer": 1}

def role_ge(role, min_role):
    return ROLE_HIERARCHY.get(role, 0) >= ROLE_HIERARCHY.get(min_role, 0)

def can_see_file(user, filename, perms):
    fp = perms.get(filename, {})
    v = fp.get("visibility", "all")
    if v == "all":
        return True
    if v.startswith("role:"):
        return role_ge(user["role"], v.split(":", 1)[1])
    if v == "specific":
        return user["id"] in fp.get("allowed_users", [])
    return True


def login_required(f):
    @wraps(f)
    def wrapper(*a, **kw):
        if "user_id" not in session:
            return jsonify({"success": False, "message": "未登录"}), 401
        user = find_user(session["user_id"])
        if not user:
            session.clear()
            return jsonify({"success": False, "message": "用户不存在"}), 401
        return f(*a, **kw)
    return wrapper

def admin_required(f):
    @wraps(f)
    def wrapper(*a, **kw):
        if "user_id" not in session:
            return jsonify({"success": False, "message": "未登录"}), 401
        user = find_user(session["user_id"])
        if not user or user["role"] != "admin":
            return jsonify({"success": False, "message": "需要管理员权限"}), 403
        return f(*a, **kw)
    return wrapper

def editor_required(f):
    @wraps(f)
    def wrapper(*a, **kw):
        if "user_id" not in session:
            return jsonify({"success": False, "message": "未登录"}), 401
        user = find_user(session["user_id"])
        if not user or user["role"] not in ("admin", "editor"):
            return jsonify({"success": False, "message": "需要编辑者或管理员权限"}), 403
        return f(*a, **kw)
    return wrapper


def get_current_user():
    if "user_id" not in session:
        return None
    return find_user(session["user_id"])


def sanitize_user(u):
    return {
        "id": u["id"],
        "name": u["name"],
        "role": u["role"],
        "hr": u.get("hr", False),
        "first_login": u.get("first_login", False),
        "department": u.get("department", ""),
        "position": u.get("position", ""),
    }


@app.context_processor
def inject_user():
    u = get_current_user()
    return dict(current_user=sanitize_user(u) if u else None)


@app.route("/")
def index_page():
    u = get_current_user()
    if not u:
        return redirect("/login")
    return render_template("index.html")

@app.route("/login")
def login_page():
    u = get_current_user()
    if u:
        return redirect("/")
    return render_template("login.html")

@app.route("/account")
def account_page():
    u = get_current_user()
    if not u:
        return redirect("/login")
    return render_template("account.html")

@app.route("/shared/<path:filename>")
def serve_shared(filename):
    if "user_id" not in session:
        abort(401)
    user = find_user(session["user_id"])
    if not user:
        abort(401)
    perms = load_perms()
    if not can_see_file(user, filename, perms):
        abort(403)
    return send_from_directory(str(SHARED_DIR), filename)


@app.route("/api/login", methods=["POST"])
def api_login():
    data = request.get_json(silent=True) or {}
    uid = data.get("id", "").strip()
    pw = data.get("password", "")
    user = find_user(uid)
    if not user:
        return jsonify({"success": False, "message": "工号不存在"})
    if user["password"] != pw:
        return jsonify({"success": False, "message": "密码错误"})
    session["user_id"] = user["id"]
    session.permanent = True
    force = user.get("first_login", False)
    return jsonify({
        "success": True,
        "user": sanitize_user(user),
        "force_change": force
    })

@app.route("/api/logout", methods=["POST"])
def api_logout():
    session.clear()
    return jsonify({"success": True})

@app.route("/api/check-auth", methods=["GET"])
def api_check_auth():
    u = get_current_user()
    if not u:
        return jsonify({"success": False, "message": "未登录"}), 401
    return jsonify({"success": True, "user": sanitize_user(u)})


@app.route("/api/user/profile", methods=["GET"])
@login_required
def api_get_profile():
    user = find_user(session["user_id"])
    return jsonify({"success": True, "user": sanitize_user(user)})

@app.route("/api/user/profile", methods=["PUT"])
@login_required
def api_update_profile():
    data = request.get_json(silent=True) or {}
    current = find_user(session["user_id"])
    users = load_keys()
    for u in users:
        if u["id"] == session["user_id"]:
            u["name"] = data.get("name", u["name"])
            u["department"] = data.get("department", u.get("department", ""))
            u["position"] = data.get("position", u.get("position", ""))
            break
    save_keys(users)
    return jsonify({"success": True})


@app.route("/api/change-password", methods=["POST"])
@login_required
def api_change_password():
    data = request.get_json(silent=True) or {}
    old = data.get("old_password", "")
    new = data.get("new_password", "")
    if not password_ok(new):
        return jsonify({"success": False, "message": "密码需包含大小写字母+数字，至少8位"})
    users = load_keys()
    for u in users:
        if u["id"] == session["user_id"]:
            if u["password"] != old:
                return jsonify({"success": False, "message": "当前密码错误"})
            u["password"] = new
            u["first_login"] = False
            break
    save_keys(users)
    return jsonify({"success": True, "message": "密码已更新"})


@app.route("/api/files", methods=["GET"])
@login_required
def api_list_files():
    user = find_user(session["user_id"])
    all_files = get_shared_files()
    perms = load_perms()
    visible = [f for f in all_files if can_see_file(user, f["name"], perms)]
    return jsonify({"success": True, "files": visible, "permissions": perms})

@app.route("/api/files/upload", methods=["POST"])
@editor_required
def api_upload_files():
    files = request.files.getlist("files")
    count = 0
    for f in files:
        if f.filename.endswith(".html"):
            f.save(str(SHARED_DIR / f.filename))
            count += 1
    return jsonify({"success": True, "count": count})

@app.route("/api/files/<path:filename>", methods=["DELETE"])
@editor_required
def api_delete_file(filename):
    fp = SHARED_DIR / filename
    if not fp.exists():
        return jsonify({"success": False, "message": "文件不存在"})
    fp.unlink()
    perms = load_perms()
    perms.pop(filename, None)
    save_perms(perms)
    return jsonify({"success": True})


@app.route("/api/file-permissions", methods=["PUT"])
@editor_required
def api_set_file_permission():
    data = request.get_json(silent=True) or {}
    file_name = data.get("file", "")
    visibility = data.get("visibility", "all")
    perms = load_perms()
    if file_name not in perms:
        perms[file_name] = {"visibility": "all", "allowed_users": []}
    perms[file_name]["visibility"] = visibility
    save_perms(perms)
    return jsonify({"success": True})


@app.route("/api/users", methods=["GET"])
@admin_required
def api_list_users():
    users = load_keys()
    return jsonify({"success": True, "users": [
        sanitize_user(u) for u in users
    ]})

@app.route("/api/users/<user_id>", methods=["PUT"])
@admin_required
def api_update_user(user_id):
    data = request.get_json(silent=True) or {}
    admin_user = find_user(session["user_id"])
    users = load_keys()
    for u in users:
        if u["id"] == user_id:
            new_role = data.get("role")
            if new_role:
                if new_role not in ("admin", "editor", "viewer"):
                    return jsonify({"success": False, "message": "无效角色"})
                u["role"] = new_role
            if "name" in data:
                u["name"] = data["name"]
            if "department" in data:
                u["department"] = data["department"]
            if "position" in data:
                u["position"] = data["position"]
            if "hr" in data and new_role == "admin" and u["role"] == "admin":
                u["hr"] = data["hr"]
            break
    save_keys(users)
    return jsonify({"success": True})

@app.route("/api/users/<user_id>/hr", methods=["PUT"])
@admin_required
def api_toggle_hr(user_id):
    data = request.get_json(silent=True) or {}
    users = load_keys()
    for u in users:
        if u["id"] == user_id:
            if u["role"] != "admin":
                return jsonify({"success": False, "message": "只能为管理员设置HR权限"})
            u["hr"] = data.get("hr", False)
            break
    save_keys(users)
    return jsonify({"success": True, "message": "HR权限已更新"})

@app.route("/api/users/<user_id>/reset-password", methods=["POST"])
@admin_required
def api_reset_password(user_id):
    users = load_keys()
    for u in users:
        if u["id"] == user_id:
            new_pw = "Kebei" + u["id"]
            u["password"] = new_pw
            u["first_login"] = True
            break
    save_keys(users)
    return jsonify({"success": True, "message": f"密码已重置为 Kebei{user_id}"})


if __name__ == "__main__":
    SHARED_DIR.mkdir(parents=True, exist_ok=True)
    port = int(os.environ.get("PORT", 5000))
    host = os.environ.get("HOST", "0.0.0.0")
    debug = os.environ.get("FLASK_DEBUG", "1") == "1"
    print(f"[server] 科贝智色文件共享服务启动 http://{host}:{port} debug={debug}")
    app.run(host=host, port=port, debug=debug)
