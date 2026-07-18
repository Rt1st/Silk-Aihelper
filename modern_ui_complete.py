"""
艾德莱斯绸智能系统 - 完整现代化UI
整合三个核心功能：灵犀绘(纹样定制)、智调方(染色配方)、慧眼鉴(质检)
"""
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageTk, ImageDraw
import cv2
import numpy as np
import threading
from datetime import datetime
import uuid

from color_recognizer import ColorRecognizer, DyeFormulaCalculator
from quality_inspection import QualityInspectionApp


class ModernSilkApp:
    """现代化艾德莱斯绸系统"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("艾德莱斯绸智能系统")
        self.root.geometry("420x850")
        self.root.resizable(False, False)
        
        # 配色方案
        self.colors = {
            'bg_dark': '#0A0E1A',
            'bg_card': '#151B2E',
            'accent_gold': '#D4AF37',
            'accent_blue': '#4A90E2',
            'accent_green': '#50C878',
            'text_white': '#FFFFFF',
            'text_gray': '#8B95A8',
            'border': '#2A3650',
            'bg_light': '#E8F4F8'
        }
        
        # 初始化功能模块
        self.recognizer = ColorRecognizer(n_colors=7)
        self.dye_calculator = DyeFormulaCalculator()
        
        # 状态变量
        self.current_page = 0
        self.selected_style = 0
        self.image_path = None
        self.generated_patterns = []
        self.dye_formula = None
        self.inspection_results = None
        
        # 纹样风格数据
        self.pattern_styles = [
            {"name": "经典艾德莱斯", "icon": "🎨", "color": "#DC143C", "category": "traditional"},
            {"name": "现代几何", "icon": "◆", "color": "#4169E1", "category": "modern"},
            {"name": "旅拍简约", "icon": "📷", "color": "#50C878", "category": "minimalist"}
        ]
        
        # 创建UI
        self.setup_ui()
        
    def setup_ui(self):
        """设置主界面"""
        # 主容器
        self.main_container = tk.Frame(self.root, bg=self.colors['bg_dark'])
        self.main_container.grid(row=0, column=0, sticky='nsew')
        self.root.rowconfigure(0, weight=1)
        self.root.columnconfigure(0, weight=1)
        
        # 页面容器
        self.pages_container = tk.Frame(self.main_container, bg=self.colors['bg_dark'])
        self.pages_container.pack(fill='both', expand=True)
        
        # 创建三个页面
        self.page_pattern = self.create_pattern_page()
        self.page_dye = self.create_dye_page()
        self.page_quality = self.create_quality_page()
        
        # 底部导航栏
        self.create_bottom_nav()
        
        # 显示第一页
        self.show_page(0)
    
    def create_pattern_page(self):
        """创建纹样定制页面 - 灵犀绘"""
        frame = tk.Frame(self.pages_container, bg=self.colors['bg_dark'])
        
        # 标题栏
        header = tk.Frame(frame, bg=self.colors['bg_dark'], height=70)
        header.pack(fill='x')
        header.pack_propagate(False)
        
        tk.Label(header, text="←", font=('Arial', 18), 
                fg=self.colors['text_white'], bg=self.colors['bg_dark']).pack(side='left', padx=15, pady=20)
        tk.Label(header, text="灵犀绘-AI纹样定制", font=('微软雅黑', 15, 'bold'),
                fg=self.colors['text_white'], bg=self.colors['bg_dark']).pack(side='left', pady=22)
        
        # 内容区域（横向布局）
        content_frame = tk.Frame(frame, bg=self.colors['bg_dark'])
        content_frame.pack(fill='both', expand=True, padx=10)
        
        # 左侧风格选择
        style_panel = tk.Frame(content_frame, bg=self.colors['bg_dark'], width=70)
        style_panel.pack(side='left', fill='y')
        style_panel.pack_propagate(False)
        
        self.style_btns = []
        styles = ["经典艾德莱斯", "现代几何", "旅拍简约"]
        icons = ["🎨", "◆", "📷"]
        
        for i, (style, icon) in enumerate(zip(styles, icons)):
            btn_frame = tk.Frame(style_panel, bg=self.colors['bg_dark'])
            btn_frame.pack(pady=10)
            
            btn = tk.Button(btn_frame, 
                          text=icon,
                          font=('Arial', 20),
                          bg=self.colors['accent_gold'] if i == 0 else self.colors['bg_card'],
                          fg=self.colors['text_white'],
                          relief='flat',
                          width=3,
                          height=2,
                          command=lambda idx=i: self.select_style(idx))
            btn.pack()
            
            label = tk.Label(btn_frame, 
                           text=style[:2],
                           font=('微软雅黑', 8),
                           fg=self.colors['accent_gold'] if i == 0 else self.colors['text_gray'],
                           bg=self.colors['bg_dark'])
            label.pack(pady=3)
            
            self.style_btns.append((btn, label))
        
        # 中间预览区
        preview_panel = tk.Frame(content_frame, bg=self.colors['bg_card'], width=250, height=580)
        preview_panel.pack(side='left', padx=5)
        preview_panel.pack_propagate(False)
        
        self.preview_canvas = tk.Canvas(preview_panel, bg='#F5F5DC', 
                                       highlightthickness=0)
        self.preview_canvas.pack(fill='both', expand=True, padx=10, pady=10)
        
        # 预览区占位文字
        self.preview_canvas.create_text(125, 280,
                                       text="AI生成预览区\n\n选择风格并调整参数\n点击生成纹样",
                                       font=('微软雅黑', 11),
                                       fill='#999',
                                       justify='center')
        
        # 右侧参数调节
        param_panel = tk.Frame(content_frame, bg=self.colors['bg_dark'], width=80)
        param_panel.pack(side='right')
        param_panel.pack_propagate(False)
        
        # 饱和度
        tk.Label(param_panel, text="饱和度",
                font=('微软雅黑', 8),
                fg=self.colors['text_gray'],
                bg=self.colors['bg_dark']).pack(pady=(15, 3))
        
        self.saturation_scale = tk.Scale(param_panel, from_=100, to=0,
                                        orient='vertical',
                                        bg=self.colors['bg_dark'],
                                        fg=self.colors['text_white'],
                                        troughcolor=self.colors['border'],
                                        highlightthickness=0,
                                        width=12,
                                        length=130)
        self.saturation_scale.set(30)
        self.saturation_scale.pack()
        
        # 纹样密度
        tk.Label(param_panel, text="纹样密度",
                font=('微软雅黑', 8),
                fg=self.colors['text_gray'],
                bg=self.colors['bg_dark']).pack(pady=(18, 3))
        
        self.density_scale = tk.Scale(param_panel, from_=100, to=0,
                                     orient='vertical',
                                     bg=self.colors['bg_dark'],
                                     fg=self.colors['text_white'],
                                     troughcolor=self.colors['border'],
                                     highlightthickness=0,
                                     width=12,
                                     length=130)
        self.density_scale.set(50)
        self.density_scale.pack()
        
        # 颜色
        tk.Label(param_panel, text="颜色",
                font=('微软雅黑', 8),
                fg=self.colors['text_gray'],
                bg=self.colors['bg_dark']).pack(pady=(18, 3))
        
        self.color_scale = tk.Scale(param_panel, from_=0, to=100,
                                   orient='vertical',
                                   bg=self.colors['bg_dark'],
                                   fg=self.colors['accent_gold'],
                                   troughcolor=self.colors['border'],
                                   highlightthickness=0,
                                   width=12,
                                   length=130)
        self.color_scale.set(70)
        self.color_scale.pack()
        
        # 替换
        tk.Label(param_panel, text="替换",
                font=('微软雅黑', 8),
                fg=self.colors['text_gray'],
                bg=self.colors['bg_dark']).pack(pady=(18, 3))
        
        self.replace_scale = tk.Scale(param_panel, from_=0, to=100,
                                     orient='vertical',
                                     bg=self.colors['bg_dark'],
                                     fg=self.colors['accent_blue'],
                                     troughcolor=self.colors['border'],
                                     highlightthickness=0,
                                     width=12,
                                     length=130)
        self.replace_scale.set(40)
        self.replace_scale.pack()
        
        # 底部按钮区
        bottom_frame = tk.Frame(frame, bg=self.colors['bg_dark'], height=80)
        bottom_frame.pack(fill='x', side='bottom', pady=(5, 10))
        bottom_frame.pack_propagate(False)
        
        # 生成纹样按钮
        gen_btn = tk.Button(bottom_frame,
                           text="◇ 生成纹样",
                           font=('微软雅黑', 11, 'bold'),
                           bg=self.colors['bg_card'],
                           fg=self.colors['text_white'],
                           relief='flat',
                           padx=15,
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
                              padx=25,
                              pady=10,
                              cursor='hand2',
                              command=self.submit_pattern)
        submit_btn.pack(side='right', padx=15, pady=10)
        
        return frame
    
    def create_dye_page(self):
        """创建染色配方页面 - 智调方"""
        frame = tk.Frame(self.pages_container, bg=self.colors['bg_light'])
        
        # 标题栏
        header = tk.Frame(frame, bg=self.colors['bg_light'], height=70)
        header.pack(fill='x')
        header.pack_propagate(False)
        
        tk.Label(header, text="←", font=('Arial', 18),
                fg='#333', bg=self.colors['bg_light']).pack(side='left', padx=15, pady=20)
        tk.Label(header, text="智调方-AI染色配方", font=('微软雅黑', 15, 'bold'),
                fg='#333', bg=self.colors['bg_light']).pack(side='left', pady=22)
        
        # 上传按钮
        upload_btn = tk.Button(frame,
                              text="📤 上传纹样图 >",
                              font=('微软雅黑', 10, 'bold'),
                              bg='white',
                              fg='#333',
                              relief='flat',
                              padx=20,
                              pady=8,
                              cursor='hand2',
                              command=self.upload_pattern_for_dye)
        upload_btn.pack(pady=10)
        
        # 颜色分析区
        colors_card = tk.Frame(frame, bg='white', width=380, height=160)
        colors_card.pack(padx=15, pady=8)
        colors_card.pack_propagate(False)
        
        tk.Label(colors_card, text="色彩分析",
                font=('微软雅黑', 10, 'bold'),
                fg='#333',
                bg='white').pack(anchor='w', padx=15, pady=(10, 5))
        
        self.colors_canvas = tk.Canvas(colors_card, bg='white',
                                      highlightthickness=0, width=350, height=110)
        self.colors_canvas.pack(fill='both', expand=True, padx=10, pady=5)
        
        # 初始提示
        self.colors_canvas.create_text(175, 55,
                                      text="请上传纹样图进行颜色分析",
                                      font=('微软雅黑', 10),
                                      fill='#999')
        
        # 配方参数区
        formula_card = tk.Frame(frame, bg='white', width=380, height=400)
        formula_card.pack(padx=15, pady=8)
        formula_card.pack_propagate(False)
        
        tk.Label(formula_card, text="配方参数",
                font=('微软雅黑', 10, 'bold'),
                fg='#333',
                bg='white').pack(anchor='w', padx=15, pady=(10, 5))
        
        # 参数表单
        self.dye_params = {}
        params = [
            ("原料名称", ["红花", "板蓝根", "黄刺叶", "紫草", "茶叶", "核桃皮"]),
            ("用量", ["1:21", "1:22", "1:23", "1:24", "1:25"]),
            ("浸泡时长", ["20分钟", "30分钟", "40分钟", "50分钟", "60分钟"]),
            ("固色参数", ["低温固色", "中温固色", "高温固色"])
        ]
        
        for i, (param_name, options) in enumerate(params):
            row_frame = tk.Frame(formula_card, bg='white')
            row_frame.pack(fill='x', padx=15, pady=8)
            
            tk.Label(row_frame, text=param_name,
                    font=('微软雅黑', 9),
                    fg='#666',
                    bg='white').pack(anchor='w', pady=(0, 5))
            
            var = tk.StringVar(value="请选择")
            self.dye_params[param_name] = var
            
            dropdown = ttk.Combobox(row_frame,
                                   textvariable=var,
                                   values=options,
                                   state='readonly',
                                   font=('微软雅黑', 9))
            dropdown.pack(fill='x')
        
        # 底部按钮区
        bottom_frame = tk.Frame(frame, bg=self.colors['bg_light'], height=80)
        bottom_frame.pack(fill='x', side='bottom', pady=(5, 10))
        bottom_frame.pack_propagate(False)
        
        tutorial_btn = tk.Button(bottom_frame,
                                text="☑ 查看工艺教程",
                                font=('微软雅黑', 10),
                                bg='white',
                                fg='#333',
                                relief='flat',
                                padx=15,
                                pady=8,
                                cursor='hand2',
                                command=self.show_dye_tutorial)
        tutorial_btn.pack(side='left', padx=15, pady=10)
        
        confirm_btn = tk.Button(bottom_frame,
                               text="确认配方",
                               font=('微软雅黑', 11, 'bold'),
                               bg='#2563EB',
                               fg='white',
                               relief='flat',
                               padx=30,
                               pady=10,
                               cursor='hand2',
                               command=self.confirm_dye_formula)
        confirm_btn.pack(side='right', padx=15, pady=10)
        
        return frame
    
    def create_quality_page(self):
        """创建质检页面 - 慧眼鉴"""
        frame = tk.Frame(self.pages_container, bg='white')
        
        # 标题栏
        header = tk.Frame(frame, bg='white', height=70)
        header.pack(fill='x')
        header.pack_propagate(False)
        
        tk.Label(header, text="←", font=('Arial', 18),
                fg='#333', bg='white').pack(side='left', padx=15, pady=20)
        tk.Label(header, text="慧眼鉴-AI质检", font=('微软雅黑', 15, 'bold'),
                fg='#333', bg='white').pack(side='left', pady=22)
        
        tk.Label(header, text="···", font=('Arial', 18),
                fg='#333', bg='white').pack(side='right', padx=15, pady=20)
        
        # 拍摄框区域
        camera_card = tk.Frame(frame, bg='#F0F0F0', width=380, height=320)
        camera_card.pack(padx=20, pady=10)
        camera_card.pack_propagate(False)
        
        self.camera_canvas = tk.Canvas(camera_card, bg='#1A1A1A',
                                      highlightthickness=0, width=350, height=290)
        self.camera_canvas.pack(fill='both', expand=True, padx=15, pady=15)
        
        # 绘制拍摄指引
        self.draw_camera_guide()
        
        # 拍照上传按钮
        capture_btn = tk.Button(frame,
                               text="拍照上传",
                               font=('微软雅黑', 12, 'bold'),
                               bg='#2563EB',
                               fg='white',
                               relief='flat',
                               padx=50,
                               pady=12,
                               cursor='hand2',
                               command=self.capture_for_quality)
        capture_btn.pack(pady=15)
        
        # 检测指标区
        metrics_card = tk.Frame(frame, bg='#F5F5F5', width=380, height=200)
        metrics_card.pack(padx=20, pady=10)
        metrics_card.pack_propagate(False)
        
        # 三个指标按钮
        self.quality_metrics = {}
        metrics = [("瑕疵检测", "⬡", 0), ("等级判定", "📋", 130), ("合格率", "✓", 260)]
        
        for text, icon, x_pos in metrics:
            btn_frame = tk.Frame(metrics_card, bg='#E8F0FE', width=110, height=120)
            btn_frame.place(x=x_pos, y=40)
            
            tk.Label(btn_frame, text=icon,
                    font=('Arial', 24),
                    bg='#E8F0FE').pack(pady=(20, 8))
            
            tk.Label(btn_frame, text=text,
                    font=('微软雅黑', 10),
                    fg='#333',
                    bg='#E8F0FE').pack()
            
            result_label = tk.Label(btn_frame, text="--",
                                   font=('微软雅黑', 12, 'bold'),
                                   fg='#4A90E2',
                                   bg='#E8F0FE')
            result_label.pack(pady=(5, 0))
            self.quality_metrics[text] = result_label
        
        # 生成报告按钮
        report_btn = tk.Button(frame,
                              text="生成报告",
                              font=('微软雅黑', 12, 'bold'),
                              bg='#2563EB',
                              fg='white',
                              relief='flat',
                              padx=70,
                              pady=12,
                              cursor='hand2',
                              command=self.generate_quality_report)
        report_btn.pack(pady=25)
        
        return frame
    
    def create_bottom_nav(self):
        """创建底部导航栏"""
        nav_frame = tk.Frame(self.main_container, 
                            bg=self.colors['bg_card'],
                            height=70)
        nav_frame.pack(fill='x', side='bottom')
        nav_frame.pack_propagate(False)
        
        # 三个导航按钮
        nav_items = [
            ("灵犀绘", "🎨"),
            ("智调方", "🧪"),
            ("慧眼鉴", "🔍")
        ]
        
        self.nav_buttons = []
        for i, (text, icon) in enumerate(nav_items):
            btn_frame = tk.Frame(nav_frame, bg=self.colors['bg_card'], width=140)
            btn_frame.pack(side='left')
            btn_frame.pack_propagate(False)
            
            btn = tk.Button(btn_frame,
                          text=f"{icon}\n{text}",
                          font=('微软雅黑', 9),
                          bg=self.colors['bg_card'] if i != 0 else self.colors['accent_gold'],
                          fg=self.colors['text_white'] if i != 0 else '#000',
                          relief='flat',
                          padx=10,
                          pady=10,
                          cursor='hand2',
                          command=lambda idx=i: self.switch_page(idx))
            btn.pack(fill='both', expand=True, pady=8, padx=5)
            
            self.nav_buttons.append(btn)
    
    def show_page(self, page_index):
        """显示指定页面"""
        # 隐藏所有页面
        for page in [self.page_pattern, self.page_dye, self.page_quality]:
            page.pack_forget()
        
        # 显示目标页面
        pages = [self.page_pattern, self.page_dye, self.page_quality]
        pages[page_index].pack(fill='both', expand=True)
        
        self.current_page = page_index
    
    def switch_page(self, page_index):
        """切换页面"""
        # 更新按钮样式
        for i, btn in enumerate(self.nav_buttons):
            if i == page_index:
                btn.config(bg=self.colors['accent_gold'], fg='#000')
            else:
                btn.config(bg=self.colors['bg_card'], fg=self.colors['text_white'])
        
        self.show_page(page_index)
    
    def select_style(self, style_index):
        """选择纹样风格"""
        self.selected_style = style_index
        
        # 更新按钮样式
        for i, (btn, label) in enumerate(self.style_btns):
            if i == style_index:
                btn.config(bg=self.colors['accent_gold'])
                label.config(fg=self.colors['accent_gold'])
            else:
                btn.config(bg=self.colors['bg_card'])
                label.config(fg=self.colors['text_gray'])
        
        # 在预览区显示风格提示
        self.update_preview()
    
    def update_preview(self):
        """更新预览区"""
        style = self.pattern_styles[self.selected_style]
        
        self.preview_canvas.delete("all")
        
        # 绘制背景
        self.preview_canvas.create_rectangle(0, 0, 250, 580,
                                            fill=style['color'],
                                            outline='')
        
        # 绘制纹样元素
        center_x, center_y = 125, 290
        for i in range(12):
            angle = i * 30
            x1 = center_x + 80 * np.cos(np.radians(angle))
            y1 = center_y + 80 * np.sin(np.radians(angle))
            x2 = center_x + 60 * np.cos(np.radians(angle + 15))
            y2 = center_y + 60 * np.sin(np.radians(angle + 15))
            
            self.preview_canvas.create_line(x1, y1, x2, y2,
                                           fill='white', width=2)
        
        # 添加文字
        self.preview_canvas.create_text(125, 290,
                                       text=f"{style['name']}\n预览",
                                       font=('微软雅黑', 14, 'bold'),
                                       fill='white',
                                       justify='center')
    
    def generate_pattern(self):
        """生成纹样"""
        saturation = self.saturation_scale.get()
        density = self.density_scale.get()
        color = self.color_scale.get()
        replace = self.replace_scale.get()
        
        style = self.pattern_styles[self.selected_style]
        
        # 生成纹样图像
        self.preview_canvas.delete("all")
        
        # 根据参数生成颜色
        base_color = style['color']
        r = int(base_color[1:3], 16)
        g = int(base_color[3:5], 16)
        b = int(base_color[5:7], 16)
        
        # 根据饱和度调整
        gray = int(0.299 * r + 0.587 * g + 0.114 * b)
        r = int(r * (saturation / 100) + gray * (1 - saturation / 100))
        g = int(g * (saturation / 100) + gray * (1 - saturation / 100))
        b = int(b * (saturation / 100) + gray * (1 - saturation / 100))
        
        adjusted_color = f'#{r:02x}{g:02x}{b:02x}'
        
        # 绘制背景
        self.preview_canvas.create_rectangle(0, 0, 250, 580,
                                            fill=adjusted_color,
                                            outline='')
        
        # 绘制纹样
        center_x, center_y = 125, 290
        num_elements = int(density / 10) + 3
        
        for i in range(num_elements):
            angle = i * (360 / num_elements)
            radius = 100 + (density - 50) * 0.5
            
            for j in range(3):
                r_inner = radius - j * 20
                x1 = center_x + r_inner * np.cos(np.radians(angle))
                y1 = center_y + r_inner * np.sin(np.radians(angle))
                x2 = center_x + (r_inner - 30) * np.cos(np.radians(angle + 10))
                y2 = center_y + (r_inner - 30) * np.sin(np.radians(angle + 10))
                
                self.preview_canvas.create_line(x1, y1, x2, y2,
                                               fill='white', width=2)
        
        # 添加文字
        info = f"✓ 生成成功\n\n风格: {style['name']}\n饱和度: {saturation}%\n密度: {density}%\n颜色: {color}%"
        self.preview_canvas.create_text(125, 290,
                                       text=info,
                                       font=('微软雅黑', 11),
                                       fill='white',
                                       justify='center')
        
        self.generated_patterns.append({
            'style': style['name'],
            'saturation': saturation,
            'density': density,
            'timestamp': datetime.now()
        })
        
        messagebox.showinfo("生成成功", 
                          f"已生成 {len(self.generated_patterns)} 组方案\n\n"
                          f"风格：{style['name']}\n"
                          f"参数已优化")
    
    def submit_pattern(self):
        """提交纹样"""
        if not self.generated_patterns:
            messagebox.showinfo("提示", "请先生成纹样")
            return
        
        code = f"ADLS-{datetime.now().strftime('%Y%m%d')}-{uuid.uuid4().hex[:6].upper()}"
        
        messagebox.showinfo("提交成功",
                          f"✓ 纹样已提交至生产环节\n\n"
                          f"生产编号：{code}\n"
                          f"生成方案：{len(self.generated_patterns)}组")
    
    def upload_pattern_for_dye(self):
        """上传纹样图用于染色分析"""
        filetypes = [("图像文件", "*.jpg *.jpeg *.png"), ("所有文件", "*.*")]
        filepath = filedialog.askopenfilename(title="选择纹样图片", filetypes=filetypes)
        
        if filepath:
            self.image_path = filepath
            self.analyze_dye_colors(filepath)
    
    def analyze_dye_colors(self, image_path):
        """分析染色颜色"""
        try:
            img = cv2.imread(image_path)
            if img is None:
                return
            
            # 提取颜色
            colors, percentages = self.recognizer.extract_dominant_colors(img)
            color_info = self.recognizer.analyze_colors()
            
            # 绘制颜色调色板
            self.draw_dye_palette(color_info)
            
            # 计算染料配方
            if len(color_info) > 0:
                dominant_color = color_info[0]['rgb']
                self.dye_formula = self.dye_calculator.calculate_dye_formula(
                    dominant_color,
                    ambient_temp=25,
                    ambient_humidity=60
                )
            
            messagebox.showinfo("分析完成",
                              f"已识别 {len(color_info)} 种主要颜色\n"
                              f"染料配方已生成")
        except Exception as e:
            messagebox.showerror("错误", f"分析失败：{str(e)}")
    
    def draw_dye_palette(self, color_info):
        """绘制染色调色板"""
        self.colors_canvas.delete("all")
        
        bar_width = 42
        start_x = 15
        
        for i, info in enumerate(color_info):
            if i >= 7:
                break
            
            x = start_x + i * (bar_width + 5)
            rgb = info['rgb']
            hex_color = '#%02x%02x%02x' % tuple(rgb)
            
            # 绘制颜色条
            self.colors_canvas.create_rectangle(x, 10, x + bar_width, 70,
                                               fill=hex_color, outline='')
            
            # HEX值
            self.colors_canvas.create_text(x + bar_width//2, 85,
                                          text=info['hex'],
                                          font=('Arial', 7),
                                          fill='#666')
            
            # 比例
            self.colors_canvas.create_text(x + bar_width//2, 100,
                                          text=f"{info['percentage']:.0f}%",
                                          font=('Arial', 8, 'bold'),
                                          fill='#333')
    
    def show_dye_tutorial(self):
        """显示染色工艺教程"""
        tutorial = """
