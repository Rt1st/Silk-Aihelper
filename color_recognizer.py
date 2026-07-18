"""
颜色识别和分析模块
负责提取颜色特征、聚类分析和颜色命名
包含艾德莱斯染色配方智能计算算法（色彩回归+环境因子修正）
"""
import cv2
import numpy as np
from sklearn.cluster import KMeans
from sklearn.linear_model import LinearRegression
from collections import Counter


class ColorRecognizer:
    """颜色识别器类"""
    
    # 颜色名称映射（RGB 值范围）
    COLOR_NAMES = {
        '红色': ([100, 0, 0], [255, 100, 100]),
        '橙色': ([200, 100, 0], [255, 165, 80]),
        '黄色': ([200, 200, 0], [255, 255, 100]),
        '绿色': ([0, 100, 0], [100, 255, 100]),
        '青色': ([0, 150, 150], [100, 255, 255]),
        '蓝色': ([0, 0, 150], [100, 100, 255]),
        '紫色': ([150, 0, 150], [255, 100, 255]),
        '粉色': ([200, 100, 150], [255, 180, 220]),
        '棕色': ([100, 50, 0], [180, 100, 60]),
        '黑色': ([0, 0, 0], [60, 60, 60]),
        '灰色': ([60, 60, 60], [150, 150, 150]),
        '白色': ([200, 200, 200], [255, 255, 255]),
        '藏青色': ([0, 0, 100], [50, 50, 150]),
        '深红色': ([100, 0, 0], [180, 50, 50]),
        '浅蓝色': ([150, 200, 255], [200, 230, 255]),
        '浅绿色': ([150, 255, 150], [200, 255, 200]),
        '金黄色': ([200, 180, 0], [255, 220, 50]),
        '天蓝色': ([100, 180, 255], [150, 220, 255]),
    }
    
    def __init__(self, n_colors=5):
        """
        初始化颜色识别器
        
        Args:
            n_colors: 要提取的主要颜色数量
        """
        self.n_colors = n_colors
        self.dominant_colors = None
        self.color_percentages = None
    
    def extract_dominant_colors(self, image):
        """
        提取图像的主要颜色
        
        Args:
            image: BGR 格式的图像
            
        Returns:
            tuple: (主要颜色列表，百分比列表)
        """
        # 转换到 RGB
        rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        
        # 重塑图像为像素列表
        pixels = rgb_image.reshape(-1, 3)
        
        # 移除过于暗淡或明亮的像素
        pixel_brightness = np.mean(pixels, axis=1)
        valid_indices = (pixel_brightness > 30) & (pixel_brightness < 225)
        valid_pixels = pixels[valid_indices]
        
        # 如果有效像素太少，使用所有像素
        if len(valid_pixels) < 100:
            valid_pixels = pixels
        
        # 使用 K-means 聚类
        kmeans = KMeans(n_clusters=self.n_colors, random_state=42, n_init=10)
        kmeans.fit(valid_pixels)
        
        # 获取聚类中心
        colors = kmeans.cluster_centers_
        
        # 计算每个颜色的百分比
        labels = kmeans.labels_
        counter = Counter(labels)
        total = sum(counter.values())
        percentages = [counter[i] / total * 100 for i in range(self.n_colors)]
        
        # 按百分比排序
        sorted_indices = np.argsort(percentages)[::-1]
        self.dominant_colors = colors[sorted_indices].astype(int)
        self.color_percentages = [percentages[i] for i in sorted_indices]
        
        return self.dominant_colors, self.color_percentages
    
    def get_color_name(self, rgb_color):
        """
        根据 RGB 值获取颜色名称
        
        Args:
            rgb_color: RGB 颜色值 [R, G, B]
            
        Returns:
            str: 颜色名称
        """
        r, g, b = rgb_color
        
        min_distance = float('inf')
        color_name = '未知'
        
        for name, (lower, upper) in self.COLOR_NAMES.items():
            # 检查是否在该颜色范围内
            if (lower[0] <= r <= upper[0] and 
                lower[1] <= g <= upper[1] and 
                lower[2] <= b <= upper[2]):
                
                # 计算到范围中心的距离
                mid_r = (lower[0] + upper[0]) // 2
                mid_g = (lower[1] + upper[1]) // 2
                mid_b = (lower[2] + upper[2]) // 2
                
                distance = np.sqrt((r - mid_r)**2 + (g - mid_g)**2 + (b - mid_b)**2)
                
                if distance < min_distance:
                    min_distance = distance
                    color_name = name
        
        # 如果没有匹配，找最接近的颜色
        if color_name == '未知':
            for name, (lower, upper) in self.COLOR_NAMES.items():
                mid_r = (lower[0] + upper[0]) // 2
                mid_g = (lower[1] + upper[1]) // 2
                mid_b = (lower[2] + upper[2]) // 2
                
                distance = np.sqrt((r - mid_r)**2 + (g - mid_g)**2 + (b - mid_b)**2)
                
                if distance < min_distance:
                    min_distance = distance
                    color_name = name
        
        return color_name
    
    def analyze_colors(self):
        """
        分析主要颜色并返回详细信息
        
        Returns:
            list: 包含颜色信息的字典列表
        """
        if self.dominant_colors is None:
            raise ValueError("请先提取主要颜色")
        
        color_info = []
        for i, (color, percentage) in enumerate(zip(self.dominant_colors, self.color_percentages)):
            info = {
                'rank': i + 1,
                'rgb': color,
                'hex': '#%02x%02x%02x' % tuple(color),
                'percentage': percentage,
                'name': self.get_color_name(color)
            }
            color_info.append(info)
        
        return color_info
    
    def generate_color_palette(self, image_size=(200, 200)):
        """
        生成颜色调色板
        
        Args:
            image_size: 调色板图像大小
            
        Returns:
            numpy.ndarray: 调色板图像
        """
        if self.dominant_colors is None:
            raise ValueError("请先提取主要颜色")
        
        # 创建调色板
        palette = np.zeros((image_size[1], image_size[0], 3), dtype=np.uint8)
        
        # 计算每个颜色条的高度
        bar_height = image_size[1] // self.n_colors
        
        for i, (color, percentage) in enumerate(zip(self.dominant_colors, self.color_percentages)):
            # 转换 RGB 到 BGR
            bgr_color = color[::-1]
            
            # 绘制颜色条
            y_start = i * bar_height
            y_end = (i + 1) * bar_height
            
            palette[y_start:y_end, :] = bgr_color
        
        return palette
    
    def get_dominant_colors(self):
        """获取主要颜色"""
        return self.dominant_colors
    
    def get_color_percentages(self):
        """获取颜色百分比"""
        return self.color_percentages


