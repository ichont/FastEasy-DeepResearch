"""
HTML报告生成器
支持生成带有交互式元素、数据可视化和多模态内容（图表、图像等）的HTML报告
"""

import os
import base64
import json
import re
from typing import List, Dict, Any
from datetime import datetime
def extract_key_points(content: str) -> List[str]:
    """从段落内容中提取关键点"""
    # 简单的关键点提取逻辑，可以根据需要进行优化
    sentences = content.split('。')
    key_points = []
    
    # 提取包含数字、关键词的句子作为关键点
    for sentence in sentences:
        sentence = sentence.strip()
        if sentence and (any(char.isdigit() for char in sentence) or 
                         any(keyword in sentence for keyword in ["重要", "关键", "主要", "核心", "显著", "提升", "降低", "增加", "减少"])):
            # 限制关键点长度
            if len(sentence) > 10 and len(sentence) < 200:
                key_points.append(sentence + "。")
    
    # 如果没有提取到足够的关键点，则取前几句
    if len(key_points) < 3:
        for sentence in sentences[:3]:
            sentence = sentence.strip()
            if sentence and len(sentence) > 10 and len(sentence) < 200:
                if sentence not in key_points:
                    key_points.append(sentence + "。")
    
    return key_points[:5]  # 最多返回5个关键点


def generate_visualization_data(paragraphs: List[Dict[str, str]]) -> Dict[str, Any]:
    """生成用于可视化的数据"""
    # 统计各段落字数
    word_counts = []
    titles = []
    
    for paragraph in paragraphs:
        titles.append(paragraph['title'])
        # 简单的字符计数作为字数统计
        word_counts.append(len(paragraph['content']))
    
    return {
        "labels": titles,
        "datasets": [{
            "label": "段落字数统计",
            "data": word_counts,
            "backgroundColor": [
                'rgba(255, 99, 132, 0.6)',
                'rgba(54, 162, 235, 0.6)',
                'rgba(255, 205, 86, 0.6)',
                'rgba(75, 192, 192, 0.6)',
                'rgba(153, 102, 255, 0.6)',
                'rgba(255, 159, 64, 0.6)'
            ],
            "borderColor": [
                'rgba(255, 99, 132, 1)',
                'rgba(54, 162, 235, 1)',
                'rgba(255, 205, 86, 1)',
                'rgba(75, 192, 192, 1)',
                'rgba(153, 102, 255, 1)',
                'rgba(255, 159, 64, 1)'
            ],
            "borderWidth": 1
        }]
    }


