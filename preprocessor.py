"""
图像预处理模块
负责读取、调整大小、去噪和增强图像
"""
import cv2
import numpy as np
from PIL import Image


class ImagePreprocessor:
    """图像预处理器类"""
    
    def __init__(self, image_path=None):
        """
        初始化预处理器
        
        Args:
            image_path: 图像路径，可以为 None
        """
        self.image_path = image_path
        self.original_image = None
        self.processed_image = None
    
    def load_image(self, image_path):
        """
        加载图像
        
        Args:
            image_path: 图像文件路径
            
        Returns:
            bool: 加载是否成功
        """
        try:
            self.image_path = image_path
            # 使用 OpenCV 读取图像
            self.original_image = cv2.imread(image_path)
            
            if self.original_image is None:
                # 如果 OpenCV 失败，尝试使用 PIL
                img_pil = Image.open(image_path)
                self.original_image = cv2.cvtColor(np.array(img_pil), cv2.COLOR_RGB2BGR)
            
            self.processed_image = self.original_image.copy()
            return True
        except Exception as e:
            print(f"加载图像失败：{str(e)}")
            return False
    
    def resize_image(self, max_width=800, max_height=600):
        """
        调整图像大小
        
        Args:
            max_width: 最大宽度
            max_height: 最大高度
            
        Returns:
            numpy.ndarray: 调整后的图像
        """
        if self.original_image is None:
            raise ValueError("请先加载图像")
        
        height, width = self.original_image.shape[:2]
        
        # 计算缩放比例
        scale = min(max_width / width, max_height / height)
        
        if scale < 1.0:
            new_width = int(width * scale)
            new_height = int(height * scale)
            self.processed_image = cv2.resize(
                self.original_image, 
                (new_width, new_height), 
                interpolation=cv2.INTER_AREA
            )
        else:
            self.processed_image = self.original_image.copy()
        
        return self.processed_image
    
    def denoise(self, strength=10):
        """
        去噪处理
        
        Args:
            strength: 去噪强度
            
        Returns:
            numpy.ndarray: 去噪后的图像
        """
        if self.processed_image is None:
            self.processed_image = self.original_image.copy()
        
        # 使用非局部均值去噪
        self.processed_image = cv2.fastNlMeansDenoisingColored(
            self.processed_image, 
            None, 
            h=strength, 
            hForColorComponents=strength
        )
        
        return self.processed_image
    
    def enhance_contrast(self):
        """
        增强对比度
        
        Returns:
            numpy.ndarray: 增强后的图像
        """
        if self.processed_image is None:
            self.processed_image = self.original_image.copy()
        
        # 转换到 LAB 色彩空间
        lab = cv2.cvtColor(self.processed_image, cv2.COLOR_BGR2LAB)
        
        # 对 L 通道（亮度）应用 CLAHE
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        lab[:, :, 0] = clahe.apply(lab[:, :, 0])
        
        # 转换回 BGR
        self.processed_image = cv2.cvtColor(lab, cv2.COLOR_LAB2BGR)
        
        return self.processed_image
    
    def get_processed_image(self):
        """获取处理后的图像"""
        return self.processed_image
    
    def get_original_image(self):
        """获取原始图像"""
        return self.original_image
    
    def reset(self):
        """重置为原始图像"""
        if self.original_image is not None:
            self.processed_image = self.original_image.copy()
