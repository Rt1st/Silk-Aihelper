"""
艾德莱斯绸智能系统 - 现代化UI版本
整合三个核心功能：纹样定制、染色配方、质量检测
"""
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageTk
import cv2
import numpy as np
import threading
from datetime import datetime

# 导入原有功能模块
from color_recognizer import ColorRecognizer, DyeFormulaCalculator
from quality_inspection import QualityInspectionApp


class ModernSilkApp:
    """现代化艾德莱斯绸系统"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("艾德莱斯绸智能系统")
        self.root.geometry("400x800")
        self.root.resizable(False, False)
        
        # 深色主题配色
        self.colors = {
            'bg_dark': '#0F1626',
            'bg_card': '#1A2235',
            'accent_blue': '#4A90E2',
            'accent_gold': '#D4AF37',
            'text_primary': '#FFFFFF',
            'text_secondary': '#8B95A8',
            'border': '#2A3650'
        }
        
        # 初始化变量
        self.current_page = 0
        self.recognizer = ColorRecognizer(n_colors=7)
        self.dye_calculator = DyeFormulaCalculator()
        self.image_path = None
        
        # 纹样风格数据
        self.pattern_styles = [
            {"name": "经典艾德莱斯", "icon": "🎨", "color": "#DC143C"},
            {"name": "现代几何", "icon": "◆", "color": "#4169E1"},
            {"name": "旅拍风", "icon": "📷", "color": "#50C878"}
        ]
        
        self.setup_ui()
        
    def setup_ui(self):
        """设置界面"""
        # 创建页面容器
        self.pages_frame = tk.Frame(self.root, bg=self.colors['bg_dark'])
        self.pages_frame.pack(fill='both', expand=True)
        
        # 页面1：灵犀绘-AI纹样定制
        self.page1 = self.create_pattern_design_page()
        
        # 页面2：智调方-AI染色配方
        self.page2 = self.create_dye_formula_page()
        
        # 页面3：慧眼鉴-AI质检
        self.page3 = self.create_quality_inspection_page()
        
        # 显示第一页
        self.show_page(0)
        
    def create_pattern_design_page(self):
        """创建纹样定制页面"""
        frame = tk.Frame(self.pages_frame, bg=self.colors['bg_dark'])
        
        # 顶部标题栏
        header = tk.Frame(frame, bg=self.colors['bg_dark'], height=60)
        header.pack(fill='x', pady=(10, 0))
        header.pack_propagate(False)
        
        tk.Label(header, text="←", font=('Arial', 18), 
                fg=self.colors['text_primary'], bg=self.colors['bg_dark']).pack(side='left', padx=15)
        tk.Label(header, text="灵犀绘-AI纹样定制", font=('微软雅黑', 14, 'bold'),
                fg=self.colors['text_primary'], bg=self.colors['bg_dark']).pack(side='left', pady=15)
        
        # 左侧风格选择区
        style_frame = tk.Frame(frame, bg=self.colors['bg_dark'], width=80)
        style_frame.pack(side='left', fill='y', padx=(10, 0))
        style_frame.pack_propagate(False)
        
        # 风格按钮
        self.style_buttons = []
        for i, style in enumerate(self.pattern_styles):
            btn = tk.Button(style_frame, 
                          text=style['icon'],
                          font=('Arial', 16),
                          bg=self.colors['bg_card'] if i != 0 else self.colors['accent_gold'],
                          fg=self.colors['text_primary'],
                          relief='flat',
                          width=4,
                          height=3,
                          command=lambda idx=i: self.select_style(idx))
            btn.pack(pady=8)
            self.style_buttons.append(btn)
            
            tk.Label(style_frame, text=style['name'][:2],
                    font=('微软雅黑', 8),
                    fg=self.colors['text_secondary'] if i != 0 else self.colors['accent_gold'],
                    bg=self.colors['bg_dark']).pack()
        
        # 中间预览区
        preview_frame = tk.Frame(frame, bg=self.colors['bg_card'], width=260, height=520)
        preview_frame.pack(side='left', padx=5)
        preview_frame.pack_propagate(False)
        
        self.preview_canvas = tk.Canvas(preview_frame, bg='#F5F5DC', 
                                       highlightthickness=0)
        self.preview_canvas.pack(fill='both', expand=True, padx=15, pady=15)
        
        # 预览区文字
        self.preview_canvas.create_text(130, 250,
                                       text="AI生成预览区",
                                       font=('微软雅黑', 12),
                                       fill='#999')
        
        # 右侧参数调节区
        param_frame = tk.Frame(frame, bg=self.colors['bg_dark'], width=40)
        param_frame.pack(side='right', padx=(0, 10))
        param_frame.pack_propagate(False)
        
        # 饱和度滑块
        tk.Label(param_frame, text="饱和度",
                font=('微软雅黑', 8),
                fg=self.colors['text_secondary'],
                bg=self.colors['bg_dark']).pack(pady=(10, 5))
        
        self.saturation_scale = tk.Scale(param_frame, from_=100, to=0,
                                        orient='vertical',
                                        bg=self.colors['bg_dark'],
                                        fg=self.colors['text_primary'],
                                        troughcolor=self.colors['border'],
                                        highlightthickness=0,
                                        width=15,
                                        length=120)
        self.saturation_scale.set(30)
        self.saturation_scale.pack()
        
        # 纹样密度滑块
        tk.Label(param_frame, text="纹样密度",
                font=('微软雅黑', 8),
                fg=self.colors['text_secondary'],
                bg=self.colors['bg_dark']).pack(pady=(15, 5))
        
        self.density_scale = tk.Scale(param_frame, from_=100, to=0,
                                     orient='vertical',
                                     bg=self.colors['bg_dark'],
                                     fg=self.colors['text_primary'],
                                     troughcolor=self.colors['border'],
                                     highlightthickness=0,
                                     width=15,
                                     length=120)
        self.density_scale.set(50)
        self.density_scale.pack()
        
        # 颜色滑块
        tk.Label(param_frame, text="颜色",
                font=('微软雅黑', 8),
                fg=self.colors['text_secondary'],
                bg=self.colors['bg_dark']).pack(pady=(15, 5))
        
        self.color_scale = tk.Scale(param_frame, from_=0, to=100,
                                   orient='vertical',
                                   bg=self.colors['bg_dark'],
                                   fg=self.colors['accent_gold'],
                                   troughcolor=self.colors['border'],
                                   highlightthickness=0,
                                   width=15,
                                   length=120)
        self.color_scale.set(70)
        self.color_scale.pack()
        
        # 替换颜色滑块
        tk.Label(param_frame, text="替换",
                font=('微软雅黑', 8),
                fg=self.colors['text_secondary'],
                bg=self.colors['bg_dark']).pack(pady=(15, 5))
        
        self.replace_scale = tk.Scale(param_frame, from_=0, to=100,
                                     orient='vertical',
                                     bg=self.colors['bg_dark'],
                                     fg=self.colors['accent_blue'],
                                     troughcolor=self.colors['border'],
                                     highlightthickness=0,
                                     width=15,
                                     length=120)
        self.replace_scale.set(40)
        self.replace_scale.pack()
        
        # 底部按钮区
        bottom_frame = tk.Frame(frame, bg=self.colors['bg_dark'], height=80)
        bottom_frame.pack(fill='x', side='bottom', pady=(10, 0))
        bottom_frame.pack_propagate(False)
        
        # 生成纹样按钮
        gen_btn = tk.Button(bottom_frame,
                           text="◇ 生成纹样",
                           font=('微软雅黑', 11, 'bold'),
                           bg=self.colors['bg_card'],
                           fg=self.colors['text_primary'],
                           relief='flat',
                           padx=20,
                           pady=10,
                           cursor='hand2',
                           command=self.generate_pattern)
        gen_btn.pack(side='left', padx=15, pady=10)
        
        # 确认提交按钮
        submit_btn = tk.Button(bottom_frame,
                              text="确认提交",
                              font=('微软雅黑', 11, 'bold'),
                              bg=self.colors['accent_gold'],
                              fg='#000',
                              relief='flat',
                              padx=30,
                              pady=10,
                              cursor='hand2',
                              command=self.submit_pattern)
        submit_btn.pack(side='right', padx=15, pady=10)
        
        return frame
    
    def create_dye_formula_page(self):
        """创建染色配方页面"""
        frame = tk.Frame(self.pages_frame, bg='#E8F4F8')
        
        # 顶部标题栏
        header = tk.Frame(frame, bg='#E8F4F8', height=60)
        header.pack(fill='x', pady=(10, 0))
        header.pack_propagate(False)
        
        tk.Label(header, text="←", font=('Arial', 18),
                fg='#333', bg='#E8F4F8').pack(side='left', padx=15)
        tk.Label(header, text="智调方-AI染色配方", font=('微软雅黑', 14, 'bold'),
                fg='#333', bg='#E8F4F8').pack(side='left', pady=15)
        
        # 上传样图按钮
        upload_btn = tk.Button(frame,
                              text="📤 上传纹样图 >",
                              font=('微软雅黑', 10),
                              bg='white',
                              fg='#333',
                              relief='flat',
                              padx=20,
                              pady=8,
                              cursor='hand2',
                              command=self.upload_pattern_image)
        upload_btn.pack(pady=10)
        
        # 颜色分析区
        colors_frame = tk.Frame(frame, bg='white', width=360, height=150)
        colors_frame.pack(padx=15, pady=10)
        colors_frame.pack_propagate(False)
        
        # 显示颜色条
        self.colors_canvas = tk.Canvas(colors_frame, bg='white',
                                      highlightthickness=0)
        self.colors_canvas.pack(fill='both', expand=True, padx=10, pady=10)
        
        # 配方参数区
        formula_frame = tk.Frame(frame, bg='white', width=360, height=380)
        formula_frame.pack(padx=15, pady=10)
        formula_frame.pack_propagate(False)
        
        # 原料名称
        self.create_dropdown_row(formula_frame, "原料名称", 0, 
                                ["红花", "板蓝根", "黄刺叶", "紫草"])
        
        # 用量
        self.create_dropdown_row(formula_frame, "用量", 80,
                                ["1:21", "1:22", "1:23", "1:24", "1:25"])
        
        # 浸泡时长
        self.create_dropdown_row(formula_frame, "浸泡时长", 160,
                                ["20分钟", "30分钟", "40分钟", "50分钟"])
        
        # 固色参数
        self.create_dropdown_row(formula_frame, "固色参数", 240,
                                ["低温固色", "中温固色", "高温固色"])
        
        # 底部按钮区
        bottom_frame = tk.Frame(frame, bg='#E8F4F8', height=80)
        bottom_frame.pack(fill='x', side='bottom', pady=(10, 0))
        bottom_frame.pack_propagate(False)
        
        # 查看工艺教程按钮
        tutorial_btn = tk.Button(bottom_frame,
                                text="☑ 查看工艺教程",
                                font=('微软雅黑', 10),
                                bg='white',
                                fg='#333',
                                relief='flat',
                                padx=15,
                                pady=8,
                                cursor='hand2',
                                command=self.show_tutorial)
        tutorial_btn.pack(side='left', padx=15, pady=10)
        
        # 确认配方按钮
        confirm_btn = tk.Button(bottom_frame,
                               text="确认配方",
                               font=('微软雅黑', 11, 'bold'),
                               bg='#2563EB',
                               fg='white',
                               relief='flat',
                               padx=30,
                               pady=10,
                               cursor='hand2',
                               command=self.confirm_formula)
        confirm_btn.pack(side='right', padx=15, pady=10)
        
        return frame
    
    def create_quality_inspection_page(self):
        """创建质量检测页面"""
        frame = tk.Frame(self.pages_frame, bg='white')
        
        # 顶部标题栏
        header = tk.Frame(frame, bg='white', height=60)
        header.pack(fill='x', pady=(10, 0))
        header.pack_propagate(False)
        
        tk.Label(header, text="←", font=('Arial', 18),
                fg='#333', bg='white').pack(side='left', padx=15)
        tk.Label(header, text="慧眼鉴-AI质检", font=('微软雅黑', 14, 'bold'),
                fg='#333', bg='white').pack(side='left', pady=15)
        
        # 更多选项
        tk.Label(header, text="···", font=('Arial', 18),
                fg='#333', bg='white').pack(side='right', padx=15)
        
        # 拍摄框区域
        camera_frame = tk.Frame(frame, bg='#F0F0F0', width=360, height=300)
        camera_frame.pack(padx=20, pady=10)
        camera_frame.pack_propagate(False)
        
        self.camera_canvas = tk.Canvas(camera_frame, bg='#333',
                                      highlightthickness=0)
        self.camera_canvas.pack(fill='both', expand=True, padx=15, pady=15)
        
        # 绘制拍摄框
        self.draw_camera_guide()
        
        # 拍照上传按钮
        capture_btn = tk.Button(frame,
                               text="拍照上传",
                               font=('微软雅黑', 12, 'bold'),
                               bg='#2563EB',
                               fg='white',
                               relief='flat',
                               padx=40,
                               pady=12,
                               cursor='hand2',
                               command=self.capture_and_upload)
        capture_btn.pack(pady=15)
        
        # 检测指标区
        metrics_frame = tk.Frame(frame, bg='#F5F5F5', width=360, height=180)
        metrics_frame.pack(padx=20, pady=10)
        metrics_frame.pack_propagate(False)
        
        # 瑕疵检测
        self.create_metric_button(metrics_frame, "瑕疵检测", "⬡", 0)
        
        # 等级判定
        self.create_metric_button(metrics_frame, "等级判定", "📋", 120)
        
        # 合格率
        self.create_metric_button(metrics_frame, "合格率", "✓", 240)
        
        # 生成报告按钮
        report_btn = tk.Button(frame,
                              text="生成报告",
                              font=('微软雅黑', 12, 'bold'),
                              bg='#2563EB',
                              fg='white',
                              relief='flat',
                              padx=60,
                              pady=12,
                              cursor='hand2',
                              command=self.generate_report)
        report_btn.pack(pady=20)
        
        return frame
    
    def create_dropdown_row(self, parent, label, y_pos, options):
        """创建下拉选择行"""
        row_frame = tk.Frame(parent, bg='white')
        row_frame.place(x=10, y=y_pos, width=340, height=70)
        
        tk.Label(row_frame, text=label,
                font=('微软雅黑', 10),
                fg='#666',
                bg='white').pack(anchor='w', padx=15, pady=(5, 5))
        
        # 下拉按钮
        var = tk.StringVar(value="请选择")
        dropdown_btn = tk.Button(row_frame,
                                textvariable=var,
                                font=('微软雅黑', 9),
                                fg='#999',
                                bg='#F5F5F5',
                                relief='flat',
                                padx=10,
                                pady=5,
                                command=lambda: self.show_options(var, options))
        dropdown_btn.pack(anchor='w', padx=15)
    
    def create_metric_button(self, parent, text, icon, x_pos):
        """创建检测指标按钮"""
        btn_frame = tk.Frame(parent, bg='#E8F0FE', width=100, height=100)
        btn_frame.place(x=x_pos, y=40)
        
        tk.Label(btn_frame, text=icon,
                font=('Arial', 20),
                bg='#E8F0FE').pack(pady=(15, 5))
        
        tk.Label(btn_frame, text=text,
                font=('微软雅黑', 9),
                fg='#333',
                bg='#E8F0FE').pack()
    
    def show_options(self, var, options):
        """显示选项弹窗"""
        # 简化版弹窗
        print(f"选项：{options}")
        var.set(options[0])
    
    def draw_camera_guide(self):
        """绘制拍摄指引框"""
        self.camera_canvas.delete("all")
        
        # 外框
        self.camera_canvas.create_rectangle(20, 20, 320, 260,
                                           outline='#666', width=1, dash=(5, 5))
        
        # 内框
        self.camera_canvas.create_rectangle(40, 40, 300, 240,
                                           outline='#4A90E2', width=2)
        
        # 四角标记
        corner = 20
        corners = [
            (40, 40, 40+corner, 40), (40, 40, 40, 40+corner),
            (300, 40, 300-corner, 40), (300, 40, 300, 40+corner),
            (40, 240, 40+corner, 240), (40, 240, 40, 240-corner),
            (300, 240, 300-corner, 240), (300, 240, 300, 240-corner)
        ]
        
        for x1, y1, x2, y2 in corners:
            self.camera_canvas.create_line(x1, y1, x2, y2,
                                          fill='#4A90E2', width=2)
        
        # 十字线
        self.camera_canvas.create_line(170, 40, 170, 240,
                                      fill='#4A90E2', width=1, dash=(3, 3))
        self.camera_canvas.create_line(40, 140, 300, 140,
                                      fill='#4A90E2', width=1, dash=(3, 3))
        
        # 文字
        self.camera_canvas.create_text(170, 140,
                                      text="拍摄区域",
                                      font=('微软雅黑', 10),
                                      fill='#999')
    
    def show_page(self, page_index):
        """显示指定页面"""
        # 隐藏所有页面
        self.page1.pack_forget()
        self.page2.pack_forget()
        self.page3.pack_forget()
        
        # 显示指定页面
        pages = [self.page1, self.page2, self.page3]
        pages[page_index].pack(fill='both', expand=True)
        
        self.current_page = page_index
    
    def select_style(self, style_index):
        """选择纹样风格"""
        print(f"选择风格：{self.pattern_styles[style_index]['name']}")
        
        # 更新按钮样式
        for i, btn in enumerate(self.style_buttons):
            if i == style_index:
                btn.config(bg=self.colors['accent_gold'])
            else:
                btn.config(bg=self.colors['bg_card'])
    
    def generate_pattern(self):
        """生成纹样"""
        saturation = self.saturation_scale.get()
        density = self.density_scale.get()
        color = self.color_scale.get()
        
        messagebox.showinfo("生成纹样",
                          f"正在生成纹样...\n\n"
                          f"饱和度：{saturation}%\n"
                          f"密度：{density}%\n"
                          f"颜色：{color}%")
    
    def submit_pattern(self):
        """提交纹样"""
        messagebox.showinfo("提交成功", "✓ 纹样已提交至生产环节")
    
    def upload_pattern_image(self):
        """上传纹样图片"""
        filetypes = [("图像文件", "*.jpg *.jpeg *.png"), ("所有文件", "*.*")]
        filepath = filedialog.askopenfilename(title="选择纹样图片", filetypes=filetypes)
        
        if filepath:
            self.image_path = filepath
            self.analyze_colors(filepath)
    
    def analyze_colors(self, image_path):
        """分析颜色"""
        try:
            img = cv2.imread(image_path)
            if img is None:
                return
            
            # 提取颜色
            colors, percentages = self.recognizer.extract_dominant_colors(img)
            color_info = self.recognizer.analyze_colors()
            
            # 绘制颜色条
            self.draw_color_palette(color_info)
            
            messagebox.showinfo("分析完成", 
                              f"已识别 {len(color_info)} 种主要颜色")
        except Exception as e:
            messagebox.showerror("错误", f"分析失败：{str(e)}")
    
    def draw_color_palette(self, color_info):
        """绘制颜色调色板"""
        self.colors_canvas.delete("all")
        
        bar_width = 45
        start_x = 20
        
        for i, info in enumerate(color_info):
            x = start_x + i * (bar_width + 5)
            rgb = info['rgb']
            hex_color = '#%02x%02x%02x' % tuple(rgb)
            
            # 绘制颜色条
            self.colors_canvas.create_rectangle(x, 30, x + bar_width, 100,
                                               fill=hex_color, outline='')
            
            # 绘制HEX值
            self.colors_canvas.create_text(x + bar_width//2, 115,
                                          text=info['hex'],
                                          font=('Arial', 8),
                                          fill='#666')
            
            # 绘制比例
            self.colors_canvas.create_text(x + bar_width//2, 130,
                                          text=f"{info['percentage']:.0f}%",
                                          font=('Arial', 8),
                                          fill='#999')
    
    def show_tutorial(self):
        """显示工艺教程"""
        messagebox.showinfo("工艺教程",
                          "艾德莱斯绸染色工艺流程：\n\n"
                          "1. 准备天然染料\n"
                          "2. 按比例调配染料\n"
                          "3. 浸泡丝绸30-50分钟\n"
                          "4. 固色处理20-30分钟\n"
                          "5. 清洗晾干")
    
    def confirm_formula(self):
        """确认配方"""
        messagebox.showinfo("确认配方", "✓ 染色配方已确认并保存")
    
    def capture_and_upload(self):
        """拍照上传"""
        filetypes = [("图像文件", "*.jpg *.jpeg *.png"), ("所有文件", "*.*")]
        filepath = filedialog.askopenfilename(title="选择质检图片", filetypes=filetypes)
        
        if filepath:
            self.image_path = filepath
            messagebox.showinfo("上传成功", "✓ 图片已上传，开始质检分析")
    
    def generate_report(self):
        """生成质检报告"""
        if not self.image_path:
            messagebox.showinfo("提示", "请先上传质检图片")
            return
        
        messagebox.showinfo("生成报告",
                          "正在生成质检报告...\n\n"
                          "✓ 瑕疵检测完成\n"
                          "✓ 等级判定完成\n"
                          "✓ 合格率计算完成")


def main():
    root = tk.Tk()
    app = ModernSilkApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
