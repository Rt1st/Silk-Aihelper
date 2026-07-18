"""
艾德莱斯绸布料颜色识别系统 - GUI 界面
基于机器视觉的颜色识别分析系统
"""
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import cv2
import numpy as np
from PIL import Image, ImageTk
import threading

from preprocessor import ImagePreprocessor
from color_recognizer import ColorRecognizer


class SilkColorRecognitionApp:
    """艾德莱斯绸颜色识别应用主类"""
    
    def __init__(self, root):
        """
        初始化应用
        
        Args:
            root: Tkinter 根窗口
        """
        self.root = root
        self.root.title("艾德莱斯绸布料颜色识别系统 - 基于机器视觉")
        self.root.geometry("1400x900")
        
        # 初始化变量
        self.image_path = None
        self.preprocessor = ImagePreprocessor()
        self.recognizer = ColorRecognizer(n_colors=5)
        
        # 设置样式
        self.setup_styles()
        
        # 创建界面
        self.create_ui()
        
        # 显示欢迎信息
        self.show_welcome_message()
    
    def setup_styles(self):
        """设置界面样式"""
        style = ttk.Style()
        
        # 标题样式
        style.configure('Title.TLabel', font=('微软雅黑', 18, 'bold'), foreground='#2c3e50')
        
        # 按钮样式
        style.configure('Accent.TButton', 
                       font=('微软雅黑', 11, 'bold'),
                       padding=10)
        
        # 标签框架样式
        style.configure('Info.TLabelframe.Label', 
                       font=('微软雅黑', 11, 'bold'),
                       foreground='#34495e')
    
    def create_ui(self):
        """创建用户界面"""
        # 主容器
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 配置网格权重
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(1, weight=1)
        
        # 标题
        title_label = ttk.Label(main_frame, 
                               text="🎨 艾德莱斯绸布料颜色识别系统",
                               style='Title.TLabel')
        title_label.grid(row=0, column=0, pady=(0, 20))
        
        # 内容区域（分为左右两部分）
        content_frame = ttk.Frame(main_frame)
        content_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        content_frame.columnconfigure(0, weight=1)
        content_frame.columnconfigure(1, weight=1)
        content_frame.rowconfigure(0, weight=1)
        
        # 左侧面板 - 图像显示
        left_panel = ttk.Frame(content_frame, relief='sunken', borderwidth=2)
        left_panel.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 5))
        left_panel.columnconfigure(0, weight=1)
        left_panel.rowconfigure(0, weight=1)
        
        self.create_left_panel(left_panel)
        
        # 右侧面板 - 结果和控制
        right_panel = ttk.Frame(content_frame, relief='sunken', borderwidth=2)
        right_panel.grid(row=0, column=1, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(5, 0))
        right_panel.columnconfigure(0, weight=1)
        right_panel.rowconfigure(1, weight=1)
        
        self.create_right_panel(right_panel)
    
    def create_left_panel(self, parent):
        """创建左侧面板"""
        # 图像画布
        canvas_frame = ttk.Frame(parent)
        canvas_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=10)
        canvas_frame.columnconfigure(0, weight=1)
        canvas_frame.rowconfigure(0, weight=1)
        
        self.canvas = tk.Canvas(canvas_frame, bg='white', width=600, height=500)
        self.canvas.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=10, pady=10)
        
        # 控制面板
        control_frame = ttk.Frame(parent)
        control_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=10)
        
        # 选择图片按钮
        select_btn = ttk.Button(control_frame, 
                               text="📁 选择图片",
                               command=self.select_image,
                               style='Accent.TButton')
        select_btn.pack(side=tk.LEFT, padx=5, pady=5)
        
        # 开始识别按钮
        recognize_btn = ttk.Button(control_frame,
                                  text="🔍 开始识别",
                                  command=self.start_recognition,
                                  style='Accent.TButton')
        recognize_btn.pack(side=tk.LEFT, padx=5, pady=5)
        
        # 重置按钮
        reset_btn = ttk.Button(control_frame,
                              text="🔄 重置",
                              command=self.reset_app)
        reset_btn.pack(side=tk.LEFT, padx=5, pady=5)
    
    def create_right_panel(self, parent):
        """创建右侧面板"""
        # 顶部信息区
        top_frame = ttk.Frame(parent)
        top_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=10)
        top_frame.columnconfigure(0, weight=1)
        
        # 状态标签
        self.status_label = ttk.Label(top_frame, 
                                     text="状态：就绪",
                                     font=('微软雅黑', 10))
        self.status_label.grid(row=0, column=0, sticky=tk.W, padx=10)
        
        # 滚动文本框（显示结果）
        result_frame = ttk.LabelFrame(parent, text="识别结果", padding=10)
        result_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=10, pady=10)
        result_frame.columnconfigure(0, weight=1)
        result_frame.rowconfigure(0, weight=1)
        
        # 创建带滚动条的文本框
        text_frame = ttk.Frame(result_frame)
        text_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        text_frame.columnconfigure(0, weight=1)
        text_frame.rowconfigure(0, weight=1)
        
        self.result_text = tk.Text(text_frame, 
                                   wrap=tk.WORD, 
                                   width=50, 
                                   height=20,
                                   font=('微软雅黑', 10))
        self.result_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        scrollbar = ttk.Scrollbar(text_frame, orient=tk.VERTICAL, 
                                 command=self.result_text.yview)
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.result_text.config(yscrollcommand=scrollbar.set)
        
        # 调色板画布
        palette_frame = ttk.LabelFrame(parent, text="颜色调色板", padding=10)
        palette_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), padx=10, pady=10)
        palette_frame.columnconfigure(0, weight=1)
        
        self.palette_canvas = tk.Canvas(palette_frame, bg='white', height=150)
        self.palette_canvas.grid(row=0, column=0, sticky=(tk.W, tk.E))
    
    def show_welcome_message(self):
        """显示欢迎信息"""
        welcome_text = """
╔══════════════════════════════════════════════════╗
║   欢迎使用艾德莱斯绸布料颜色识别系统！           ║
║                                                   ║
║  本系统基于机器视觉技术，可以：                   ║
║  ✓ 自动识别布料中的主要颜色                       ║
║  ✓ 分析颜色分布比例                               ║
║  ✓ 生成颜色调色板                                 ║
║  ✓ 提供详细的颜色信息                             ║
║                                                   ║
║  使用方法：                                       ║
║  1. 点击"选择图片"加载布料图像                    ║
║  2. 点击"开始识别"进行分析                        ║
║  3. 查看右侧的识别结果                            ║
╚══════════════════════════════════════════════════╝
        """
        self.result_text.insert(tk.END, welcome_text)
    
    def select_image(self):
        """选择图片文件"""
        filetypes = [
            ("图像文件", "*.jpg *.jpeg *.png *.bmp *.gif"),
            ("所有文件", "*.*")
        ]
        
        filepath = filedialog.askopenfilename(
            title="选择布料图片",
            filetypes=filetypes
        )
        
        if filepath:
            self.image_path = filepath
            self.load_and_display_image(filepath)
    
    def load_and_display_image(self, filepath):
        """加载并显示图片"""
        try:
            # 更新状态
            self.status_label.config(text=f"状态：正在加载图片...")
            self.root.update()
            
            # 加载图像
            success = self.preprocessor.load_image(filepath)
            
            if not success:
                messagebox.showerror("错误", "无法加载图片，请检查文件格式")
                return
            
            # 调整大小
            processed = self.preprocessor.resize_image(max_width=580, max_height=480)
            
            # 转换颜色空间
            rgb_image = cv2.cvtColor(processed, cv2.COLOR_BGR2RGB)
            
            # 转换为 PIL 图像
            pil_image = Image.fromarray(rgb_image)
            
            # 转换为 PhotoImage
            photo = ImageTk.PhotoImage(image=pil_image)
            
            # 在画布上显示
            self.canvas.delete("all")
            self.canvas.create_image(290, 240, image=photo, anchor=tk.CENTER)
            self.canvas.image = photo  # 保持引用
            
            # 更新状态
            self.status_label.config(text=f"状态：图片已加载 - {filepath.split('/')[-1]}")
            
            # 清空结果
            self.result_text.delete(1.0, tk.END)
            self.result_text.insert(tk.END, f"已加载图片：{filepath.split('/')[-1]}\n")
            self.result_text.insert(tk.END, f"图片尺寸：{processed.shape[1]} x {processed.shape[0]}\n")
            self.result_text.insert(tk.END, "\n请点击'开始识别'按钮进行颜色分析...\n")
            
        except Exception as e:
            messagebox.showerror("错误", f"加载图片时出错：{str(e)}")
            self.status_label.config(text="状态：加载失败")
    
    def start_recognition(self):
        """开始颜色识别"""
        if self.image_path is None:
            messagebox.showinfo("提示", "请先选择一张图片")
            return
        
        # 禁用按钮防止重复点击
        self.status_label.config(text="状态：正在识别颜色...")
        self.root.update()
        
        # 在新线程中执行识别
        thread = threading.Thread(target=self.run_recognition)
        thread.daemon = True
        thread.start()
    
    def run_recognition(self):
        """执行颜色识别（在后台线程）"""
        try:
            # 获取处理后的图像
            image = self.preprocessor.get_processed_image()
            
            # 增强对比度
            enhanced = self.preprocessor.enhance_contrast()
            
            # 提取主要颜色
            colors, percentages = self.recognizer.extract_dominant_colors(enhanced)
            
            # 分析颜色
            color_info = self.recognizer.analyze_colors()
            
            # 在主线程中更新 UI
            self.root.after(0, self.display_results, color_info)
            
        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("错误", f"识别失败：{str(e)}"))
            self.root.after(0, lambda: self.status_label.config(text="状态：识别失败"))
    
    def display_results(self, color_info):
        """显示识别结果"""
        # 清空结果文本框
        self.result_text.delete(1.0, tk.END)
        
        # 添加标题
        header = "═" * 50 + "\n"
        header += "       艾德莱斯绸颜色识别结果\n"
        header += "═" * 50 + "\n\n"
        self.result_text.insert(tk.END, header)
        
        # 显示每种颜色的信息
        for info in color_info:
            color_line = f"排名 #{info['rank']}: {info['name']}\n"
            rgb_line = f"  RGB 值：({info['rgb'][0]}, {info['rgb'][1]}, {info['rgb'][2]})\n"
            hex_line = f"  HEX 值：{info['hex']}\n"
            percent_line = f"  占比：{info['percentage']:.2f}%\n"
            separator = "-" * 50 + "\n"
            
            self.result_text.insert(tk.END, color_line)
            self.result_text.insert(tk.END, rgb_line)
            self.result_text.insert(tk.END, hex_line)
            self.result_text.insert(tk.END, percent_line)
            self.result_text.insert(tk.END, separator)
        
        # 总结
        summary = "\n📊 颜色分析总结:\n"
        summary += f"  • 共识别出 {len(color_info)} 种主要颜色\n"
        
        dominant = max(color_info, key=lambda x: x['percentage'])
        summary += f"  • 主导颜色：{dominant['name']} ({dominant['percentage']:.2f}%)\n"
        
        total_covered = sum(info['percentage'] for info in color_info)
        summary += f"  • 颜色覆盖率：{total_covered:.2f}%\n"
        
        self.result_text.insert(tk.END, summary)
        
        # 绘制调色板
        self.draw_palette()
        
        # 更新状态
        self.status_label.config(text="状态：识别完成 ✓")
        messagebox.showinfo("成功", "颜色识别完成！")
    
    def draw_palette(self):
        """绘制颜色调色板"""
        self.palette_canvas.delete("all")
        
        colors = self.recognizer.get_dominant_colors()
        percentages = self.recognizer.get_color_percentages()
        
        if colors is None:
            return
        
        canvas_width = self.palette_canvas.winfo_width()
        bar_width = canvas_width // len(colors)
        
        for i, (color, percentage) in enumerate(zip(colors, percentages)):
            # 转换 RGB 到十六进制
            hex_color = '#%02x%02x%02x' % tuple(color)
            
            # 计算条形宽度（根据百分比）
            adjusted_width = int(bar_width * (percentage / 100) * 2)
            
            # 绘制颜色矩形
            x1 = i * bar_width
            y1 = 20
            x2 = (i + 1) * bar_width
            y2 = 100
            
            self.palette_canvas.create_rectangle(x1, y1, x2, y2, fill=hex_color, outline='black')
            
            # 添加颜色名称和百分比
            label_y = 120
            name = self.recognizer.get_color_name(color)
            label_text = f"{name}\n{percentage:.1f}%"
            
            self.palette_canvas.create_text(
                x1 + bar_width // 2, label_y,
                text=label_text,
                font=('微软雅黑', 9),
                justify=tk.CENTER
            )
    
    def reset_app(self):
        """重置应用"""
        self.image_path = None
        self.preprocessor.reset()
        
        # 清空画布
        self.canvas.delete("all")
        self.palette_canvas.delete("all")
        
        # 清空文本框
        self.result_text.delete(1.0, tk.END)
        
        # 重置状态
        self.status_label.config(text="状态：就绪")
        
        # 显示欢迎信息
        self.show_welcome_message()
        
        messagebox.showinfo("提示", "已重置，可以重新选择图片")


def main():
    """主函数"""
    root = tk.Tk()
    app = SilkColorRecognitionApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
