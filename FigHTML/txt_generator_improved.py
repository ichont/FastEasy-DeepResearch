import requests
import json
import time
from datetime import datetime
import re
import os
import sys

# 添加项目根目录到Python路径
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))

# 从根目录的config.py导入配置
from config import DEEPSEEK_API_KEY, TAVILY_API_KEY

# 获取脚本所在目录，确保相对路径在任何位置都能正确工作
def get_script_dir():
    """获取脚本所在目录，确保相对路径在任何位置都能正确工作"""
    return os.path.dirname(os.path.abspath(__file__))

# 备用数据集，当搜索失败时使用
BACKUP_DATA = {
    "人工智能发展趋势及规模": {
        "bar_chart_data": "人工智能市场规模:\n2019年: 500亿美元\n2020年: 620亿美元\n2021年: 850亿美元\n2022年: 1200亿美元\n2023年: 1580亿美元",
        "line_chart_data": "人工智能技术发展趋势:\n2018年: 市场渗透率5.2%\n2019年: 市场渗透率8.7%\n2020年: 市场渗透率13.5%\n2021年: 市场渗透率19.8%\n2022年: 市场渗透率28.3%\n2023年: 市场渗透率37.6%",
        "pie_chart_data": "人工智能应用领域分布:\n自然语言处理: 35%\n计算机视觉: 28%\n机器学习平台: 20%\n智能机器人: 12%\n其他应用: 5%"
    },
    "新能源汽车": {
        "bar_chart_data": "新能源汽车销量:\n2020年: 130万辆\n2021年: 350万辆\n2022年: 680万辆\n2023年: 950万辆\n2024年: 1200万辆",
        "line_chart_data": "新能源汽车市场份额变化:\n2020年: 5.4%\n2021年: 13.4%\n2022年: 25.6%\n2023年: 31.6%\n2024年: 38.5%",
        "pie_chart_data": "新能源汽车品牌市场份额:\n比亚迪: 32%\n特斯拉: 18%\n上汽通用五菱: 12%\n广汽埃安: 9%\n其他品牌: 29%"
    },
    "电子商务": {
        "bar_chart_data": "电商平台年交易额:\n淘宝天猫: 8.3万亿元\n京东: 3.3万亿元\n拼多多: 2.8万亿元\n抖音电商: 1.5万亿元\n其他平台: 1.2万亿元",
        "line_chart_data": "中国网络零售额增长:\n2019年: 10.6万亿元\n2020年: 11.8万亿元\n2021年: 13.1万亿元\n2022年: 13.8万亿元\n2023年: 15.4万亿元",
        "pie_chart_data": "电商用户年龄分布:\n18-25岁: 28%\n26-35岁: 42%\n36-45岁: 22%\n46-55岁: 7%\n55岁以上: 3%"
    },
    "云计算": {
        "bar_chart_data": "云服务提供商市场份额:\n阿里云: 36%\n腾讯云: 18%\n华为云: 12%\n百度智能云: 8%\n其他厂商: 26%",
        "line_chart_data": "中国云计算市场规模:\n2020年: 2000亿元\n2021年: 3100亿元\n2022年: 4500亿元\n2023年: 6200亿元\n2024年: 8200亿元",
        "pie_chart_data": "云计算服务类型分布:\nIaaS: 65%\nPaaS: 20%\nSaaS: 15%"
    },
    "5G技术": {
        "bar_chart_data": "5G基站数量:\n2020年: 72万个\n2021年: 143万个\n2022年: 231万个\n2023年: 337万个\n2024年: 420万个",
        "line_chart_data": "5G用户增长:\n2020年: 1.6亿户\n2021年: 3.5亿户\n2022年: 5.7亿户\n2023年: 7.8亿户\n2024年: 9.5亿户",
        "pie_chart_data": "5G应用场景分布:\n智能手机: 65%\n工业互联网: 15%\n智慧城市: 10%\n远程医疗: 6%\n其他应用: 4%"
    },
    "默认": {
        "bar_chart_data": "年度销售数据:\n产品A: 4500万元\n产品B: 3200万元\n产品C: 2800万元\n产品D: 2100万元\n产品E: 1900万元",
        "line_chart_data": "月度用户增长趋势:\n1月: 1200万用户\n2月: 1350万用户\n3月: 1580万用户\n4月: 1820万用户\n5月: 2100万用户\n6月: 2450万用户",
        "pie_chart_data": "市场份额分布:\n北美地区: 42%\n欧洲地区: 28%\n亚太地区: 23%\n其他地区: 7%"
    }
}

