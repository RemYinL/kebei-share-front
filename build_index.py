"""Generate index.html with embedded base64 assets."""
import json
import os
from pathlib import Path

HERE = Path(__file__).resolve().parent
SHARED_DIR = HERE / "shared"
LOGO1_PATH = Path("/mnt/c/Users/22602/Desktop/图片1.png")
LOGO2_PATH = Path("/mnt/c/Users/22602/Desktop/kebeizhise/参考资料/科贝智色logo.PNG")
FILES_JSON_PATH = HERE / "files.json"

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

def build():
    logo1_b64 = b64encode(LOGO1_PATH)
    logo2_b64 = b64encode(LOGO2_PATH)
    files = get_shared_files()
    files_json = json.dumps(files, ensure_ascii=False)

    html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>多端文件共享 · 科贝智色</title>
<style>
  *, *::before, *::after {{ margin: 0; padding: 0; box-sizing: border-box; }}
  @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Noto+Sans+SC:wght@300;400;500;700&display=swap');
  :root {{
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
  }}
  html, body {{ height: 100%; overflow-x: hidden; }}
  body {{
    font-family: var(--font);
    background: var(--bg);
    color: var(--text);
    min-height: 100vh;
    position: relative;
  }}
  body::before {{
    content: '';
    position: fixed;
    top: -50%;
    left: -50%;
    width: 200%;
    height: 200%;
    background:
      radial-gradient(ellipse 80% 60% at 20% 20%, rgba(124,92,252,0.06) 0%, transparent 60%),
      radial-gradient(ellipse 60% 50% at 80% 80%, rgba(249,115,22,0.04) 0%, transparent 60%),
      radial-gradient(ellipse 50% 40% at 50% 50%, rgba(59,130,246,0.03) 0%, transparent 50%);
    pointer-events: none;
    z-index: 0;
  }}
  .container {{
    position: relative;
    z-index: 1;
    max-width: 1200px;
    margin: 0 auto;
    padding: 32px 24px 80px;
  }}
  header {{
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 16px 0;
    margin-bottom: 60px;
  }}
  .logo-left img {{ height: 36px; width: auto; opacity: 0.9; }}
  .logo-right {{
    display: flex;
    align-items: center;
    gap: 10px;
    text-decoration: none;
    color: var(--text);
  }}
  .logo-right img {{ height: 32px; width: auto; border-radius: 6px; }}
  .logo-right span {{
    font-size: 18px;
    font-weight: 600;
    letter-spacing: 2px;
    background: linear-gradient(135deg, #7c5cfc, #f97316);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
  }}
  .hero {{
    text-align: center;
    margin-bottom: 64px;
  }}
  .hero h1 {{
    font-size: clamp(2.2rem, 6vw, 4rem);
    font-weight: 700;
    letter-spacing: -0.02em;
    background: linear-gradient(135deg, #fff 0%, rgba(255,255,255,0.6) 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin-bottom: 12px;
  }}
  .hero p {{
    font-size: 1.05rem;
    color: var(--text-secondary);
    font-weight: 400;
  }}
  .grid {{
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
    gap: 20px;
  }}
  .card {{
    background: var(--surface);
    backdrop-filter: blur(24px) saturate(1.4);
    -webkit-backdrop-filter: blur(24px) saturate(1.4);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 24px;
    transition: all 0.3s cubic-bezier(0.25,0.1,0.25,1);
    cursor: pointer;
    position: relative;
    overflow: hidden;
  }}
  .card::before {{
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 1px;
    background: linear-gradient(90deg, transparent, var(--border-hover), transparent);
    opacity: 0;
    transition: opacity 0.3s;
  }}
  .card:hover {{
    background: var(--surface-hover);
    border-color: var(--border-hover);
    transform: translateY(-4px);
    box-shadow: 0 12px 40px rgba(0,0,0,0.3), 0 0 0 1px rgba(255,255,255,0.05) inset;
  }}
  .card:hover::before {{ opacity: 1; }}
  .card h3 {{
    font-size: 1rem;
    font-weight: 600;
    margin-bottom: 8px;
    line-height: 1.4;
    word-break: break-all;
  }}
  .card .meta {{
    font-size: 0.82rem;
    color: var(--text-secondary);
    display: flex;
    align-items: center;
    gap: 6px;
  }}
  .empty {{
    grid-column: 1 / -1;
    text-align: center;
    padding: 80px 20px;
    color: var(--text-muted);
  }}
  .empty svg {{ width: 48px; height: 48px; margin-bottom: 16px; opacity: 0.3; }}
  footer {{
    text-align: center;
    padding: 40px 0;
    color: var(--text-muted);
    font-size: 0.8rem;
  }}
  @media (max-width: 640px) {{
    .container {{ padding: 20px 16px 60px; }}
    header {{ margin-bottom: 40px; }}
    .hero {{ margin-bottom: 40px; }}
    .grid {{ grid-template-columns: 1fr; }}
  }}
</style>
</head>
<body>
<div class="container">
  <header>
    <a href="/" class="logo-left">
      <img src="data:image/png;base64,{logo1_b64}" alt="Logo">
    </a>
    <a href="https://kebeizhise.cn" class="logo-right" target="_blank">
      <img src="data:image/png;base64,{logo2_b64}" alt="科贝智色">
      <span>科贝智色</span>
    </a>
  </header>

  <div class="hero">
    <h1>多端文件共享</h1>
    <p>拖入 HTML 文件即可分享 · 全平台无缝访问</p>
  </div>

  <div class="grid" id="fileGrid">
    <div class="empty" id="emptyState">
      <p>暂无共享文件</p>
    </div>
  </div>

  <footer>
    <p>Powered by 科贝智色 &middot; 多端文件共享</p>
  </footer>
</div>

<script>
const files = {files_json};

function render() {{
  const grid = document.getElementById('fileGrid');
  if (!files.length) return;
  const empty = document.getElementById('emptyState');
  if (empty) empty.remove();
  grid.innerHTML = files.map(f => `
    <a class="card" href="shared/${{f.name}}" target="_blank">
      <h3>${{f.name.replace('.html', '')}}</h3>
      <div class="meta">${{f.time}}</div>
    </a>
  `).join('');
}}
render();
</script>
</body>
</html>"""
    with open(HERE / "index.html", "w", encoding="utf-8") as f:
        f.write(html)
    print(f"[build] index.html generated with {len(files)} shared file(s)")

    # also write files.json for any dynamic use
    with open(FILES_JSON_PATH, "w", encoding="utf-8") as f:
        json.dump(files, f, ensure_ascii=False, indent=2)
    print(f"[build] files.json updated")

if __name__ == "__main__":
    build()
