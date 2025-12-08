"""
基本使用示例
演示如何使用Deep Search Agent进行基本的深度搜索，并整合FigHTML图表功能
"""

import os
import sys
from datetime import datetime

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src import DeepSearchAgent, load_config
from src.utils.config import print_config
from src.utils.html_integrator import execute_fightml, extract_chart_content, integrate_chart_html
from src.utils.html_generator import generate_html_report, save_html_report

def basic_example():
    """基本使用示例，整合FigHTML图表功能"""
    print("=" * 60)
    print("Deep Search Agent - 整合FigHTML图表功能示例")
    print("=" * 60)
    
    try:
        # 定义研究主题
        query = "中国应急管理产业发展趋势"
        print(f"研究主题: {query}")
        
        # 步骤1: 运行FigHTML生成图表HTML
        print("\n" + "=" * 60)
        print("[步骤1] 运行FigHTML生成图表...")
        print("=" * 60)
        
        # 获取FigHTML目录路径
        fig_html_dir = os.path.join(os.path.dirname(__file__), '..', 'FigHTML')
        
        # 执行FigHTML生成图表
        chart_html_path = execute_fightml(query, fig_html_dir)
        
        if not chart_html_path or not os.path.exists(chart_html_path):
            print("警告: FigHTML图表生成失败或文件不存在，将继续生成研究报告但不包含图表")
            chart_content = ""
        else:
            print(f"FigHTML图表生成成功: {chart_html_path}")
            # 提取图表内容
            chart_content = extract_chart_content(chart_html_path)
            print("图表内容提取成功")
        
        # 步骤2: 运行DeepSearchAgent生成研究报告
        print("\n" + "=" * 60)
        print("[步骤2] 运行DeepSearchAgent生成研究报告...")
        print("=" * 60)
        
        # 加载配置（指定项目根目录下的config.py）
        print("正在加载配置...")
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        config_path = os.path.join(project_root, 'config.py')
        config = load_config(config_path)
        print_config(config)
        
        # 创建Agent
        print("正在初始化Agent...")
        agent = DeepSearchAgent(config)
        
        # 执行研究
        print(f"开始研究: {query}")
        final_report = agent.research(query, save_report=False)  # 暂时不保存报告，后面手动整合后保存
        
        # 显示结果预览
        print("\n" + "=" * 60)
        print("研究完成！最终报告预览:")
        print("=" * 60)
        print(final_report[:500] + "..." if len(final_report) > 500 else final_report)
        
        # 显示进度信息
        progress = agent.get_progress_summary()
        print(f"\n进度信息:")
        print(f"- 总段落数: {progress['total_paragraphs']}")
        print(f"- 已完成段落: {progress['completed_paragraphs']}")
        print(f"- 完成进度: {progress['progress_percentage']:.1f}%")
        print(f"- 是否完成: {progress['is_completed']}")
        
        # 步骤3: 整合图表和研究报告
        print("\n" + "=" * 60)
        print("[步骤3] 整合图表和研究报告...")
        print("=" * 60)
        
        # 提取段落数据用于HTML报告
        paragraphs_data = []
        lines = final_report.split('\n')
        current_title = ""
        current_content = ""
        
        for line in lines:
            if line.startswith('# ') and not current_title:
                # 这是报告标题
                continue
            elif line.startswith('## '):
                # 新的段落标题
                if current_title and current_content:
                    paragraphs_data.append({
                        "title": current_title,
                        "content": current_content.strip()
                    })
                current_title = line[3:].strip()  # 去掉 ## 前缀
                current_content = ""
            elif line.strip():
                # 段落内容
                current_content += line + "\n"
        
        # 添加最后一个段落
        if current_title and current_content:
            paragraphs_data.append({
                "title": current_title,
                "content": current_content.strip()
            })
        
        # 生成HTML报告
        html_content = generate_html_report(agent.state.report_title, paragraphs_data, config.output_dir)
        
        # 如果有图表内容，整合到HTML中
        if chart_content:
            html_content = integrate_chart_html(html_content, chart_content)
            print("图表已成功整合到研究报告中")
        else:
            print("未整合图表到研究报告中")
        
        # 保存整合后的HTML报告
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        query_safe = "".join(c for c in query if c.isalnum() or c in (' ', '-', '_')).rstrip()
        query_safe = query_safe.replace(' ', '_')[:30]
        
        html_filepath = save_html_report(html_content, agent.state.report_title, config.output_dir)
        print(f"整合后的HTML报告已保存到: {html_filepath}")
        
        # 同时保存Markdown报告
        md_filename = f"deep_search_report_{query_safe}_{timestamp}.md"
        md_filepath = os.path.join(config.output_dir, md_filename)
        with open(md_filepath, 'w', encoding='utf-8') as f:
            f.write(final_report)
        print(f"Markdown报告已保存到: {md_filepath}")
        
        # 保存状态
        if config.save_intermediate_states:
            state_filename = f"state_{query_safe}_{timestamp}.json"
            state_filepath = os.path.join(config.output_dir, state_filename)
            agent.state.save_to_file(state_filepath)
            print(f"状态已保存到: {state_filepath}")
        
        print("\n" + "=" * 60)
        print("所有操作完成！")
        print(f"最终整合报告: {html_filepath}")
        print("=" * 60)
        
    except Exception as e:
        print(f"示例运行失败: {str(e)}")
        print("请检查：")
        print("1. 是否安装了所有依赖：pip install -r requirements.txt")
        print("2. 是否设置了必要的API密钥")
        print("3. 网络连接是否正常")
        print("4. 配置文件是否正确")
        import traceback
        traceback.print_exc()


def main():
    """主函数"""
    basic_example()


if __name__ == "__main__":
    main()
