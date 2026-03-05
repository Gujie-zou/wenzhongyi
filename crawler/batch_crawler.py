#!/usr/bin/env python3
"""
批量抓取温暖中医文章并精读
"""

import requests
import re
import json
import time

class BatchCrawler:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        })
        self.articles = []
        
        # 之前搜索到的文章链接
        self.urls = [
            'https://www.cnblogs.com/testzcy/p/18072171',  # 夏桑菊颗粒
            'https://www.cnblogs.com/testzcy/p/18641631',  # 减肥
            'https://www.cnblogs.com/testzcy/p/18667956',  # 荆防颗粒
            'https://www.cnblogs.com/testzcy/p/17920682.html',  # 金嗓利咽丸
            'https://www.cnblogs.com/testzcy/p/18084427',  # 附子理中丸
            'https://www.cnblogs.com/testzcy/p/18678614',  # 小青龙颗粒
            'https://www.cnblogs.com/testzcy/p/18174886',  # 黄连黄芩
            'https://www.cnblogs.com/testzcy/p/18678615',  # 益肝明目口服液
            'https://www.cnblogs.com/testzcy/p/18623717',  # 鼻炎
            'https://www.cnblogs.com/testzcy/p/18270539',  # 湿疹
            'https://www.cnblogs.com/testzcy/p/18543912',  # 丹鹿通督片
            'https://www.cnblogs.com/testzcy/p/17920669.html',  # 祛斑
        ]
    
    def fetch(self, url):
        try:
            resp = self.session.get(url, timeout=15)
            resp.encoding = 'utf-8'
            html = resp.text
            
            if '温暖中医' not in html:
                return None
            
            text = re.sub(r'\u003cscript[^\u003e]*\u003e.*?\u003c/script\u003e', '', html, flags=re.DOTALL)
            text = re.sub(r'\u003cstyle[^\u003e]*\u003e.*?\u003c/style\u003e', '', text, flags=re.DOTALL)
            text = re.sub(r'\u003c[^\u003e]+\u003e', ' ', text)
            text = re.sub(r'\s+', ' ', text).strip()
            
            match = re.search(r'文/温暖中医(.*?)版\s*\|\s*权', text, re.DOTALL)
            return match.group(1).strip() if match else None
        except:
            return None
    
    def analyze(self, content, url):
        if not content:
            return None
        
        # 提取药名
        medicine = self.extract_medicine(content)
        if not medicine:
            return None
        
        return {
            'url': url,
            'medicine_name': medicine,
            'category': self.categorize(content),
            'core_effect': self.extract_effect(content),
            'indications': self.extract_indications(content),
            'symptoms': self.extract_symptoms(content),
            'formula': self.extract_formula(content),
            'content': content[:1000],
        }
    
    def extract_medicine(self, text):
        patterns = [
            r'中成药(?:叫|名)\s*([\u4e00-\u9fa5]{2,12}(?:颗粒|丸|散|胶囊|片|口服液))',
            r'([\u4e00-\u9fa5]{2,8}(?:汤|方))[\s：:]',
        ]
        for p in patterns:
            m = re.search(p, text)
            if m:
                return m.group(1).strip()
        return None
    
    def categorize(self, text):
        if any(kw in text for kw in ['感冒', '风寒', '流感', '咳嗽']):
            return '感冒/咳嗽'
        if any(kw in text for kw in ['脾胃', '胃寒', '消化不良', '腹泻']):
            return '脾胃/消化'
        if any(kw in text for kw in ['色斑', '黄褐斑', '雀斑', '痤疮', '湿疹']):
            return '皮肤/美容'
        if any(kw in text for kw in ['颈椎', '肩周', '腰痛', '关节']):
            return '颈椎/关节'
        if any(kw in text for kw in ['鼻炎', '鼻塞', '流涕']):
            return '鼻炎/呼吸道'
        if any(kw in text for kw in ['眼睛', '明目', '近视', '肝血']):
            return '眼睛/肝血'
        if any(kw in text for kw in ['减肥', '肥胖', '消肿', '利水']):
            return '减肥/利水'
        if any(kw in text for kw in ['口臭', '上火', '溃疡']):
            return '口臭/上火'
        return '其他'
    
    def extract_effect(self, text):
        sentences = text.split('。')
        for s in sentences[:5]:
            if any(kw in s for kw in ['功效', '作用', '可以', '能够', '主治']) and 10 < len(s) < 80:
                return s.strip()
        return sentences[0][:60] if sentences else ''
    
    def extract_indications(self, text):
        indications = []
        if '感冒' in text:
            indications.append('感冒')
        if '风寒' in text:
            indications.append('风寒')
        if '咳嗽' in text:
            indications.append('咳嗽')
        if '鼻炎' in text:
            indications.append('鼻炎')
        if '脾胃' in text:
            indications.append('脾胃虚弱')
        if '色斑' in text or '黄褐斑' in text:
            indications.append('色斑')
        return indications
    
    def extract_symptoms(self, text):
        symptoms = []
        symptom_map = {
            '怕冷': '怕冷',
            '恶寒': '怕冷',
            '鼻塞': '鼻塞',
            '流涕': '流涕',
            '咳嗽': '咳嗽',
            '痰多': '痰多',
            '胃痛': '胃痛',
            '腹胀': '腹胀',
            '色斑': '色斑',
            '黄褐斑': '黄褐斑',
        }
        for kw, label in symptom_map.items():
            if kw in text:
                symptoms.append(label)
        return symptoms[:5]
    
    def extract_formula(self, text):
        pattern = r'([\u4e00-\u9fa5]{1,4})(?:\d+[-~]?\d*)\s*克'
        matches = re.findall(pattern, text)
        seen = set()
        herbs = []
        for m in matches:
            if m not in seen and m not in ['一次', '一天', '一个'] and len(m) >= 1:
                herbs.append(m)
                seen.add(m)
        return herbs[:10]
    
    def crawl_all(self):
        for url in self.urls:
            print(f"抓取: {url}")
            content = self.fetch(url)
            if content:
                analysis = self.analyze(content, url)
                if analysis:
                    self.articles.append(analysis)
                    print(f"  ✓ {analysis['medicine_name']} - {analysis['category']}")
                else:
                    print(f"  ✗ 无法识别药名")
            else:
                print(f"  ✗ 无内容")
            time.sleep(0.5)
        return self.articles

if __name__ == '__main__':
    crawler = BatchCrawler()
    articles = crawler.crawl_all()
    with open('/root/.openclaw/workspace/wenzhongyi/data/articles_batch.json', 'w', encoding='utf-8') as f:
        json.dump(articles, f, ensure_ascii=False, indent=2)
    print(f"\n共抓取 {len(articles)} 篇")
