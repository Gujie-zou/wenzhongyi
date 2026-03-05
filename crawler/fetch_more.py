#!/usr/bin/env python3
"""
温暖中医文章精读 - 基于搜索结果的真实链接
"""

import requests
import re
import json
import time

# 真实的文章链接列表
ARTICLE_URLS = [
    # 已精读
    {'url': 'https://www.cnblogs.com/testzcy/p/18188726', 'name': '葛根汤颗粒'},
    {'url': 'https://www.cnblogs.com/testzcy/p/18922556', 'name': '复方木尼孜其颗粒'},
    {'url': 'https://www.163.com/dy/article/KEJ1RQG70552PZ4D.html', 'name': '健脾补血颗粒'},
    {'url': 'https://www.10100.com/article/27473726', 'name': '泻黄散'},
    
    # 新发现的文章
    {'url': 'https://www.cnblogs.com/testzcy/p/18072171', 'name': '夏桑菊颗粒'},
    {'url': 'https://www.cnblogs.com/testzcy/p/18641631', 'name': '减肥中成药'},
    {'url': 'https://www.cnblogs.com/testzcy/p/18667956', 'name': '荆防颗粒'},
    {'url': 'https://www.cnblogs.com/testzcy/p/17920682.html', 'name': '金嗓利咽丸'},
    {'url': 'https://www.cnblogs.com/testzcy/p/18084427', 'name': '附子理中丸'},
    {'url': 'https://www.cnblogs.com/testzcy/p/18678614', 'name': '小青龙颗粒'},
    {'url': 'https://www.cnblogs.com/testzcy/p/18174886', 'name': '幽门螺杆菌'},
    {'url': 'https://www.cnblogs.com/testzcy/p/18678615', 'name': '益肝明目口服液'},
    {'url': 'https://www.cnblogs.com/testzcy/p/18623717', 'name': '鼻炎药'},
    {'url': 'https://www.cnblogs.com/testzcy/p/18270539', 'name': '松花散'},
    {'url': 'https://www.cnblogs.com/testzcy/p/18543912', 'name': '丹鹿通督片'},
    {'url': 'https://www.cnblogs.com/testzcy/p/17920669.html', 'name': '祛斑中成药'},
]

def fetch_content(url):
    try:
        resp = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=15)
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

def analyze_carefully(content, url):
    """仔细分析文章内容"""
    if not content:
        return None
    
    result = {
        'url': url,
        'medicine_name': None,
        'formula': [],
        'indications': [],
        'symptoms': [],
        'core_effect': '',
        'key_points': [],
        'content_summary': content[:800],
    }
    
    # 提取药名
    med_patterns = [
        r'中成药(?:制剂)?(?:叫|名)\s*([\u4e00-\u9fa5]{2,12}(?:颗粒|丸|散|胶囊|片|口服液))',
        r'([\u4e00-\u9fa5]{2,8}(?:汤|方))[\s：:]',
        r'今天我们一起来学[\s\u3000]*[一-十]?[\s\u3000]*个[\s\u3000]*([\u4e00-\u9fa5]{2,12}(?:药|颗粒|丸|散))',
    ]
    for p in med_patterns:
        m = re.search(p, content)
        if m:
            result['medicine_name'] = m.group(1).strip()
            break
    
    # 提取方剂组成
    formula_match = re.findall(r'([\u4e00-\u9fa5]{1,4})(?:\d+[-~]?\d*)\s*克', content)
    seen = set()
    for herb in formula_match:
        if herb not in seen and herb not in ['一次', '一天', '一个', '这是', '可以']:
            result['formula'].append(herb)
            seen.add(herb)
    result['formula'] = result['formula'][:12]
    
    # 提取主治
    ind_patterns = [
        r'用于([\u4e00-\u9fa5、，]+?)(?:。|；)',
        r'治疗([\u4e00-\u9fa5、，]+?)(?:。|；)',
        r'主治([\u4e00-\u9fa5、，]+?)(?:。|；)',
    ]
    for p in ind_patterns:
        m = re.search(p, content)
        if m:
            items = re.split(r'[、，,]', m.group(1))
            result['indications'] = [i.strip() for i in items if len(i.strip()) >= 2][:5]
            break
    
    # 提取核心功效（找包含关键词的句子）
    sentences = content.split('。')
    for s in sentences:
        s = s.strip()
        if any(kw in s for kw in ['功效', '作用', '可以', '能够', '专门']) and 15 < len(s) < 100:
            result['core_effect'] = s
            break
    if not result['core_effect'] and sentences:
        result['core_effect'] = sentences[0][:80]
    
    return result

# 抓取并分析
articles = []
for item in ARTICLE_URLS[4:]:  # 从第5篇开始（前4篇已精读）
    print(f"\n抓取: {item['name']}")
    content = fetch_content(item['url'])
    if content:
        analysis = analyze_carefully(content, item['url'])
        if analysis and analysis['medicine_name']:
            articles.append(analysis)
            print(f"  ✓ {analysis['medicine_name']}")
            print(f"    主治: {analysis['indications'][:3]}")
        else:
            print(f"  ✗ 无法识别药名")
    else:
        print(f"  ✗ 无内容")
    time.sleep(0.5)

# 保存
with open('/root/.openclaw/workspace/wenzhongyi/data/articles_fetched.json', 'w', encoding='utf-8') as f:
    json.dump(articles, f, ensure_ascii=False, indent=2)

print(f"\n共抓取 {len(articles)} 篇新文章")
