# 温暖中医项目 - GitHub 部署指南

## 📋 项目信息
- **GitHub 用户名**：gujie-zou
- **仓库名**：wenzhongyi
- **在线网址**：https://gujie-zou.github.io/wenzhongyi/
- **本地路径**：`/root/.openclaw/workspace/wenzhongyi/`

---

## 🚀 首次部署到 GitHub Pages

### 第一步：在 GitHub 创建仓库
1. 访问 https://github.com
2. 点击右上角 `+` 号 → `New repository`
3. 填写信息：
   - Repository name: `wenzhongyi`
   - Description: `温暖中医 - 中成药方剂索引`
   - 选择 `Public`（公开）
4. 点击 `Create repository`

### 第二步：本地初始化并推送
```bash
# 进入项目目录
cd /root/.openclaw/workspace/wenzhongyi

# 初始化 Git 仓库
git init

# 添加远程仓库
git remote add origin https://github.com/gujie-zou/wenzhongyi.git

# 添加所有文件
git add .

# 提交更改
git commit -m "Initial commit: 温暖中医项目 - 10篇方剂"

# 推送到 GitHub
git branch -M main
git push -u origin main
```

### 第三步：开启 GitHub Pages
1. 打开 GitHub 仓库页面
2. 点击 `Settings`（设置）
3. 左侧菜单选择 `Pages`
4. Source 选择 `Deploy from a branch`
5. Branch 选择 `main` / `(root)`
6. 点击 `Save`

### 第四步：等待部署
- 约 2-5 分钟后访问：https://gujie-zou.github.io/wenzhongyi/

---

## 🔄 后续更新到 GitHub（每次有新文章时执行）

### 方法：命令行更新

```bash
# 1. 进入项目目录
cd /root/.openclaw/workspace/wenzhongyi

# 2. 查看文件状态（确认有更新）
git status

# 3. 添加所有更改
git add .

# 4. 提交更改（写清楚更新内容）
git commit -m "更新：新增X篇文章 - 药名1、药名2、药名3"

# 例如：
# git commit -m "更新：新增6篇文章 - 明目地黄丸、夏桑菊颗粒、胆石通胶囊、三七脂肝丸、辛芩颗粒、羌黄祛痹颗粒"

# 5. 推送到 GitHub
git push origin main
```

### 更新后
- GitHub Pages 会自动重新部署
- 约 2-5 分钟后，访问 https://gujie-zou.github.io/wenzhongyi/ 查看更新

---

## 📁 需要提交的文件

```
wenzhongyi/
├── PROJECT.md              # 项目说明文档
├── DEPLOY.md               # 本部署指南
├── data/
│   ├── articles_final.json    # 文章数据（重要）
│   ├── index_v2.json          # 索引数据
│   └── ...
├── web/
│   └── index.html          # 网站首页（重要）
├── crawler/                # 爬虫脚本
└── scripts/                # 生成脚本
```

---

## ⚠️ 常见问题

### Q1: 推送时提示需要用户名密码？
需要使用 GitHub Personal Access Token：
1. GitHub → Settings → Developer settings → Personal access tokens
2. 生成 Token，复制
3. 推送时密码处粘贴 Token

### Q2: 网站没有更新？
1. 确认已 `git push` 成功
2. 访问 GitHub 仓库 → Actions，查看部署状态
3. 等待 2-5 分钟缓存刷新

### Q3: 如何查看部署状态？
- GitHub 仓库 → Settings → Pages
- 绿色勾表示部署成功，黄色圆圈表示正在部署

---

## 📝 本次更新记录

**日期**：2026-03-05  
**更新内容**：
- 新增6篇文章
- 更新 PROJECT.md
- 更新 DEPLOY.md（本文件）
- 总计：10篇方剂

**执行命令**：
```bash
cd /root/.openclaw/workspace/wenzhongyi
git add .
git commit -m "更新：新增6篇文章 - 明目地黄丸、夏桑菊颗粒、胆石通胶囊、三七脂肝丸、辛芩颗粒、羌黄祛痹颗粒"
git push origin main
```
