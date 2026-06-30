# 多端文件共享 · 科贝智色

Cloudflare Pages 静态文件共享平台，绑定 `share.hnust-kebei.uk`。

## 项目结构

```
html-share/
├── index.html              # 前端主页面（内嵌 base64 logo + 文件列表）
├── build_index.py          # 构建脚本
├── sync.py                 # 同步+部署工具（核心入口）
├── files.json              # 共享文件元数据（自动生成）
├── shared/                 # 存放共享的 .html 文件
├── cloudflare.toml.example # Cloudflare 配置模板
├── workspace/              # 工作区记忆 & 日志
└── README.md
```

## 使用方式

添加/更新/删除 `shared/` 中的 `.html` 文件后运行：

```bash
python sync.py              # 构建 + 自动部署到 Cloudflare
python sync.py --no-deploy  # 仅构建，跳过部署
python sync.py --deploy-only# 仅部署，不重新构建
python sync.py --watch      # 监听模式（需 pip install watchdog）
```

## 首次部署配置

```bash
cp cloudflare.toml.example cloudflare.toml
# 编辑 cloudflare.toml 填入 api_token 和 account_id
```

## 分支命名规范

`opencode-YY/MM/DD/HH-主要修改概述`
