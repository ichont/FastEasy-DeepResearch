#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
HTML整合器模块
用于整合FigHTML图表和DeepSearchAgent研究报告
"""

import os
import sys
from datetime import datetime
import importlib.util
import re


def get_script_dir():
    """获取脚本所在目录的路径，支持作为模块导入时的情况"""
    # 如果__file__存在，使用它来确定脚本目录
    if hasattr(sys.modules[__name__], '__file__'):
        return os.path.dirname(os.path.abspath(sys.modules[__name__].__file__))
    # 否则使用当前工作目录
    return os.getcwd()


def load_module_from_file(module_name, file_path):
    """从文件路径动态加载模块"""
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def execute_fightml(query, fig_html_dir):
    """
    执行FigHTML生成图表
    
    Args:
        query (str): 搜索查询
        fig_html_dir (str): FigHTML目录路径
        
    Returns:
        str: 生成的HTML文件路径，如果失败则返回None
    """
    try:
        print(f"正在执行FigHTML生成图表，查询: {query}")
        
        # 检查FigHTML目录是否存在
        if not os.path.exists(fig_html_dir):
            print(f"错误: FigHTML目录不存在: {fig_html_dir}")
            return None
        
        # 获取Figmain.py路径
        figmain_path = os.path.join(fig_html_dir, "Figmain.py")
        if not os.path.exists(figmain_path):
            print(f"错误: Figmain.py不存在: {figmain_path}")
            return None
        
        # 检查必要的文件是否存在
        required_files = ["txt_generator_improved.py", "html_generator_improved.py"]
        for file in required_files:
            file_path = os.path.join(fig_html_dir, file)
            if not os.path.exists(file_path):
                print(f"错误: 找不到必要文件 {file_path}")
                return None
        
        # 确保output目录存在
        output_dir = os.path.join(fig_html_dir, "output")
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
            print(f"已创建output目录: {output_dir}")
        
        # 直接执行FigHTML流程，而不是动态导入模块
        # 第一步：生成TXT文件
        print("=== 第一步：生成TXT数据文件 ===")
        print(f"搜索主题: {query}")
        
        # 加载txt_generator_improved模块
        txt_generator_path = os.path.join(fig_html_dir, "txt_generator_improved.py")
        txt_generator = load_module_from_file("txt_generator", txt_generator_path)
        
        # 调用main函数生成TXT文件，传入搜索主题
        txt_generator.main(query)
        
        # 查找最新生成的TXT文件
        txt_files = [f for f in os.listdir(output_dir) if f.endswith('.txt')]
        if not txt_files:
            print("错误: output目录中没有找到TXT文件")
            return None
        
        # 选择最新的文件
        latest_file = sorted(txt_files)[-1]
        txt_file_path = os.path.join(output_dir, latest_file)
        print(f"✅ TXT文件已生成: {txt_file_path}")
        
        # 第二步：生成HTML文件
        print("\n=== 第二步：生成HTML可视化报告 ===")
        
        # 加载html_generator_improved模块
        html_generator_path = os.path.join(fig_html_dir, "html_generator_improved.py")
        html_generator = load_module_from_file("html_generator", html_generator_path)
        
        # 调用main函数生成HTML文件，传入搜索主题
        html_generator.main(query)
        
        # 查找最新生成的HTML文件
        html_files = [f for f in os.listdir(output_dir) if f.endswith('.html')]
        if not html_files:
            print("错误: output目录中没有找到HTML文件")
            return None
        
        # 选择最新的文件
        latest_file = sorted(html_files)[-1]
        html_file_path = os.path.join(output_dir, latest_file)
        print(f"✅ HTML文件已生成: {html_file_path}")
        
        # 第三步：确保文件名对应
        print("\n=== 第三步：确保文件名对应 ===")
        
        # 提取TXT文件的基本名称（不含扩展名）
        txt_basename = os.path.splitext(os.path.basename(txt_file_path))[0]
        
        # 构建HTML文件的新路径
        html_new_name = f"{txt_basename}.html"
        final_html_path = os.path.join(output_dir, html_new_name)
        
        # 如果HTML文件已经是对应的名称，则不需要重命名
        if html_file_path != final_html_path:
            try:
                os.rename(html_file_path, final_html_path)
                print(f"✅ HTML文件已重命名为: {final_html_path}")
            except Exception as e:
                print(f"重命名HTML文件失败: {e}")
                final_html_path = html_file_path
        else:
            print("文件名已对应，无需重命名")
        
        print("\n=== FigHTML流程完成 ===")
        print(f"最终HTML文件: {final_html_path}")
        
        if os.path.exists(final_html_path):
            print(f"FigHTML图表生成成功: {final_html_path}")
            return final_html_path
        else:
            print("FigHTML图表生成失败")
            return None
            
    except Exception as e:
        print(f"执行FigHTML时出错: {e}")
        import traceback
        traceback.print_exc()
        return None


def extract_chart_content(html_file_path):
    """
    从HTML文件中提取图表内容
    
    Args:
        html_file_path (str): HTML文件路径
        
    Returns:
        str: 提取的图表HTML内容
    """
    try:
        if not os.path.exists(html_file_path):
            print(f"错误: HTML文件不存在: {html_file_path}")
            return ""
        
        with open(html_file_path, 'r', encoding='utf-8') as f:
            html_content = f.read()
        
        # 根据用户需求，直接返回整个HTML文件内容，不进行任何提取或处理
        print(f"已直接读取整个HTML文件内容，长度: {len(html_content)}")
        return html_content
        
    except Exception as e:
        print(f"提取图表内容时出错: {e}")
        import traceback
        traceback.print_exc()
        return ""


def integrate_chart_html(html_content, chart_content):
    """
    将图表内容整合到HTML报告中
    
    Args:
        html_content (str): 原始HTML报告内容
        chart_content (str): 图表HTML内容
        
    Returns:
        str: 整合后的HTML内容
    """
    try:
        if not chart_content:
            print("警告: 图表内容为空，不进行整合")
            return html_content
        
        # 直接在报告末尾添加完整的图表HTML内容，不进行提取和处理
        # 找到body结束标签
        body_end_pattern = r'(</body>)'
        match = re.search(body_end_pattern, html_content, re.IGNORECASE)
        if match:
            insertion_point = match.start()
            # 添加一个完整的section包含整个fightml报告
            chart_section = f'\n<div class="chart-section" style="margin-top: 50px;">\n<h2>数据可视化分析报告</h2>\n{chart_content}\n</div>\n'
            integrated_content = html_content[:insertion_point] + chart_section + html_content[insertion_point:]
            print("图表内容已直接添加到HTML报告末尾")
            return integrated_content
        
        # 如果找不到body结束标签，直接添加到文件末尾
        integrated_content = html_content + f'\n<div class="chart-section" style="margin-top: 50px;">\n<h2>数据可视化分析报告</h2>\n{chart_content}\n</div>\n'
        print("图表内容已直接添加到HTML报告末尾")
        return integrated_content
        
    except Exception as e:
        print(f"整合图表内容时出错: {e}")
        import traceback
        traceback.print_exc()
        return html_content