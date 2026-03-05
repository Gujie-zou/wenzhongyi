#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
温暖中医文章爬虫 - 多平台搜索抓取
尝试从知乎、简书、今日头条等平台抓取
"""

import requests
import json
import re
import time
from datetime import datetime
from urllib.parse import quote

# 搜索关键词列表
SEARCH_QUERIES = [
    "温暖中医 中成药",
    "温暖中医 方剂",
    "温暖中医 感冒",
    "温暖中医 脾胃",
    "温暖中医 气血"
]

# User-Agent
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
}

def search_zhihu(query):
    """搜索知乎"""
    try:
        url = f"https://www.zhihu.com/api/v4/search_v3?t=general&q={quote(query)}"
        resp = requests.get(url, headers=HEADERS, timeout=10)
        if resp.status_code == 200:
            data = resp.json()
            articles = []
            for item in data.get('data', []):
                if item.get('type') == 'search_result':
                    obj = item.get('object', {})
                    if '温暖中医' in obj.get('content', ''):
                        articles.append({
                            'title': obj.get('title', ''),
                            'url': obj.get('url', ''),
                            'source': '知乎'
                        })
            return articles
    except Exception as e:
        print(f"  知乎搜索失败: {e}")
    return []

def search_jianshu(query):
    """搜索简书"""
    try:
        url = f"https://www.jianshu.com/search/do?q={quote(query)}&type=note"
        resp = requests.get(url, headers=HEADERS, timeout=10)
        if resp.status_code == 200:
            data = resp.json()
            articles = []
            for item in data.get('entries', []):
                if '温暖中医' in item.get('title', '') or '温暖中医' in item.get('content', ''):
                    articles.append({
                        'title': item.get('title', ''),
                        'url': f"https://www.jianshu.com/p/{item.get('slug', '')}",
                        'source': '简书'
                    })
            return articles
    except Exception as e:
        print(f"  简书搜索失败: {e}")
    return []

def search_bing(query):
    """使用Bing搜索找到相关文章链接"""
    try:
        url = f"https://www.bing.com/search?q={quote(query + ' 温暖中医')}"
        resp = requests.get(url, headers=HEADERS, timeout=10)
        if resp.status_code == 200:
            html = resp.text
            # 提取链接
            links = re.findall(r'href="(https?://[^"]+)"', html)
            # 过滤出可能的 article 链接
            articles = []
            for link in links:
                if any(x in link for x in ['zhihu.com', 'jianshu.com', 'sohu.com', '163.com', 'qq.com']):
                    if '温暖中医' in link or 'wenzhongyi' in link.lower():
                        articles.append({
                            'title': '待抓取',
                            'url': link,
                            'source': 'Bing搜索'
                        })
            return articles[:10]  # 限制数量
    except Exception as e:
        print(f"  Bing搜索失败: {e}")
    return []

def fetch_article(url):
    """抓取单篇文章内容"""
    try:
        resp = requests.get(url, headers=HEADERS, timeout=15)
        resp.encoding = 'utf-8'
        html = resp.text
        
        # 检查是否包含温暖中医
        if '温暖中医' not in html:
            return None
        
        # 提取标题
        title_match = re.search(r'<title>(.*?)</title>', html, re.DOTALL)
        title = title_match.group(1).strip() if title_match else "未知标题"
        title = re.sub(r'[\n\r\t]', '', title)
        
        # 提取正文（简化版）
        text = re.sub(r'<script[^>]*>.*?</script>', '', html, flags=re.DOTALL)
        text = re.sub(r'<style[^>]*>.*?</style>', '', text, flags=re.DOTALL)
        text = re.sub(r'<[^>]+>', '\n', text)
        text = re.sub(r'\n+', '\n', text)
        
        # 找到"温暖中医"相关段落
        lines = text.split('\n')
        content_lines = []
        capture = False
        for line in lines:
            line = line.strip()
            if '温暖中医' in line or '文/' in line:
                capture = True
            if capture and len(line) > 10:
                content_lines.append(line)
            if len(content_lines) > 50:  # 限制长度
                break
        
        content = '\n'.join(content_lines[:30])
        
        # 提取药名（简单规则）
        medicines = []
        medicine_keywords = ['颗粒', '胶囊', '丸', '散', '汤', '口服液', '片']
        for line in content_lines[:20]:
            for keyword in medicine_keywords:
                if keyword in line and len(line) < 50:
                    # 提取可能的药名
                    matches = re.findall(r'([\u4e00-\u9fa5]{2,8})' + keyword, line)
                    medicines.extend(matches)
        
        # 提取病症
        diseases = []
        disease_keywords = ['感冒', '咳嗽', '胃痛', '胃胀', '口臭', '上火', '色斑', '气血不足', '脾胃', '肝火', '风寒', '风热']
        for keyword in disease_keywords:
            if keyword in content:
                diseases.append(keyword)
        
        return {
            'title': title,
            'url': url,
            'source': '温暖中医',
            'medicines': list(set(medicines))[:10],
            'diseases': list(set(diseases)),
            'preview': content[:300] + '...' if len(content) > 300 else content,
            'fetched_at': datetime.now().isoformat()
        }
    except Exception as e:
        print(f"  抓取失败 {url}: {e}")
        return None

def main():
    print("=" * 60)
    print("温暖中医文章爬虫 - 多平台搜索")
    print("=" * 60)
    
    all_articles = []
    
    # 使用Bing搜索找链接
    for query in SEARCH_QUERIES[:2]:  # 先搜2个关键词
        print(f"\n🔍 搜索: {query}")
        links = search_bing(query)
        print(f"  找到 {len(links)} 个可能链接")
        
        for item in links[:5]:  # 每个关键词抓5篇
            url = item['url']
            print(f"\n  抓取: {url[:60]}...")
            article = fetch_article(url)
            if article:
                print(f"  ✓ 成功: {article['title'][:40]}")
                print(f"    药名: {', '.join(article['medicines'][:5]) or '无'}")
                print(f"    病症: {', '.join(article['diseases']) or '无'}")
                all_articles.append(article)
            else:
                print(f"  ✗ 失败")
            time.sleep(1)
    
    # 保存结果
    print(f"\n" + "=" * 60)
    print(f"共抓取 {len(all_articles)} 篇新文章")
    
    if all_articles:
        output_file = '/root/.openclaw/workspace/wenzhongyi/data/articles_fetched_new.json'
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(all_articles, f, ensure_ascii=False, indent=2)
        print(f"已保存到: {output_file}")
    else:
        print("未找到新文章")
    
    return all_articles

if __name__ == '__main__':
    main()
