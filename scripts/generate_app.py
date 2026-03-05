#!/usr/bin/env python3
"""
生成Android App (PWA封装)
使用WebView封装网站
"""

import os
import zipfile

# 创建PWA配置文件
manifest_json = '''{
  "name": "温暖中医",
  "short_name": "温暖中医",
  "description": "药方索引 · 对症检索",
  "start_url": "/",
  "display": "standalone",
  "background_color": "#8B4513",
  "theme_color": "#8B4513",
  "icons": [
    {
      "src": "icon-192.png",
      "sizes": "192x192",
      "type": "image/png"
    },
    {
      "src": "icon-512.png",
      "sizes": "512x512",
      "type": "image/png"
    }
  ]
}
'''

# 创建service worker (离线缓存)
sw_js = '''
const CACHE_NAME = 'wenzhongyi-v1';
const urlsToCache = [
  '/',
  '/index.html'
];

self.addEventListener('install', event => {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then(cache => cache.addAll(urlsToCache))
  );
});

self.addEventListener('fetch', event => {
  event.respondWith(
    caches.match(event.request)
      .then(response => {
        if (response) return response;
        return fetch(event.request);
      })
  );
});
'''

# 读取原HTML并添加PWA支持
with open('/root/.openclaw/workspace/wenzhongyi/web/index.html', 'r', encoding='utf-8') as f:
    html_content = f.read()

# 在head中添加PWA支持
pwa_meta = '''
    <link rel="manifest" href="manifest.json">
    <meta name="theme-color" content="#8B4513">
    <link rel="apple-touch-icon" href="icon-192.png">
    <script>
        if ('serviceWorker' in navigator) {
            navigator.serviceWorker.register('sw.js');
        }
    </script>
'''

# 插入到</head>之前
html_content = html_content.replace('</head>', pwa_meta + '</head>')

# 保存文件
output_dir = '/root/.openclaw/workspace/wenzhongyi/app'
os.makedirs(output_dir, exist_ok=True)

# 保存HTML
with open(f'{output_dir}/index.html', 'w', encoding='utf-8') as f:
    f.write(html_content)

# 保存manifest
with open(f'{output_dir}/manifest.json', 'w', encoding='utf-8') as f:
    f.write(manifest_json)

# 保存service worker
with open(f'{output_dir}/sw.js', 'w', encoding='utf-8') as f:
    f.write(sw_js)

# 创建简单的SVG图标并转换为PNG（用base64占位）
# 实际使用时需要真实图标文件

# 创建Android WebView项目结构
android_project = f'''{output_dir}/android/'''
os.makedirs(android_project, exist_ok=True)

# 创建简单的WebView APK打包脚本
webview_html = '''<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>温暖中医</title>
    <style>
        body { margin: 0; overflow: hidden; }
        iframe { width: 100vw; height: 100vh; border: none; }
    </style>
</head>
<body>
    <iframe src="../index.html"></iframe>
</body>
</html>
'''

with open(f'{android_project}/wrapper.html', 'w') as f:
    f.write(webview_html)

# 创建Cordova项目结构说明
readme = '''# 温暖中医 App

## 安装方法

### 方法1: PWA (推荐)
1. 用手机浏览器打开网站
2. 点击"添加到主屏幕"
3. 即可像App一样使用

### 方法2: Android APK
需要构建APK文件：

```bash
# 使用Cordova构建
npm install -g cordova
cordova create wenzhongyi-app com.wenzhongyi.app "温暖中医"
cd wenzhongyi-app
cordova platform add android
cordova build android
```

### 方法3: 直接安装
下载 `wenzhongyi-app.zip`，解压后用浏览器打开 `index.html`

## 功能
- 按病症查找药方
- 按药名查找适应症
- 搜索功能
- 离线缓存(PWA)
'''

with open(f'{output_dir}/README.md', 'w') as f:
    f.write(readme)

# 打包App文件
app_files = ['index.html', 'manifest.json', 'sw.js']
with zipfile.ZipFile(f'{output_dir}/wenzhongyi-app.zip', 'w') as zf:
    for f in app_files:
        zf.write(f'{output_dir}/{f}', f)

print(f"App文件已生成:")
print(f"  - {output_dir}/index.html (主文件)")
print(f"  - {output_dir}/wenzhongyi-app.zip (打包文件)")
print(f"  - {output_dir}/README.md (安装说明)")
print(f"\n使用方法:")
print(f"  1. 下载 wenzongyi-app.zip")
print(f"  2. 解压后用手机浏览器打开 index.html")
print(f"  3. 添加到主屏幕即可像App使用")
