"""
纹样图片批量导入工具
帮助你将图片快速导入到 patterns 文件夹并自动重命名
"""
import os
import shutil
from tkinter import Tk, filedialog, messagebox


def create_patterns_folder():
    """创建 patterns 文件夹"""
    if not os.path.exists("patterns"):
        os.makedirs("patterns")
        print("✓ 已创建 patterns 文件夹")
    else:
        print("ℹ patterns 文件夹已存在")


def batch_import_images():
    """批量导入图片并重命名"""
    root = Tk()
    root.withdraw()  # 隐藏主窗口
    
    print("\n请选择你的纹样图片文件（可多选）")
    files = filedialog.askopenfilenames(
        title="选择纹样图片",
        filetypes=[("图片文件", "*.jpg *.jpeg *.png"), ("所有文件", "*.*")]
    )
    
    if not files:
        print("未选择文件")
        return
    
    create_patterns_folder()
    
    categories = ["传统经典", "国潮现代", "旅拍简约"]
    print(f"\n共选择了 {len(files)} 张图片")
    print("请按照分类顺序依次选择：")
    print("  1-8: 传统经典")
    print("  9-16: 国潮现代") 
    print("  17-24: 旅拍简约\n")
    
    for i, file in enumerate(files):
        if i >= 24:
            break
            
        category_idx = i // 8
        num_in_category = (i % 8) + 1
        
        ext = os.path.splitext(file)[1]
        new_name = f"{categories[category_idx]}_{num_in_category}{ext}"
        new_path = os.path.join("patterns", new_name)
        
        try:
            shutil.copy2(file, new_path)
            print(f"✓ {file.split('/')[-1]} → {new_name}")
        except Exception as e:
            print(f"✗ 复制失败：{e}")
    
    print(f"\n完成！共导入 {min(len(files), 24)} 张图片到 patterns 文件夹")
    print("\n提示：如果数量不足 24 张，剩余位置会显示为文字按钮")
    messagebox.showinfo("导入完成", f"成功导入 {len(files)} 张纹样图片！")
    root.destroy()


if __name__ == "__main__":
    print("=" * 50)
    print("艾德莱斯绸纹样图片导入工具")
    print("=" * 50)
    batch_import_images()
