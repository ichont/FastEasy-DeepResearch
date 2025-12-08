import requests
import json
import re
import os
from datetime import datetime
import sys

# 添加项目根目录到Python路径
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))

# 从根目录的config.py导入配置
from config import DEEPSEEK_API_KEY

# 获取脚本所在目录，确保相对路径在任何位置都能正确工作
def get_script_dir():
    """获取脚本所在目录，确保相对路径在任何位置都能正确工作"""
    return os.path.dirname(os.path.abspath(__file__))

def call_deepseek_api(prompt):
    """
    调用DeepSeek API获取数据提取结果
    """
    url = "https://api.deepseek.com/v1/chat/completions"
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {DEEPSEEK_API_KEY}"
    }
    
    data = {
        "model": "deepseek-chat",
        "messages": [
            {
                "role": "system",
                "content": "你是一个数据提取和图表制作专家，擅长从文本中提取结构化数据并生成图表配置。"
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        "temperature": 0.3,
        "max_tokens": 2000
    }
    
    try:
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        result = response.json()
        return result['choices'][0]['message']['content']
    except Exception as e:
        print(f"DeepSeek API调用失败: {e}")
        return None

def extract_chart_data(txt_content):
    """
    使用DeepSeek AI从TXT内容中提取图表数据
    
    Args:
        txt_content: TXT文件内容
        
    Returns:
        dict: 包含图表数据的字典
    """
    prompt = f"""
    请从以下文本内容中提取图表数据，并按照指定的JSON格式返回。
    
    文本内容:
    {txt_content}
    
    请按照以下JSON格式返回数据，不要添加任何其他文字说明：
    {{
        "charts": [
            {{
                "type": "bar",
                "title": "图表标题",
                "xAxisLabel": "横轴标签",
                "yAxisLabel": "纵轴标签",
                "data": [
                    {{"label": "标签1", "value": 数值1}},
                    {{"label": "标签2", "value": 数值2}}
                ]
            }},
            {{
                "type": "line",
                "title": "图表标题",
                "xAxisLabel": "横轴标签",
                "yAxisLabel": "纵轴标签",
                "data": [
                    {{"label": "标签1", "value": 数值1}},
                    {{"label": "标签2", "value": 数值2}}
                ]
            }},
            {{
                "type": "pie",
                "title": "图表标题",
                "data": [
                    {{"label": "标签1", "value": 百分比数值1}},
                    {{"label": "标签2", "value": 百分比数值2}}
                ]
            }}
        ]
    }}
    
    注意事项：
    1. 数值应该是数字类型，不要包含单位或百分号
    2. 饼图数据应该是百分比数值（如32.93而不是32.93%）
    3. 如果文本中有多个相同类型的图表，请提取最完整的一个
    4. 确保JSON格式正确，可以被直接解析
    """
    
    response = call_deepseek_api(prompt)
    
    # 尝试提取JSON部分
    if response:
        try:
            # 查找JSON部分
            json_match = re.search(r'\{[\s\S]*\}', response)
            if json_match:
                json_str = json_match.group()
                return json.loads(json_str)
            else:
                # 如果没有找到JSON，尝试直接解析整个响应
                return json.loads(response)
        except json.JSONDecodeError as e:
            print(f"JSON解析错误: {e}")
            print(f"原始响应: {response}")
            return None
    
    return None

def generate_chart_analysis(txt_content, chart_data):
    """
    使用DeepSeek AI生成图表分析
    
    Args:
        txt_content: TXT文件内容
        chart_data: 图表数据
        
    Returns:
        dict: 包含每个图表分析的字典
    """
    analysis_results = {}
    
    if 'charts' not in chart_data:
        return analysis_results
    
    for i, chart in enumerate(chart_data['charts']):
        chart_type = chart.get('type', 'unknown')
        chart_title = chart.get('title', f'图表 {i+1}')
        chart_data_list = chart.get('data', [])
        
        # 准备数据摘要
        data_summary = ""
        if chart_type == 'bar':
            labels = [item['label'] for item in chart_data_list]
            values = [item['value'] for item in chart_data_list]
            max_value = max(values) if values else 0
            max_label = labels[values.index(max_value)] if values and max_value in values else ""
            data_summary = f"柱状图包含{len(labels)}个类别，最大值为{max_label}({max_value})"
        elif chart_type == 'line':
            labels = [item['label'] for item in chart_data_list]
            values = [item['value'] for item in chart_data_list]
            if len(values) >= 2:
                trend = "上升" if values[-1] > values[0] else "下降"
                change_rate = ((values[-1] - values[0]) / values[0]) * 100 if values[0] != 0 else 0
                data_summary = f"折线图显示{trend}趋势，变化率为{change_rate:.2f}%"
        elif chart_type == 'pie':
            labels = [item['label'] for item in chart_data_list]
            values = [item['value'] for item in chart_data_list]
            max_value = max(values) if values else 0
            max_label = labels[values.index(max_value)] if values and max_value in values else ""
            data_summary = f"饼图包含{len(labels)}个部分，最大部分为{max_label}({max_value}%)"
        
        prompt = f"""
        请基于以下图表信息，提供简洁专业的数据分析（100字以内）：
        
        图表标题: {chart_title}
        图表类型: {chart_type}
        数据摘要: {data_summary}
        
        原始数据上下文:
        {txt_content[:500]}...
        
        请提供简洁的数据分析，重点突出关键洞察和趋势，不要超过100字。
        """
        
        analysis = call_deepseek_api(prompt)
        if analysis:
            analysis_results[f"chart_{i}"] = analysis.strip()
    
    return analysis_results

def generate_html(chart_data, report_info, analysis_results, user_query=None):
    """
    生成包含图表的HTML页面
    
    Args:
        chart_data: 图表数据
        report_info: 报告信息
        analysis_results: 图表分析结果
        user_query: 用户搜索关键词
        
    Returns:
        str: HTML内容
    """
    # 根据用户查询生成动态标题
    if user_query:
        title = f"{user_query}数据可视化报告"
        header_title = f"{user_query}数据可视化报告"
    else:
        title = "数据可视化报告"
        header_title = "数据可视化报告"
    
    html_content = f"""
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <script>
        // Chart.js将通过CDN加载，确保离线可用
    </script>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
        
        * {{
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Inter', 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 0;
            background: linear-gradient(135deg, #f5f7fa 0%, #e4e8f0 100%);
            color: #2d3748;
            line-height: 1.6;
        }}
        
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }}
        
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 40px 30px;
            border-radius: 16px;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
            margin-bottom: 30px;
            text-align: center;
        }}
        
        h1 {{
            font-size: 2.5rem;
            font-weight: 700;
            margin: 0 0 10px 0;
            letter-spacing: -0.5px;
        }}
        
        .subtitle {{
            font-size: 1.1rem;
            opacity: 0.9;
            margin: 0;
            font-weight: 400;
        }}
        
        .report-info {{
            display: flex;
            justify-content: center;
            gap: 30px;
            margin-top: 20px;
            flex-wrap: wrap;
        }}
        
        .info-item {{
            background: rgba(255, 255, 255, 0.2);
            padding: 10px 20px;
            border-radius: 30px;
            font-size: 0.9rem;
        }}
        
        .chart-container {{
            background: white;
            border-radius: 16px;
            box-shadow: 0 8px 25px rgba(0, 0, 0, 0.08);
            margin-bottom: 30px;
            overflow: hidden;
            transition: transform 0.3s ease, box-shadow 0.3s ease;
        }}
        
        .chart-container:hover {{
            transform: translateY(-5px);
            box-shadow: 0 12px 35px rgba(0, 0, 0, 0.12);
        }}
        
        .chart-header {{
            padding: 25px 30px 15px;
            border-bottom: 1px solid #eaeaea;
        }}
        
        .chart-title {{
            font-size: 1.5rem;
            font-weight: 600;
            color: #2d3748;
            margin: 0 0 5px 0;
        }}
        
        .chart-subtitle {{
            color: #718096;
            font-size: 0.9rem;
            margin: 0;
        }}
        
        .chart-wrapper {{
            position: relative;
            height: 400px;
            padding: 20px 30px;
        }}
        
        .chart-analysis {{
            background: #f7fafc;
            padding: 20px 30px;
            border-top: 1px solid #eaeaea;
        }}
        
        .analysis-title {{
            font-size: 1.1rem;
            font-weight: 600;
            color: #2d3748;
            margin: 0 0 10px 0;
            display: flex;
            align-items: center;
        }}
        
        .analysis-title::before {{
            content: "💡";
            margin-right: 8px;
        }}
        
        .analysis-content {{
            color: #4a5568;
            margin: 0;
            line-height: 1.6;
        }}
        
        .footer {{
            text-align: center;
            padding: 30px 0;
            color: #718096;
            font-size: 0.9rem;
        }}
        
        .footer a {{
            color: #667eea;
            text-decoration: none;
        }}
        
        @media (max-width: 768px) {{
            .container {{
                padding: 15px;
            }}
            
            .header {{
                padding: 30px 20px;
            }}
            
            h1 {{
                font-size: 2rem;
            }}
            
            .report-info {{
                flex-direction: column;
                gap: 10px;
                align-items: center;
            }}
            
            .chart-wrapper {{
                height: 300px;
                padding: 15px;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>{header_title}</h1>
            <p class="subtitle">基于AI智能分析的数据洞察</p>
            <div class="report-info">
                <div class="info-item">生成时间: {report_info.get('生成时间', '')}</div>
                <div class="info-item">原始查询: {report_info.get('原始查询', '')}</div>
            </div>
        </div>
"""
    
    # 为每个图表生成HTML
    if 'charts' in chart_data:
        for i, chart in enumerate(chart_data['charts']):
            chart_id = f"chart_{i}"
            chart_type = chart.get('type', 'bar')
            chart_title = chart.get('title', f'图表 {i+1}')
            chart_analysis = analysis_results.get(f"chart_{i}", "数据分析正在生成中...")
            
            # 根据图表类型设置副标题
            if chart_type == 'bar':
                chart_subtitle = "柱状图 - 类别数据对比"
            elif chart_type == 'line':
                chart_subtitle = "折线图 - 趋势变化分析"
            elif chart_type == 'pie':
                chart_subtitle = "饼图 - 占比分布情况"
            else:
                chart_subtitle = "数据可视化"
            
            html_content += f"""
        <div class="chart-container">
            <div class="chart-header">
                <h2 class="chart-title">{chart_title}</h2>
                <p class="chart-subtitle">{chart_subtitle}</p>
            </div>
            <div class="chart-wrapper">
                <canvas id="{chart_id}"></canvas>
            </div>
            <div class="chart-analysis">
                <h3 class="analysis-title">数据分析</h3>
                <p class="analysis-content">{chart_analysis}</p>
            </div>
        </div>
"""
    
    html_content += """
        <div class="footer">
            <p>本报告由AI自动生成 | 数据来源: 互联网搜索</p>
        </div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <script>
"""
    
    # 为每个图表生成JavaScript代码
    if 'charts' in chart_data:
        for i, chart in enumerate(chart_data['charts']):
            chart_id = f"chart_{i}"
            chart_type = chart.get('type', 'bar')
            chart_title = chart.get('title', f'图表 {i+1}')
            chart_data_list = chart.get('data', [])
            
            # 准备数据
            labels = [item['label'] for item in chart_data_list]
            values = [item['value'] for item in chart_data_list]
            
            # 生成图表配置
            if chart_type == 'bar':
                html_content += f"""
        // 柱状图 {i+1}
        (function() {{
            const ctx_{i} = document.getElementById('{chart_id}').getContext('2d');
            new Chart(ctx_{i}, {{
                type: 'bar',
                data: {{
                    labels: {json.dumps(labels)},
                    datasets: [{{
                        label: '{chart.get('yAxisLabel', '数值')}',
                        data: {json.dumps(values)},
                        backgroundColor: [
                            'rgba(102, 126, 234, 0.7)',
                            'rgba(118, 75, 162, 0.7)',
                            'rgba(237, 100, 166, 0.7)',
                            'rgba(255, 159, 64, 0.7)',
                            'rgba(72, 187, 120, 0.7)',
                            'rgba(66, 153, 225, 0.7)'
                        ],
                        borderColor: [
                            'rgba(102, 126, 234, 1)',
                            'rgba(118, 75, 162, 1)',
                            'rgba(237, 100, 166, 1)',
                            'rgba(255, 159, 64, 1)',
                            'rgba(72, 187, 120, 1)',
                            'rgba(66, 153, 225, 1)'
                        ],
                        borderWidth: 1,
                        borderRadius: 5,
                        borderSkipped: false,
                    }}]
                }},
                options: {{
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: {{
                        y: {{
                            beginAtZero: true,
                            title: {{
                                display: true,
                                text: '{chart.get('yAxisLabel', '数值')}',
                                font: {{
                                    size: 14,
                                    weight: 'bold'
                                }}
                            }},
                            grid: {{
                                color: 'rgba(0, 0, 0, 0.05)'
                            }}
                        }},
                        x: {{
                            title: {{
                                display: true,
                                text: '{chart.get('xAxisLabel', '类别')}',
                                font: {{
                                    size: 14,
                                    weight: 'bold'
                                }}
                            }},
                            grid: {{
                                display: false
                            }}
                        }}
                    }},
                    plugins: {{
                        legend: {{
                            display: false
                        }},
                        title: {{
                            display: false
                        }},
                        tooltip: {{
                            backgroundColor: 'rgba(0, 0, 0, 0.8)',
                            padding: 12,
                            cornerRadius: 8,
                            titleFont: {{
                                size: 14,
                                weight: 'bold'
                            }},
                            bodyFont: {{
                                size: 13
                            }}
                        }}
                    }}
                }}
            }});
        }})();
"""
            elif chart_type == 'line':
                html_content += f"""
        // 折线图 {i+1}
        (function() {{
            const ctx_{i} = document.getElementById('{chart_id}').getContext('2d');
            new Chart(ctx_{i}, {{
                type: 'line',
                data: {{
                    labels: {json.dumps(labels)},
                    datasets: [{{
                        label: '{chart.get('yAxisLabel', '数值')}',
                        data: {json.dumps(values)},
                        fill: true,
                        backgroundColor: 'rgba(102, 126, 234, 0.1)',
                        borderColor: 'rgba(102, 126, 234, 1)',
                        tension: 0.4,
                        pointBackgroundColor: 'rgba(102, 126, 234, 1)',
                        pointBorderColor: '#fff',
                        pointHoverBackgroundColor: '#fff',
                        pointHoverBorderColor: 'rgba(102, 126, 234, 1)',
                        pointRadius: 5,
                        pointHoverRadius: 7,
                        borderWidth: 3
                    }}]
                }},
                options: {{
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: {{
                        y: {{
                            beginAtZero: true,
                            title: {{
                                display: true,
                                text: '{chart.get('yAxisLabel', '数值')}',
                                font: {{
                                    size: 14,
                                    weight: 'bold'
                                }}
                            }},
                            grid: {{
                                color: 'rgba(0, 0, 0, 0.05)'
                            }}
                        }},
                        x: {{
                            title: {{
                                display: true,
                                text: '{chart.get('xAxisLabel', '类别')}',
                                font: {{
                                    size: 14,
                                    weight: 'bold'
                                }}
                            }},
                            grid: {{
                                display: false
                            }}
                        }}
                    }},
                    plugins: {{
                        legend: {{
                            display: false
                        }},
                        title: {{
                            display: false
                        }},
                        tooltip: {{
                            backgroundColor: 'rgba(0, 0, 0, 0.8)',
                            padding: 12,
                            cornerRadius: 8,
                            titleFont: {{
                                size: 14,
                                weight: 'bold'
                            }},
                            bodyFont: {{
                                size: 13
                            }}
                        }}
                    }}
                }}
            }});
        }})();
"""
            elif chart_type == 'pie':
                html_content += f"""
        // 饼图 {i+1}
        (function() {{
            const ctx_{i} = document.getElementById('{chart_id}').getContext('2d');
            new Chart(ctx_{i}, {{
                type: 'pie',
                data: {{
                    labels: {json.dumps(labels)},
                    datasets: [{{
                        data: {json.dumps(values)},
                        backgroundColor: [
                            'rgba(102, 126, 234, 0.7)',
                            'rgba(118, 75, 162, 0.7)',
                            'rgba(237, 100, 166, 0.7)',
                            'rgba(255, 159, 64, 0.7)',
                            'rgba(72, 187, 120, 0.7)',
                            'rgba(66, 153, 225, 0.7)'
                        ],
                        borderColor: [
                            'rgba(102, 126, 234, 1)',
                            'rgba(118, 75, 162, 1)',
                            'rgba(237, 100, 166, 1)',
                            'rgba(255, 159, 64, 1)',
                            'rgba(72, 187, 120, 1)',
                            'rgba(66, 153, 225, 1)'
                        ],
                        borderWidth: 2,
                        hoverOffset: 20
                    }}]
                }},
                options: {{
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {{
                        legend: {{
                            position: 'right',
                            labels: {{
                                font: {{
                                    size: 13
                                }},
                                padding: 20,
                                usePointStyle: true,
                                pointStyle: 'circle'
                            }}
                        }},
                        title: {{
                            display: false
                        }},
                        tooltip: {{
                            backgroundColor: 'rgba(0, 0, 0, 0.8)',
                            padding: 12,
                            cornerRadius: 8,
                            titleFont: {{
                                size: 14,
                                weight: 'bold'
                            }},
                            bodyFont: {{
                                size: 13
                            }},
                            callbacks: {{
                                label: function(context) {{
                                    return context.label + ': ' + context.raw + '%';
                                }}
                            }}
                        }}
                    }},
                    layout: {{
                        padding: {{
                            left: 20,
                            right: 20,
                            top: 10,
                            bottom: 10
                        }}
                    }}
                }}
            }});
        }})();
"""
    
    html_content += """
    </script>
</body>
</html>
"""
    
    return html_content

def extract_report_info(txt_content):
    """
    从TXT内容中提取报告信息
    
    Args:
        txt_content: TXT文件内容
        
    Returns:
        dict: 报告信息
    """
    report_info = {}
    
    # 提取生成时间
    time_match = re.search(r'生成时间:\s*(.+)', txt_content)
    if time_match:
        report_info['生成时间'] = time_match.group(1).strip()
    
    # 提取原始查询
    query_match = re.search(r'原始查询:\s*(.+)', txt_content)
    if query_match:
        report_info['原始查询'] = query_match.group(1).strip()
    
    return report_info

def main(user_query=None):
    print("=== HTML图表生成器 ===")
    
    # 获取脚本所在目录
    script_dir = get_script_dir()
    
    # 查找output目录中的最新TXT文件
    output_dir = os.path.join(script_dir, "output")
    if not os.path.exists(output_dir):
        print(f"错误: 找不到output目录")
        return
    
    # 获取所有TXT文件
    txt_files = [f for f in os.listdir(output_dir) if f.endswith('.txt')]
    if not txt_files:
        print("错误: output目录中没有找到TXT文件")
        return
    
    # 选择最新的文件
    latest_file = sorted(txt_files)[-1]
    file_path = os.path.join(output_dir, latest_file)
    
    print(f"正在处理文件: {file_path}")
    
    # 读取TXT文件内容
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            txt_content = f.read()
    except Exception as e:
        print(f"读取文件失败: {e}")
        return
    
    print("正在提取图表数据...")
    
    # 提取报告信息
    report_info = extract_report_info(txt_content)
    
    # 使用DeepSeek提取图表数据
    chart_data = extract_chart_data(txt_content)
    
    if not chart_data:
        print("错误: 无法提取图表数据")
        return
    
    print("正在生成图表分析...")
    
    # 生成图表分析
    analysis_results = generate_chart_analysis(txt_content, chart_data)
    
    print("正在生成HTML文件...")
    
    # 生成HTML内容
    html_content = generate_html(chart_data, report_info, analysis_results, user_query)
    
    # 保存HTML文件到output目录
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    html_filename = os.path.join(output_dir, f"chart_report_{timestamp}.html")
    
    try:
        with open(html_filename, 'w', encoding='utf-8') as f:
            f.write(html_content)
        print(f"✅ HTML文件已生成: {html_filename}")
    except Exception as e:
        print(f"保存HTML文件失败: {e}")

if __name__ == "__main__":
    # 检查API密钥是否已配置
    if not DEEPSEEK_API_KEY or "your_deepseek_api_key_here" in DEEPSEEK_API_KEY:
        print("⚠️  警告: 请先在根目录的config.py文件中配置您的API密钥!")
        print("您需要在config.py中设置以下变量:")
        print("- DEEPSEEK_API_KEY: 设置为您的DeepSeek API密钥")
    else:
        main()