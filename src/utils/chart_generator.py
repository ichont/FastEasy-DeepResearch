"""
图表生成工具
支持多种图表类型（柱状图、折线图、饼图等）
"""

import base64
import io
from typing import List, Dict, Any, Union
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')  # 使用非交互式后端
import numpy as np

# 设置中文字体支持
plt.rcParams['font.sans-serif'] = ['SimHei', 'Arial Unicode MS', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

class ChartGenerator:
    """图表生成器类"""
    
    def __init__(self):
        """初始化图表生成器"""
        pass
    
    def generate_bar_chart(self, data: Dict[str, float], title: str = "柱状图") -> str:
        """
        生成柱状图并返回Base64编码的图片
        
        Args:
            data: 数据字典，键为标签，值为数值
            title: 图表标题
            
        Returns:
            Base64编码的图片字符串
        """
        # 准备数据
        labels = list(data.keys())
        values = list(data.values())
        
        # 创建图表
        fig, ax = plt.subplots(figsize=(10, 6))
        bars = ax.bar(labels, values, color=plt.cm.Set3(np.linspace(0, 1, len(labels))))
        
        # 设置标题和标签
        ax.set_title(title, fontsize=16, pad=20)
        ax.set_ylabel('数值')
        
        # 旋转x轴标签以防重叠
        plt.setp(ax.get_xticklabels(), rotation=45, ha="right", rotation_mode="anchor")
        
        # 在柱子上添加数值标签
        for bar in bars:
            height = bar.get_height()
            ax.annotate(f'{height:.1f}',
                        xy=(bar.get_x() + bar.get_width() / 2, height),
                        xytext=(0, 3),  # 3 points vertical offset
                        textcoords="offset points",
                        ha='center', va='bottom')
        
        # 调整布局
        plt.tight_layout()
        
        # 保存为base64字符串
        img_buffer = io.BytesIO()
        plt.savefig(img_buffer, format='png', dpi=300, bbox_inches='tight')
        img_buffer.seek(0)
        img_base64 = base64.b64encode(img_buffer.read()).decode('utf-8')
        plt.close(fig)  # 关闭图表释放内存
        
        return img_base64
    
    def generate_line_chart(self, data: Dict[str, List[float]], labels: List[str], title: str = "折线图") -> str:
        """
        生成折线图并返回Base64编码的图片
        
        Args:
            data: 数据字典，键为系列名称，值为数值列表
            labels: x轴标签列表
            title: 图表标题
            
        Returns:
            Base64编码的图片字符串
        """
        # 创建图表
        fig, ax = plt.subplots(figsize=(12, 6))
        
        # 绘制每条线
        for series_name, values in data.items():
            ax.plot(labels, values, marker='o', linewidth=2, label=series_name)
        
        # 设置标题和标签
        ax.set_title(title, fontsize=16, pad=20)
        ax.set_xlabel('时间/类别')
        ax.set_ylabel('数值')
        
        # 旋转x轴标签以防重叠
        plt.setp(ax.get_xticklabels(), rotation=45, ha="right", rotation_mode="anchor")
        
        # 添加图例
        ax.legend()
        
        # 添加网格
        ax.grid(True, alpha=0.3)
        
        # 调整布局
        plt.tight_layout()
        
        # 保存为base64字符串
        img_buffer = io.BytesIO()
        plt.savefig(img_buffer, format='png', dpi=300, bbox_inches='tight')
        img_buffer.seek(0)
        img_base64 = base64.b64encode(img_buffer.read()).decode('utf-8')
        plt.close(fig)  # 关闭图表释放内存
        
        return img_base64
    
    def generate_pie_chart(self, data: Dict[str, float], title: str = "饼图") -> str:
        """
        生成饼图并返回Base64编码的图片
        
        Args:
            data: 数据字典，键为标签，值为数值
            title: 图表标题
            
        Returns:
            Base64编码的图片字符串
        """
        # 准备数据
        labels = list(data.keys())
        values = list(data.values())
        
        # 创建图表
        fig, ax = plt.subplots(figsize=(10, 8))
        
        # 生成颜色
        colors = plt.cm.Set3(np.linspace(0, 1, len(labels)))
        
        # 绘制饼图
        wedges, texts, autotexts = ax.pie(values, labels=labels, autopct='%1.1f%%', 
                                          colors=colors, startangle=90)
        
        # 设置标题
        ax.set_title(title, fontsize=16, pad=20)
        
        # 调整文本大小
        for autotext in autotexts:
            autotext.set_color('white')
            autotext.set_fontweight('bold')
        
        # 添加图例
        ax.legend(wedges, labels, title="类别", loc="center left", bbox_to_anchor=(1, 0, 0.5, 1))
        
        # 确保饼图是圆形
        ax.axis('equal')
        
        # 调整布局
        plt.tight_layout()
        
        # 保存为base64字符串
        img_buffer = io.BytesIO()
        plt.savefig(img_buffer, format='png', dpi=300, bbox_inches='tight')
        img_buffer.seek(0)
        img_base64 = base64.b64encode(img_buffer.read()).decode('utf-8')
        plt.close(fig)  # 关闭图表释放内存
        
        return img_base64
    
    def generate_chart_html(self, chart_base64: str, chart_type: str, title: str = "") -> str:
        """
        生成包含图表的HTML代码
        
        Args:
            chart_base64: Base64编码的图片字符串
            chart_type: 图表类型
            title: 图表标题
            
        Returns:
            HTML代码字符串
        """
        html = f"""
        <div class="chart-container">
            <h3>{title}</h3>
            <img src="data:image/png;base64,{chart_base64}" alt="{chart_type}图表" style="max-width: 100%; height: auto;">
        </div>
        """
        return html

# 全局实例
chart_generator = ChartGenerator()

# 便捷函数
def generate_bar_chart(data: Dict[str, float], title: str = "柱状图") -> str:
    """生成柱状图"""
    return chart_generator.generate_bar_chart(data, title)

def generate_line_chart(data: Dict[str, List[float]], labels: List[str], title: str = "折线图") -> str:
    """生成折线图"""
    return chart_generator.generate_line_chart(data, labels, title)

def generate_pie_chart(data: Dict[str, float], title: str = "饼图") -> str:
    """生成饼图"""
    return chart_generator.generate_pie_chart(data, title)

def generate_chart_html(chart_base64: str, chart_type: str, title: str = "") -> str:
    """生成包含图表的HTML代码"""
    return chart_generator.generate_chart_html(chart_base64, chart_type, title)