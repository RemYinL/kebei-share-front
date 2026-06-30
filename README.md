# 多端文件共享 · 科贝智色

基于 Cloudflare Pages 的静态文件共享平台。

## 项目结构

```
html-share/
├── index.html          # 前端主页面（内嵌 logo 与文件列表）
├── build_index.py      # 构建脚本（将 base64 logo 嵌入 HTML）
├── sync.py             # 同步工具（新增/更新/删除 .html 文件后运行）
├── files.json          # 共享文件元数据（自动生成）
├── shared/             # 存放共享的 .html 文件
│   └── 创投审查.html
├── workspace/           # 工作区记忆目录
│   ├── progress.json   # 开发进度
│   └── sync.log        # 同步日志
└── README.md
```

## 使用方式

### 添加共享文件
将 `.html` 文件放入 `shared/` 目录，然后运行：

```bash
python sync.py
```

### 自动监听模式
```bash
python sync.py --watch    # 需要 pip install watchdog
```

### 手动构建
```bash
python build_index.py
```

## 部署

Cloudflare Pages 绑定域名 `share.hnust-kebei.uk`，静态部署整个目录即可。

## 分支命名规范

`opencode-YY/MM/DD/HH-主要修改概述`
