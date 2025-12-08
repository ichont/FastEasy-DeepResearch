"""
LangChain RAG (Retrieval Augmented Generation) 模块
为DeepSearchAgent提供增强的文档检索和生成能力
"""

import os
import faiss
import numpy as np
from typing import List, Dict, Any, Optional
from langchain.docstore.in_memory import InMemoryDocstore
from langchain.vectorstores import FAISS
from langchain.embeddings import OpenAIEmbeddings, HuggingFaceEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document


class LangChainRAG:
    """基于LangChain的RAG实现类"""
    
    def __init__(self, llm_provider: str = "openai", api_key: Optional[str] = None):
        """
        初始化LangChainRAG
        
        Args:
            llm_provider: LLM提供商 ("openai" 或 "deepseek")
            api_key: API密钥
        """
        self.llm_provider = llm_provider
        self.api_key = api_key
        self.vector_store = None
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            separators=["\n\n", "\n", ". ", " ", ""]
        )
        
        # 初始化嵌入模型
        if llm_provider == "openai":
            if api_key:
                self.embeddings = OpenAIEmbeddings(openai_api_key=api_key)
            else:
                raise ValueError("OpenAI API key is required for OpenAI embeddings")
        else:
            # 使用Sentence Transformers的开源嵌入模型
            self.embeddings = HuggingFaceEmbeddings(
                model_name="sentence-transformers/all-MiniLM-L6-v2"
            )
    
    def load_documents(self, documents: List[str]) -> List[Document]:
        """
        加载文档
        
        Args:
            documents: 文档字符串列表
            
        Returns:
            Document对象列表
        """
        docs = []
        for i, doc_text in enumerate(documents):
            docs.append(Document(
                page_content=doc_text,
                metadata={"source": f"doc_{i}"}
            ))
        return docs
    
    def split_documents(self, documents: List[Document]) -> List[Document]:
        """
        分割文档
        
        Args:
            documents: Document对象列表
            
        Returns:
            分割后的Document对象列表
        """
        return self.text_splitter.split_documents(documents)
    
    def create_vector_store(self, documents: List[Document]) -> FAISS:
        """
        创建向量存储
        
        Args:
            documents: Document对象列表
            
        Returns:
            FAISS向量存储对象
        """
        # 如果已有向量存储，则添加文档
        if self.vector_store is not None:
            self.vector_store.add_documents(documents)
            return self.vector_store
            
        # 否则创建新的向量存储
        self.vector_store = FAISS.from_documents(
            documents, 
            self.embeddings
        )
        return self.vector_store
    
    def retrieve_documents(self, query: str, k: int = 4) -> List[Document]:
        """
        检索相关文档
        
        Args:
            query: 查询字符串
            k: 返回的文档数量
            
        Returns:
            相关文档列表
        """
        if self.vector_store is None:
            raise ValueError("Vector store is not initialized. Please load documents first.")
            
        return self.vector_store.similarity_search(query, k=k)
    
    def enhance_search_results(self, search_results: List[Dict[str, Any]], 
                              query: str) -> List[Dict[str, Any]]:
        """
        增强搜索结果
        
        Args:
            search_results: 原始搜索结果列表
            query: 查询字符串
            
        Returns:
            增强后的搜索结果列表
        """
        # 提取搜索结果的内容
        documents_content = [result.get('content', '') for result in search_results if result.get('content')]
        
        # 加载和分割文档
        docs = self.load_documents(documents_content)
        split_docs = self.split_documents(docs)
        
        # 创建向量存储
        self.create_vector_store(split_docs)
        
        # 检索相关文档
        relevant_docs = self.retrieve_documents(query, k=min(4, len(split_docs)))
        
        # 将检索到的文档信息添加到原始搜索结果中
        enhanced_results = search_results.copy()
        for i, doc in enumerate(relevant_docs):
            if i < len(enhanced_results):
                enhanced_results[i]['relevance_score'] = getattr(doc, 'metadata', {}).get('score', 1.0)
                enhanced_results[i]['chunk_source'] = getattr(doc, 'metadata', {}).get('source', '')
            else:
                enhanced_results.append({
                    'content': doc.page_content,
                    'relevance_score': getattr(doc, 'metadata', {}).get('score', 1.0),
                    'chunk_source': getattr(doc, 'metadata', {}).get('source', ''),
                    'title': f"Enhanced Result {i+1}"
                })
                
        return enhanced_results


# 示例使用方法
def example_usage():
    """示例使用方法"""
    # 初始化RAG模块
    rag = LangChainRAG(llm_provider="openai", api_key="your-api-key")
    
    # 示例文档
    documents = [
        "人工智能是计算机科学的一个分支，它企图了解智能的实质，并生产出一种新的能以人类智能相似的方式做出反应的智能机器。",
        "机器学习是人工智能的一个子集，它使计算机能够从数据中学习并做出决策或预测。",
        "深度学习是机器学习的一个子集，它模仿人脑的神经网络结构来处理数据。"
    ]
    
    # 加载和分割文档
    docs = rag.load_documents(documents)
    split_docs = rag.split_documents(docs)
    
    # 创建向量存储
    vector_store = rag.create_vector_store(split_docs)
    
    # 检索相关文档
    query = "什么是深度学习？"
    results = rag.retrieve_documents(query, k=2)
    
    for doc in results:
        print(f"Content: {doc.page_content}")
        print(f"Metadata: {doc.metadata}")
        print("---")


if __name__ == "__main__":
    example_usage()