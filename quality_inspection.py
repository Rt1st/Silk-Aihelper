"""
慧眼鉴 - 成品机器视觉质量检测模块
基于 OpenCV 的绸缎成品质量检测系统
包含艾德莱斯绸品质检测算法（YOLOv8+图像分割）
"""
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageTk, ImageDraw
import cv2
import numpy as np
import threading
import uuid
from datetime import datetime


class QualityInspectionApp:
    """慧眼鉴 - 质量检测应用"""
    
    # 标准检测参数
    STANDARD_PARAMS = {
        'max_variance': 500,  # 最大颜色方差
        'keypoint_template': None,  # 特征点模板
        'defect_threshold': 0.1  # 瑕疵阈值
    }
    
    def __init__(self, root):
        self.root = root
        self.root.title("慧眼鉴 - 绸缎成品机器视觉质量检测")
        self.root.geometry("1200x900")
        
        # 初始化变量
        self.image_path = None
        self.camera_active = False
        self.cap = None
        self.detection_results = None
        self.product_grade = None
        self.traceability_code = None
        
        # 设置样式
        self.setup_styles()
        self.create_ui()
        
    def setup_styles(self):
        """设置样式"""
        style = ttk.Style()
        style.configure('Title.TLabel', font=('微软雅黑', 16, 'bold'), foreground='#2c3e50')
        style.configure('Accent.TButton', font=('微软雅黑', 11, 'bold'), padding=10)
        
    def create_ui(self):
        """创建界面 - 三段式布局"""
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        
        # 顶部拍摄区
        top_panel = ttk.LabelFrame(main_frame, text="📷 拍摄区", padding=10)
        top_panel.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        main_frame.columnconfigure(0, weight=1)
        self.create_capture_panel(top_panel)
        
        # 中间检测结果区
        center_panel = ttk.LabelFrame(main_frame, text="🔍 检测结果", padding=10)
        center_panel.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=10)
        main_frame.rowconfigure(1, weight=1)
        self.create_inspection_panel(center_panel)
        
        # 底部分级/溯源区
        bottom_panel = ttk.LabelFrame(main_frame, text="📊 分级/溯源", padding=10)
        bottom_panel.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=(10, 0))
        self.create_traceability_panel(bottom_panel)
        
    def create_capture_panel(self, parent):
        """创建拍摄区"""
        # 摄像头控制区
        control_frame = ttk.Frame(parent)
        control_frame.pack(fill='x', pady=(0, 10))
        
        # 摄像头切换按钮
        self.camera_btn = tk.Button(control_frame, text="📷 切换摄像头",
                                   font=('微软雅黑', 10),
                                   bg='#3498db', fg='white',
                                   relief='flat', cursor='hand2',
                                   command=self.toggle_camera)
        self.camera_btn.pack(side='left', padx=10)
        
        # 拍照按钮
        capture_btn = tk.Button(control_frame, text="📸 拍照",
                               font=('微软雅黑', 10, 'bold'),
                               bg='#e74c3c', fg='white',
                               relief='flat', cursor='hand2',
                               command=self.capture_image)
        capture_btn.pack(side='left', padx=10)
        
        # 上传图片按钮
        upload_btn = tk.Button(control_frame, text="📁 上传图片",
                              font=('微软雅黑', 10),
                              bg='#2ecc71', fg='white',
                              relief='flat', cursor='hand2',
                              command=self.upload_image)
        upload_btn.pack(side='left', padx=10)
        
        # 拍摄指引提示
        guide_label = ttk.Label(control_frame, 
                               text="💡 拍摄指引：将绸缎平整放置，确保光线均匀，摄像头距离 30-50cm",
                               font=('微软雅黑', 9),
                               foreground='#f39c12')
        guide_label.pack(side='right', padx=10)
        
        # 拍摄区域（带指引框）
        self.capture_canvas = tk.Canvas(parent, bg='#ecf0f1', height=300,
                                       highlightthickness=2,
                                       highlightbackground='#bdc3c7')
        self.capture_canvas.pack(fill='both', expand=True)
        
        # 绘制拍摄指引框
        self.draw_capture_guide()
        
    def draw_capture_guide(self):
        """绘制拍摄指引框"""
        self.capture_canvas.delete("all")
        
        # 外框
        self.capture_canvas.create_rectangle(50, 50, 750, 250, 
                                            outline='#95a5a6', width=2, dash=(5, 5))
        
        # 内框（适配绸缎尺寸）
        self.capture_canvas.create_rectangle(100, 80, 700, 220,
                                            outline='#3498db', width=3)
        
        # 四角标记
        corner_size = 20
        corners = [
            (100, 80, 100+corner_size, 80), (100, 80, 100, 80+corner_size),
            (700, 80, 700-corner_size, 80), (700, 80, 700, 80+corner_size),
            (100, 220, 100+corner_size, 220), (100, 220, 100, 220-corner_size),
            (700, 220, 700-corner_size, 220), (700, 220, 700, 220-corner_size)
        ]
        
        for x1, y1, x2, y2 in corners:
            self.capture_canvas.create_line(x1, y1, x2, y2, fill='#e74c3c', width=3)
        
        # 文字提示
        self.capture_canvas.create_text(400, 150,
                                       text="绸缎成品拍摄区域\n建议尺寸：60cm × 140cm",
                                       font=('微软雅黑', 12),
                                       fill='#7f8c8d', justify='center')
        
    def create_inspection_panel(self, parent):
        """创建检测结果区"""
        # 分为左右两部分
        left_frame = ttk.Frame(parent)
        left_frame.pack(side='left', fill='both', expand=True, padx=(0, 5))
        
        right_frame = ttk.Frame(parent)
        right_frame.pack(side='right', fill='both', expand=True, padx=(5, 0))
        
        # 左侧：带标注的图像
        self.inspection_canvas = tk.Canvas(left_frame, bg='white',
                                          highlightthickness=1,
                                          highlightbackground='#ddd')
        self.inspection_canvas.pack(fill='both', expand=True)
        
        # 右侧：检测指标
        metrics_frame = ttk.Frame(right_frame)
        metrics_frame.pack(fill='both', expand=True)
        
        # 指标 1：染色均匀度
        uniformity_frame = self.create_metric_card(metrics_frame, 
                                                  "染色均匀度", "98%", "#2ecc71", 0)
        uniformity_frame.pack(fill='x', pady=10, padx=10)
        
        # 指标 2：纹样对齐度
        alignment_frame = self.create_metric_card(metrics_frame,
                                                 "纹样对齐度", "99%", "#3498db", 1)
        alignment_frame.pack(fill='x', pady=10, padx=10)
        
        # 指标 3：瑕疵数量
        defect_frame = self.create_metric_card(metrics_frame,
                                              "瑕疵数量", "0", "#e74c3c", 2)
        defect_frame.pack(fill='x', pady=10, padx=10)
        
        # 开始检测按钮
        inspect_btn = tk.Button(metrics_frame, text="🔍 开始检测",
                               font=('微软雅黑', 12, 'bold'),
                               bg='#9b59b6', fg='white',
                               relief='flat', padx=20, pady=10,
                               cursor='hand2',
                               command=self.start_inspection)
        inspect_btn.pack(pady=20)
        
    def create_metric_card(self, parent, title, value, color, index):
        """创建指标卡片"""
        frame = ttk.Frame(parent, relief='raised', borderwidth=1)
        
        title_label = ttk.Label(frame, text=title,
                               font=('微软雅黑', 11))
        title_label.pack(pady=(10, 5))
        
        value_label = tk.Label(frame, text=value,
                              font=('微软雅黑', 24, 'bold'),
                              fg=color)
        value_label.pack(pady=(0, 10))
        
        # 进度条
        progress = ttk.Progressbar(frame, orient='horizontal',
                                  length=200, mode='determinate')
        progress.pack(pady=5, padx=20)
        
        if value.replace('%', '').isdigit():
            progress['value'] = int(value.replace('%', ''))
        
        return frame
        
    def create_traceability_panel(self, parent):
        """创建分级/溯源区"""
        # 分级显示
        grade_frame = ttk.Frame(parent)
        grade_frame.pack(side='left', fill='both', expand=True, padx=(0, 10))
        
        grade_title = ttk.Label(grade_frame, text="产品等级",
                               font=('微软雅黑', 12, 'bold'))
        grade_title.pack(pady=5)
        
        self.grade_label = tk.Label(grade_frame, text="待检测",
                                   font=('微软雅黑', 28, 'bold'),
                                   fg='#95a5a6')
        self.grade_label.pack(pady=10)
        
        # 分级说明
        grade_info = ttk.Label(grade_frame,
                              text="A 级≥95 分 | 精品级≥90 分 | B 级≥80 分 | 待返工<80 分",
                              font=('微软雅黑', 9),
                              foreground='#7f8c8d')
        grade_info.pack()
        
        # 溯源信息
        trace_frame = ttk.Frame(parent)
        trace_frame.pack(side='right', fill='both', expand=True, padx=(10, 0))
        
        trace_title = ttk.Label(trace_frame, text="产品溯源",
                               font=('微软雅黑', 12, 'bold'))
        trace_title.pack(pady=5)
        
        # 溯源码显示区
        self.code_canvas = tk.Canvas(trace_frame, bg='white', height=100,
                                    highlightthickness=2,
                                    highlightbackground='#3498db',
                                    cursor='hand2')
        self.code_canvas.pack(pady=10)
        self.code_canvas.bind("<Button-1>", lambda e: self.show_traceability_info())
        
        # 生成溯源码按钮
        generate_btn = tk.Button(trace_frame, text="📝 生成溯源码",
                                font=('微软雅黑', 10),
                                bg='#1abc9c', fg='white',
                                relief='flat', cursor='hand2',
                                command=self.generate_traceability_code)
        generate_btn.pack(pady=5)
        
    def toggle_camera(self):
        """切换摄像头"""
        if not self.camera_active:
            # 尝试打开摄像头
            self.cap = cv2.VideoCapture(0)
            if self.cap.isOpened():
                self.camera_active = True
                self.camera_btn.config(text="📷 使用后置", bg='#e74c3c')
                self.show_camera_feed()
            else:
                messagebox.showwarning("警告", "无法打开摄像头")
        else:
            # 关闭摄像头
            if self.cap:
                self.cap.release()
            self.camera_active = False
            self.camera_btn.config(text="📷 使用前置", bg='#3498db')
            self.draw_capture_guide()
            
    def show_camera_feed(self):
        """显示摄像头画面"""
        if self.camera_active:
            ret, frame = self.cap.read()
            if ret:
                # 调整大小
                frame = cv2.resize(frame, (700, 300))
                # 转换颜色
                rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                # 转换为 PIL 图像
                pil_image = Image.fromarray(rgb_frame)
                # 转换为 PhotoImage
                photo = ImageTk.PhotoImage(image=pil_image)
                
                self.capture_canvas.delete("all")
                self.capture_canvas.create_image(0, 0, image=photo, anchor='nw')
                self.capture_canvas.image = photo
                
                # 继续显示
                self.root.after(10, self.show_camera_feed)
                
    def capture_image(self):
        """拍照"""
        if self.camera_active and self.cap:
            ret, frame = self.cap.read()
            if ret:
                self.image_path = "temp_capture.jpg"
                cv2.imwrite(self.image_path, frame)
                self.show_captured_image(frame)
                messagebox.showinfo("成功", "照片已拍摄")
        else:
            messagebox.showwarning("警告", "请先打开摄像头")
            
    def upload_image(self):
        """上传图片"""
        filetypes = [("图像文件", "*.jpg *.jpeg *.png"), ("所有文件", "*.*")]
        filepath = filedialog.askopenfilename(title="选择绸缎图片", filetypes=filetypes)
        
        if filepath:
            self.image_path = filepath
            try:
                img = cv2.imread(filepath)
                img = cv2.resize(img, (700, 300))
                self.show_captured_image(img)
            except Exception as e:
                messagebox.showerror("错误", f"加载图片失败：{str(e)}")
                
    def show_captured_image(self, image):
        """显示拍摄的图片"""
        rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        pil_image = Image.fromarray(rgb_image)
        photo = ImageTk.PhotoImage(image=pil_image)
        
        self.capture_canvas.delete("all")
        self.capture_canvas.create_image(0, 0, image=photo, anchor='nw')
        self.capture_canvas.image = photo
        
    def start_inspection(self):
        """开始质量检测"""
        if not self.image_path:
            messagebox.showinfo("提示", "请先拍摄或上传图片")
            return
            
        # 禁用按钮
        self.root.update()
        
        # 在后台线程执行检测
        thread = threading.Thread(target=self.run_inspection)
        thread.daemon = True
        thread.start()
        
    def run_inspection(self):
        """执行质量检测"""
        try:
            # 读取图像
            image = cv2.imread(self.image_path)
            if image is None:
                raise ValueError("无法读取图像")
            
            # 运行检测算法
            results = self.inspect_quality(image)
            
            # 在主线程更新 UI
            self.root.after(0, self.display_inspection_results, results)
            
        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("错误", f"检测失败：{str(e)}"))
            
    def inspect_quality(self, image):
        """
        艾德莱斯绸品质检测核心算法（增强版）
        返回检测结果
        """
        # 1. 图像预处理（去噪/增强/透视校正）
        processed_img = self.image_preprocess(image)
        
        # 2. 染色均匀度检测（颜色方差计算）
        color_variance = self.calculate_color_variance(processed_img)
        dye_uniformity = 100 - (color_variance / self.STANDARD_PARAMS['max_variance']) * 100
        dye_uniformity = max(0, min(100, dye_uniformity))
        
        # 3. 纹样对齐度检测（特征点匹配）
        pattern_keypoints = self.detect_pattern_keypoints(processed_img)
        alignment_degree = self.calculate_alignment(pattern_keypoints)
        
        # 4. 瑕疵检测（识别3类核心瑕疵：破洞、污渍、线头错误）
        defects = self.yolov8_detect(processed_img, 
                                     defect_classes=['hole', 'stain', 'thread_error'])
        defect_rate = len(defects) / (processed_img.shape[0] * processed_img.shape[1] / 10000)
        
        # 5. 产品分级判定
        if dye_uniformity >= 95 and alignment_degree >= 98 and defect_rate <= 0.1:
            grade = "精品级"
            grade_color = "#2ecc71"
        elif dye_uniformity >= 90 and alignment_degree >= 95 and defect_rate <= 0.3:
            grade = "合格级"
            grade_color = "#3498db"
        else:
            grade = "待返工"
            grade_color = "#e74c3c"
        
        return {
            'dye_uniformity': round(dye_uniformity, 1),
            'alignment_degree': round(alignment_degree, 1),
            'defect_rate': round(defect_rate, 3),
            'grade': grade,
            'grade_color': grade_color,
            'defect_positions': [defect['bbox'] for defect in defects],
            'defects': defects,
            'defect_count': len(defects),
            'image': image,
            'processed_image': processed_img
        }
    
    def image_preprocess(self, image, operations=None):
        """
        图像预处理（去噪/增强/透视校正，提升检测精度）
        
        Args:
            image: 原始图像
            operations: 处理操作列表
            
        Returns:
            numpy.ndarray: 处理后的图像
        """
        if operations is None:
            operations = ['denoise', 'contrast_enhance', 'perspective_correct']
        
        processed = image.copy()
        
        # 1. 去噪
        if 'denoise' in operations:
            processed = cv2.fastNlMeansDenoisingColored(processed, None, 10, 10, 7, 21)
        
        # 2. 对比度增强
        if 'contrast_enhance' in operations:
            lab = cv2.cvtColor(processed, cv2.COLOR_BGR2LAB)
            l, a, b = cv2.split(lab)
            clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
            cl = clahe.apply(l)
            limg = cv2.merge((cl, a, b))
            processed = cv2.cvtColor(limg, cv2.COLOR_LAB2BGR)
        
        # 3. 透视校正（简化版）
        if 'perspective_correct' in operations:
            gray = cv2.cvtColor(processed, cv2.COLOR_BGR2GRAY)
            edges = cv2.Canny(gray, 50, 150)
            contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            if contours:
                largest_contour = max(contours, key=cv2.contourArea)
                peri = cv2.arcLength(largest_contour, True)
                approx = cv2.approxPolyDP(largest_contour, 0.02 * peri, True)
                
                if len(approx) == 4:
                    pts = approx.reshape(4, 2)
                    rect = self.order_points(pts)
                    (tl, tr, br, bl) = rect
                    
                    widthA = np.linalg.norm(br - bl)
                    widthB = np.linalg.norm(tr - tl)
                    maxWidth = max(int(widthA), int(widthB))
                    
                    heightA = np.linalg.norm(tr - br)
                    heightB = np.linalg.norm(tl - bl)
                    maxHeight = max(int(heightA), int(heightB))
                    
                    dst = np.array([
                        [0, 0],
                        [maxWidth - 1, 0],
                        [maxWidth - 1, maxHeight - 1],
                        [0, maxHeight - 1]
                    ], dtype='float32')
                    
                    M = cv2.getPerspectiveTransform(rect, dst)
                    processed = cv2.warpPerspective(processed, M, (maxWidth, maxHeight))
        
        return processed
    
    def order_points(self, pts):
        """排序四点坐标（左上、右上、右下、左下）"""
        rect = np.zeros((4, 2), dtype='float32')
        s = pts.sum(axis=1)
        rect[0] = pts[np.argmin(s)]
        rect[2] = pts[np.argmax(s)]
        diff = np.diff(pts, axis=1)
        rect[1] = pts[np.argmin(diff)]
        rect[3] = pts[np.argmax(diff)]
        return rect
    
    def calculate_color_variance(self, image):
        """
        计算颜色方差（用于染色均匀度评估）
        
        Args:
            image: 输入图像
            
        Returns:
            float: 颜色方差值
        """
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        saturation = hsv[:, :, 1]
        variance = np.var(saturation)
        return variance
    
    def detect_pattern_keypoints(self, image):
        """
        检测纹样特征点
        
        Args:
            image: 输入图像
            
        Returns:
            list: 特征点列表
        """
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # 使用ORB检测器
        orb = cv2.ORB_create(nfeatures=500)
        keypoints, descriptors = orb.detectAndCompute(gray, None)
        
        if keypoints is None:
            return []
        
        return [{'pt': kp.pt, 'size': kp.size, 'angle': kp.angle} for kp in keypoints]
    
    def calculate_alignment(self, keypoints):
        """
        计算纹样对齐度
        
        Args:
            keypoints: 特征点列表
            
        Returns:
            float: 对齐度百分比
        """
        if not keypoints or len(keypoints) < 10:
            return 90.0
        
        # 提取特征点坐标
        points = np.array([kp['pt'] for kp in keypoints])
        
        # 计算角度分布
        angles = []
        for i in range(len(points) - 1):
            dx = points[i + 1][0] - points[i][0]
            dy = points[i + 1][1] - points[i][1]
            angle = np.arctan2(dy, dx) * 180 / np.pi
            angles.append(abs(angle))
        
        if not angles:
            return 90.0
        
        # 计算角度标准差（越小越对齐）
        angle_std = np.std(angles)
        alignment = max(0, min(100, 100 - angle_std))
        
        return alignment
    
    def yolov8_detect(self, image, defect_classes=None):
        """
        瑕疵检测（模拟YOLOv8功能）
        实际项目中应替换为真实的YOLOv8模型
        
        Args:
            image: 输入图像
            defect_classes: 瑕疵类别列表
            
        Returns:
            list: 检测到的瑕疵列表
        """
        if defect_classes is None:
            defect_classes = ['hole', 'stain', 'thread_error']
        
        defects = []
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # 1. 检测破洞（暗区域）
        if 'hole' in defect_classes:
            _, dark_mask = cv2.threshold(gray, 30, 255, cv2.THRESH_BINARY_INV)
            contours, _ = cv2.findContours(dark_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            for contour in contours:
                area = cv2.contourArea(contour)
                if 200 < area < 10000:
                    x, y, w, h = cv2.boundingRect(contour)
                    defects.append({
                        'type': 'hole',
                        'bbox': (x, y, w, h),
                        'confidence': 0.85
                    })
        
        # 2. 检测污渍（颜色异常区域）
        if 'stain' in defect_classes:
            lower_defect = np.array([0, 50, 50])
            upper_defect = np.array([10, 255, 200])
            mask = cv2.inRange(hsv, lower_defect, upper_defect)
            
            contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            for contour in contours:
                area = cv2.contourArea(contour)
                if 100 < area < 5000:
                    x, y, w, h = cv2.boundingRect(contour)
                    defects.append({
                        'type': 'stain',
                        'bbox': (x, y, w, h),
                        'confidence': 0.78
                    })
        
        # 3. 检测线头错误（边缘异常）
        if 'thread_error' in defect_classes:
            edges = cv2.Canny(gray, 50, 150)
            lines = cv2.HoughLinesP(edges, 1, np.pi/180, threshold=50,
                                   minLineLength=30, maxLineGap=10)
            
            if lines is not None:
                for line in lines:
                    x1, y1, x2, y2 = line[0]
                    length = np.sqrt((x2-x1)**2 + (y2-y1)**2)
                    if length > 100:  # 异常长线
                        defects.append({
                            'type': 'thread_error',
                            'bbox': (min(x1,x2), min(y1,y2), abs(x2-x1), abs(y2-y1)),
                            'confidence': 0.72
                        })
        
        return defects
        
    def display_inspection_results(self, results):
        """显示检测结果"""
        self.detection_results = results
        
        # 1. 显示带标注的图像
        self.show_annotated_image(results['image'], results['defects'])
        
        # 2. 更新指标（使用新算法的结果）
        self.update_metrics_enhanced(
            results['dye_uniformity'], 
            results['alignment_degree'],
            results['defect_count'],
            results['defect_rate']
        )
        
        # 3. 更新等级
        self.grade_label.config(text=results['grade'],
                               fg=results['grade_color'])
        
        messagebox.showinfo("检测完成", 
                          f"检测结果：{results['grade']}\n"
                          f"染色均匀度：{results['dye_uniformity']}%\n"
                          f"纹样对齐度：{results['alignment_degree']}%\n"
                          f"瑕疵率：{results['defect_rate']}每万像素\n"
                          f"瑕疵数量：{results['defect_count']}")
        
    def show_annotated_image(self, image, defects):
        """显示带标注的图像"""
        # 在图像上标注瑕疵
        annotated = image.copy()
        
        for (x, y, w, h, defect_type) in defects:
            # 画红色矩形框
            cv2.rectangle(annotated, (x, y), (x + w, y + h),
                         (0, 0, 255), 2)
            
            # 添加文字标签
            cv2.putText(annotated, defect_type, (x, y - 10),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
        
        # 调整大小并显示
        annotated = cv2.resize(annotated, (600, 400))
        rgb_image = cv2.cvtColor(annotated, cv2.COLOR_BGR2RGB)
        pil_image = Image.fromarray(rgb_image)
        photo = ImageTk.PhotoImage(image=pil_image)
        
        self.inspection_canvas.delete("all")
        self.inspection_canvas.create_image(0, 0, image=photo, anchor='nw')
        self.inspection_canvas.image = photo
        
    def update_metrics_enhanced(self, uniformity, alignment, defect_count, defect_rate):
        """更新指标显示（增强版）"""
        print(f"=== 艾德莱斯绸品质检测报告 ===")
        print(f"染色均匀度：{uniformity}%")
        print(f"纹样对齐度：{alignment}%")
        print(f"瑕疵率：{defect_rate}每万像素")
        print(f"瑕疵数量：{defect_count}")
        print(f"================================")
    
    def check_color_uniformity(self, hsv):
        """检查染色均匀度（保留旧方法用于兼容）"""
        saturation = hsv[:, :, 1]
        std_dev = np.std(saturation)
        uniformity = max(0, min(100, 100 - std_dev / 2))
        return round(uniformity, 1)
        
    def check_pattern_alignment(self, image):
        """检查纹样对齐度（保留旧方法用于兼容）"""
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        edges = cv2.Canny(gray, 50, 150)
        lines = cv2.HoughLinesP(edges, 1, np.pi/180, threshold=100,
                               minLineLength=100, maxLineGap=10)
        
        if lines is not None:
            angles = []
            for line in lines:
                x1, y1, x2, y2 = line[0]
                angle = np.abs(np.arctan2(y2 - y1, x2 - x1) * 180 / np.pi)
                if angle > 45:
                    angles.append(angle)
            
            if len(angles) > 0:
                angle_std = np.std(angles)
                alignment = max(0, min(100, 100 - angle_std))
                return round(alignment, 1)
        
        return 95.0
        
    def detect_defects(self, image, hsv):
        """检测瑕疵（保留旧方法用于兼容）"""
        defects = []
        lower_defect = np.array([0, 50, 50])
        upper_defect = np.array([10, 255, 200])
        mask = cv2.inRange(hsv, lower_defect, upper_defect)
        
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL,
                                      cv2.CHAIN_APPROX_SIMPLE)
        
        defect_count = 0
        for contour in contours:
            area = cv2.contourArea(contour)
            if 100 < area < 5000:
                x, y, w, h = cv2.boundingRect(contour)
                defects.append((x, y, w, h, '色差点'))
                defect_count += 1
        
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        _, dark_mask = cv2.threshold(gray, 30, 255, cv2.THRESH_BINARY_INV)
        
        contours, _ = cv2.findContours(dark_mask, cv2.RETR_EXTERNAL,
                                      cv2.CHAIN_APPROX_SIMPLE)
        
        for contour in contours:
            area = cv2.contourArea(contour)
            if 200 < area < 10000:
                x, y, w, h = cv2.boundingRect(contour)
                defects.append((x, y, w, h, '破损'))
                defect_count += 1
        
        return defects, defect_count
        
    def generate_traceability_code(self):
        """生成溯源码"""
        if not self.detection_results:
            messagebox.showinfo("提示", "请先完成质量检测")
            return
            
        # 生成唯一溯源码
        self.traceability_code = f"ADLS-{datetime.now().strftime('%Y%m%d')}-{uuid.uuid4().hex[:8].upper()}"
        
        # 显示溯源码
        self.code_canvas.delete("all")
        self.code_canvas.create_text(200, 50,
                                    text=self.traceability_code,
                                    font=('Courier', 16, 'bold'),
                                    fill='#2c3e50')
        self.code_canvas.create_text(200, 80,
                                    text="点击查看详情",
                                    font=('微软雅黑', 9),
                                    fill='#7f8c8d')
        
        messagebox.showinfo("成功", f"溯源码已生成：{self.traceability_code}")
        
    def show_traceability_info(self):
        """显示溯源信息"""
        if not self.traceability_code:
            messagebox.showinfo("提示", "请先生成溯源码")
            return
            
        # 模拟溯源信息
        info = f"""
╔═══════════════════════════════════════╗
║        产品溯源信息                   ║
╠═══════════════════════════════════════╣
║ 溯源码：{self.traceability_code}
║
║ 织造匠人：艾合买提·玉素甫
║ 生产时间：2026-03-31 14:30
║ 染色配方：
║   • 中国红 (DC143C) - 35%
║   • 帝王黄 (FFD700) - 28%
║   • 宝石蓝 (4169E1) - 22%
║   • 翡翠绿 (50C878) - 15%
║
║ 质检等级：{self.detection_results['grade']}
╚═══════════════════════════════════════╝
        """
        
        messagebox.showinfo("溯源信息", info)


def main():
    root = tk.Tk()
    app = QualityInspectionApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
