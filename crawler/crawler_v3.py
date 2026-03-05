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
            
            text = re.sub(r'<script[^>]*>.*?</script>', '', html, flags=re.DOTALL)
            text = re.sub(r'<style[^>]*>.*?</style>', '', text, flags=re.DOTALL)
            text = re.sub(r'<[^>]+>', ' ', text)
            text = re.sub(r'\s+', ' ', text).strip()
            
            match = re.search(r'文/温暖中医(.*?)版\s*\|\s*权', text, re.DOTALL)
            if match:
                return match.group(1).strip()
            return None
        except Exception as e:
            return None
    
    def analyze_article(self, content, url):
        """精读文章"""
        if not content or len(content) < 200:
            return None
        
        return {
            'url': url,
            'medicine_name': self.extract_medicine_name(content),
            'formula': self.extract_formula(content),
            'indications': self.extract_indications(content),
            'symptoms': self.extract_symptoms(content),
            'core_effect': self.extract_core_effect(content),
            'content': content[:1500],
        }
    
    def extract_medicine_name(self, content):
        patterns = [
            r'中成药(?:叫|名)\s*([\u4e00-\u9fa5]{2,12}(?:颗粒|丸|散|胶囊|片))',
            r'([\u4e00-\u9fa5]{2,8}(?:汤|方))[\s：:]',
        ]
        for p in patterns:
            m = re.search(p, content)
            if m:
                return m.group(1).strip()
        return None
    
    def extract_formula(self, content):
        pattern = r'([\u4e00-\u9fa5]{1,4})\d+\s*克'
        matches = re.findall(pattern, content)
        seen = set()
        herbs = []
        for m in matches:
            if m not in seen and m not in ['一次', '一天']:
                herbs.append(m)
                seen.add(m)
        return herbs[:12]
    
    def extract_indications(self, content):
        indications = []
        patterns = [
            r'用于([\u4e00-\u9fa5、，]+?)(?:。|；)',
            r'治疗([\u4e00-\u9fa5、，]+?)(?:。|；)',
            r'主治([\u4e00-\u9fa5、，]+?)(?:。|；)',
        ]
        for p in patterns:
            m = re.search(p, content)
            if m:
                text = m.group(1)
                items = re.split(r'[、，,]', text)
                indications.extend([i.strip() for i in items if len(i.strip()) >= 2])
        return list(set(indications))[:5]
    
    def extract_symptoms(self, content):
        symptoms = []
        symptom_keywords = {
            '怕冷': '怕冷怕风',
            '后背僵硬': '后背僵硬',
            '感冒': '感冒',
            '色斑': '色斑黄褐斑',
            '脾胃': '脾胃虚弱',
            '气血不足': '气血不足',
            '口臭': '口臭',
            '口腔溃疡': '口腔溃疡',
        }
        for kw, label in symptom_keywords.items():
            if kw in content:
                symptoms.append(label)
        return symptoms
    
    def extract_core_effect(self, content):
        sentences = content.split('。')
        for s in sentences:
            if any(kw in s for kw in ['功效', '作用', '可以', '能够']) and len(s) > 10 and len(s) < 80:
                return s.strip()
        return sentences[0][:60] if sentences else ''
    
    def crawl_all(self):
        for item in self.article_urls:
            print(f"抓取: {item['url'][:50]}...")
            content = self.fetch_content(item['url'])
            if content:
                analysis = self.analyze_article(content, item['url'])
                if analysis and analysis['medicine_name']:
                    self.articles.append(analysis)
                    print(f"  ✓ {analysis['medicine_name']}")
                else:
                    print(f"  ✗ 无法识别药名")
            else:
                print(f"  ✗ 无内容")
            time.sleep(0.5)
        return self.articles

if __name__ == '__main__':
    crawler = WenZhongYiCrawler()
    articles = crawler.crawl_all()
    with open('/root/.openclaw/workspace/wenzhongyi/data/articles_new.json', 'w', encoding='utf-8') as f:
        json.dump(articles, f, ensure_ascii=False, indent=2)
    print(f"\n共抓取 {len(articles)} 篇")
