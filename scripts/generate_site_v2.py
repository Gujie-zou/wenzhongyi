#!/usr/bin/env python3
"""生成完整网站 - 从articles_final.json"""
import json

with open('/root/.openclaw/workspace/wenzhongyi/data/articles_final.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

articles = data['articles']

# 按分类分组
categories = {}
for art in articles:
    cat = art['category']
    if cat not in categories:
        categories[cat] = []
    categories[cat].append(art)

# 生成HTML
html = '''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>温暖中医 · 药方索引</title>
<style>
* { margin: 0; padding: 0; box-sizing: border-box; }
body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; background: linear-gradient(135deg, #f5f0e8 0%, #e8e0d5 100%); color: #4a4a4a; line-height: 1.8; min-height: 100vh; }
.header { background: linear-gradient(135deg, #8B4513 0%, #A0522D 100%); color: white; padding: 2.5rem 1rem; text-align: center; box-shadow: 0 4px 20px rgba(139, 69, 19, 0.3); }
.header h1 { font-size: 2rem; margin-bottom: 0.5rem; letter-spacing: 2px; }
.source-note { background: #fff8f0; border-left: 4px solid #8B4513; padding: 1rem 1.5rem; margin: 1.5rem auto; max-width: 900px; border-radius: 0 8px 8px 0; font-size: 0.9rem; color: #666; }
.container { max-width: 900px; margin: 0 auto; padding: 1rem; }
.search-box { background: white; padding: 1.2rem; border-radius: 12px; margin: 1.5rem 0; box-shadow: 0 2px 12px rgba(0,0,0,0.08); }
.search-box input { width: 100%; padding: 14px 20px; border: 2px solid #e8e0d5; border-radius: 10px; font-size: 16px; outline: none; }
.search-box input:focus { border-color: #8B4513; }
.tabs { display: flex; gap: 10px; margin: 1.5rem 0; background: white; padding: 6px; border-radius: 12px; box-shadow: 0 2px 12px rgba(0,0,0,0.06); }
.tab { flex: 1; padding: 12px; border: none; background: transparent; border-radius: 8px; cursor: pointer; font-size: 15px; color: #666; transition: all 0.3s; }
.tab.active { background: #8B4513; color: white; font-weight: 500; }
.tab-content { display: none; }
.tab-content.active { display: block; }
.medicine-card { background: white; border-radius: 16px; padding: 1.5rem; margin-bottom: 1.2rem; box-shadow: 0 4px 15px rgba(0,0,0,0.06); cursor: pointer; transition: all 0.3s; }
.medicine-card:hover { transform: translateY(-3px); box-shadow: 0 8px 25px rgba(139, 69, 19, 0.15); }
.medicine-name { font-size: 1.3rem; font-weight: 600; color: #8B4513; margin-bottom: 0.5rem; }
.medicine-effect { color: #666; font-size: 0.95rem; margin-bottom: 0.8rem; }
.medicine-tags { display: flex; flex-wrap: wrap; gap: 8px; }
.tag { padding: 5px 12px; border-radius: 20px; font-size: 0.85rem; }
.tag-symptom { background: #fff3e0; color: #e65100; }
.tag-category { background: #e8f5e9; color: #2e7d32; }
.detail-panel { display: none; margin-top: 1.5rem; padding-top: 1.5rem; border-top: 1px dashed #e0d5c8; }
.detail-panel.active { display: block; }
.detail-panel h4 { color: #8B4513; margin: 1rem 0 0.5rem; font-size: 1rem; }
.detail-panel p { color: #555; font-size: 0.95rem; margin-bottom: 0.8rem; line-height: 1.8; }
.source-link { display: inline-block; background: #8B4513; color: white; padding: 10px 20px; border-radius: 8px; text-decoration: none; margin-top: 0.5rem; font-size: 0.9rem; }
.category-section { margin-bottom: 2rem; }
.category-title { font-size: 1.2rem; color: #8B4513; font-weight: 600; margin-bottom: 1rem; padding-bottom: 0.5rem; border-bottom: 2px solid #e8e0d5; }
.footer { text-align: center; padding: 3rem 2rem; color: #999; font-size: 0.85rem; }
.update-time { text-align: center; color: #999; font-size: 0.8rem; margin-top: 0.5rem; }
</style>
</head>
<body>
<div class="header"><h1>🏥 温暖中医</h1><p>药方索引 · 对症检索 · 精读整理</p></div>
<div class="source-note"><strong>📚 内容来源</strong>：本网站所有内容均整理自微信公众号「温暖中医」，仅供个人学习参考。版权归原作者及原公众号所有。</div>
<div class="container">
<div class="search-box"><input type="text" id="search" placeholder="搜索药名、症状或病症..." onkeyup="doSearch()"></div>
<div class="tabs">
<button class="tab active" onclick="switchTab('by-medicine')">💊 按方剂(''' + str(len(articles)) + ''')</button>
<button class="tab" onclick="switchTab('by-disease')">🩺 按病症(''' + str(len(categories)) + ''')</button>
</div>
'''

# 按方剂
html += '''<div id="by-medicine" class="tab-content active">'''
for art in articles:
    tags = ''.join([f'<span class="tag tag-symptom">{s}</span>' for s in art['symptoms'][:4]])
    formula_str = '、'.join([f["name"] + (f" {f['dose']}" if f.get('dose') else '') for f in art.get('formula_composition', [])[:6]])
    if not formula_str:
        formula_str = "详见原文"
    
    html += f'''
<div class="medicine-card" onclick="toggleDetail('med-{art['id']}')">
<div class="medicine-name">{art['medicine_name']}</div>
<div class="medicine-effect">{art['core_effect']}</div>
<div class="medicine-tags"><span class="tag tag-category">{art['category']}</span>{tags}</div>
<div id="med-{art['id']}" class="detail-panel" onclick="event.stopPropagation()">
<h4>📋 方剂组成</h4><p>{formula_str}</p>
<h4>🎯 主治</h4><p>{'、'.join(art['indications'])}</p>
<h4>😷 适用症状</h4><p>{'、'.join(art['symptoms'])}</p>
<a href="{art['url']}" class="source-link" target="_blank">查看原文 →</a>
</div></div>'''
html += '</div>'

# 按病症
html += '''<div id="by-disease" class="tab-content">'''
for cat in sorted(categories.keys()):
    arts = categories[cat]
    html += f'''
<div class="category-section">
<div class="category-title">{cat} ({len(arts)}篇)</div>
'''
    for art in arts:
        html += f'''
<div class="medicine-card" onclick="toggleDetail('dis-{art['id']}')">
<div class="medicine-name">{art['medicine_name']}</div>
<div class="medicine-effect">{art['core_effect']}</div>
<div id="dis-{art['id']}" class="detail-panel" onclick="event.stopPropagation()">
<h4>🎯 主治</h4><p>{'、'.join(art['indications'])}</p>
<h4>💡 要点</h4><p>{art['key_points'][0] if art.get('key_points') else ''}</p>
<a href="{art['url']}" class="source-link" target="_blank">查看原文 →</a>
</div></div>'''
    html += '</div>'
html += '</div>'

html += '''
</div>
<div class="update-time">最后更新：2026年3月5日</div>
<div class="footer">
<p>内容整理自微信公众号「温暖中医」</p>
<p>本站仅供个人学习参考，版权归原作者</p>
<p>© 2026 温暖中医索引 · 共''' + str(len(articles)) + '''篇方剂</p>
</div>
<script>
function switchTab(n){document.querySelectorAll('.tab').forEach(t=>t.classList.remove('active'));event.target.classList.add('active');document.querySelectorAll('.tab-content').forEach(c=>c.classList.remove('active'));document.getElementById(n).classList.add('active');}
function toggleDetail(i){document.querySelectorAll('.detail-panel').forEach(p=>p.classList.remove('active'));var d=document.getElementById(i);if(d.classList.contains('active')){d.classList.remove('active');}else{d.classList.add('active');}}
function doSearch(){var q=document.getElementById('search').value.toLowerCase();document.querySelectorAll('.medicine-card').forEach(c=>c.style.display=c.innerText.toLowerCase().includes(q)?'block':'none');}
</script>
</body></html>'''

with open('/root/.openclaw/workspace/wenzhongyi/web/index.html', 'w', encoding='utf-8') as f:
    f.write(html)

print(f"✓ 网站已更新：{len(articles)}篇方剂，{len(categories)}个病症分类")
print("\n分类统计:")
for cat, arts in sorted(categories.items()):
    print(f"  {cat}: {len(arts)}篇")
    for a in arts:
        print(f"    - {a['medicine_name']}")
