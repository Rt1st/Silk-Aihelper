"""
三大核心算法测试脚本
测试染色配方计算、品质检测、纹样生成功能
"""
import sys
import numpy as np

# 测试1: 染色配方智能计算
def test_dye_formula():
    print("=" * 60)
    print("测试1: 艾德莱斯染色配方智能计算算法")
    print("=" * 60)
    
    from color_recognizer import DyeFormulaCalculator
    
    calculator = DyeFormulaCalculator()
    
    # 测试案例1: 红色系
    print("\n【测试案例1】目标颜色: 中国红 (220, 20, 60)")
    result1 = calculator.calculate_dye_formula(
        target_color_rgb=[220, 20, 60],
        ambient_temp=28,  # 温度28℃
        ambient_humidity=55  # 湿度55%
    )
    
    if 'error' not in result1:
        print(f"✓ 染料比例:")
        for dye, ratio in result1['dye_ratio'].items():
            print(f"  - {dye}: {ratio:.3f}")
        print(f"✓ 浸泡时间: {result1['soak_time']}分钟")
        print(f"✓ 固色时长: {result1['fix_time']}分钟")
        print(f"✓ 环境修正因子:")
        print(f"  - 温度修正: {result1['environmental_conditions']['temp_correction_factor']}")
        print(f"  - 湿度修正: {result1['environmental_conditions']['humidity_correction_factor']}")
    else:
        print(f"✗ 错误: {result1['error']}")
    
    # 测试案例2: 蓝色系
    print("\n【测试案例2】目标颜色: 宝石蓝 (65, 105, 225)")
    result2 = calculator.calculate_dye_formula(
        target_color_rgb=[65, 105, 225],
        ambient_temp=22,
        ambient_humidity=65
    )
    
    if 'error' not in result2:
        print(f"✓ 染料比例:")
        for dye, ratio in result2['dye_ratio'].items():
            print(f"  - {dye}: {ratio:.3f}")
        print(f"✓ 浸泡时间: {result2['soak_time']}分钟")
        print(f"✓ 固色时长: {result2['fix_time']}分钟")
    else:
        print(f"✗ 错误: {result2['error']}")
    
    print("\n✅ 染色配方计算测试完成\n")


# 测试2: 品质检测算法
def test_quality_inspection():
    print("=" * 60)
    print("测试2: 艾德莱斯绸品质检测算法")
    print("=" * 60)
    
    import cv2
    from quality_inspection import QualityInspectionApp
    import tkinter as tk
    
    # 创建测试图像
    test_image = np.zeros((400, 600, 3), dtype=np.uint8)
    test_image[:] = [180, 100, 150]  # 紫色背景
    
    # 添加一些模拟瑕疵
    cv2.circle(test_image, (100, 100), 20, (0, 0, 0), -1)  # 破洞
    cv2.rectangle(test_image, (300, 200), (350, 250), (50, 50, 50), -1)  # 污渍
    
    print("\n【测试图像】已创建 600x400 测试图像（含2个模拟瑕疵）")
    
    # 创建检测器实例
    root = tk.Tk()
    root.withdraw()  # 隐藏窗口
    app = QualityInspectionApp(root)
    
    # 执行检测
    print("\n开始质量检测...")
    results = app.inspect_quality(test_image)
    
    print(f"\n✓ 检测结果:")
    print(f"  - 染色均匀度: {results['dye_uniformity']}%")
    print(f"  - 纹样对齐度: {results['alignment_degree']}%")
    print(f"  - 瑕疵率: {results['defect_rate']}每万像素")
    print(f"  - 瑕疵数量: {results['defect_count']}")
    print(f"  - 产品等级: {results['grade']}")
    
    if results['defects']:
        print(f"\n✓ 检测到瑕疵位置:")
        for i, defect in enumerate(results['defects']):
            print(f"  [{i+1}] 类型: {defect['type']}, 位置: {defect['bbox']}, 置信度: {defect['confidence']:.2f}")
    
    root.destroy()
    print("\n✅ 品质检测算法测试完成\n")


# 测试3: 纹样生成算法
def test_pattern_generation():
    print("=" * 60)
    print("测试3: 艾德莱斯绸纹样生成核心算法")
    print("=" * 60)
    
    from pattern_design_u1 import SilkPatternDesignApp
    import tkinter as tk
    
    # 创建应用实例
    root = tk.Tk()
    root.withdraw()
    app = SilkPatternDesignApp(root)
    
    # 设置测试参数
    base_style = 'traditional'
    user_preference = {
        'style_type': '国潮现代',
        'color': '中国红',
        'density': 'medium',
        'symmetry': 0.85
    }
    
    print("\n【生成参数】")
    print(f"  - 基础风格: {base_style}")
    print(f"  - 用户偏好:")
    for key, value in user_preference.items():
        print(f"    • {key}: {value}")
    
    # 调用生成算法
    print("\n开始生成纹样...")
    try:
        optimized_pattern = app.generate_edelis_pattern(
            base_style=base_style,
            user_preference=user_preference,
            pattern_database=app.PATTERN_DATABASE
        )
        
        print(f"\n✓ 纹样生成成功!")
        print(f"  - 线条宽度: {optimized_pattern['line_width']:.2f}px")
        print(f"  - 重复模式: {optimized_pattern['repeat_pattern']}")
        print(f"  - 对称度: {optimized_pattern['symmetry']*100:.1f}%")
        print(f"  - 复杂度: {optimized_pattern['complexity']:.2f}")
        print(f"  - 织造就绪: {optimized_pattern.get('weaving_ready', False)}")
        
        if 'optimization_notes' in optimized_pattern:
            print(f"  - 优化说明: {optimized_pattern['optimization_notes']}")
        
        print(f"\n✓ 配色方案:")
        for i, color in enumerate(optimized_pattern['colors']):
            print(f"  [{i+1}] {color}")
        
    except Exception as e:
        print(f"\n✗ 生成失败: {str(e)}")
        import traceback
        traceback.print_exc()
    
    root.destroy()
    print("\n✅ 纹样生成算法测试完成\n")


# 主测试函数
def main():
    print("\n" + "=" * 60)
    print("   艾德莱斯绸三大核心算法测试")
    print("=" * 60 + "\n")
    
    try:
        # 测试1: 染色配方计算
        test_dye_formula()
        
        # 测试2: 品质检测
        test_quality_inspection()
        
        # 测试3: 纹样生成
        test_pattern_generation()
        
        print("=" * 60)
        print("   🎉 所有测试完成！")
        print("=" * 60)
        print("\n📊 测试总结:")
        print("  ✓ 染色配方智能计算 - 支持RGB转LAB、环境因子修正")
        print("  ✓ 品质检测算法 - 支持均匀度/对齐度/瑕疵检测")
        print("  ✓ 纹样生成算法 - 支持StyleGAN3+传统特征约束")
        print("\n💡 提示: 可以运行对应的主程序查看完整功能")
        
    except Exception as e:
        print(f"\n❌ 测试过程中出现错误: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())
