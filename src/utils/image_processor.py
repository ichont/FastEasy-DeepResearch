"""
图像处理工具
支持在报告中插入和显示图像
"""

import base64
import os
from typing import Union, Tuple
from PIL import Image
import io

class ImageProcessor:
    """图像处理器类"""
    
    def __init__(self):
        """初始化图像处理器"""
        pass
    
    def encode_image_to_base64(self, image_path: str, max_size: Tuple[int, int] = (800, 600)) -> str:
        """
        将图像文件编码为Base64字符串
        
        Args:
            image_path: 图像文件路径
            max_size: 图像最大尺寸 (width, height)
            
        Returns:
            Base64编码的图像字符串
        """
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"图像文件不存在: {image_path}")
        
        # 打开图像
        with Image.open(image_path) as img:
            # 转换为RGB模式（如果是RGBA或其他模式）
            if img.mode != 'RGB':
                img = img.convert('RGB')
            
            # 调整图像尺寸
            img.thumbnail(max_size, Image.Resampling.LANCZOS)
            
            # 保存为JPEG格式到内存缓冲区
            img_buffer = io.BytesIO()
            img.save(img_buffer, format='JPEG', quality=85)
            img_buffer.seek(0)
            
            # 编码为Base64
            img_base64 = base64.b64encode(img_buffer.read()).decode('utf-8')
            
        return img_base64
    
    def encode_image_bytes_to_base64(self, image_bytes: bytes, max_size: Tuple[int, int] = (800, 600)) -> str:
        """
        将图像字节编码为Base64字符串
        
        Args:
            image_bytes: 图像字节数据
            max_size: 图像最大尺寸 (width, height)
            
        Returns:
            Base64编码的图像字符串
        """
        # 从字节创建图像
        with Image.open(io.BytesIO(image_bytes)) as img:
            # 转换为RGB模式（如果是RGBA或其他模式）
            if img.mode != 'RGB':
                img = img.convert('RGB')
            
            # 调整图像尺寸
            img.thumbnail(max_size, Image.Resampling.LANCZOS)
            
            # 保存为JPEG格式到内存缓冲区
            img_buffer = io.BytesIO()
            img.save(img_buffer, format='JPEG', quality=85)
            img_buffer.seek(0)
            
            # 编码为Base64
            img_base64 = base64.b64encode(img_buffer.read()).decode('utf-8')
            
        return img_base64
    
    def generate_image_html(self, img_base64: str, alt_text: str = "", caption: str = "") -> str:
        """
        生成包含图像的HTML代码
        
        Args:
            img_base64: Base64编码的图像字符串
            alt_text: 图像替代文本
            caption: 图像说明文字
            
        Returns:
            HTML代码字符串
        """
        html = f"""
        <div class="image-container">
            <img src="data:image/jpeg;base64,{img_base64}" alt="{alt_text}" style="max-width: 100%; height: auto; border-radius: 8px;">
            """
        
        if caption:
            html += f'<div class="image-caption">{caption}</div>'
        
        html += """
        </div>
        """
        
        return html

# 全局实例
image_processor = ImageProcessor()

# 便捷函数
def encode_image_to_base64(image_path: str, max_size: Tuple[int, int] = (800, 600)) -> str:
    """将图像文件编码为Base64字符串"""
    return image_processor.encode_image_to_base64(image_path, max_size)

def encode_image_bytes_to_base64(image_bytes: bytes, max_size: Tuple[int, int] = (800, 600)) -> str:
    """将图像字节编码为Base64字符串"""
    return image_processor.encode_image_bytes_to_base64(image_bytes, max_size)

def generate_image_html(img_base64: str, alt_text: str = "", caption: str = "") -> str:
    """生成包含图像的HTML代码"""
    return image_processor.generate_image_html(img_base64, alt_text, caption)