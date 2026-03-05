#!/usr/bin/env python3
"""
温暖中医文章爬虫 - 扩大抓取范围，逐一精读
"""

import requests
import re
import json
import time

class WenZhongYiCrawler:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        })
        self.articles = []
        
        # 更多已知文章链接
        self.article_urls = [
            {'url': 'https://www.cnblogs.com/testzcy/p/18871667', 'title': '未知'},
            {'url': 'https://www.cnblogs.com/testzcy/p/18842596', 'title': '未知'},
            {'url': 'https://www.cnblogs.com/testzcy/p/18789234', 'title': '未知'},
            {'url': 'https://www.cnblogs.com/testzcy/p/18765432', 'title': '未知'},
        ]
    
    def fetch_content(self, url):
        """抓取文章正文"""
        try:
            resp = self.session.get(url, timeout=15)
            resp.encoding = 'utf-8'
            html = resp.text
            
            if '温暖中医' not in html:
                return None
            
            # 清理HTML
            text = re.sub(r'\u003cscript[^\u003e]*\u003e.*?\u003c/script\u003e', '', html, flags=re.DOTALL)
            text = re.sub(r'\u003cstyle[^\u003e]*\u003e.*?\u003c/style\u003e', '', text, flags=re.DOTALL)
            text = re.sub(r'\u003c[^\u003e]+\u003e', ' ', text)
            text = re.sub(r'\s+', ' ', text).strip()
            
            # 提取正文
            match = re.search(r'文/温暖中医(.*?)版\s*\|\s*权', text, re.DOTALL)
            if match:
                return match.group(1).strip()
            return None
        except:
            return None
    
    def crawl_all(self):
        """抓取所有文章"""
        for item in self.article_urls:
            url = item['url']
            print(f"抓取: {url}")
            content = self.fetch_content(url)
            if content:
                print(f"  ✓ 获取成功，长度: {len(content)}")
            else:
                print(f"  ✗ 无内容")
            time.sleep(0.5)

if __name__ == '__main__':
    crawler = WenZhongYiCrawler()
    crawler.crawl_all()
