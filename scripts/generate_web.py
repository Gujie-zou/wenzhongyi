#!/usr/bin/env python3
"""
生成温暖中医索引网站
"""

import json
import os

# 读取数据
with open('/root/.openclaw/workspace/wenzhongyi/data/articles.json', 'r', encoding='utf-8') as f:
    articles = json.load(f)

# 手动清理后的药名映射（从样本中提取的真实药名）
medicine_mapping = {
    '葛根汤': ['风寒感冒', '颈椎病', '肩周炎', '落枕'],
    '葛根汤颗粒': ['风寒感冒', '颈椎病', '肩周炎', '落枕'],
    '复方木尼孜其颗粒': ['黄褐斑', '雀斑', '色斑', '失眠'],
    '四君子汤': ['脾胃虚弱', '气血不足'],
    '健脾补血颗粒': ['脾胃虚弱', '贫血', '气血不足'],
    '藿香清胃胶囊': ['口臭', '胃火', '消化不良'],
    '泻黄散': ['脾胃伏火', '口臭', '口腔溃疡'],
    '栀子豉汤': ['虚烦', '失眠', '胸闷'],
    '龙胆泻肝汤': ['肝火旺', '口苦', '头晕'],
}

# 病症分类
disease_categories = {
    '感冒咳嗽': ['感冒', '风寒', '风热', '咳嗽', '发烧'],
    '结节肿块': ['结节', '甲状腺结节', '乳腺结节', '肺结节', '肌瘤', '囊肿'],
    '脾胃消化': ['脾胃', '胃寒', '胃胀', '消化不良', '脾虚', '腹泻', '便秘'],
    '失眠焦虑': ['失眠', '睡不着', '多梦', '心悸', '焦虑'],
    '皮肤美容': ['祛斑', '黄褐斑', '雀斑', '痤疮', '痘痘', '湿疹'],
    '颈椎肩周': ['颈椎', '肩周炎', '落枕', '肩颈', '背痛'],
    '妇科问题': ['妇科', '月经', '痛经', '宫寒', '更年期'],
    '心脑血管': ['高血压', '低血压', '头晕', '头痛'],
    '肝胆问题': ['肝', '胆', '黄疸', '口苦', '肝火'],
    '肾虚腰酸': ['肾', '腰酸', '肾虚', '水肿'],
    '风湿关节': ['风湿', '关节', '类风湿', '痛风'],
}

