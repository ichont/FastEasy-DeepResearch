"""
搜索工具实现
支持多种搜索引擎，主要使用Tavily搜索
集成了LangChain RAG功能以增强搜索能力
"""

import os
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from tavily import TavilyClient

# 尝试导入LangChain RAG模块（如果可用）
try:
    from ..utils.langchain_rag import LangChainRAG
    LANGCHAIN_AVAILABLE = True
except ImportError:
    LANGCHAIN_AVAILABLE = False
    print("警告: 未找到LangChain RAG模块，将使用基础搜索功能")


@dataclass
class SearchResult:
    """搜索结果数据类"""
    title: str
    url: str
    content: str
    score: Optional[float] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            "title": self.title,
            "url": self.url,
            "content": self.content,
            "score": self.score
        }


class TavilySearch:
    """Tavily搜索客户端封装"""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        初始化Tavily搜索客户端
        
        Args:
            api_key: Tavily API密钥，如果不提供则从环境变量读取
        """
        if api_key is None:
            api_key = os.getenv("TAVILY_API_KEY")
            if not api_key:
                raise ValueError("Tavily API Key未找到！请设置TAVILY_API_KEY环境变量或在初始化时提供")
        
        self.client = TavilyClient(api_key=api_key)
    
    def search(self, query: str, max_results: int = 5, include_raw_content: bool = True, 
               timeout: int = 240) -> List[SearchResult]:
        """
        执行搜索
        
        Args:
            query: 搜索查询
            max_results: 最大结果数量
            include_raw_content: 是否包含原始内容
            timeout: 超时时间（秒）
            
        Returns:
            搜索结果列表
        """
        try:
            # 调用Tavily API
            response = self.client.search(
                query=query,
                max_results=max_results,
                include_raw_content=include_raw_content,
                timeout=timeout
            )
            
            # 解析结果
            results = []
            if 'results' in response:
                for item in response['results']:
                    result = SearchResult(
                        title=item.get('title', ''),
                        url=item.get('url', ''),
                        content=item.get('content', ''),
                        score=item.get('score')
                    )
                    results.append(result)
            
            return results
            
        except Exception as e:
            print(f"搜索错误: {str(e)}")
            return []


# 全局搜索客户端实例
_tavily_client = None


def get_tavily_client() -> TavilySearch:
    """获取全局Tavily客户端实例"""
    global _tavily_client
    if _tavily_client is None:
        _tavily_client = TavilySearch()
    return _tavily_client


def tavily_search(query: str, max_results: int = 5, include_raw_content: bool = True, 
                  timeout: int = 240, api_key: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    便捷的Tavily搜索函数
    
    Args:
        query: 搜索查询
        max_results: 最大结果数量
        include_raw_content: 是否包含原始内容
        timeout: 超时时间（秒）
        api_key: Tavily API密钥，如果提供则使用此密钥，否则使用全局客户端
        
    Returns:
        搜索结果字典列表，保持与原始经验贴兼容的格式
    """
    try:
        if api_key:
            # 使用提供的API密钥创建临时客户端
            client = TavilySearch(api_key)
        else:
            # 使用全局客户端
            client = get_tavily_client()
        
        results = client.search(query, max_results, include_raw_content, timeout)
        
        # 转换为字典格式以保持兼容性
        return [result.to_dict() for result in results]
        
    except Exception as e:
        print(f"搜索功能调用错误: {str(e)}")
        return []


def enhanced_tavily_search(query: str, max_results: int = 5, include_raw_content: bool = True,
                           timeout: int = 240, api_key: Optional[str] = None,
                           enhance_with_rag: bool = False, rag_top_k: int = 3) -> List[Dict[str, Any]]:
    """
    增强版Tavily搜索函数，可选择性地使用LangChain RAG来增强搜索结果
    
    Args:
        query: 搜索查询
        max_results: 最大结果数量
        include_raw_content: 是否包含原始内容
        timeout: 超时时间（秒）
        api_key: Tavily API密钥，如果提供则使用此密钥，否则使用全局客户端
        enhance_with_rag: 是否使用RAG增强搜索结果
        rag_top_k: 使用RAG时返回的最相关文档数量
        
    Returns:
        搜索结果字典列表，保持与原始经验贴兼容的格式
    """
    # 首先执行常规Tavily搜索
    tavily_results = tavily_search(query, max_results, include_raw_content, timeout, api_key)
    
    # 如果不需要RAG增强或LangChain不可用，直接返回Tavily结果
    if not enhance_with_rag or not LANGCHAIN_AVAILABLE:
        return tavily_results
    
    try:
        # 初始化LangChain RAG
        # 注意：这里我们使用OpenAI嵌入模型作为默认选项，因为大多数用户可能已经有OpenAI API密钥
        # 在实际应用中，应该从配置中获取这些值
        rag = LangChainRAG(
            embedding_provider="openai",  # 默认使用OpenAI
            openai_api_key=os.getenv("OPENAI_API_KEY"),  # 从环境变量获取API密钥
            deepseek_api_key=os.getenv("DEEPSEEK_API_KEY")  # 也传递DeepSeek API密钥以备选择
        )
        
        # 使用RAG增强搜索结果
        enhanced_results = rag.enhance_search_results(query, tavily_results, top_k=rag_top_k)
        return enhanced_results
        
    except Exception as e:
        print(f"使用RAG增强搜索结果时出错: {str(e)}")
        # 出错时返回原始Tavily结果
        return tavily_results


def test_search(query: str = "人工智能发展趋势 2025", max_results: int = 3):
    """
    测试搜索功能
    
    Args:
        query: 测试查询
        max_results: 最大结果数量
    """
    print(f"\n=== 测试Tavily搜索功能 ===")
    print(f"搜索查询: {query}")
    print(f"最大结果数: {max_results}")
    
    try:
        results = tavily_search(query, max_results=max_results)
        
        if results:
            print(f"\n找到 {len(results)} 个结果:")
            for i, result in enumerate(results, 1):
                print(f"\n结果 {i}:")
                print(f"标题: {result['title']}")
                print(f"链接: {result['url']}")
                print(f"内容摘要: {result['content'][:200]}...")
                if result.get('score'):
                    print(f"相关度评分: {result['score']}")
        else:
            print("未找到搜索结果")
            
    except Exception as e:
        print(f"搜索测试失败: {str(e)}")


if __name__ == "__main__":
    # 运行测试
    test_search()
