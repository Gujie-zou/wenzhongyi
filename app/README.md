# 温暖中医 App

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