def generate_html():
    html = '''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>温暖中医 · 药方索引</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
            background: #f5f5f0;
            color: #333;
            line-height: 1.6;
        }
        .header {
            background: linear-gradient(135deg, #8B4513 0%, #A0522D 100%);
            color: white;
            padding: 2rem 1rem;
            text-align: center;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        .header h1 { font-size: 1.8rem; margin-bottom: 0.5rem; }
        .header p { opacity: 0.9; font-size: 0.9rem; }
        .container {
            max-width: 800px;
            margin: 0 auto;
            padding: 1rem;
        }
        .search-box {
            background: white;
            padding: 1rem;
            border-radius: 12px;
            margin: 1rem 0;
            box-shadow: 0 2px 8px rgba(0,0,0,0.05);
        }
        .search-box input {
            width: 100%;
            padding: 12px 16px;
            border: 2px solid #e0e0e0;
            border-radius: 8px;
            font-size: 16px;
            outline: none;
        }
        .search-box input:focus { border-color: #8B4513; }
        .tabs {
            display: flex;
            gap: 8px;
            margin: 1rem 0;
            overflow-x: auto;
        }
        .tab {
            flex: 1;
            padding: 12px;
            background: white;
            border: none;
            border-radius: 8px;
            cursor: pointer;
            font-size: 14px;
            white-space: nowrap;
            transition: all 0.3s;
        }
        .tab.active {
            background: #8B4513;
            color: white;
        }
        .section {
            background: white;
            border-radius: 12px;
            padding: 1rem;
            margin-bottom: 1rem;
            box-shadow: 0 2px 8px rgba(0,0,0,0.05);
        }
        .section-title {
            font-size: 1.1rem;
            color: #8B4513;
            margin-bottom: 1rem;
            padding-bottom: 0.5rem;
            border-bottom: 2px solid #f0e6dc;
        }
        .item {
            padding: 12px;
            border-radius: 8px;
            margin-bottom: 8px;
            background: #fafafa;
            transition: all 0.2s;
        }
        .item:hover { background: #f0e6dc; }
        .item-title {
            font-weight: 600;
            color: #333;
            margin-bottom: 4px;
        }
        .item-tags {
            display: flex;
            flex-wrap: wrap;
            gap: 6px;
            margin-top: 6px;
        }
        .tag {
            padding: 2px 8px;
            border-radius: 4px;
            font-size: 12px;
        }
        .tag-medicine { background: #e8f5e9; color: #2e7d32; }
        .tag-disease { background: #fff3e0; color: #ef6c00; }
        .item-link {
            display: inline-block;
            margin-top: 8px;
            color: #8B4513;
            text-decoration: none;
            font-size: 13px;
        }
        .item-link:hover { text-decoration: underline; }
        .hidden { display: none; }
        .footer {
            text-align: center;
            padding: 2rem;
            color: #999;
            font-size: 12px;
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>🏥 温暖中医</h1>
        <p>药方索引 · 对症检索</p>
    </div>
    
    <div class="container">
        <div class="search-box">
            <input type="text" id="search" placeholder="搜索药名或症状..." onkeyup="doSearch()">
        </div>
        
        <div class="tabs">
            <button class="tab active" onclick="showTab('disease')">按病症</button>
            <button class="tab" onclick="showTab('medicine')">按药名</button>
            <button class="tab" onclick="showTab('all')">全部文章</button>
        </div>
        
        <div id="disease-section" class="tab-content">
            <div class="section">
                <div class="section-title">🩺 按病症查找</div>
'''
    
    # 按病症分类
    for disease, articles_list in disease_categories.items():
        html += f'''
                <div class="item" data-search="{disease}">
                    <div class="item-title">{disease}</div>
                    <div class="item-tags">
'''
        # 找到对应的文章
        for art in articles:
            if any(d in art.get('diseases', []) for d in articles_list):
                for med in art.get('medicines', [])[:3]:
                    if len(med) < 10:  # 过滤噪声
                        html += f'<span class="tag tag-medicine">{med}</span>'
        html += '''
                    </div>
                </div>
'''
    
    html += '''
            </div>
        </div>
        
        <div id="medicine-section" class="tab-content hidden">
            <div class="section">
                <div class="section-title">💊 按药名查找</div>
'''
    
    # 按药名分类
    for med, diseases in medicine_mapping.items():
        html += f'''
                <div class="item" data-search="{med} {' '.join(diseases)}">
                    <div class="item-title">{med}</div>
                    <div class="item-tags">
'''
        for d in diseases:
            html += f'<span class="tag tag-disease">{d}</span>'
        html += '''
                    </div>
'''
        # 找到对应的文章链接
        for art in articles:
            if med in str(art.get('medicines', [])):
                html += f'<a href="{art["url"]}" class="item-link" target="_blank">查看原文 →</a>'
                break
        html += '''
                </div>
'''
    
    html += '''
            </div>
        </div>
        
        <div id="all-section" class="tab-content hidden">
            <div class="section">
                <div class="section-title">📚 全部文章</div>
'''
    
    # 全部文章
    for art in articles:
        html += f'''
                <div class="item" data-search="{art['title']} {' '.join(art.get('medicines', []))} {' '.join(art.get('diseases', []))}">
                    <div class="item-title">{art['title']}</div>
                    <div class="item-tags">
'''
        for med in art.get('medicines', [])[:5]:
            if len(med) < 15:
                html += f'<span class="tag tag-medicine">{med}</span>'
        for dis in art.get('diseases', []):
            html += f'<span class="tag tag-disease">{dis}</span>'
        html += f'''
                    </div>
                    <a href="{art['url']}" class="item-link" target="_blank">查看原文 →</a>
                </div>
'''
    
    html += '''
            </div>
        </div>
        
        <div class="footer">
            <p>数据来源：微信公众号「温暖中医」</p>
            <p>本站仅为索引整理，版权归原作者</p>
        </div>
    </div>
    
    <script>
        function showTab(tab) {
            document.querySelectorAll('.tab-content').forEach(el => el.classList.add('hidden'));
            document.getElementById(tab + '-section').classList.remove('hidden');
            document.querySelectorAll('.tab').forEach(el => el.classList.remove('active'));
            event.target.classList.add('active');
        }
        
        function doSearch() {
            const query = document.getElementById('search').value.toLowerCase();
            document.querySelectorAll('.item').forEach(item => {
                const text = item.getAttribute('data-search') || '';
                if (text.toLowerCase().includes(query)) {
                    item.style.display = 'block';
                } else {
                    item.style.display = 'none';
                }
            });
        }
    </script>
</body>
</html>
'''
    
    return html

# 生成HTML
html_content = generate_html()
output_path = '/root/.openclaw/workspace/wenzhongyi/web/index.html'
os.makedirs(os.path.dirname(output_path), exist_ok=True)

with open(output_path, 'w', encoding='utf-8') as f:
    f.write(html_content)

print(f"网站已生成: {output_path}")
print(f"文章数: {len(articles)}")
print(f"药名索引: {len(medicine_mapping)} 种")
print(f"病症分类: {len(disease_categories)} 类")
