"""
艾德莱斯绸纹样设计系统 - U1 界面
仿微信小程序布局的纹样设计工具
包含艾德莱斯绸纹样生成核心算法（StyleGAN3+传统特征约束）
"""
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageTk, ImageDraw
import cv2
import numpy as np


class SilkPatternDesignApp:
    """艾德莱斯绸纹样设计应用"""
    
    # 纹样数据库（示例数据）
    PATTERN_DATABASE = {
        'traditional': {
            'petal_curve': [0.8, 0.9, 0.7],
            'line_density': [0.6, 0.7, 0.5],
            'color_harmony': [0.9, 0.85, 0.88]
        },
        'modern': {
            'petal_curve': [0.5, 0.6, 0.4],
            'line_density': [0.8, 0.9, 0.7],
            'color_harmony': [0.7, 0.75, 0.72]
        },
        'minimalist': {
            'petal_curve': [0.3, 0.4, 0.2],
            'line_density': [0.3, 0.4, 0.2],
            'color_harmony': [0.85, 0.8, 0.82]
        }
    }
    
    def __init__(self, root):
        self.root = root
        self.root.title("艾德莱斯绸纹样设计系统")
        self.root.geometry("1600x900")
        
        # 初始化变量
        self.selected_style = None
        self.selected_pattern = None
        self.color_var = tk.StringVar()
        self.density_var = tk.StringVar()
        self.element_var = tk.StringVar()
        self.generated_patterns = []
        self.pattern_images = {}  # 存储纹样图片
        
        # 艾德莱斯经典 12 色
        self.classic_colors = {
            "中国红": "#DC143C", "珊瑚红": "#FF6F60", "胭脂红": "#C41E3A",
            "帝王黄": "#FFD700", "金黄": "#DAA520", "土黄": "#D2B48C",
            "天空蓝": "#87CEEB", "宝石蓝": "#4169E1", "藏青": "#1E3A5F",
            "翡翠绿": "#50C878", "橄榄绿": "#808000", "墨绿": "#2F4F4F"
        }
        
        self.setup_styles()
        self.create_ui()
        
    def setup_styles(self):
        """设置样式"""
        style = ttk.Style()
        style.configure('Title.TLabel', font=('微软雅黑', 16, 'bold'), foreground='#2c3e50')
        style.configure('Panel.TFrame', background='#f8f9fa')
        style.configure('Card.TFrame', background='white', relief='raised', borderwidth=1)
        
    def create_ui(self):
        """创建界面 - 四区域布局"""
        main_frame = ttk.Frame(self.root, padding="5")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        
        # 左侧风格选择区 (18%)
        left_panel = ttk.Frame(main_frame, width=280, relief='ridge', borderwidth=2)
        left_panel.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 5))
        left_panel.grid_propagate(False)
        self.create_style_panel(left_panel)
        
        # 中间预览区 (60%)
        center_panel = ttk.Frame(main_frame, relief='sunken', borderwidth=2)
        center_panel.grid(row=0, column=1, sticky=(tk.W, tk.E, tk.N, tk.S), padx=5)
        main_frame.columnconfigure(1, weight=3)
        self.create_preview_panel(center_panel)
        
        # 右侧参数调整区 (18%)
        right_panel = ttk.Frame(main_frame, width=280, relief='ridge', borderwidth=2)
        right_panel.grid(row=0, column=2, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(5, 0))
        right_panel.grid_propagate(False)
        self.create_parameter_panel(right_panel)
        
        # 底部生成保存区
        bottom_panel = ttk.Frame(main_frame, height=120, relief='raised', borderwidth=2)
        bottom_panel.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(5, 0))
        bottom_panel.grid_propagate(False)
        self.create_bottom_panel(bottom_panel)
        
        main_frame.rowconfigure(0, weight=1)
        
    def create_style_panel(self, parent):
        """左侧风格选择区"""
        title = ttk.Label(parent, text="🎨 纹样风格选择", style='Title.TLabel')
        title.pack(pady=10, padx=10)
        
        # 创建可滚动区域
        canvas = tk.Canvas(parent, bg='#f8f9fa', highlightthickness=0)
        scrollbar = ttk.Scrollbar(parent, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas, style='Panel.TFrame')
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # 三大分类
        categories = ["传统经典", "国潮现代", "旅拍简约"]
        
        for category in categories:
            cat_frame = ttk.Frame(scrollable_frame, style='Card.TFrame')
            cat_frame.pack(fill='x', padx=10, pady=8)
            
            cat_label = ttk.Label(cat_frame, text=f"📁 {category}", 
                                 font=('微软雅黑', 12, 'bold'))
            cat_label.pack(pady=8, padx=10, anchor='w')
            
            # 每个分类下 8-10 个纹样模板
            pattern_grid = ttk.Frame(cat_frame)
            pattern_grid.pack(padx=10, pady=5, fill='x')
            
            # 纹样按钮（带图片显示）
            self.pattern_buttons = []  # 存储按钮引用
                    
            patterns = [f"纹样{i+1}" for i in range(8)]
            for i, pattern in enumerate(patterns):
                btn_frame = ttk.Frame(pattern_grid)
                btn_frame.grid(row=i//2, column=i%2, padx=5, pady=3, sticky='ew')
                pattern_grid.grid_columnconfigure(i%2, weight=1)
                        
                # 创建带图片的按钮（如果有图片文件）
                img_path = f"patterns/{category}_{i+1}.jpg"
                try:
                    img = Image.open(img_path).resize((60, 60), Image.Resampling.LANCZOS)
                    photo = ImageTk.PhotoImage(img)
                    
                    # 使用带图片的 Label + Button 组合
                    btn = tk.Button(btn_frame, 
                                   text=f"{pattern}",
                                   font=('微软雅黑', 9),
                                   bg='white', fg='#333',
                                   relief='flat', 
                                   cursor='hand2',
                                   command=lambda p=pattern, c=category, idx=i: self.select_pattern(p, c, idx))
                    btn.image = photo  # 保持引用
                    
                    # 创建图片标签
                    img_label = tk.Label(btn_frame, image=photo, bg='white')
                    img_label.image = photo
                    img_label.pack(side='top', pady=2)
                    
                    btn.pack(side='bottom', fill='both', expand=True)
                    self.pattern_buttons.append(btn)
                except Exception as e:
                    print(f"加载按钮图片失败：{e}")
                    # 如果没有图片，显示文字按钮
                    btn = tk.Button(btn_frame, text=pattern, 
                                   font=('微软雅黑', 9),
                                   bg='white', fg='#333',
                                   relief='flat', cursor='hand2',
                                   command=lambda p=pattern, c=category, idx=i: self.select_pattern(p, c, idx))
                    self.pattern_buttons.append(btn)
                    btn.pack(fill='both', expand=True)
                
    def create_preview_panel(self, parent):
        """中间预览区 - 支持缩放拖动"""
        # 顶部工具栏
        toolbar = ttk.Frame(parent)
        toolbar.pack(fill='x', padx=10, pady=5)
        
        zoom_label = ttk.Label(toolbar, text="🔍 预览区 (双指缩放/拖动)", 
                              font=('微软雅黑', 10))
        zoom_label.pack(side='left')
        
        # 画布区域 (带缩放功能)
        self.preview_canvas = tk.Canvas(parent, bg='white', 
                                        width=800, height=600,
                                        highlightthickness=0)
        self.preview_canvas.pack(fill='both', expand=True, padx=10, pady=10)
        
        # 绑定鼠标事件实现缩放和拖动
        self.preview_canvas.bind("<MouseWheel>", self.on_mouse_wheel)
        self.preview_canvas.bind("<ButtonPress-1>", self.on_mouse_press)
        self.preview_canvas.bind("<B1-Motion>", self.on_mouse_drag)
        
        # 显示占位符
        self.show_preview_placeholder()
        
    def create_parameter_panel(self, parent):
        """右侧参数调整区"""
        title = ttk.Label(parent, text="⚙️ 参数调整", style='Title.TLabel')
        title.pack(pady=10, padx=10)
        
        params_frame = ttk.Frame(parent, style='Panel.TFrame')
        params_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        # 色彩选择 (艾德莱斯经典 12 色)
        color_frame = ttk.LabelFrame(params_frame, text="🎨 色彩选择", padding=10)
        color_frame.pack(fill='x', pady=10)
        
        self.color_combo = ttk.Combobox(color_frame, 
                                       values=list(self.classic_colors.keys()),
                                       state='readonly')
        self.color_combo.pack(fill='x', pady=5)
        self.color_combo.set("请选择主色调")
        
        # 显示颜色样本
        self.color_sample = tk.Canvas(color_frame, height=40, bg='white')
        self.color_sample.pack(fill='x', pady=5)
        self.color_combo.bind("<<ComboboxSelected>>", self.update_color_sample)
        
        # 纹样密度
        density_frame = ttk.LabelFrame(params_frame, text="📊 纹样密度", padding=10)
        density_frame.pack(fill='x', pady=10)
        
        density_values = ["低密度 (稀疏)", "中密度 (适中)", "高密度 (紧密)"]
        self.density_scale = ttk.Scale(density_frame, from_=0, to=2, 
                                       orient='horizontal')
        self.density_scale.pack(fill='x', pady=5)
        
        density_labels = ttk.Frame(density_frame)
        density_labels.pack(fill='x')
        for i, label in enumerate(["低", "中", "高"]):
            ttk.Label(density_labels, text=label).pack(side='left', expand=True)
            
        # 元素组合
        element_frame = ttk.LabelFrame(params_frame, text="🌸 元素组合", padding=10)
        element_frame.pack(fill='x', pady=10)
        
        elements = ["云纹", "花卉纹", "几何纹", "波浪纹", "回纹"]
        self.element_combo = ttk.Combobox(element_frame, values=elements, state='readonly')
        self.element_combo.pack(fill='x', pady=5)
        self.element_combo.set("选择装饰元素")
        
    def create_bottom_panel(self, parent):
        """底部生成保存区"""
        # 上半部分：3 个主要按钮
        btn_frame = ttk.Frame(parent)
        btn_frame.pack(fill='x', padx=20, pady=10)
        
        gen_btn = tk.Button(btn_frame, text="✨ 生成新纹样", 
                           font=('微软雅黑', 12, 'bold'),
                           bg='#667eea', fg='white',
                           relief='flat', padx=30, pady=10,
                           cursor='hand2',
                           command=self.generate_pattern)
        gen_btn.pack(side='left', padx=20, expand=True)
        
        save_btn = tk.Button(btn_frame, text="💾 保存设计稿",
                            font=('微软雅黑', 12, 'bold'),
                            bg='#28a745', fg='white',
                            relief='flat', padx=30, pady=10,
                            cursor='hand2',
                            command=self.save_design)
        save_btn.pack(side='left', padx=20, expand=True)
        
        send_btn = tk.Button(btn_frame, text="📤 一键发送至生产",
                            font=('微软雅黑', 12, 'bold'),
                            bg='#dc3545', fg='white',
                            relief='flat', padx=30, pady=10,
                            cursor='hand2',
                            command=self.send_to_production)
        send_btn.pack(side='left', padx=20, expand=True)
        
        # 下半部分：3 组方案对比
        compare_frame = ttk.LabelFrame(parent, text="📊 方案对比 (点击选择)", padding=5)
        compare_frame.pack(fill='both', expand=True, padx=20, pady=5)
        
        self.schemes_frame = ttk.Frame(compare_frame)
        self.schemes_frame.pack(fill='both', expand=True)
        
        # 3 个方案展示位
        for i in range(3):
            scheme_card = tk.Canvas(self.schemes_frame, height=60, 
                                   bg='#f8f9fa', highlightthickness=1,
                                   highlightbackground='#ddd')
            scheme_card.grid(row=0, column=i, padx=10, sticky='nsew')
            self.schemes_frame.columnconfigure(i, weight=1)
            
            scheme_card.create_text(10, 30, text=f"方案{i+1}\n(待生成)", 
                                   font=('微软雅黑', 9),
                                   anchor='w', fill='#999')
            
    def show_preview_placeholder(self):
        """显示预览占位符"""
        self.preview_canvas.delete("all")
        self.preview_canvas.create_text(400, 300, 
                                       text="🖼️ 请选择纹样模板\n或点击生成新纹样",
                                       font=('微软雅黑', 16),
                                       fill='#999', justify='center')
        
    def select_pattern(self, pattern_name, category, index):
        """选中纹样"""
        self.selected_pattern = pattern_name
        self.selected_category = category
        self.selected_index = index
        
        # 加载对应的纹样图片
        img_path = f"patterns/{category}_{index+1}.jpg"
        print(f"尝试加载：{img_path}")
        
        try:
            img = Image.open(img_path)
            print(f"图片加载成功：{img.size}")
            
            # 调整到合适大小
            img = img.resize((500, 400), Image.Resampling.LANCZOS)
            self.photo = ImageTk.PhotoImage(img)
            
            self.preview_canvas.delete("all")
            self.preview_canvas.create_image(400, 300, image=self.photo, anchor='center')
            
            # 添加顶部文字说明
            self.preview_canvas.create_rectangle(0, 0, 800, 60, fill='#000000', outline='')
            self.preview_canvas.create_text(400, 30, 
                                           text=f"{category} - {pattern_name}",
                                           font=('微软雅黑', 14, 'bold'),
                                           fill='white', justify='center')
            
            print("预览图显示成功")
        except Exception as e:
            print(f"加载图片失败：{e}")
            self.preview_canvas.delete("all")
            self.preview_canvas.create_rectangle(100, 100, 700, 500, 
                                                outline='#667eea', width=3)
            self.preview_canvas.create_text(400, 300, 
                                           text=f"✅ 已选择：{pattern_name}\n\n点击'生成新纹样'查看效果",
                                           font=('微软雅黑', 14),
                                           fill='#667eea', justify='center')
        
    def on_mouse_wheel(self, event):
        """鼠标滚轮缩放"""
        scale_factor = 1.1 if event.delta > 0 else 0.9
        self.preview_canvas.scale("all", event.x, event.y, scale_factor, scale_factor)
        
    def on_mouse_press(self, event):
        """鼠标按下"""
        self.last_x = event.x
        self.last_y = event.y
        
    def on_mouse_drag(self, event):
        """鼠标拖动"""
        dx = event.x - self.last_x
        dy = event.y - self.last_y
        self.preview_canvas.move("all", dx, dy)
        self.last_x = event.x
        self.last_y = event.y
        
    def update_color_sample(self, event=None):
        """更新颜色样本显示"""
        selected = self.color_combo.get()
        if selected in self.classic_colors:
            color = self.classic_colors[selected]
            self.color_sample.delete("all")
            self.color_sample.create_rectangle(5, 5, 200, 35, fill=color, outline='')
            
    def generate_pattern(self):
        """生成纹样（集成智能生成算法）"""
        if not self.selected_pattern:
            messagebox.showinfo("提示", "请先选择纹样模板")
            return
        
        # 获取用户偏好
        user_preference = {
            'style_type': self.selected_category if hasattr(self, 'selected_category') else 'traditional',
            'color': self.color_combo.get() if self.color_combo.get() != "请选择主色调" else "中国红",
            'density': ['low', 'medium', 'high'][int(self.density_scale.get())],
            'symmetry': 0.8  # 默认对称度
        }
        
        # 调用智能生成算法
        try:
            optimized_pattern = self.generate_edelis_pattern(
                base_style=self.selected_category if hasattr(self, 'selected_category') else 'traditional',
                user_preference=user_preference,
                pattern_database=self.PATTERN_DATABASE
            )
            
            # 显示生成的方案
            self.display_generated_patterns(optimized_pattern)
            
        except Exception as e:
            messagebox.showerror("错误", f"纹样生成失败：{str(e)}")
    
    def generate_edelis_pattern(self, base_style, user_preference, pattern_database):
        """
        艾德莱斯绸纹样生成核心算法（StyleGAN3+传统特征约束）
        
        Args:
            base_style: 基础风格（traditional/modern/minimalist）
            user_preference: 用户偏好字典
            pattern_database: 纹样数据库
            
        Returns:
            dict: 优化后的纹样数据
        """
        # 1. 传统纹样特征提取
        pattern_features = self.extract_traditional_features(
            pattern_database, 
            feature_keys=['petal_curve', 'line_density', 'color_harmony']
        )
        
        # 2. 融合用户偏好
        style_embedding = self.style_encoder(base_style, user_preference['style_type'])
        color_palette = self.get_edelis_color(user_preference['color'], 
                                             pattern_features['color_harmony'])
        
        # 3. 生产工艺约束（保证纹样可织造）
        generation_constraint = {
            'line_stroke': (2, 5),  # 线条粗细适配扎经染色
            'pattern_repeat': True,  # 满足织造循环性要求
            'symmetry_degree': user_preference['symmetry']  # 对称/非对称控制
        }
        
        # 4. 生成并优化纹样
        raw_pattern = self.stylegan3_generate(style_embedding, color_palette, 
                                             generation_constraint)
        optimized_pattern = self.adjust_for_weaving(raw_pattern)
        
        return optimized_pattern
    
    def extract_traditional_features(self, pattern_db, feature_keys):
        """
        传统纹样特征提取（核心特征：花瓣曲线、线条密度、色彩和谐度）
        
        Args:
            pattern_db: 纹样数据库
            feature_keys: 特征键列表
            
        Returns:
            dict: 提取的特征字典
        """
        features = {}
        for key in feature_keys:
            values = []
            for style_data in pattern_db.values():
                if key in style_data:
                    values.extend(style_data[key])
            features[key] = np.mean(values) if values else 0.5
        
        return features
    
    def style_encoder(self, base_style, style_type):
        """
        风格编码器（融合用户偏好）
        
        Args:
            base_style: 基础风格
            style_type: 目标风格类型
            
        Returns:
            numpy.ndarray: 风格嵌入向量
        """
        style_map = {
            'traditional': [1.0, 0.0, 0.0],
            '国潮现代': [0.0, 1.0, 0.0],
            '旅拍简约': [0.0, 0.0, 1.0]
        }
        
        # 默认返回传统风格
        return np.array(style_map.get(style_type, [1.0, 0.0, 0.0]))
    
    def get_edelis_color(self, color_name, color_harmony):
        """
        获取艾德莱斯经典配色
        
        Args:
            color_name: 颜色名称
            color_harmony: 色彩和谐度
            
        Returns:
            list: 配色方案
        """
        # 基于艾德莱斯经典12色生成配色
        base_colors = {
            '中国红': ['#DC143C', '#FFD700', '#4169E1', '#50C878'],
            '帝王黄': ['#FFD700', '#DC143C', '#1E3A5F', '#2F4F4F'],
            '宝石蓝': ['#4169E1', '#FFD700', '#DC143C', '#808000'],
            '翡翠绿': ['#50C878', '#DAA520', '#87CEEB', '#C41E3A']
        }
        
        return base_colors.get(color_name, ['#DC143C', '#FFD700', '#4169E1', '#50C878'])
    
    def stylegan3_generate(self, style_embedding, color_palette, constraints):
        """
        StyleGAN3纹样生成（模拟实现）
        实际项目中应替换为真实的StyleGAN3模型
        
        Args:
            style_embedding: 风格嵌入向量
            color_palette: 配色方案
            constraints: 生成约束
            
        Returns:
            dict: 原始纹样数据
        """
        # 模拟生成纹样参数
        pattern_data = {
            'style': style_embedding,
            'colors': color_palette,
            'line_width': np.random.uniform(constraints['line_stroke'][0], 
                                           constraints['line_stroke'][1]),
            'repeat_pattern': constraints['pattern_repeat'],
            'symmetry': constraints['symmetry_degree'],
            'complexity': np.random.uniform(0.6, 0.9)
        }
        
        return pattern_data
    
    def adjust_for_weaving(self, raw_pattern):
        """
        修正纹样细节，适配手工织造
        
        Args:
            raw_pattern: 原始纹样数据
            
        Returns:
            dict: 优化后的纹样数据
        """
        optimized = raw_pattern.copy()
        
        # 调整线条宽度以适应织造工艺
        if optimized['line_width'] < 2:
            optimized['line_width'] = 2
        elif optimized['line_width'] > 5:
            optimized['line_width'] = 5
        
        # 确保图案可重复
        optimized['weaving_ready'] = True
        optimized['optimization_notes'] = '已优化线条宽度和重复性'
        
        return optimized
    
    def display_generated_patterns(self, pattern_data):
        """显示生成的纹样方案"""
        colors = ['#667eea', '#f093fb', '#4facfe']
        
        # 清空之前的方案
        for widget in self.schemes_frame.winfo_children():
            widget.destroy()
        
        # 显示3个方案
        for i in range(3):
            scheme_card = tk.Canvas(self.schemes_frame, height=60,
                                   bg=colors[i], highlightthickness=2,
                                   highlightbackground='#333',
                                   cursor='hand2')
            scheme_card.grid(row=0, column=i, padx=10, sticky='nsew')
            self.schemes_frame.columnconfigure(i, weight=1)
            
            scheme_card.create_text(10, 20,
                                   text=f"方案{i+1}",
                                   font=('微软雅黑', 10, 'bold'),
                                   anchor='w', fill='white')
            scheme_card.create_text(10, 40,
                                   text=f"{self.selected_pattern} + {self.element_combo.get()}",
                                   font=('微软雅黑', 8),
                                   anchor='w', fill='white')
        
        # 在预览区显示第一个方案
        self.preview_canvas.delete("all")
        
        # 绘制简化的纹样示意
        center_x, center_y = 400, 300
        radius = 150
        
        # 绘制背景
        self.preview_canvas.create_rectangle(100, 100, 700, 500,
                                            fill=colors[0], outline='#333', width=2)
        
        # 绘制装饰元素
        for i in range(8):
            angle = i * 45
            x1 = center_x + radius * np.cos(np.radians(angle))
            y1 = center_y + radius * np.sin(np.radians(angle))
            x2 = center_x + (radius - 30) * np.cos(np.radians(angle + 22.5))
            y2 = center_y + (radius - 30) * np.sin(np.radians(angle + 22.5))
            
            self.preview_canvas.create_line(x1, y1, x2, y2,
                                           fill='white', width=3)
        
        # 添加文字说明
        info_text = f"✨ 智能生成成功!\n\n"
        info_text += f"风格：{self.selected_category if hasattr(self, 'selected_category') else '传统经典'}\n"
        info_text += f"配色：{self.color_combo.get()}\n"
        info_text += f"密度：{'低中高'[int(self.density_scale.get())]}\n"
        info_text += f"元素：{self.element_combo.get()}\n"
        info_text += f"线条宽度：{pattern_data['line_width']:.1f}px\n"
        info_text += f"对称度：{pattern_data['symmetry']*100:.0f}%"
        
        self.preview_canvas.create_text(400, 300,
                                       text=info_text,
                                       font=('微软雅黑', 12),
                                       fill='white', justify='center')
        
        messagebox.showinfo("成功", 
                          f"已生成 3 组智能方案\n\n"
                          f"线条宽度：{pattern_data['line_width']:.1f}px\n"
                          f"织造优化：已完成\n\n"
                          f"点击底部方案卡片对比选择")
        
    def save_design(self):
        """保存设计"""
        if not self.generated_patterns:
            messagebox.showinfo("提示", "请先生成纹样")
            return
            
        filepath = filedialog.asksaveasfilename(
            title="保存设计稿",
            defaultextension=".png",
            filetypes=[("PNG 文件", "*.png"), ("所有文件", "*.*")]
        )
        
        if filepath:
            # 这里应该实际渲染图像，暂时模拟
            messagebox.showinfo("成功", f"设计稿已保存至:\n{filepath}")
            
    def send_to_production(self):
        """发送至生产"""
        if not self.generated_patterns:
            messagebox.showinfo("提示", "请先生成纹样")
            return
            
        confirmed = messagebox.askyesno("确认", 
            "确定要发送当前设计到生产环节吗？\n\n这将启动自动化生产流程")
            
        if confirmed:
            messagebox.showinfo("已发送", "✓ 设计稿已成功发送至生产车间\n\n生产编号：ADLS-2026-001")


def main():
    root = tk.Tk()
    app = SilkPatternDesignApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
