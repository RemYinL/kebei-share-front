#!/usr/bin/env python3
"""
sync.py — 共享文件同步工具

用法:
  python sync.py             扫描 shared/ 并重建 index.html
  python sync.py --watch     持续监听 shared/ 目录变化（需安装 watchdog）

当您在 shared/ 中新增/更新/删除 .html 文件后运行此脚本，
它会自动更新 files.json 和 index.html，使前端保持同步。
"""
import argparse
import json
import os
import sys
import time
from datetime import datetime, timezone, timedelta
from pathlib import Path

HERE = Path(__file__).resolve().parent
SHARED_DIR = HERE / "shared"
FILES_JSON = HERE / "files.json"
BUILD_SCRIPT = HERE / "build_index.py"
LOG_FILE = HERE / "workspace" / "sync.log"
CF_CONFIG = HERE / "cloudflare.toml"


def log(msg):
    ts = datetime.now(timezone(timedelta(hours=8))).strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{ts}] {msg}"
    print(line)
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(line + "\n")


def scan_shared():
    files = []
    if not SHARED_DIR.exists():
        SHARED_DIR.mkdir(parents=True)
        return files
    for f in sorted(SHARED_DIR.iterdir()):
        if f.suffix.lower() == ".html":
            mtime = f.stat().st_mtime
            tz = timezone(timedelta(hours=8))
            ts = datetime.fromtimestamp(mtime, tz).strftime("%Y-%m-%d %H:%M:%S")
            files.append({"name": f.name, "time": ts})
    return files


def build_index():
    """调用 build_index.py 重建 index.html"""
    import subprocess
    result = subprocess.run(
        [sys.executable, str(BUILD_SCRIPT)],
        capture_output=True, text=True, cwd=HERE
    )
    if result.returncode != 0:
        log(f"build_index.py FAILED: {result.stderr}")
        return False
    for line in result.stdout.strip().split("\n"):
        if line:
            log(line)
    return True


def sync(skip_deploy=False):
    log("=== 开始同步 ===")
    files = scan_shared()
    with open(FILES_JSON, "w", encoding="utf-8") as f:
        json.dump(files, f, ensure_ascii=False, indent=2)
    log(f"files.json updated: {len(files)} file(s)")

    if BUILD_SCRIPT.exists():
        build_index()
    else:
        log("WARNING: build_index.py not found, index.html not rebuilt")

    if not skip_deploy:
        deploy_cloudflare()

    log("=== 同步完成 ===")


def load_cf_config():
    if not CF_CONFIG.exists():
        return None
    try:
        import tomllib
        with open(CF_CONFIG, "rb") as f:
            cfg = tomllib.load(f)
    except ImportError:
        try:
            import tomli as tomllib
            with open(CF_CONFIG, "rb") as f:
                cfg = tomllib.load(f)
        except ImportError:
            import configparser
            cfg_parser = configparser.ConfigParser()
            cfg_parser.read(CF_CONFIG)
            section = cfg_parser["cloudflare"] if cfg_parser.has_section("cloudflare") else {}
            return {
                "api_token": section.get("api_token", ""),
                "account_id": section.get("account_id", ""),
                "project_name": section.get("project_name", "kebei-share"),
            }
    return cfg.get("cloudflare", {})


def deploy_cloudflare():
    import subprocess
    cfg = load_cf_config()
    if not cfg:
        log("cloudflare.toml not found, skipping deploy")
        return

    token = cfg.get("api_token", "")
    account_id = cfg.get("account_id", "")
    project = cfg.get("project_name", "kebei-share")
    if not token or not account_id:
        log("CF config incomplete (api_token/account_id), skipping deploy")
        return

    log("=== 部署到 Cloudflare Pages ===")
    env = os.environ.copy()
    env["CLOUDFLARE_API_TOKEN"] = token
    env["CLOUDFLARE_ACCOUNT_ID"] = account_id

    result = subprocess.run(
        ["npx", "-y", "wrangler@latest", "pages", "deploy",
         "--project-name", project, "--branch", "main", "."],
        capture_output=True, text=True, cwd=HERE, env=env, timeout=180
    )
    for line in result.stdout.strip().split("\n"):
        if line:
            log(line.strip())
    if result.stderr:
        for line in result.stderr.strip().split("\n"):
            if line and "wrangler" in line.lower():
                log(line.strip())
    if result.returncode != 0:
        log(f"部署失败 (rc={result.returncode})")
    else:
        log("部署成功!")


def watch():
    try:
        from watchdog.observers import Observer
        from watchdog.events import FileSystemEventHandler
    except ImportError:
        print("请先安装 watchdog: pip install watchdog")
        sys.exit(1)

    class Handler(FileSystemEventHandler):
        def on_any_event(self, event):
            if event.src_path.endswith(".html"):
                time.sleep(0.5)  # debounce
                sync()

    log("=== 启动监听模式 ===")
    observer = Observer()
    observer.schedule(Handler(), str(SHARED_DIR), recursive=False)
    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="共享文件同步工具")
    parser.add_argument("--watch", action="store_true", help="持续监听 shared/ 目录变化")
    parser.add_argument("--no-deploy", action="store_true", help="跳过 Cloudflare 部署")
    parser.add_argument("--deploy-only", action="store_true", help="仅部署，不扫描/构建")
    args = parser.parse_args()

    if args.deploy_only:
        deploy_cloudflare()
    elif args.watch:
        watch()
    else:
        sync(skip_deploy=args.no_deploy)
