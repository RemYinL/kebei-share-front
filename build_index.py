"""Generate index.html with embedded base64 assets and auth."""
import json
import os
from pathlib import Path

HERE = Path(__file__).resolve().parent
SHARED_DIR = HERE / "shared"
LOGO1_PATH = Path("/mnt/c/Users/22602/Desktop/图片1.png")
LOGO2_PATH = Path("/mnt/c/Users/22602/Desktop/kebeizhise/参考资料/科贝智色logo.PNG")
FILES_JSON_PATH = HERE / "files.json"
KEYS_PATH = HERE / "keys" / "keys.json"

STYLE_COMMON = """
  *, *::before, *::after { margin: 0; padding: 0; box-sizing: border-box; }
  @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Noto+Sans+SC:wght@300;400;500;700&display=swap');
  :root {
    --bg: #0a0a0f;
    --surface: rgba(255,255,255,0.04);
    --surface-hover: rgba(255,255,255,0.07);
    --border: rgba(255,255,255,0.08);
    --border-hover: rgba(255,255,255,0.15);
    --text: #f0f0f4;
    --text-secondary: rgba(255,255,255,0.5);
    --text-muted: rgba(255,255,255,0.25);
    --accent: #7c5cfc;
    --accent-glow: rgba(124,92,252,0.15);
    --radius: 16px;
    --radius-sm: 10px;
    --font: 'Inter', 'Noto Sans SC', -apple-system, BlinkMacSystemFont, sans-serif;
  }
  html, body { height: 100%; overflow-x: hidden; }
  body {
    font-family: var(--font);
    background: var(--bg);
    color: var(--text);
    min-height: 100vh;
    position: relative;
  }
  body::before {
    content: '';
    position: fixed;
    top: -50%; left: -50%;
    width: 200%; height: 200%;
    background:
      radial-gradient(ellipse 80% 60% at 20% 20%, rgba(124,92,252,0.06) 0%, transparent 60%),
      radial-gradient(ellipse 60% 50% at 80% 80%, rgba(249,115,22,0.04) 0%, transparent 60%),
      radial-gradient(ellipse 50% 40% at 50% 50%, rgba(59,130,246,0.03) 0%, transparent 50%);
    pointer-events: none;
    z-index: 0;
  }
"""

def b64encode(path):
    import base64
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode()

def get_shared_files():
    files = []
    if SHARED_DIR.exists():
        for f in sorted(SHARED_DIR.glob("*.html")):
            mtime = f.stat().st_mtime
            from datetime import datetime, timezone, timedelta
            tz = timezone(timedelta(hours=8))
            ts = datetime.fromtimestamp(mtime, tz).strftime("%Y-%m-%d %H:%M:%S")
            files.append({"name": f.name, "time": ts})
    return files

def load_users():
    if KEYS_PATH.exists():
        return json.loads(KEYS_PATH.read_text(encoding="utf-8"))
    return []

def build_login(users, logo1_b64, logo2_b64):
    users_json = json.dumps(users, ensure_ascii=False)

    html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>登录 · 科贝智色</title>
