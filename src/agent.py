"""
Deep Search Agent主类
整合所有模块，实现完整的深度搜索流程
"""

import json
import os
from datetime import datetime
from typing import Optional, Dict, Any, List

from .llms import DeepSeekLLM, OpenAILLM, BaseLLM
from .nodes import (
    ReportStructureNode,
    FirstSearchNode, 
    ReflectionNode,
    FirstSummaryNode,
    ReflectionSummaryNode,
    ReportFormattingNode
)
from .state import State
from .tools import tavily_search, enhanced_tavily_search
from .utils import Config, load_config, format_search_results_for_prompt


class DeepSearchAgent:
    """Deep Search Agent主类"""
    
    def __init__(self, config: Optional[Config] = None, enable_rag: bool = False, rag_top_k: int = 3, enable_multimodal: bool = False):
        """
        初始化Deep Search Agent
        
        Args:
            config: 配置对象，如果不提供则自动加载
            enable_rag: 是否启用RAG增强搜索功能
            rag_top_k: 使用RAG时返回的最相关文档数量
            enable_multimodal: 是否启用多模态内容生成功能
        """
        # 加载配置
        self.config = config or load_config()
        
        # 初始化LLM客户端
        self.llm_client = self._initialize_llm()
        
        # 初始化节点
        self._initialize_nodes()
        
        # RAG配置
        self.enable_rag = enable_rag
        self.rag_top_k = rag_top_k
        
        # 多模态配置
        self.enable_multimodal = enable_multimodal
        if self.enable_multimodal:
            try:
                from .utils.chart_generator import chart_generator
                from .utils.image_processor import image_processor
                self.chart_generator = chart_generator
                self.image_processor = image_processor
                print("多模态内容生成功能已启用")
            except ImportError as e:
                print(f"无法导入多模态工具，将禁用该功能: {str(e)}")
                self.enable_multimodal = False
        
        # 状态
        self.state = State()
        
        # 确保输出目录存在
        os.makedirs(self.config.output_dir, exist_ok=True)
        
        print(f"Deep Search Agent 已初始化")
        print(f"使用LLM: {self.llm_client.get_model_info()}")
        if self.enable_rag:
            print(f"RAG增强搜索已启用，返回Top-K文档数: {self.rag_top_k}")
        if self.enable_multimodal:
            print("多模态内容生成功能已启用")
    
    def _initialize_llm(self) -> BaseLLM:
        """初始化LLM客户端"""
        if self.config.default_llm_provider == "deepseek":
            return DeepSeekLLM(
                api_key=self.config.deepseek_api_key,
                model_name=self.config.deepseek_model
            )
        elif self.config.default_llm_provider == "openai":
            return OpenAILLM(
                api_key=self.config.openai_api_key,
                model_name=self.config.openai_model
            )
        else:
            raise ValueError(f"不支持的LLM提供商: {self.config.default_llm_provider}")
    
    def _initialize_nodes(self):
        """初始化处理节点"""
        self.first_search_node = FirstSearchNode(self.llm_client)
        self.reflection_node = ReflectionNode(self.llm_client)
        self.first_summary_node = FirstSummaryNode(self.llm_client)
        self.reflection_summary_node = ReflectionSummaryNode(self.llm_client)
        self.report_formatting_node = ReportFormattingNode(self.llm_client)
    
    def research(self, query: str, save_report: bool = True) -> str:
        """
        执行深度研究
        
        Args:
            query: 研究查询
            save_report: 是否保存报告到文件
            
        Returns:
            最终报告内容
        """
        print(f"\n{'='*60}")
        print(f"开始深度研究: {query}")
        print(f"{'='*60}")
        
        try:
            # Step 1: 生成报告结构
            self._generate_report_structure(query)
            
            # Step 2: 处理每个段落
            self._process_paragraphs()
            
            # Step 3: 生成最终报告
            final_report = self._generate_final_report()
            
            # Step 4: 保存报告
            if save_report:
                self._save_report(final_report)
            
            print(f"\n{'='*60}")
            print("深度研究完成！")
            print(f"{'='*60}")
            
            return final_report
            
        except Exception as e:
            print(f"研究过程中发生错误: {str(e)}")
            raise e
    
    def _generate_report_structure(self, query: str):
        """生成报告结构"""
        print(f"\n[步骤 1] 生成报告结构...")
        
        # 创建报告结构节点
        report_structure_node = ReportStructureNode(self.llm_client, query)
        
        # 生成结构并更新状态
        self.state = report_structure_node.mutate_state(state=self.state)
        
        print(f"报告结构已生成，共 {len(self.state.paragraphs)} 个段落:")
        for i, paragraph in enumerate(self.state.paragraphs, 1):
            print(f"  {i}. {paragraph.title}")
    
    def _process_paragraphs(self):
        """处理所有段落"""
        total_paragraphs = len(self.state.paragraphs)
        
        for i in range(total_paragraphs):
            print(f"\n[步骤 2.{i+1}] 处理段落: {self.state.paragraphs[i].title}")
            print("-" * 50)
            
            # 初始搜索和总结
            self._initial_search_and_summary(i)
            
            # 反思循环
            self._reflection_loop(i)
            
            # 标记段落完成
            self.state.paragraphs[i].research.mark_completed()
            
            progress = (i + 1) / total_paragraphs * 100
            print(f"段落处理完成 ({progress:.1f}%)")
    
    def _initial_search_and_summary(self, paragraph_index: int):
        """执行初始搜索和总结"""
        paragraph = self.state.paragraphs[paragraph_index]
        
        # 准备搜索输入
        search_input = {
            "title": paragraph.title,
            "content": paragraph.content
        }
        
        # 生成搜索查询
        print("  - 生成搜索查询...")
        search_output = self.first_search_node.run(search_input)
        search_query = search_output["search_query"]
        reasoning = search_output["reasoning"]
        
        print(f"  - 搜索查询: {search_query}")
        print(f"  - 推理: {reasoning}")
        
        # 执行搜索
        print("  - 执行网络搜索...")
        search_results = enhanced_tavily_search(
            search_query,
            max_results=self.config.max_search_results,
            timeout=self.config.search_timeout,
            api_key=self.config.tavily_api_key,
            enhance_with_rag=self.enable_rag,
            rag_top_k=self.rag_top_k
        )
        
        if search_results:
            print(f"  - 找到 {len(search_results)} 个搜索结果")
            for j, result in enumerate(search_results, 1):
                print(f"    {j}. {result['title'][:50]}...")
        else:
            print("  - 未找到搜索结果")
        
        # 更新状态中的搜索历史
        paragraph.research.add_search_results(search_query, search_results)
        
        # 生成初始总结
        print("  - 生成初始总结...")
        summary_input = {
            "title": paragraph.title,
            "content": paragraph.content,
            "search_query": search_query,
            "search_results": format_search_results_for_prompt(
                search_results, self.config.max_content_length
            )
        }
        
        # 更新状态
        self.state = self.first_summary_node.mutate_state(
            summary_input, self.state, paragraph_index
        )
        
        print("  - 初始总结完成")
    
    def _reflection_loop(self, paragraph_index: int):
        """执行反思循环"""
        paragraph = self.state.paragraphs[paragraph_index]
        
        for reflection_i in range(self.config.max_reflections):
            print(f"  - 反思 {reflection_i + 1}/{self.config.max_reflections}...")
            
            # 准备反思输入
            reflection_input = {
                "title": paragraph.title,
                "content": paragraph.content,
                "paragraph_latest_state": paragraph.research.latest_summary
            }
            
            # 生成反思搜索查询
            reflection_output = self.reflection_node.run(reflection_input)
            search_query = reflection_output["search_query"]
            reasoning = reflection_output["reasoning"]
            
            print(f"    反思查询: {search_query}")
            print(f"    反思推理: {reasoning}")
            
            # 执行反思搜索
            search_results = enhanced_tavily_search(
                search_query,
                max_results=self.config.max_search_results,
                timeout=self.config.search_timeout,
                api_key=self.config.tavily_api_key,
                enhance_with_rag=self.enable_rag,
                rag_top_k=self.rag_top_k
            )
            
            if search_results:
                print(f"    找到 {len(search_results)} 个反思搜索结果")
            
            # 更新搜索历史
            paragraph.research.add_search_results(search_query, search_results)
            
            # 生成反思总结
            reflection_summary_input = {
                "title": paragraph.title,
                "content": paragraph.content,
                "search_query": search_query,
                "search_results": format_search_results_for_prompt(
                    search_results, self.config.max_content_length
                ),
                "paragraph_latest_state": paragraph.research.latest_summary
            }
            
            # 更新状态
            self.state = self.reflection_summary_node.mutate_state(
                reflection_summary_input, self.state, paragraph_index
            )
            
            print(f"    反思 {reflection_i + 1} 完成")
    
    def _generate_final_report(self) -> str:
        """生成最终报告"""
        print(f"\n[步骤 3] 生成最终报告...")
        
        # 准备报告数据
        report_data = []
        for paragraph in self.state.paragraphs:
            report_data.append({
                "title": paragraph.title,
                "paragraph_latest_state": paragraph.research.latest_summary
            })
        
        # 格式化报告
        try:
            final_report = self.report_formatting_node.run(report_data)
        except Exception as e:
            print(f"LLM格式化失败，使用备用方法: {str(e)}")
            final_report = self.report_formatting_node.format_report_manually(
                report_data, self.state.report_title
            )
        
        # 更新状态
        self.state.final_report = final_report
        self.state.mark_completed()
        
        print("最终报告生成完成")
        return final_report
    
    def _save_report(self, report_content: str):
        """保存报告到文件（包括Markdown和HTML格式）"""
        # 生成文件名
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        query_safe = "".join(c for c in self.state.query if c.isalnum() or c in (' ', '-', '_')).rstrip()
        query_safe = query_safe.replace(' ', '_')[:30]
        
        # 保存Markdown报告
        md_filename = f"deep_search_report_{query_safe}_{timestamp}.md"
        md_filepath = os.path.join(self.config.output_dir, md_filename)
        
        with open(md_filepath, 'w', encoding='utf-8') as f:
            f.write(report_content)
        
        print(f"Markdown报告已保存到: {md_filepath}")
        
        # 生成并保存HTML报告
        try:
            from .utils.html_generator import generate_html_report, save_html_report
            
            # 提取段落数据用于HTML报告
            paragraphs_data = []
            lines = report_content.split('\n')
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
            # 如果启用了多模态功能，生成一些示例图表和图像
            images = None
            if self.enable_multimodal:
                try:
                    # 生成示例图表
                    chart_html = self.chart_generator.generate_bar_chart(
                        [len(p["content"]) for p in paragraphs_data], 
                        [p["title"] for p in paragraphs_data], 
                        "段落字数统计", 
                        "段落", 
                        "字数"
                    )
                    
                    # 生成示例图像（这里我们创建一个简单的图表作为图像）
                    import matplotlib.pyplot as plt
                    import io
                    import base64
                    
                    # 创建一个简单的图表
                    fig, ax = plt.subplots(figsize=(10, 6))
                    ax.bar(range(len(paragraphs_data)), [len(p["content"]) for p in paragraphs_data])
                    ax.set_xlabel("段落")
                    ax.set_ylabel("字数")
                    ax.set_title("段落字数统计")
                    plt.xticks(range(len(paragraphs_data)), [p["title"] for p in paragraphs_data], rotation=45, ha="right")
                    plt.tight_layout()
                    
                    # 将图表转换为base64编码
                    buffer = io.BytesIO()
                    plt.savefig(buffer, format='png')
                    buffer.seek(0)
                    image_base64 = base64.b64encode(buffer.read()).decode('utf-8')
                    plt.close(fig)
                    
                    images = [image_base64]
                    print("已生成多模态内容（图表和图像）")
                except Exception as e:
                    print(f"生成多模态内容时出错: {str(e)}")
            
            html_content = generate_html_report(self.state.report_title, paragraphs_data, self.config.output_dir, images)
            html_filepath = save_html_report(html_content, self.state.report_title, self.config.output_dir)
            print(f"HTML报告已保存到: {html_filepath}")
            
        except Exception as e:
            print(f"生成HTML报告时出错: {str(e)}")
            print("将继续保存Markdown格式报告")
        
        # 保存状态（如果配置允许）
        if self.config.save_intermediate_states:
            state_filename = f"state_{query_safe}_{timestamp}.json"
            state_filepath = os.path.join(self.config.output_dir, state_filename)
            self.state.save_to_file(state_filepath)
            print(f"状态已保存到: {state_filepath}")
    
    def get_progress_summary(self) -> Dict[str, Any]:
        """获取进度摘要"""
        return self.state.get_progress_summary()
    
    def load_state(self, filepath: str):
        """从文件加载状态"""
        self.state = State.load_from_file(filepath)
        print(f"状态已从 {filepath} 加载")
    
    def save_state(self, filepath: str):
        """保存状态到文件"""
        self.state.save_to_file(filepath)
        print(f"状态已保存到 {filepath}")


def create_agent(config_file: Optional[str] = None) -> DeepSearchAgent:
    """
    创建Deep Search Agent实例的便捷函数
    
    Args:
        config_file: 配置文件路径
        
    Returns:
        DeepSearchAgent实例
    """
    config = load_config(config_file)
    return DeepSearchAgent(config)
