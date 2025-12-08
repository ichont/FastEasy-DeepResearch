#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
from datetime import datetime
import importlib.util

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

def run_txt_generator(user_query):
    """运行TXT生成器"""
    print("=== 第一步：生成TXT数据文件 ===")
    print(f"搜索主题: {user_query}")
    
    # 获取脚本目录
    script_dir = get_script_dir()
    
    # 加载txt_generator_improved模块
    txt_generator_path = os.path.join(script_dir, "txt_generator_improved.py")
    txt_generator = load_module_from_file("txt_generator", txt_generator_path)
    
    # 调用main函数生成TXT文件，传入搜索主题
    txt_generator.main(user_query)
    
    # 查找最新生成的TXT文件
    output_dir = os.path.join(script_dir, "output")
    if not os.path.exists(output_dir):
        print(f"错误: 找不到output目录")
        return None
    
    # 获取所有TXT文件
    txt_files = [f for f in os.listdir(output_dir) if f.endswith('.txt')]
    if not txt_files:
        print("错误: output目录中没有找到TXT文件")
        return None
    
    # 选择最新的文件
    latest_file = sorted(txt_files)[-1]
    file_path = os.path.join(output_dir, latest_file)
    
    print(f"✅ TXT文件已生成: {file_path}")
    return file_path

def run_html_generator(txt_file_path, user_query):
    """运行HTML生成器"""
    print("\n=== 第二步：生成HTML可视化报告 ===")
    
    # 获取脚本目录
    script_dir = get_script_dir()
    
    # 加载html_generator_improved模块
    html_generator_path = os.path.join(script_dir, "html_generator_improved.py")
    html_generator = load_module_from_file("html_generator", html_generator_path)
    
    # 调用main函数生成HTML文件，传入搜索主题
    html_generator.main(user_query)
    
    # 查找最新生成的HTML文件
    output_dir = os.path.join(script_dir, "output")
    if not os.path.exists(output_dir):
        print(f"错误: 找不到output目录")
        return None
    
    # 获取所有HTML文件
    html_files = [f for f in os.listdir(output_dir) if f.endswith('.html')]
    if not html_files:
        print("错误: output目录中没有找到HTML文件")
        return None
    
    # 选择最新的文件
    latest_file = sorted(html_files)[-1]
    file_path = os.path.join(output_dir, latest_file)
    
    print(f"✅ HTML文件已生成: {file_path}")
    return file_path

def rename_files_to_match(txt_file_path, html_file_path):
    """重命名文件使TXT和HTML文件名对应"""
    print("\n=== 第三步：确保文件名对应 ===")
    
    # 获取脚本目录
    script_dir = get_script_dir()
    
    # 提取TXT文件的基本名称（不含扩展名）
    txt_basename = os.path.splitext(os.path.basename(txt_file_path))[0]
    
    # 构建HTML文件的新路径
    output_dir = os.path.join(script_dir, "output")
    html_new_name = f"{txt_basename}.html"
    html_new_path = os.path.join(output_dir, html_new_name)
    
    # 如果HTML文件已经是对应的名称，则不需要重命名
    if html_file_path == html_new_path:
        print("文件名已对应，无需重命名")
        return html_file_path
    
    # 重命名HTML文件
    try:
        os.rename(html_file_path, html_new_path)
        print(f"✅ HTML文件已重命名为: {html_new_path}")
        return html_new_path
    except Exception as e:
        print(f"重命名HTML文件失败: {e}")
        return html_file_path

def main():
    """主函数，整合TXT生成和HTML生成流程"""
    print("=== 自动化数据可视化报告生成器 ===")
    print(f"开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 设置搜索主题 - 可以在这里修改搜索关键词
    user_query = "中国应急管理产业发展趋势"  # 静态搜索主题
    
    # 获取脚本目录
    script_dir = get_script_dir()
    
    # 检查必要的文件是否存在
    required_files = ["txt_generator_improved.py", "html_generator_improved.py"]
    for file in required_files:
        file_path = os.path.join(script_dir, file)
        if not os.path.exists(file_path):
            print(f"错误: 找不到必要文件 {file_path}")
            return
    
    # 确保output目录存在
    output_dir = os.path.join(script_dir, "output")
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        print(f"已创建output目录: {output_dir}")
    
    try:
        # 第一步：生成TXT文件
        txt_file_path = run_txt_generator(user_query)
        if not txt_file_path:
            print("TXT文件生成失败，终止流程")
            return
        
        # 第二步：生成HTML文件
        html_file_path = run_html_generator(txt_file_path, user_query)
        if not html_file_path:
            print("HTML文件生成失败，终止流程")
            return
        
        # 第三步：确保文件名对应
        final_html_path = rename_files_to_match(txt_file_path, html_file_path)
        
        print("\n=== 流程完成 ===")
        print(f"TXT文件: {txt_file_path}")
        print(f"HTML文件: {final_html_path}")
        print(f"完成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        """
        # 询问是否打开HTML文件
        try:
            choice = input("\n是否在浏览器中打开HTML文件? (y/n): ").strip().lower()
            if choice in ['y', 'yes', '是']:
                import webbrowser
                webbrowser.open(f"file://{os.path.abspath(final_html_path)}")
                print("已在浏览器中打开HTML文件")
        except Exception as e:
            print(f"无法打开浏览器: {e}")

        """
            
    except Exception as e:
        print(f"流程执行过程中发生错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()