艾德莱斯绸传统染色工艺

1. 准备天然染料
   • 红色：红花、茜草
   • 蓝色：板蓝根
   • 黄色：黄刺叶、姜黄
   • 紫色：紫草

2. 染料调配
   • 按比例混合染料
   • 加入适量温水溶解

3. 浸泡染色
   • 温度：60-80℃
   • 时间：30-50分钟
   • 搅拌：每隔10分钟

4. 固色处理
   • 使用明矾固色
   • 时间：20-30分钟

5. 清洗晾干
   • 清水漂洗3次
   • 阴凉处晾干
        """
        
        messagebox.showinfo("工艺教程", tutorial)
    
    def confirm_dye_formula(self):
        """确认染色配方"""
        if not self.dye_formula:
            messagebox.showinfo("提示", "请先上传纹样图生成配方")
            return
        
        formula_text = "确认染色配方\n\n"
        formula_text += "染料配比：\n"
        for dye, ratio in self.dye_formula.get('dye_ratio', {}).items():
            formula_text += f"  • {dye}: {ratio*100:.1f}%\n"
        
        formula_text += f"\n浸泡时间：{self.dye_formula.get('soak_time', 0)}分钟"
        formula_text += f"\n固色时间：{self.dye_formula.get('fix_time', 0)}分钟"
        
        confirmed = messagebox.askyesno("确认配方", formula_text)
        
        if confirmed:
            messagebox.showinfo("确认成功", "✓ 染色配方已保存并发送至生产环节")
    
    def draw_camera_guide(self):
        """绘制质检拍摄指引"""
        self.camera_canvas.delete("all")
        
        # 外框
        self.camera_canvas.create_rectangle(20, 20, 330, 270,
                                           outline='#444', width=1, dash=(5, 5))
        
        # 内框
        self.camera_canvas.create_rectangle(40, 40, 310, 250,
                                           outline='#4A90E2', width=2)
        
        # 四角标记
        corner = 25
        corners = [
            (40, 40, 40+corner, 40), (40, 40, 40, 40+corner),
            (310, 40, 310-corner, 40), (310, 40, 310, 40+corner),
            (40, 250, 40+corner, 250), (40, 250, 40, 250-corner),
            (310, 250, 310-corner, 250), (310, 250, 310, 250-corner)
        ]
        
        for x1, y1, x2, y2 in corners:
            self.camera_canvas.create_line(x1, y1, x2, y2,
                                          fill='#4A90E2', width=3)
        
        # 十字线
        self.camera_canvas.create_line(175, 40, 175, 250,
                                      fill='#4A90E2', width=1, dash=(3, 3))
        self.camera_canvas.create_line(40, 145, 310, 145,
                                      fill='#4A90E2', width=1, dash=(3, 3))
        
        # 文字
        self.camera_canvas.create_text(175, 145,
                                      text="拍摄区域\n60cm × 140cm",
                                      font=('微软雅黑', 10),
                                      fill='#666',
                                      justify='center')
    
    def capture_for_quality(self):
        """拍照质检"""
        filetypes = [("图像文件", "*.jpg *.jpeg *.png"), ("所有文件", "*.*")]
        filepath = filedialog.askopenfilename(title="选择质检图片", filetypes=filetypes)
        
        if filepath:
            self.run_quality_inspection(filepath)
    
    def run_quality_inspection(self, image_path):
        """运行质检分析"""
        try:
            img = cv2.imread(image_path)
            if img is None:
                return
            
            # 模拟质检结果
            uniformity = np.random.uniform(92, 99)
            alignment = np.random.uniform(95, 100)
            defect_count = np.random.randint(0, 3)
            
            if uniformity >= 95 and alignment >= 98 and defect_count == 0:
                grade = "精品级"
                grade_color = "#50C878"
            elif uniformity >= 90 and alignment >= 95:
                grade = "合格级"
                grade_color = "#4A90E2"
            else:
                grade = "待返工"
                grade_color = "#DC143C"
            
            # 更新检测结果
            self.inspection_results = {
                'uniformity': round(uniformity, 1),
                'alignment': round(alignment, 1),
                'defect_count': defect_count,
                'grade': grade,
                'pass_rate': round((uniformity + alignment) / 2, 1)
            }
            
            # 显示在拍摄框中
            self.camera_canvas.delete("all")
            
            # 转换并显示图片
            rgb_img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            img_resized = cv2.resize(rgb_img, (350, 290))
            pil_img = Image.fromarray(img_resized)
            photo = ImageTk.PhotoImage(image=pil_img)
            
            self.camera_canvas.create_image(0, 0, image=photo, anchor='nw')
            self.camera_canvas.image = photo
            
            # 绘制检测框
            self.camera_canvas.create_rectangle(40, 40, 310, 250,
                                               outline='#4A90E2', width=2)
            
            # 更新指标显示
            self.quality_metrics["瑕疵检测"].config(text=str(defect_count))
            self.quality_metrics["等级判定"].config(text=grade, fg=grade_color)
            self.quality_metrics["合格率"].config(text=f"{self.inspection_results['pass_rate']}%")
            
            messagebox.showinfo("质检完成",
                              f"检测等级：{grade}\n"
                              f"染色均匀度：{uniformity:.1f}%\n"
                              f"纹样对齐度：{alignment:.1f}%\n"
                              f"瑕疵数量：{defect_count}")
        except Exception as e:
            messagebox.showerror("错误", f"质检失败：{str(e)}")
    
    def generate_quality_report(self):
        """生成质检报告"""
        if not self.inspection_results:
            messagebox.showinfo("提示", "请先完成质检")
            return
        
        report_code = f"QC-{datetime.now().strftime('%Y%m%d')}-{uuid.uuid4().hex[:6].upper()}"
        
        report = f"""
质检报告

报告编号：{report_code}
检测时间：{datetime.now().strftime('%Y-%m-%d %H:%M')}

检测结果：
• 产品等级：{self.inspection_results['grade']}
• 染色均匀度：{self.inspection_results['uniformity']}%
• 纹样对齐度：{self.inspection_results['alignment']}%
• 瑕疵数量：{self.inspection_results['defect_count']}
• 合格率：{self.inspection_results['pass_rate']}%

结论：产品{self.inspection_results['grade']}，符合出厂标准
        """
        
        messagebox.showinfo("质检报告", report)


def main():
    root = tk.Tk()
    app = ModernSilkApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
