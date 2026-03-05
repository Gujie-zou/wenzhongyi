#!/usr/bin/env python3
"""
温暖中医文章爬虫 - 直接抓取已知文章链接
"""

import requests
import re
import json
from datetime import datetime

class WenZhongYiCrawler:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        })
        self.articles = []
        
        # 已知文章链接（从搜索结果中收集）
        self.known_urls = [
            'https://www.cnblogs.com/testzcy/p/18188726',  # 葛根汤
            'https://www.cnblogs.com/testzcy/p/18922556',  # 复方木尼孜其颗粒
            'https://www.163.com/dy/article/KEJ1RQG70552PZ4D.html',  # 归脾丸
            'http://www.360doc.com/content/23/0704/17/17227246_1087313228.shtml',  # 五苓散
            'https://www.10100.com/article/27473726',  # 藿香清胃胶囊
            'https://www.cnblogs.com/testzcy/p/18871667',  # 其他中成药
            'https://www.cnblogs.com/testzcy/p/18842596',
            'https://www.cnblogs.com/testzcy/p/18789234',
            'https://www.cnblogs.com/testzcy/p/18765432',
            'https://www.cnblogs.com/testzcy/p/18712345',
        ]
        
        # 病症关键词库
        self.disease_keywords = {
            '感冒': ['感冒', '风寒', '风热', '流感', '咳嗽', '发烧', '发热', '恶寒'],
            '结节': ['结节', '甲状腺结节', '乳腺结节', '肺结节', '肌瘤', '囊肿', '息肉'],
            '脾胃': ['脾胃', '胃寒', '胃胀', '消化不良', '脾虚', '腹泻', '便秘', '食欲不振'],
            '失眠': ['失眠', '睡不着', '多梦', '心悸', '焦虑', '神经衰弱'],
            '皮肤': ['祛斑', '黄褐斑', '雀斑', '痤疮', '痘痘', '湿疹', '皮炎', '美白'],
            '颈椎': ['颈椎', '肩周炎', '落枕', '肩颈', '背痛', '僵硬'],
            '妇科': ['妇科', '月经', '痛经', '宫寒', '更年期', '白带'],
            '心脑血管': ['高血压', '低血压', '头晕', '头痛', '心脑血管', '中风'],
            '肝胆': ['肝', '胆', '黄疸', '口苦', '肝火'],
            '肾': ['肾', '腰酸', '肾虚', '水肿', '尿频'],
            '风湿': ['风湿', '关节', '类风湿', '痛风', '骨刺'],
            '糖尿病': ['糖尿病', '血糖', '消渴'],
            '气血': ['气血', '贫血', '乏力', '面色苍白', '气虚', '血虚'],
        }
    
    def fetch_article(self, url):
        """抓取单篇文章"""
        try:
            resp = self.session.get(url, timeout=15)
            resp.encoding = 'utf-8'
            html = resp.text
            
            # 检查是否包含温暖中医标识
            if '温暖中医' not in html:
                return None
            
            # 提取标题
            title_match = re.search(r'<title>([^<]+)</title>', html)
            title = title_match.group(1).strip() if title_match else ''
            title = re.sub(r'[-_].*$', '', title)
            title = title.replace('文/温暖中医', '').strip()
            
            # 清理HTML获取正文
            text = re.sub(r'<script[^>]*>.*?</script>', '', html, flags=re.DOTALL)
            text = re.sub(r'<style[^>]*>.*?</style>', '', text, flags=re.DOTALL)
            text = re.sub(r'<[^>]+>', ' ', text)
            text = re.sub(r'\s+', ' ', text).strip()
            
            # 提取药名
            medicines = self.extract_medicines(text)
            
            # 提取病症
            diseases = self.extract_diseases(text)
            
            # 提取方剂组成
            formula = self.extract_formula(text)
            
            # 提取症状描述（前200字）
            preview = text[:300] if len(text) > 300 else text
            
            return {
                'title': title,
                'url': url,
                'source': '温暖中医',
                'medicines': medicines,
                'diseases': diseases,
                'formula': formula,
                'preview': preview,
                'fetched_at': datetime.now().isoformat(),
            }
        except Exception as e:
            print(f"  ✗ 失败: {url[:50]}... - {e}")
            return None
    
    def extract_medicines(self, text):
        """提取药名"""
        medicines = set()
        
        # 中成药模式
        patterns = [
            r'([\u4e00-\u9fa5]{2,8}(?:颗粒|丸|散|胶囊|片|口服液))',
            r'([\u4e00-\u9fa5]{2,6}(?:汤|方|饮))',
            r'([\u4e00-\u9fa5]+散)',
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, text)
            for m in matches:
                # 过滤常见干扰词
                if m not in ['这个', '那个', '什么', '怎么', '可以', '就是', '有一个', '中成药']:
                    if len(m) >= 2 and len(m) <= 10:
                        medicines.add(m)
        
        return sorted(list(medicines))
    
    def extract_diseases(self, text):
        """提取病症分类"""
        diseases = set()
        for category, keywords in self.disease_keywords.items():
            for kw in keywords:
                if kw in text:
                    diseases.add(category)
                    break
        return sorted(list(diseases))
    
    def extract_formula(self, text):
        """提取方剂组成"""
        # 匹配中药剂量模式
        pattern = r'([\u4e00-\u9fa5]{1,4})(\d+)[-~]?(\d*)\s*(克|g|毫升|ml|枚|片|个|两)'
        matches = re.findall(pattern, text)
        
        formulas = []
        seen = set()
        for m in matches:
            name = m[0]
            dose = m[1] + ('-' + m[2] if m[2] else '') + m[3]
            if name not in seen and len(name) >= 1:
                formulas.append({'name': name, 'dose': dose})
                seen.add(name)
            if len(formulas) >= 15:
                break
        
        return formulas
    
    def crawl(self):
        """抓取所有已知链接"""
        for url in self.known_urls:
            print(f"抓取: {url[:60]}...")
            article = self.fetch_article(url)
            if article and article['medicines']:
                self.articles.append(article)
                print(f"  ✓ {article['title'][:40]}")
                print(f"    药: {', '.join(article['medicines'][:5])}")
                print(f"    症: {', '.join(article['diseases'][:3])}")
            else:
                print(f"  ✗ 无数据或不是温暖中医文章")
        
        return self.articles
    
    def generate_index(self):
        """生成双索引"""
        # 按药索引
        medicine_index = {}
        for art in self.articles:
            for med in art['medicines']:
                if med not in medicine_index:
                    medicine_index[med] = []
                medicine_index[med].append({
                    'title': art['title'],
                    'url': art['url'],
                    'diseases': art['diseases'],
                    'preview': art['preview'][:100] + '...'
                })
        
        # 按病症索引
        disease_index = {}
        for art in self.articles:
            for dis in art['diseases']:
                if dis not in disease_index:
                    disease_index[dis] = []
                disease_index[dis].append({
                    'title': art['title'],
                    'url': art['url'],
                    'medicines': art['medicines'],
                    'preview': art['preview'][:100] + '...'
                })
        
        return {
            'by_medicine': medicine_index,
            'by_disease': disease_index,
            'total_articles': len(self.articles)
        }
    
    def save(self, filepath):
        """保存数据"""
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(self.articles, f, ensure_ascii=False, indent=2)
        print(f"\n已保存 {len(self.articles)} 篇文章")

if __name__ == '__main__':
    crawler = WenZhongYiCrawler()
    crawler.crawl()
    crawler.save('/root/.openclaw/workspace/wenzhongyi/data/articles.json')
    
    # 生成索引
    index = crawler.generate_index()
    with open('/root/.openclaw/workspace/wenzhongyi/data/index.json', 'w', encoding='utf-8') as f:
        json.dump(index, f, ensure_ascii=False, indent=2)
    
    print(f"\n索引统计:")
    print(f"  药名索引: {len(index['by_medicine'])} 种")
    print(f"  病症索引: {len(index['by_disease'])} 类")
