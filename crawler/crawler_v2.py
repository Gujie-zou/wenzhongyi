#!/usr/bin/env python3
"""
温暖中医文章爬虫 - 仔细阅读每篇文章，准确提取信息
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
    
    def fetch_and_parse(self, url, title_hint=""):
        """抓取并仔细解析文章"""
        try:
            resp = self.session.get(url, timeout=15)
            resp.encoding = 'utf-8'
            html = resp.text
            
            if '温暖中医' not in html:
                return None
            
            # 提取正文（更精确）
            # 移除脚本和样式
            text = re.sub(r'\u003cscript[^\u003e]*\u003e.*?\u003c/script\u003e', '', html, flags=re.DOTALL)
            text = re.sub(r'\u003cstyle[^\u003e]*\u003e.*?\u003c/style\u003e', '', text, flags=re.DOTALL)
            text = re.sub(r'\u003c[^\u003e]+\u003e', ' ', text)
            text = re.sub(r'\s+', ' ', text).strip()
            
            # 找到"文/温暖中医"之后的正文
            match = re.search(r'文/温暖中医.*?(?=版权|声明|相关推荐|$)', text, re.DOTALL)
            if match:
                content = match.group(0)
            else:
                content = text[:3000]  # 取前3000字符
            
            return self.analyze_content(content, url)
        except Exception as e:
            print(f"  ✗ 抓取失败: {e}")
            return None
    
    def analyze_content(self, content, url):
        """仔细分析文章内容"""
        
        # 1. 提取标题（从文章第一句或内容推断）
        title = self.extract_title(content)
        
        # 2. 提取中成药/方剂名称（仔细识别）
        medicines = self.extract_medicines_carefully(content)
        
        # 3. 提取主治病症
        diseases = self.extract_diseases_carefully(content)
        
        # 4. 提取方剂组成
        formula = self.extract_formula_carefully(content)
        
        # 5. 提取关键功效描述
        effects = self.extract_effects(content)
        
        return {
            'title': title,
            'url': url,
            'medicines': medicines,
            'diseases': diseases,
            'formula': formula,
            'effects': effects,
            'content_summary': content[:500] + '...' if len(content) > 500 else content,
        }
    
    def extract_title(self, content):
        """从内容提取标题"""
        # 找第一个句号前的内容，通常包含主题
        lines = content.split('。')
        first_line = lines[0] if lines else content[:50]
        
        # 提取药名+功效作为标题
        med_match = re.search(r'(.*?)(?:颗粒|丸|散|胶囊|汤|方)(?:.*?(?:治疗|用于|针对|适用于))?(.*?)(?:。|；|$)', content)
        if med_match:
            medicine = med_match.group(0).strip()
            if len(medicine) < 50:
                return medicine
        
        return first_line[:40] if len(first_line) > 10 else "温暖中医文章"
    
    def extract_medicines_carefully(self, content):
        """仔细提取药名，过滤噪声"""
        medicines = []
        
        # 中成药模式（更严格）
        patterns = [
            r'([\u4e00-\u9fa5]{2,6}(?:颗粒|丸|散|胶囊|片|口服液))',
            r'([\u4e00-\u9fa5]{2,5}(?:汤|方|饮))',
        ]
        
        seen = set()
        for pattern in patterns:
            matches = re.findall(pattern, content)
            for m in matches:
                # 严格过滤
                if self.is_valid_medicine(m) and m not in seen:
                    medicines.append(m)
                    seen.add(m)
        
        return medicines
    
    def is_valid_medicine(self, name):
        """判断是否是有效药名"""
        # 排除常见干扰词
        invalid_words = ['这个', '那个', '什么', '怎么', '可以', '就是', '有一个', 
                        '中成药', '专门的', '此方', '此方剂', '这个方', '此方药',
                        '到体表', '个孩子', '央视女', '如有', '年才', '此前',
                        '纪录片', '联系', '费下载', '点击上方']
        
        for invalid in invalid_words:
            if invalid in name:
                return False
        
        # 长度检查
        if len(name) < 2 or len(name) > 12:
            return False
        
        return True
    
    def extract_diseases_carefully(self, content):
        """仔细提取病症"""
        disease_keywords = {
            '风寒感冒': ['风寒感冒', '受风寒', '怕冷怕风', '恶寒', '风寒侵袭'],
            '颈椎病': ['颈椎病', '颈椎', '肩颈', '后背僵硬', '项背强急'],
            '肩周炎': ['肩周炎', '肩膀', '肩部'],
            '落枕': ['落枕'],
            '脾胃虚弱': ['脾胃虚弱', '脾胃', '脾虚', '消化不良', '食欲不振'],
            '气血不足': ['气血不足', '气血', '贫血', '面色苍白'],
            '失眠': ['失眠', '睡不着', '多梦'],
            '黄褐斑': ['黄褐斑', '雀斑', '色斑', '祛斑'],
            '口臭': ['口臭', '口苦', '口腔异味'],
            '胃火': ['胃火', '脾胃伏火'],
            '肝火旺': ['肝火', '肝胆火旺'],
            '三焦之火': ['三焦', '上中下三焦'],
        }
        
        diseases = []
        for disease, keywords in disease_keywords.items():
            for kw in keywords:
                if kw in content:
                    diseases.append(disease)
                    break
        
        return diseases
    
    def extract_formula_carefully(self, content):
        """仔细提取方剂组成"""
        # 找"克"前面的药名和剂量
        pattern = r'([\u4e00-\u9fa5]{1,4})(\d+)[-~]?(\d*)\s*克'
        matches = re.findall(pattern, content)
        
        formulas = []
        seen = set()
        for m in matches:
            name = m[0]
            dose = m[1] + ('-' + m[2] if m[2] else '') + '克'
            
            # 过滤无效药名
            if name not in seen and len(name) >= 1 and len(name) <= 4:
                if name not in ['一次', '一天', '一个', '一次', '这是']:
                    formulas.append({'name': name, 'dose': dose})
                    seen.add(name)
        
        return formulas[:12]  # 最多12味药
    
    def extract_effects(self, content):
        """提取功效描述"""
        effects = []
        
        # 找功效描述模式
        patterns = [
            r'(?:可以|能够|具有|有)(.*?(?:作用|功效|效果|疗效))',
            r'(?:主治|适用于|针对)(.*?)(?:。|；)',
            r'(?:治疗|缓解|改善)(.*?)(?:。|；)',
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, content)
            effects.extend(matches[:2])
        
        return effects
    
    def crawl_articles(self):
        """抓取文章列表"""
        urls = [
            'https://www.cnblogs.com/testzcy/p/18188726',  # 葛根汤
            'https://www.cnblogs.com/testzcy/p/18922556',  # 复方木尼孜其颗粒
            'https://www.163.com/dy/article/KEJ1RQG70552PZ4D.html',  # 健脾补血颗粒
            'https://www.10100.com/article/27473726',  # 藿香清胃胶囊/泻黄散
        ]
        
        for url in urls:
            print(f"\n抓取: {url}")
            article = self.fetch_and_parse(url)
            if article:
                self.articles.append(article)
                print(f"  ✓ {article['title'][:40]}")
                print(f"    药: {article['medicines']}")
                print(f"    症: {article['diseases']}")
                print(f"    效: {article['effects'][:2] if article['effects'] else '无'}")
        
        return self.articles

if __name__ == '__main__':
    crawler = WenZhongYiCrawler()
    articles = crawler.crawl_articles()
    
    # 保存详细分析结果
    with open('/root/.openclaw/workspace/wenzhongyi/data/articles_detailed.json', 'w', encoding='utf-8') as f:
        json.dump(articles, f, ensure_ascii=False, indent=2)
    
    print(f"\n\n共分析 {len(articles)} 篇文章")
