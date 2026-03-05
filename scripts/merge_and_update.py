#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
合并新文章并更新温暖中医网站
"""

import json
from datetime import datetime

# 读取现有数据
with open('/root/.openclaw/workspace/wenzhongyi/data/articles_final.json', 'r', encoding='utf-8') as f:
    existing = json.load(f)

with open('/root/.openclaw/workspace/wenzhongyi/data/articles_fetched_new.json', 'r', encoding='utf-8') as f:
    new_articles = json.load(f)

# 现有文章ID
existing_ids = {a['id'] for a in existing['articles']}
next_id = max(existing_ids) + 1 if existing_ids else 1

# 新文章列表
new_added = []

# 转换新文章格式
for article in new_articles:
    # 检查是否已存在（通过URL）
    url_exists = any(a['url'] == article['url'] for a in existing['articles'])
    if url_exists:
        print(f"跳过已存在: {article['title'][:30]}")
        continue
    
    # 确定分类
    diseases = article.get('diseases', [])
    medicines = article.get('medicines', [])
    
    # 分类映射
    category = "其他"
    if any(d in diseases for d in ['感冒', '风寒', '风热', '流感']):
        category = "感冒/发热"
    elif any(d in diseases for d in ['眼睛干涩', '眼睛胀痛', '视物不清', '眼痒', '肝火旺']):
        category = "眼睛/肝火"
    elif any(d in diseases for d in ['颈椎病', '肩颈僵硬', '肩周炎', '落枕']):
        category = "颈椎/肩周"
    elif any(d in diseases for d in ['胆结石', '胆囊炎', '脂肪肝', '肝痞']):
        category = "肝胆/消化"
    elif any(d in diseases for d in ['鼻炎', '鼻塞', '鼻涕']):
        category = "鼻炎/呼吸"
    elif any(d in diseases for d in ['黄褐斑', '色斑', '痤疮', '湿疹']):
        category = "皮肤/美容"
    elif any(d in diseases for d in ['脾胃虚弱', '胃胀', '胃痛', '口臭']):
        category = "脾胃/消化"
    elif any(d in diseases for d in ['气血不足', '贫血']):
        category = "气血/补益"
    
    # 构建新条目
    new_entry = {
        "id": next_id,
        "medicine_name": medicines[0] if medicines else "未知",
        "original_formula": medicines[1] if len(medicines) > 1 else None,
        "category": category,
        "core_effect": article.get('preview', '')[:100] + "...",
        "formula_composition": [],
        "indications": diseases,
        "symptoms": diseases,
        "key_points": [article.get('preview', '')[:200]],
        "source": "微信公众号「温暖中医」",
        "url": article['url'],
        "author_note": "",
        "fetched_at": article.get('fetched_at', datetime.now().isoformat())
    }
    
    existing['articles'].append(new_entry)
    new_added.append(new_entry)
    next_id += 1
    print(f"✓ 新增: {new_entry['medicine_name']} ({category})")

# 保存合并后的数据
with open('/root/.openclaw/workspace/wenzhongyi/data/articles_final.json', 'w', encoding='utf-8') as f:
    json.dump(existing, f, ensure_ascii=False, indent=2)

print(f"\n共新增 {len(new_added)} 篇文章")
print(f"总计 {len(existing['articles'])} 篇文章")

# 生成索引
categories = {}
for article in existing['articles']:
    cat = article['category']
    if cat not in categories:
        categories[cat] = []
    categories[cat].append({
        'id': article['id'],
        'name': article['medicine_name'],
        'effect': article['core_effect'][:50] + '...'
    })

# 保存索引
with open('/root/.openclaw/workspace/wenzhongyi/data/index_v2.json', 'w', encoding='utf-8') as f:
    json.dump(categories, f, ensure_ascii=False, indent=2)

print("\n索引分类:")
for cat, items in sorted(categories.items()):
    print(f"  {cat}: {len(items)} 篇")