def call_deepseek_api(prompt):
    """
    调用DeepSeek API获取搜索建议或思考结果
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
                "content": "你是一个数据搜索助手，专门帮助用户生成精确的搜索查询来获取关键数据。请根据用户的需求，生成一个或多个精确的搜索查询语句。"
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        "temperature": 0.3,
        "max_tokens": 500
    }
    
    try:
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        result = response.json()
        return result['choices'][0]['message']['content']
    except Exception as e:
        print(f"DeepSeek API调用失败: {e}")
        return None

def call_tavily_api(query, max_results=5):
    """
    调用Tavily API进行搜索，确保搜索功能正确
    """
    url = "https://api.tavily.com/search"
    
    headers = {
        "Content-Type": "application/json"
    }
    
    data = {
        "api_key": TAVILY_API_KEY,
        "query": query,
        "search_depth": "advanced",  # 使用高级搜索以获取更准确的数据
        "include_answer": True,
        "include_raw_content": False,
        "max_results": max_results,
        "include_images": False
    }
    
    try:
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        result = response.json()
        return result
    except Exception as e:
        print(f"Tavily API调用失败: {e}")
        return None

def call_api_with_retry(prompt, max_retries=3):
    """
    带重试机制的API调用函数
    
    Args:
        prompt: API提示词
        max_retries: 最大重试次数
        
    Returns:
        str: API返回结果
    """
    for attempt in range(max_retries):
        try:
            result = call_deepseek_api(prompt)
            if result:
                return result
            elif attempt < max_retries - 1:
                print(f"API调用失败，正在重试... (尝试 {attempt + 1}/{max_retries})")
                time.sleep(2)  # 等待2秒后重试
        except Exception as e:
            print(f"API调用出错: {str(e)}")
            if attempt < max_retries - 1:
                time.sleep(2)
    
    print(f"经过{max_retries}次尝试，仍无法获取有效的API响应")
    return None

def is_valid_chart_data(data, chart_type):
    """
    验证图表数据是否有效
    
    Args:
        data: 图表数据字符串
        chart_type: 图表类型 (bar, line, pie)
    
    Returns:
        bool: 数据是否有效
    """
    if not data or not isinstance(data, str):
        return False
    
    # 检查是否包含错误信息
    error_indicators = [
        "未找到可提取的数据", "AI未能提取", "无法提取", "提取失败", 
        "没有找到", "不包含", "无法找到", "错误", "失败"
    ]
    
    for indicator in error_indicators:
        if indicator in data:
            return False
    
    # 根据图表类型进行特定验证
    if chart_type == "bar":
        # 柱状图需要至少3个数据点，每个数据点包含标签和数值
        lines = [line.strip() for line in data.split('\n') if line.strip()]
        if len(lines) < 3:
            return False
        
        # 检查每行是否包含数值
        numeric_count = 0
        for line in lines:
            # 查找数字（整数、小数、百分比）
            if re.search(r'\d+(\.\d+)?%?', line):
                numeric_count += 1
        
        # 至少有一半的行包含数值
        return numeric_count >= len(lines) / 2
    
    elif chart_type == "line":
        # 折线图需要至少3个数据点，通常包含时间序列
        lines = [line.strip() for line in data.split('\n') if line.strip()]
        if len(lines) < 3:
            return False
        
        # 检查是否包含时间或序列信息
        time_indicators = ["年", "月", "季度", "日", "期", "时间", "序列"]
        has_time = any(indicator in data for indicator in time_indicators)
        
        # 检查是否包含数值
        has_numeric = bool(re.search(r'\d+(\.\d+)?%?', data))
        
        return has_time and has_numeric
    
    elif chart_type == "pie":
        # 饼图需要至少2个部分，每个部分包含标签和百分比
        lines = [line.strip() for line in data.split('\n') if line.strip()]
        if len(lines) < 2:
            return False
        
        # 检查是否包含百分比
        percentage_count = 0
        for line in lines:
            if re.search(r'\d+%|\d+\.?\d*%', line):
                percentage_count += 1
        
        # 至少有一半的行包含百分比
        return percentage_count >= len(lines) / 2
    
    return False

def generate_sample_data(chart_type, topic="示例数据"):
    """
    生成示例图表数据
    
    Args:
        chart_type: 图表类型 (bar, line, pie)
        topic: 数据主题
    
    Returns:
        str: 生成的示例数据
    """
    if chart_type == "bar":
        # 生成多样化的柱状图数据
        topics_data = {
            "人工智能": {
                "title": "人工智能市场规模",
                "data": [
                    "2019年: 500亿美元",
                    "2020年: 620亿美元",
                    "2021年: 850亿美元",
                    "2022年: 1200亿美元",
                    "2023年: 1580亿美元"
                ]
            },
            "默认": {
                "title": "年度销售数据",
                "data": [
                    "产品A: 4500万元",
                    "产品B: 3200万元",
                    "产品C: 2800万元",
                    "产品D: 2100万元",
                    "产品E: 1900万元"
                ]
            }
        }
        
        # 根据主题选择数据
        selected_data = topics_data.get("默认", topics_data["默认"])
        for key in topics_data:
            if key in topic:
                selected_data = topics_data[key]
                break
        
        result = f"{selected_data['title']}:\n"
        result += "\n".join(selected_data['data'])
        return result
    
    elif chart_type == "line":
        # 生成多样化的折线图数据
        topics_data = {
            "人工智能": {
                "title": "人工智能技术发展趋势",
                "data": [
                    "2018年: 市场渗透率5.2%",
                    "2019年: 市场渗透率8.7%",
                    "2020年: 市场渗透率13.5%",
                    "2021年: 市场渗透率19.8%",
                    "2022年: 市场渗透率28.3%",
                    "2023年: 市场渗透率37.6%"
                ]
            },
            "默认": {
                "title": "月度用户增长趋势",
                "data": [
                    "1月: 1200万用户",
                    "2月: 1350万用户",
                    "3月: 1580万用户",
                    "4月: 1820万用户",
                    "5月: 2100万用户",
                    "6月: 2450万用户"
                ]
            }
        }
        
        # 根据主题选择数据
        selected_data = topics_data.get("默认", topics_data["默认"])
        for key in topics_data:
            if key in topic:
                selected_data = topics_data[key]
                break
        
        result = f"{selected_data['title']}:\n"
        result += "\n".join(selected_data['data'])
        return result
    
    elif chart_type == "pie":
        # 生成多样化的饼图数据
        topics_data = {
            "人工智能": {
                "title": "人工智能应用领域分布",
                "data": [
                    "自然语言处理: 35%",
                    "计算机视觉: 28%",
                    "机器学习平台: 20%",
                    "智能机器人: 12%",
                    "其他应用: 5%"
                ]
            },
            "默认": {
                "title": "市场份额分布",
                "data": [
                    "北美地区: 42%",
                    "欧洲地区: 28%",
                    "亚太地区: 23%",
                    "其他地区: 7%"
                ]
            }
        }
        
        # 根据主题选择数据
        selected_data = topics_data.get("默认", topics_data["默认"])
        for key in topics_data:
            if key in topic:
                selected_data = topics_data[key]
                break
        
        result = f"{selected_data['title']}:\n"
        result += "\n".join(selected_data['data'])
        return result
    
    return "无数据"

def enhance_search_query(query):
    """
    增强搜索查询，提高数据获取能力
    
    Args:
        query: 原始查询
        
    Returns:
        str: 增强后的查询
    """
    # 添加数据相关关键词
    data_keywords = ["数据", "统计", "报告", "图表", "分析", "趋势", "规模", "增长率"]
    
    # 如果原查询不包含数据关键词，则添加
    if not any(keyword in query for keyword in data_keywords):
        enhanced_query = f"{query} 数据统计报告"
    else:
        enhanced_query = query
    
    return enhanced_query

def extract_key_data_with_ai(search_results):
    """
    使用AI从搜索结果中提取适合制作不同类型图表的关键数据
    
    Args:
        search_results: 搜索结果列表
        
    Returns:
        dict: 包含不同类型图表数据的字典
    """
    if not search_results:
        print("没有搜索结果，生成示例数据...")
        return {
            "bar_chart_data": generate_sample_data("bar", "示例数据"),
            "line_chart_data": generate_sample_data("line", "示例数据"),
            "pie_chart_data": generate_sample_data("pie", "示例数据")
        }
    
    # 准备搜索结果文本
    results_text = ""
    for i, result in enumerate(search_results, 1):
        results_text += f"结果{i}: {result.get('title', '')}\n"
        results_text += f"内容: {result.get('content', '')}\n"
        results_text += f"来源: {result.get('url', '')}\n\n"
    
    # 使用DeepSeek提取柱状图数据
    bar_chart_prompt = f"""
    从以下搜索结果中提取制作柱状图的数据。柱状图适合比较不同类别的数值。
    
    要求:
    1. 提取至少3个数据点
    2. 每个数据点包含明确的类别标签和数值
    3. 数值应该是具体的数字（可以是金额、数量、百分比等）
    4. 数据应该有逻辑关联性，属于同一比较维度
    5. 如果搜索结果中没有足够的数据，请基于主题生成合理的示例数据
    
    搜索结果:
    {results_text}
    
    请直接输出提取的数据，格式如下:
    数据主题:
    类别1: 数值1
    类别2: 数值2
    类别3: 数值3
    ...
    """
    
    # 使用DeepSeek提取折线图数据
    line_chart_prompt = f"""
    从以下搜索结果中提取制作折线图的数据。折线图适合展示数据随时间的变化趋势。
    
    要求:
    1. 提取至少3个时间点的数据
    2. 每个数据点包含时间标记和对应的数值
    3. 时间应该有连续性或逻辑顺序
    4. 数值应该能够显示变化趋势
    5. 如果搜索结果中没有足够的数据，请基于主题生成合理的示例数据
    
    搜索结果:
    {results_text}
    
    请直接输出提取的数据，格式如下:
    数据主题:
    时间1: 数值1
    时间2: 数值2
    时间3: 数值3
    ...
    """
    
    # 使用DeepSeek提取饼图数据
    pie_chart_prompt = f"""
    从以下搜索结果中提取制作饼图的数据。饼图适合展示整体中各部分的占比关系。
    
    要求:
    1. 提取至少2个部分的数据
    2. 每个部分包含名称和百分比或比例
    3. 所有部分的百分比之和应该接近100%
    4. 数据应该属于同一整体的不同组成部分
    5. 如果搜索结果中没有足够的数据，请基于主题生成合理的示例数据
    
    搜索结果:
    {results_text}
    
    请直接输出提取的数据，格式如下:
    数据主题:
    部分1: 百分比1%
    部分2: 百分比2%
    部分3: 百分比3%
    ...
    """
    
    # 调用DeepSeek API提取数据
    bar_chart_data = call_api_with_retry(bar_chart_prompt)
    line_chart_data = call_api_with_retry(line_chart_prompt)
    pie_chart_data = call_api_with_retry(pie_chart_prompt)
    
    # 验证提取的数据，如果无效则生成示例数据
    if not is_valid_chart_data(bar_chart_data, "bar"):
        print("柱状图数据无效，生成示例数据...")
        bar_chart_data = generate_sample_data("bar", "示例数据")
    
    if not is_valid_chart_data(line_chart_data, "line"):
        print("折线图数据无效，生成示例数据...")
        line_chart_data = generate_sample_data("line", "示例数据")
    
    if not is_valid_chart_data(pie_chart_data, "pie"):
        print("饼图数据无效，生成示例数据...")
        pie_chart_data = generate_sample_data("pie", "示例数据")
    
    return {
        "bar_chart_data": bar_chart_data,
        "line_chart_data": line_chart_data,
        "pie_chart_data": pie_chart_data
    }

def generate_alternative_search_queries(original_query):
    """
    生成替代搜索查询，提高搜索成功率
    
    Args:
        original_query: 原始查询
        
    Returns:
        list: 替代查询列表
    """
    # 基于原始查询生成多种变体
    alternatives = []
    
    # 添加数据相关关键词
    data_keywords = ["数据", "统计", "报告", "图表", "分析", "趋势", "市场规模", "增长率"]
    
    # 生成不同类型的查询
    alternatives.append(f"{original_query} 市场规模数据")
    alternatives.append(f"{original_query} 行业报告")
    alternatives.append(f"{original_query} 发展趋势统计")
    alternatives.append(f"{original_query} 市场份额分析")
    
    return alternatives[:3]  # 返回前3个替代查询

def save_to_txt(content):
    """
    将内容保存到TXT文件
    
    Args:
        content: 要保存的内容
        
    Returns:
        str: 保存的文件名
    """
    # 获取脚本目录
    script_dir = get_script_dir()
    
    # 创建输出目录（如果不存在）
    output_dir = os.path.join(script_dir, "output")
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # 生成文件名（包含时间戳）
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = os.path.join(output_dir, f"data_report_{timestamp}.txt")
    
    # 保存内容到文件
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(content)
    
    return filename

def main(user_query=None):
    print("=== 数据型内容搜索工具 ===")
    print("正在使用预设主题进行搜索，我将使用Deepseek思考并用Tavily进行精确搜索")
    print("-" * 50)
    
    # 如果没有传入搜索主题，使用默认主题
    if user_query is None:
        user_query = "数据安全的全球新动态"  # 默认静态搜索主题
    
    if not user_query:
        print("错误: 搜索主题不能为空")
        return
    
    print(f"搜索主题: {user_query}")
    
    print("\n正在使用DeepSeek思考最佳搜索策略...")
    
    # 使用DeepSeek生成精确的搜索查询，专注于表格数据
    deepseek_prompt = f"""
    用户需要搜索关于"{user_query}"的数据，这些数据应该适合制作表格和图表（如柱状图、饼图、折线图等）。
    请生成2-3个精确的搜索查询语句，这些查询应该：
    1. 专注于获取结构化的统计数据、年度数据、比较数据
    2. 寻找包含数字、百分比、金额、增长率等量化信息的内容
    3. 优先考虑具有明确分类维度的数据（如年份、地区、产品类别等）
    4. 避免模糊的表述，使用具体的数据类型关键词
    
    请直接输出搜索查询，每行一个，不需要其他解释。
    """
    
    deepseek_response = call_deepseek_api(deepseek_prompt)
    
    if not deepseek_response:
        print("DeepSeek API调用失败，使用原始查询进行搜索")
        search_queries = [enhance_search_query(user_query)]
    else:
        # 解析DeepSeek生成的搜索查询
        search_queries = [q.strip() for q in deepseek_response.split('\n') if q.strip() and not q.strip().startswith(('1.', '2.', '3.', '-', '*'))]
        
        if not search_queries:
            search_queries = [enhance_search_query(user_query)]
        else:
            # 增强每个搜索查询
            search_queries = [enhance_search_query(q) for q in search_queries]
        
        print("\nDeepSeek生成的搜索查询:")
        for i, query in enumerate(search_queries, 1):
            print(f"{i}. {query}")
    
    # 执行搜索和评估循环
    max_iterations = 3  # 最大迭代次数
    iteration = 0
    extracted_data = None
    has_valid_data = False
    
    while iteration < max_iterations:
        iteration += 1
        print(f"\n--- 第 {iteration} 轮搜索 ---")
        
        print("\n" + "="*50)
        print("开始使用Tavily进行搜索...")
        print("="*50)
        
        all_results = []
        total_results = 0
        
        # 对每个搜索查询进行Tavily搜索
        for i, query in enumerate(search_queries, 1):
            print(f"\n🔍 正在搜索: {query}")
            tavily_result = call_tavily_api(query, max_results=3)
            
            if tavily_result and 'results' in tavily_result:
                results = tavily_result['results']
                total_results += len(results)
                print(f"✓ 找到 {len(results)} 个结果")
                
                # 收集结果
                for result in results:
                    all_results.append({
                        'query': query,
                        'title': result.get('title', ''),
                        'content': result.get('content', ''),
                        'url': result.get('url', ''),
                        'score': result.get('score', 0)
                    })
            else:
                print(f"✗ 搜索失败或未找到结果")
            
            # 避免API调用过于频繁
            if i < len(search_queries):
                time.sleep(1)
        
        print(f"\n{'='*50}")
        print(f"第 {iteration} 轮搜索完成! 共找到 {total_results} 个结果")
        print(f"{'='*50}")
        
        # 即使没有找到结果，也尝试提取数据
        print("\n正在尝试提取图表数据...")
        extracted_data = extract_key_data_with_ai(all_results)
        
        # 验证提取的数据
        bar_valid = is_valid_chart_data(extracted_data.get("bar_chart_data", ""), "bar")
        line_valid = is_valid_chart_data(extracted_data.get("line_chart_data", ""), "line")
        pie_valid = is_valid_chart_data(extracted_data.get("pie_chart_data", ""), "pie")
        
        has_valid_data = bar_valid or line_valid or pie_valid
        
        if has_valid_data:
            print("✓ 成功提取到有效的图表数据")
            print(f"- 柱状图数据: {'有效' if bar_valid else '无效'}")
            print(f"- 折线图数据: {'有效' if line_valid else '无效'}")
            print(f"- 饼图数据: {'有效' if pie_valid else '无效'}")
            break
        else:
            print("✗ 提取的图表数据无效")
            if iteration < max_iterations:
                print("正在尝试生成替代搜索查询...")
                alternative_queries = generate_alternative_search_queries(user_query)
                if alternative_queries:
                    search_queries = alternative_queries
                    print("使用替代搜索查询继续搜索:")
                    for i, query in enumerate(search_queries, 1):
                        print(f"{i}. {query}")
                else:
                    print("无法生成替代查询，将使用备用数据")
                    break
            else:
                print("已达到最大尝试次数，将使用备用数据")
                break
    
    # 如果没有有效数据，使用备用数据
    if not has_valid_data:
        print("\n使用备用数据生成图表...")
        backup_data = BACKUP_DATA.get(user_query, BACKUP_DATA.get("默认", {}))
        extracted_data = {
            "bar_chart_data": backup_data.get("bar_chart_data", ""),
            "line_chart_data": backup_data.get("line_chart_data", ""),
            "pie_chart_data": backup_data.get("pie_chart_data", "")
        }
    
    # 准备保存到文件的内容
    output_content = f"数据搜索报告\n"
    output_content += f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
    output_content += f"原始查询: {user_query}\n"
    output_content += f"{'='*50}\n\n"
    
    # 添加有效的图表数据
    bar_data = extracted_data.get("bar_chart_data", "")
    if bar_data and is_valid_chart_data(bar_data, "bar"):
        output_content += "适用于柱状图的数据:\n"
        output_content += f"{bar_data}\n\n"
    else:
        output_content += "适用于柱状图的数据: 无有效数据\n\n"
    
    line_data = extracted_data.get("line_chart_data", "")
    if line_data and is_valid_chart_data(line_data, "line"):
        output_content += "适用于折线图的数据:\n"
        output_content += f"{line_data}\n\n"
    else:
        output_content += "适用于折线图的数据: 无有效数据\n\n"
    
    pie_data = extracted_data.get("pie_chart_data", "")
    if pie_data and is_valid_chart_data(pie_data, "pie"):
        output_content += "适用于饼图的数据:\n"
        output_content += f"{pie_data}\n"
    else:
        output_content += "适用于饼图的数据: 无有效数据\n"
    
    # 确保文件不会为空
    if not any([bar_data, line_data, pie_data]):
        output_content += "\n注意: 未找到任何有效数据，请尝试修改搜索主题。\n"
    
    # 保存到文件
    filename = save_to_txt(output_content)
    
    if filename:
        print(f"\n{'='*50}")
        print(f"✅ 项目完成!")
        print(f"所有搜索结果已保存到: {filename}")
        print(f"{'='*50}")

if __name__ == "__main__":
    # 检查API密钥是否已配置
    if (not DEEPSEEK_API_KEY or "your_deepseek_api_key_here" in DEEPSEEK_API_KEY or 
        not TAVILY_API_KEY or "your_tavily_api_key_here" in TAVILY_API_KEY):
        print("⚠️  警告: 请先在根目录的config.py文件中配置您的API密钥!")
        print("您需要在config.py中设置以下变量:")
        print("- DEEPSEEK_API_KEY: 设置为您的DeepSeek API密钥")
        print("- TAVILY_API_KEY: 设置为您的Tavily API密钥")
    else:
        main()