<style>{STYLE_COMMON}
  .login-wrap {{
    position: relative; z-index: 1;
    min-height: 100vh;
    display: flex; align-items: center; justify-content: center;
    padding: 24px;
  }}
  .login-card {{
    width: 100%; max-width: 420px;
    background: var(--surface);
    backdrop-filter: blur(28px) saturate(1.5);
    -webkit-backdrop-filter: blur(28px) saturate(1.5);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 48px 36px 40px;
    transition: all 0.3s;
  }}
  .login-card:hover {{
    border-color: var(--border-hover);
    box-shadow: 0 0 0 1px rgba(255,255,255,0.04) inset;
  }}
  .login-logo {{
    text-align: center; margin-bottom: 12px;
  }}
  .login-logo img {{ height: 40px; width: auto; opacity: 0.9; }}
  .login-brand {{
    text-align: center; margin-bottom: 36px;
  }}
  .login-brand h1 {{
    font-size: 1.4rem; font-weight: 600;
    background: linear-gradient(135deg, #7c5cfc, #f97316);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    letter-spacing: 1px;
  }}
  .login-brand p {{
    font-size: 0.85rem; color: var(--text-secondary); margin-top: 6px;
  }}
  .field {{
    margin-bottom: 20px;
  }}
  .field label {{
    display: block; font-size: 0.82rem; font-weight: 500;
    color: var(--text-secondary); margin-bottom: 6px;
  }}
  .field input {{
    width: 100%; padding: 12px 16px;
    background: rgba(255,255,255,0.04);
    border: 1px solid var(--border);
    border-radius: var(--radius-sm);
    color: var(--text);
    font-size: 0.95rem; font-family: var(--font);
    outline: none; transition: 0.25s;
  }}
  .field input:focus {{
    border-color: var(--accent);
    box-shadow: 0 0 0 3px var(--accent-glow);
  }}
  .field input::placeholder {{
    color: var(--text-muted);
  }}
  .field select {{
    width: 100%; padding: 12px 16px;
    background: rgba(255,255,255,0.04);
    border: 1px solid var(--border);
    border-radius: var(--radius-sm);
    color: var(--text);
    font-size: 0.95rem; font-family: var(--font);
    outline: none; transition: 0.25s;
    appearance: none;
    cursor: pointer;
  }}
  .field select:focus {{
    border-color: var(--accent);
    box-shadow: 0 0 0 3px var(--accent-glow);
  }}
  .field select option {{
    background: #1a1a24; color: var(--text);
  }}
  .btn {{
    width: 100%; padding: 12px;
    background: linear-gradient(135deg, #7c5cfc, #6a4ce8);
    border: none; border-radius: var(--radius-sm);
    color: #fff; font-size: 0.95rem; font-weight: 600;
    font-family: var(--font);
    cursor: pointer; transition: 0.25s;
  }}
  .btn:hover {{
    opacity: 0.88; transform: translateY(-1px);
    box-shadow: 0 6px 20px rgba(124,92,252,0.35);
  }}
  .error {{
    color: #f87171; font-size: 0.85rem;
    margin-top: 12px; text-align: center;
    min-height: 1.4em;
  }}
</style>
</head>
<body>
<div class="login-wrap">
  <div class="login-card">
    <div class="login-logo">
      <img src="data:image/png;base64,{logo1_b64}" alt="Logo">
    </div>
    <div class="login-brand">
      <h1>科贝智色</h1>
      <p>多端文件共享 · 安全访问</p>
    </div>
    <form id="loginForm" onsubmit="return handleLogin(event)">
      <div class="field">
        <label>工号</label>
        <input type="text" id="userId" placeholder="请输入工号" autocomplete="off">
      </div>
      <div class="field">
        <label>密码</label>
        <input type="password" id="password" placeholder="请输入密码">
      </div>
      <button type="submit" class="btn">登 录</button>
      <div class="error" id="errorMsg"></div>
    </form>
  </div>
</div>
<script>
var USERS = {users_json};
function handleLogin(e) {{
  e.preventDefault();
  var id = document.getElementById('userId').value.trim();
  var pw = document.getElementById('password').value;
  var err = document.getElementById('errorMsg');
  var user = USERS.find(function(u) {{ return u.id === id; }});
  if (!user) {{ err.textContent = '工号不存在'; return false; }}
  if (user.password !== pw) {{ err.textContent = '密码错误'; return false; }}
  sessionStorage.setItem('kebei_user', JSON.stringify({{id: user.id, name: user.name, role: user.role}}));
  window.location.href = '/';
  return false;
}}
</script>
</body>
</html>"""
    with open(HERE / "login.html", "w", encoding="utf-8") as f:
        f.write(html)
    print(f"[build] login.html generated ({len(users)} users)")

def build_index(users, logo1_b64, logo2_b64):
    files = get_shared_files()
    files_json = json.dumps(files, ensure_ascii=False)
    current_user_script = ""
    for u in users:
        current_user_script += f"  {{id: '{u['id']}', name: '{u['name']}', role: '{u['role']}'}},\n"

    role_labels = {
        "admin": "管理员",
        "editor": "编辑者",
        "viewer": "查看者"
    }

    html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>多端文件共享 · 科贝智色</title>
<style>{STYLE_COMMON}
  .container {{
    position: relative; z-index: 1;
    max-width: 1200px; margin: 0 auto; padding: 32px 24px 80px;
  }}
  header {{
    display: flex; align-items: center; justify-content: space-between;
    padding: 16px 0; margin-bottom: 60px;
  }}
  .header-left {{
    display: flex; align-items: center; gap: 16px;
  }}
  .logo-left img {{ height: 36px; width: auto; opacity: 0.9; }}
  .logo-right {{
    display: flex; align-items: center; gap: 10px;
    text-decoration: none; color: var(--text);
  }}
  .logo-right img {{ height: 32px; width: auto; border-radius: 6px; }}
  .logo-right span {{
    font-size: 18px; font-weight: 600; letter-spacing: 2px;
    background: linear-gradient(135deg, #7c5cfc, #f97316);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
  }}
  .user-badge {{
    display: flex; align-items: center; gap: 8px;
    padding: 6px 14px 6px 10px;
    background: var(--surface); border: 1px solid var(--border);
    border-radius: 20px; font-size: 0.82rem;
  }}
  .user-badge .role-dot {{
    width: 7px; height: 7px; border-radius: 50%; display: inline-block;
  }}
  .role-dot.admin {{ background: #7c5cfc; }}
  .role-dot.editor {{ background: #f97316; }}
  .role-dot.viewer {{ background: #34d399; }}
  .user-badge .name {{ font-weight: 500; }}
  .user-badge .role-label {{ color: var(--text-muted); font-size: 0.75rem; }}
  .btn-logout {{
    padding: 6px 14px; background: transparent;
    border: 1px solid var(--border); border-radius: 20px;
    color: var(--text-secondary); font-size: 0.8rem;
    font-family: var(--font); cursor: pointer; transition: 0.2s;
  }}
  .btn-logout:hover {{
    background: rgba(255,255,255,0.06); color: var(--text);
  }}
  .hero {{
    text-align: center; margin-bottom: 64px;
  }}
  .hero h1 {{
    font-size: clamp(2.2rem, 6vw, 4rem); font-weight: 700; letter-spacing: -0.02em;
    background: linear-gradient(135deg, #fff 0%, rgba(255,255,255,0.6) 100%);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    margin-bottom: 12px;
  }}
  .hero p {{ font-size: 1.05rem; color: var(--text-secondary); font-weight: 400; }}
  .grid {{
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
    gap: 20px;
  }}
  .card {{
    background: var(--surface);
    backdrop-filter: blur(24px) saturate(1.4);
    -webkit-backdrop-filter: blur(24px) saturate(1.4);
    border: 1px solid var(--border); border-radius: var(--radius);
    padding: 24px; cursor: pointer; position: relative; overflow: hidden;
    transition: all 0.3s cubic-bezier(0.25,0.1,0.25,1);
    text-decoration: none; display: block; color: var(--text);
  }}
  .card::before {{
    content: ''; position: absolute; top: 0; left: 0; right: 0; height: 1px;
    background: linear-gradient(90deg, transparent, var(--border-hover), transparent);
    opacity: 0; transition: opacity 0.3s;
  }}
  .card:hover {{
    background: var(--surface-hover); border-color: var(--border-hover);
    transform: translateY(-4px);
    box-shadow: 0 12px 40px rgba(0,0,0,0.3), 0 0 0 1px rgba(255,255,255,0.05) inset;
  }}
  .card:hover::before {{ opacity: 1; }}
  .card h3 {{ font-size: 1rem; font-weight: 600; margin-bottom: 8px; line-height: 1.4; word-break: break-all; }}
  .card .meta {{ font-size: 0.82rem; color: var(--text-secondary); display: flex; align-items: center; gap: 6px; }}
  .empty {{
    grid-column: 1 / -1; text-align: center; padding: 80px 20px;
    color: var(--text-muted);
  }}
  .empty svg {{ width: 48px; height: 48px; margin-bottom: 16px; opacity: 0.3; }}
  footer {{ text-align: center; padding: 40px 0; color: var(--text-muted); font-size: 0.8rem; }}
  @media (max-width: 640px) {{
    .container {{ padding: 20px 16px 60px; }}
    header {{ margin-bottom: 40px; flex-direction: column; gap: 12px; }}
    .hero {{ margin-bottom: 40px; }}
    .grid {{ grid-template-columns: 1fr; }}
    .logo-right span {{ font-size: 15px; }}
  }}
</style>
</head>
<body>
<div class="container">
  <header>
    <div class="header-left">
      <a href="/" class="logo-left">
        <img src="data:image/png;base64,{logo1_b64}" alt="Logo">
      </a>
      <div id="userBadge"></div>
    </div>
    <div style="display:flex;align-items:center;gap:12px;">
      <a href="https://kebeizhise.cn" class="logo-right" target="_blank">
        <img src="data:image/png;base64,{logo2_b64}" alt="科贝智色">
        <span>科贝智色</span>
      </a>
      <button class="btn-logout" id="logoutBtn" onclick="handleLogout()">退出</button>
    </div>
  </header>

  <div class="hero">
    <h1>多端文件共享</h1>
    <p>内部文件 · 安全共享</p>
  </div>

  <div class="grid" id="fileGrid">
    <div class="empty" id="emptyState">
      <p>暂无共享文件</p>
    </div>
  </div>

  <footer>
    <p>Powered by 科贝智色 &middot; 内部文件共享平台</p>
  </footer>
</div>

<script>
var files = {files_json};
var roleLabels = {json.dumps(role_labels, ensure_ascii=False)};

function checkAuth() {{
  var raw = sessionStorage.getItem('kebei_user');
  if (!raw) {{ window.location.href = '/login.html'; return null; }}
  try {{ return JSON.parse(raw); }} catch(e) {{ window.location.href = '/login.html'; return null; }}
}}

function renderBadge(user) {{
  var badge = document.getElementById('userBadge');
  badge.innerHTML = '<span class="user-badge">'
    + '<span class="role-dot ' + user.role + '"></span>'
    + '<span class="name">' + user.name + '</span>'
    + '<span class="role-label">' + (roleLabels[user.role] || user.role) + '</span>'
    + '</span>';
}}

function handleLogout() {{
  sessionStorage.removeItem('kebei_user');
  window.location.href = '/login.html';
}}

function render() {{
  var user = checkAuth();
  if (!user) return;
  renderBadge(user);
  var grid = document.getElementById('fileGrid');
  if (!files.length) return;
  var empty = document.getElementById('emptyState');
  if (empty) empty.remove();
  grid.innerHTML = files.map(function(f) {{
    return '<a class="card" href="shared/' + encodeURIComponent(f.name) + '" target="_blank">'
      + '<h3>' + f.name.replace('.html', '') + '</h3>'
      + '<div class="meta">' + f.time + '</div>'
      + '</a>';
  }}).join('');
}}
render();
</script>
</body>
</html>"""
    with open(HERE / "index.html", "w", encoding="utf-8") as f:
        f.write(html)
    print(f"[build] index.html generated with {len(files)} shared file(s)")

    with open(FILES_JSON_PATH, "w", encoding="utf-8") as f:
        json.dump(files, f, ensure_ascii=False, indent=2)
    print(f"[build] files.json updated")

def build():
    logo1_b64 = b64encode(LOGO1_PATH)
    logo2_b64 = b64encode(LOGO2_PATH)
    users = load_users()
    build_login(users, logo1_b64, logo2_b64)
    build_index(users, logo1_b64, logo2_b64)

if __name__ == "__main__":
    build()