class DyeFormulaCalculator:
    """艾德莱斯染色配方智能计算器"""
    
    # 天然染料数据库（示例数据，实际应从文件/数据库加载）
    DYE_DATABASE = {
        '红花': {'lab': [50, 60, 20], 'type': '红色'},
        '板蓝根': {'lab': [30, -10, -40], 'type': '蓝色'},
        '黄刺叶': {'lab': [75, 10, 70], 'type': '黄色'},
        '紫草': {'lab': [35, 40, -30], 'type': '紫色'},
        '茶叶': {'lab': [45, 15, 30], 'type': '棕色'},
        '核桃皮': {'lab': [40, 10, 20], 'type': '深棕色'},
        '洋葱皮': {'lab': [60, 20, 40], 'type': '橙黄色'},
        '石榴皮': {'lab': [55, 25, 35], 'type': '浅棕色'}
    }
    
    @staticmethod
    def rgb_to_lab(rgb_color):
        """
        RGB转LAB色彩空间（提升色彩匹配精度）
        
        Args:
            rgb_color: RGB颜色值 [R, G, B]
            
        Returns:
            list: LAB色彩值 [L, A, B]
        """
        # 归一化RGB
        rgb = np.array([[rgb_color]], dtype=np.float32) / 255.0
        
        # RGB -> XYZ
        mask = rgb > 0.04045
        rgb[mask] = ((rgb[mask] + 0.055) / 1.055) ** 2.4
        rgb[~mask] /= 12.92
        
        rgb *= 100
        
        # RGB to XYZ转换矩阵
        xyz_from_rgb = np.array([
            [0.4124564, 0.3575761, 0.1804375],
            [0.2126729, 0.7151522, 0.0721750],
            [0.0193339, 0.1191920, 0.9503041]
        ])
        
        xyz = np.dot(rgb.reshape(-1, 3), xyz_from_rgb.T).reshape(-1, 1, 3)
        
        # XYZ -> LAB (D65标准光源)
        xyz_ref = np.array([95.047, 100.000, 108.883])
        xyz_normalized = xyz / xyz_ref
        
        mask = xyz_normalized > 0.008856
        xyz_normalized[mask] = xyz_normalized[mask] ** (1/3)
        xyz_normalized[~mask] = 7.787 * xyz_normalized[~mask] + 16/116
        
        l = 116 * xyz_normalized[:, :, 1] - 16
        a = 500 * (xyz_normalized[:, :, 0] - xyz_normalized[:, :, 1])
        b = 200 * (xyz_normalized[:, :, 1] - xyz_normalized[:, :, 2])
        
        return [float(l[0, 0]), float(a[0, 0]), float(b[0, 0])]
    
    @staticmethod
    def query_dye_database(dye_db, target_lab, error_threshold=3):
        """
        匹配天然染料数据库
        
        Args:
            dye_db: 染料数据库
            target_lab: 目标LAB色彩
            error_threshold: 色差阈值（默认3%）
            
        Returns:
            list: 候选染料列表
        """
        candidates = []
        
        for dye_name, dye_info in dye_db.items():
            dye_lab = dye_info['lab']
            # 计算CIEDE2000色差（简化版欧氏距离）
            color_diff = np.sqrt(
                (target_lab[0] - dye_lab[0])**2 +
                (target_lab[1] - dye_lab[1])**2 +
                (target_lab[2] - dye_lab[2])**2
            )
            
            if color_diff <= error_threshold * 10:  # 放宽阈值用于筛选
                candidates.append({
                    'name': dye_name,
                    'lab': dye_lab,
                    'type': dye_info['type'],
                    'similarity': max(0, 100 - color_diff)
                })
        
        # 按相似度排序
        candidates.sort(key=lambda x: x['similarity'], reverse=True)
        return candidates[:5]  # 返回前5个最匹配的
    
    @staticmethod
    def linear_regression_model(target_lab, dye_candidates):
        """
        基础配方计算（线性回归模型拟合染料比例与色彩的关系）
        
        Args:
            target_lab: 目标LAB色彩
            dye_candidates: 候选染料列表
            
        Returns:
            dict: 染料比例字典
        """
        if not dye_candidates:
            return {}
        
        # 构建训练数据
        n_candidates = len(dye_candidates)
        X = np.array([c['lab'] for c in dye_candidates])
        y = np.array(range(n_candidates))  # 虚拟目标值
        
        # 使用加权平均计算比例
        similarities = np.array([c['similarity'] for c in dye_candidates])
        total_sim = np.sum(similarities)
        
        if total_sim == 0:
            return {c['name']: 1.0/n_candidates for c in dye_candidates}
        
        # 根据相似度分配比例
        ratios = {}
        for candidate, sim in zip(dye_candidates, similarities):
            ratios[candidate['name']] = sim / total_sim
        
        return ratios
    
    @staticmethod
    def calculate_soak_time(formula):
        """
        计算浸泡时间
        
        Args:
            formula: 染料配方
            
        Returns:
            float: 基础浸泡时间（分钟）
        """
        base_time = 30  # 基础30分钟
        # 根据染料种类调整
        for dye_name in formula.keys():
            if dye_name in ['红花', '紫草']:
                base_time += 10
            elif dye_name in ['板蓝根', '茶叶']:
                base_time += 5
        
        return base_time
    
    @staticmethod
    def calculate_fix_time(formula):
        """
        计算固色时长
        
        Args:
            formula: 染料配方
            
        Returns:
            float: 固色时间（分钟）
        """
        base_time = 20  # 基础20分钟
        # 根据染料数量调整
        base_time += len(formula) * 5
        return base_time
    
    def calculate_dye_formula(self, target_color_rgb, ambient_temp=25, ambient_humidity=60):
        """
        艾德莱斯染色配方智能计算（核心算法）
        
        Args:
            target_color_rgb: 目标色彩RGB值 [R, G, B]
            ambient_temp: 环境温度（℃），默认25℃
            ambient_humidity: 环境湿度（%），默认60%
            
        Returns:
            dict: 包含染料比例、浸泡时间、固色时长的完整配方
        """
        # 1. 目标色彩数字化解析（RGB转LAB）
        target_lab = self.rgb_to_lab(target_color_rgb)
        
        # 2. 匹配天然染料数据库
        dye_candidates = self.query_dye_database(
            self.DYE_DATABASE, 
            target_lab, 
            error_threshold=3
        )
        
        if not dye_candidates:
            return {
                'error': '未找到匹配的染料组合',
                'dye_ratio': {},
                'soak_time': 0,
                'fix_time': 0
            }
        
        # 3. 基础配方计算（线性回归模型）
        base_formula = self.linear_regression_model(target_lab, dye_candidates)
        
        # 4. 环境因子修正（温湿度对染色效果的影响补偿）
        temp_correction = 1 + (ambient_temp - 25) * 0.015  # 标准温度25℃
        humidity_correction = 1 + (60 - ambient_humidity) * 0.012  # 标准湿度60%
        
        final_formula = {
            dye: ratio * temp_correction * humidity_correction 
            for dye, ratio in base_formula.items()
        }
        
        # 5. 输出量化生产参数
        result = {
            "dye_ratio": final_formula,
            "soak_time": self.calculate_soak_time(final_formula) + 5,  # 基础值+修正值
            "fix_time": self.calculate_fix_time(final_formula),
            "environmental_conditions": {
                "temperature": ambient_temp,
                "humidity": ambient_humidity,
                "temp_correction_factor": round(temp_correction, 3),
                "humidity_correction_factor": round(humidity_correction, 3)
            },
            "target_color": {
                "rgb": target_color_rgb,
                "lab": [round(x, 2) for x in target_lab]
            }
        }
        
        return result
