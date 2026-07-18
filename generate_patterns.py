"""
艾德莱斯绸纹样自动生成器
使用算法生成传统纹样图案
"""
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
import math
import os


class PatternGenerator:
    """纹样生成器"""
    
    def __init__(self, size=(512, 512)):
        self.size = size
        
    def generate_traditional_pattern(self, seed=None):
        """生成传统经典纹样"""
        if seed:
            np.random.seed(seed)
            
        img = Image.new('RGB', self.size, '#F5E6D3')  # 米色底
        draw = ImageDraw.Draw(img)
        
        # 绘制云纹
        center_x, center_y = self.size[0] // 2, self.size[1] // 2
        colors = ['#DC143C', '#FFD700', '#4169E1', '#50C878']
        
        for i in range(8):
            angle = (i / 8) * 2 * math.pi
            radius = 150 + np.random.randint(-20, 20)
            x = center_x + radius * math.cos(angle)
            y = center_y + radius * math.sin(angle)
            
            # 绘制云纹圆圈
            cloud_color = colors[i % len(colors)]
            for r in range(40, 0, -8):
                draw.ellipse([x-r, y-r, x+r, y+r], 
                           fill=cloud_color, outline='#8B4513')
        
        # 添加回纹边框
        border_width = 15
        for offset in range(0, border_width, 5):
            draw.rectangle([offset, offset, 
                          self.size[0]-offset-1, self.size[1]-offset-1],
                          outline='#8B4513', width=2)
        
        return img.filter(ImageFilter.SMOOTH)
    
    def generate_modern_pattern(self, seed=None):
        """生成国潮现代纹样"""
        if seed:
            np.random.seed(seed)
            
        img = Image.new('RGB', self.size, '#1a1a2e')  # 深色底
        draw = ImageDraw.Draw(img)
        
        # 几何抽象图案
        colors = ['#e94560', '#0f3460', '#533483', '#ffd369']
        
        # 绘制交错的几何图形
        for i in range(12):
            x1 = np.random.randint(0, self.size[0])
            y1 = np.random.randint(0, self.size[1])
            x2 = x1 + np.random.randint(-100, 100)
            y2 = y1 + np.random.randint(-100, 100)
            
            color = colors[i % len(colors)]
            line_width = np.random.randint(3, 12)
            
            draw.line([(x1, y1), (x2, y2)], fill=color, width=line_width)
            
            # 添加圆形装饰
            if i % 3 == 0:
                circle_radius = np.random.randint(20, 50)
                draw.ellipse([x1-circle_radius, y1-circle_radius,
                            x1+circle_radius, y1+circle_radius],
                           outline=color, width=3)
        
        # 添加渐变效果
        overlay = Image.new('RGBA', self.size, (255, 255, 255, 0))
        overlay_draw = ImageDraw.Draw(overlay)
        for i in range(0, self.size[1], 4):
            alpha = int(50 * math.sin(i / self.size[1] * math.pi))
            overlay_draw.line([(0, i), (self.size[0], i)], 
                            fill=(255, 255, 255, alpha))
        
        img = Image.alpha_composite(img.convert('RGBA'), overlay)
        return img.convert('RGB').filter(ImageFilter.GaussianBlur(radius=1))
    
    def generate_simple_pattern(self, seed=None):
        """生成旅拍简约纹样"""
        if seed:
            np.random.seed(seed)
            
        img = Image.new('RGB', self.size, '#FAFAFA')  # 浅灰白底
        draw = ImageDraw.Draw(img)
        
        # 简约线条图案
        colors = ['#2C3E50', '#3498DB', '#E74C3C', '#95A5A6']
        
        # 绘制波浪纹
        wave_count = 5
        spacing = self.size[1] // wave_count
        
        for i in range(wave_count):
            y_base = i * spacing + spacing // 2
            color = colors[i % len(colors)]
            
            points = []
            for x in range(0, self.size[0]+1, 10):
                y = y_base + 20 * math.sin(x / 50 + i)
                points.append((x, y))
            
            # 绘制波浪线
            if len(points) > 1:
                for j in range(len(points)-1):
                    draw.line([points[j], points[j+1]], 
                            fill=color, width=4)
        
        # 添加简约花卉元素
        for i in range(6):
            fx = np.random.randint(50, self.size[0]-50)
            fy = np.random.randint(50, self.size[1]-50)
            
            # 花蕊
            draw.ellipse([fx-5, fy-5, fx+5, fy+5], 
                        fill='#FFD700')
            
            # 花瓣
            for angle in range(0, 360, 45):
                rad = math.radians(angle)
                px = fx + 15 * math.cos(rad)
                py = fy + 15 * math.sin(rad)
                draw.ellipse([px-4, py-4, px+4, py+4],
                           fill='#FF69B4')
        
        return img.filter(ImageFilter.SMOOTH_MORE)
    
    def save_pattern(self, img, filepath):
        """保存纹样"""
        img.save(filepath, 'JPEG', quality=95)


def batch_generate_patterns(output_dir='patterns'):
    """批量生成所有纹样"""
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    generator = PatternGenerator()
    categories = [
        ("传统经典", generator.generate_traditional_pattern),
        ("国潮现代", generator.generate_modern_pattern),
        ("旅拍简约", generator.generate_simple_pattern)
    ]
    
    print("开始生成纹样图案...")
    print("=" * 50)
    
    count = 0
    for category_name, generate_func in categories:
        print(f"\n正在生成 [{category_name}] 系列纹样:")
        for i in range(1, 9):
            seed = hash(f"{category_name}_{i}") % 10000
            pattern = generate_func(seed)
            
            filename = f"{category_name}_{i}.jpg"
            filepath = os.path.join(output_dir, filename)
            
            generator.save_pattern(pattern, filepath)
            print(f"  ✓ {filename}")
            count += 1
    
    print("\n" + "=" * 50)
    print(f"✓ 完成！共生成了 {count} 张纹样图案")
    print(f"📁 保存位置：{os.path.abspath(output_dir)}")


if __name__ == "__main__":
    batch_generate_patterns()
