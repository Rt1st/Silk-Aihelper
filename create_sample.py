"""
生成测试用的艾德莱斯绸布料样本图像
"""
import numpy as np
import cv2


def create_test_silk_image():
    """创建一个模拟的艾德莱斯绸布料图像"""
    
    # 创建画布 (800x600)
    image = np.zeros((600, 800, 3), dtype=np.uint8)
    
    # 艾德莱斯绸典型颜色（BGR 格式）
    colors = [
        (0, 0, 200),      # 红色
        (200, 0, 0),      # 蓝色
        (0, 200, 0),      # 绿色
        (50, 50, 255),    # 金黄色
        (150, 0, 150),    # 紫色
        (0, 255, 255),    # 青色
        (100, 100, 100),  # 灰色
        (200, 180, 70),   # 橙色
    ]
    
    # 创建波浪纹理（艾德莱斯绸的典型图案）
    for i in range(0, 800, 50):
        color_idx = (i // 50) % len(colors)
        
        # 绘制垂直波浪条纹
        for y in range(600):
            offset = int(10 * np.sin(y / 30.0 + i / 50.0))
            x_start = i + offset
            x_end = min(i + 50 + offset, 800)
            
            if 0 <= x_start < 800:
                image[y:y+1, max(0, x_start):min(800, x_end)] = colors[color_idx]
    
    # 添加一些装饰性圆点
    np.random.seed(42)
    for _ in range(100):
        x = np.random.randint(0, 800)
        y = np.random.randint(0, 600)
        radius = np.random.randint(3, 8)
        color = colors[np.random.randint(0, len(colors))]
        cv2.circle(image, (x, y), radius, color, -1)
    
    # 轻微模糊使颜色更自然
    image = cv2.GaussianBlur(image, (5, 5), 0)
    
    # 保存图像
    cv2.imwrite('sample_silk.jpg', image)
    print("测试样本图像已生成：sample_silk.jpg")
    
    return image


if __name__ == "__main__":
    create_test_silk_image()
    print("✓ 测试图像创建完成")