def generate_html_report(title: str, paragraphs: List[Dict[str, str]], output_dir: str, images: List[str] = None) -> str:
    """
    生成HTML格式的研究报告，包含交互式元素和数据可视化功能
    
    Args:
        title: 报告标题
        paragraphs: 段落数据列表，每个元素包含"title"和"content"键
        output_dir: 输出目录
        images: 图像Base64编码列表（可选）
        
    Returns:
        生成的HTML报告内容
    """
    # 生成可视化数据
    chart_data = generate_visualization_data(paragraphs)
    chart_data_json = json.dumps(chart_data, ensure_ascii=False)
    
    # 生成HTML内容
    html_content = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <!-- 引入Chart.js -->
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        /* 基础样式重置 */
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Segoe UI', 'Microsoft YaHei', sans-serif;
            line-height: 1.6;
            color: #333;
            background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
            min-height: 100vh;
            padding: 20px;
        }}
        
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 15px;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
            overflow: hidden;
        }}
        
        .header {{
            background: linear-gradient(135deg, #2c3e50 0%, #34495e 100%);
            color: white;
            padding: 40px 30px;
            text-align: center;
        }}
        
        .header h1 {{
            font-size: 2.5rem;
            margin-bottom: 10px;
            font-weight: 600;
        }}
        
        .header .subtitle {{
            font-size: 1.2rem;
            opacity: 0.9;
            font-weight: 300;
        }}
        
        .content {{
            padding: 40px 30px;
        }}
        
        .section {{
            margin-bottom: 40px;
            padding: 30px;
            background: #f8f9fa;
            border-radius: 10px;
            border-left: 5px solid #3498db;
            transition: transform 0.3s ease, box-shadow 0.3s ease;
        }}
        
        .section:hover {{
            transform: translateY(-5px);
            box-shadow: 0 5px 20px rgba(0, 0, 0, 0.1);
        }}
        
        .section h2 {{
            color: #2c3e50;
            font-size: 1.8rem;
            margin-bottom: 20px;
            padding-bottom: 10px;
            border-bottom: 2px solid #e9ecef;
        }}
        
        .section p {{
            font-size: 1.1rem;
            color: #555;
            text-align: justify;
            margin-bottom: 15px;
        }}
        
        .key-points {{
            background: linear-gradient(135deg, #fff3e0 0%, #ffe0b2 100%);
            padding: 20px;
            border-radius: 8px;
            margin: 20px 0;
            border-left: 4px solid #ff9800;
        }}
        
        .key-points h3 {{
            color: #e65100;
            margin-bottom: 15px;
        }}
        
        .key-points ul {{
            padding-left: 20px;
        }}
        
        .key-points li {{
            margin-bottom: 10px;
            color: #333;
        }}
        
        .stats-highlight {{
            background: linear-gradient(135deg, #e3f2fd 0%, #bbdefb 100%);
            padding: 20px;
            border-radius: 8px;
            margin: 20px 0;
            border-left: 4px solid #2196f3;
        }}
        
        .stats-highlight h3 {{
            color: #1976d2;
            margin-bottom: 15px;
        }}
        
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin: 25px 0;
        }}
        
        .stat-card {{
            background: white;
            padding: 20px;
            border-radius: 8px;
            text-align: center;
            box-shadow: 0 3px 10px rgba(0, 0, 0, 0.1);
            border-top: 4px solid #3498db;
        }}
        
        .stat-number {{
            font-size: 2rem;
            font-weight: bold;
            color: #2c3e50;
            margin-bottom: 10px;
        }}
        
        .stat-desc {{
            color: #666;
            font-size: 0.9rem;
        }}
        
        /* 图表容器样式 */
        .chart-container {{
            position: relative;
            height: 400px;
            margin: 30px 0;
            padding: 20px;
            background: #f8f9fa;
            border-radius: 10px;
        }}
        
        .conclusion {{
            background: linear-gradient(135deg, #e8f5e8 0%, #c8e6c9 100%);
            border-left: 5px solid #4caf50;
        }}
        
        .conclusion h2 {{
            color: #2e7d32;
        }}
        
        .footer {{
            background: #2c3e50;
            color: white;
            text-align: center;
            padding: 20px;
            font-size: 0.9rem;
        }}
        
        /* 交互控件样式 */
        .toggle-btn {{
            background: #3498db;
            color: white;
            border: none;
            padding: 10px 15px;
            border-radius: 5px;
            cursor: pointer;
            margin: 10px 5px;
            font-size: 0.9rem;
        }}
        
        .toggle-btn:hover {{
            background: #2980b9;
        }}
        
        .image-gallery {{
            display: flex;
            flex-wrap: wrap;
            gap: 20px;
            justify-content: center;
            margin: 30px 0;
        }}
        
        .image-container {{
            flex: 1 1 calc(50% - 20px);
            min-width: 300px;
            border-radius: 8px;
            overflow: hidden;
            box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        }}
        
        @media (max-width: 768px) {{
            .image-container {{
                flex: 1 1 100%;
            }}
        }}
        
        .hidden {{
            display: none;
        }}
        
        @media (max-width: 768px) {{
            .header h1 {{
                font-size: 2rem;
            }}
            
            .section {{
                padding: 20px;
            }}
            
            .stats-grid {{
                grid-template-columns: 1fr;
            }}
            
            .content {{
                padding: 20px 15px;
            }}
            
            .chart-container {{
                height: 300px;
                padding: 8px;
            }}
        }}
        
        @media (max-width: 480px) {{
            .header h1 {{
                font-size: 1.6rem;
            }}
            
            .section h2 {{
                font-size: 1.4rem;
            }}
            
            .stat-number {{
                font-size: 1.5rem;
            }}
            
            .chart-container {{
                height: 250px;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <header class="header">
            <h1>{title}</h1>
            <div class="subtitle">深度研究报告</div>
        </header>
        
        <main class="content">
            <!-- 数据可视化图表 -->
            <div class="chart-container">
                <canvas id="reportChart"></canvas>
            </div>
            
            <div style="text-align: center; margin-bottom: 30px;">
                <button class="toggle-btn" onclick="toggleAllSections()">展开/收起所有章节</button>
            </div>
"""

    # 添加各个段落
    for i, paragraph in enumerate(paragraphs):
        section_class = "section conclusion" if "结论" in paragraph["title"] or i == len(paragraphs) - 1 else "section"
        section_id = f"section-{i}"
        
        # 提取关键点
        key_points = extract_key_points(paragraph["content"])
        key_points_html = ""
        if key_points:
            key_points_html = '<div class="key-points"><h3>关键要点：</h3><ul>'
            for point in key_points:
                key_points_html += f"<li>{point}</li>"
            key_points_html += "</ul></div>"
        
        html_content += f"""
            <section class="{section_class}" id="{section_id}">
                <h2>{paragraph['title']} 
                    <button class="toggle-btn" onclick="toggleSection('{section_id}')">展开/收起</button>
                </h2>
                <div class="section-content">
                    <p>{paragraph['content'].replace(chr(10), '</p><p>')}</p>
                    {key_points_html}
                </div>
            </section>
"""

    # 添加图像内容（如果提供）
    if images:
        html_content += '<div class="image-gallery">'
        for i, img_base64 in enumerate(images):
            html_content += f'''
            <div class="image-container">
                <img src="data:image/jpeg;base64,{img_base64}" alt="图像 {i+1}" style="max-width: 100%; height: auto; border-radius: 8px;">
            </div>
            '''
        html_content += '</div>'
    
    # 添加页脚
    html_content += f"""
        </main>
        
        <footer class="footer">
            <p>{title} &copy; {datetime.now().year} 版权所有</p>
        </footer>
    </div>
    
    <script>
        // 渲染图表
        document.addEventListener('DOMContentLoaded', function() {{
            const ctx = document.getElementById('reportChart').getContext('2d');
            const chartData = {chart_data_json};
            
            new Chart(ctx, {{
                type: 'bar',
                data: chartData,
                options: {{
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: {{
                        y: {{
                            beginAtZero: true,
                            title: {{
                                display: true,
                                text: '字数'
                            }}
                        }}
                    }},
                    plugins: {{
                        title: {{
                            display: true,
                            text: '各段落字数统计'
                        }},
                        legend: {{
                            display: true,
                            position: 'top',
                        }}
                    }}
                }}
            }});
        }});
        
        // 切换章节显示/隐藏
        function toggleSection(sectionId) {{
            const section = document.getElementById(sectionId);
            const content = section.querySelector('.section-content');
            content.classList.toggle('hidden');
        }}
        
        // 切换所有章节显示/隐藏
        function toggleAllSections() {{
            const sections = document.querySelectorAll('.section-content');
            sections.forEach(section => {{
                section.classList.toggle('hidden');
            }});
        }}
        
        // 页面加载完成后默认收起所有章节内容
        document.addEventListener('DOMContentLoaded', function() {{
            // 可以在这里添加默认收起逻辑
        }});
    </script>
</body>
</html>
"""

    return html_content


def save_html_report(html_content: str, title: str, output_dir: str) -> str:
    """
    保存HTML报告到文件
    
    Args:
        html_content: HTML内容
        title: 报告标题
        output_dir: 输出目录
        
    Returns:
        保存的文件路径
    """
    # 确保输出目录存在
    os.makedirs(output_dir, exist_ok=True)
    
    # 生成文件名
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    query_safe = "".join(c for c in title if c.isalnum() or c in (' ', '-', '_')).rstrip()
    query_safe = query_safe.replace(' ', '_')[:30]
    
    filename = f"deep_search_report_{query_safe}_{timestamp}.html"
    filepath = os.path.join(output_dir, filename)
    
    # 保存HTML报告
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        # 验证文件是否成功写入且不为空
        if os.path.exists(filepath) and os.path.getsize(filepath) > 0:
            print(f"HTML报告已成功保存: {filepath}")
            print(f"文件大小: {os.path.getsize(filepath)} 字节")
            return filepath
        else:
            print(f"错误: HTML文件保存失败或文件为空: {filepath}")
            return None
    except Exception as e:
        print(f"保存HTML文件时出错: {e}")
        return None