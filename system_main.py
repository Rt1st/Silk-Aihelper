"""
艾德莱斯绸智能生产系统 - 主入口
集成三大核心算法：染色配方计算、品质检测、纹样生成
"""
import tkinter as tk
from tkinter import ttk, messagebox
import sys


class MainApplication:
    """主应用程序"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("艾德莱斯绸智能生产系统")
        self.root.geometry("800x600")
        
        # 设置样式
        style = ttk.Style()
        style.configure('Title.TLabel', font=('微软雅黑', 20, 'bold'), foreground='#2c3e50')
        style.configure('Subtitle.TLabel', font=('微软雅黑', 12), foreground='#7f8c8d')
        style.configure('Card.TFrame', background='white', relief='raised', borderwidth=2)
        
        self.create_main_ui()
    
    def create_main_ui(self):
        """创建主界面"""
        main_frame = ttk.Frame(self.root, padding="40")
        main_frame.pack(fill='both', expand=True)
        
        # 标题
        title_label = ttk.Label(main_frame, text="🧵 艾德莱斯绸智能生产系统", 
                               style='Title.TLabel')
        title_label.pack(pady=(0, 10))
        
        subtitle_label = ttk.Label(main_frame, 
                                  text="集成AI算法 · 智能染色 · 品质检测 · 纹样设计",
                                  style='Subtitle.TLabel')
        subtitle_label.pack(pady=(0, 40))
        
        # 三个核心功能卡片
        card_frame = ttk.Frame(main_frame)
        card_frame.pack(fill='both', expand=True, pady=20)
        
        # 卡片1: 染色配方计算
        card1 = self.create_function_card(
            card_frame, 
            "🎨 染色配方智能计算",
            "基于色彩回归+环境因子修正\n• RGB转LAB精准匹配\n• 天然染料数据库\n• 温湿度自动补偿",
            "#e74c3c",
            self.open_dye_calculator
        )
        card1.grid(row=0, column=0, padx=20, sticky='nsew')
        
        # 卡片2: 品质检测
        card2 = self.create_function_card(
            card_frame,
            "🔍 成品品质检测",
            "YOLOv8+图像分割技术\n• 染色均匀度分析\n• 纹样对齐度检测\n• 瑕疵自动识别",
            "#3498db",
            self.open_quality_inspection
        )
        card2.grid(row=0, column=1, padx=20, sticky='nsew')
        
        # 卡片3: 纹样生成
        card3 = self.create_function_card(
            card_frame,
            "✨ AI纹样设计",
            "StyleGAN3+传统特征约束\n• 智能风格融合\n• 工艺适配优化\n• 一键生成方案",
            "#9b59b6",
            self.open_pattern_design
        )
        card3.grid(row=0, column=2, padx=20, sticky='nsew')
        
        card_frame.columnconfigure(0, weight=1)
        card_frame.columnconfigure(1, weight=1)
        card_frame.columnconfigure(2, weight=1)
        
        # 底部信息
        info_label = ttk.Label(main_frame,
                              text="💡 点击任意功能卡片启动对应模块 | 所有算法已集成完毕",
                              font=('微软雅黑', 9),
                              foreground='#95a5a6')
        info_label.pack(pady=(20, 0))
    
    def create_function_card(self, parent, title, description, color, command):
        """创建功能卡片"""
        card = tk.Frame(parent, bg=color, cursor='hand2', relief='raised', bd=3)
        card.bind("<Button-1>", lambda e: command())
        
        # 标题
        title_label = tk.Label(card, text=title,
                              font=('微软雅黑', 14, 'bold'),
                              fg='white', bg=color)
        title_label.pack(pady=(20, 10), padx=20)
        
        # 描述
        desc_label = tk.Label(card, text=description,
                             font=('微软雅黑', 10),
                             fg='white', bg=color,
                             justify='left')
        desc_label.pack(pady=(0, 20), padx=20)
        
        # 按钮
        btn = tk.Button(card, text="启动功能 →",
                       font=('微软雅黑', 11, 'bold'),
                       bg='white', fg=color,
                       relief='flat', padx=20, pady=8,
                       cursor='hand2',
                       command=command)
        btn.pack(pady=(0, 20))
        
        return card
    
    def open_dye_calculator(self):
        """打开染色配方计算器"""
        try:
            from color_recognizer import DyeFormulaCalculator
            
            # 创建简单演示窗口
            demo_window = tk.Toplevel(self.root)
            demo_window.title("染色配方智能计算 - 演示")
            demo_window.geometry("600x500")
            
            frame = ttk.Frame(demo_window, padding="20")
            frame.pack(fill='both', expand=True)
            
            ttk.Label(frame, text="🎨 染色配方计算器",
                     font=('微软雅黑', 16, 'bold')).pack(pady=10)
            
            # 输入区
            input_frame = ttk.LabelFrame(frame, text="参数设置", padding=15)
            input_frame.pack(fill='x', pady=10)
            
            ttk.Label(input_frame, text="目标颜色 (R, G, B):").grid(row=0, column=0, sticky='w', pady=5)
            r_var = tk.StringVar(value="220")
            g_var = tk.StringVar(value="20")
            b_var = tk.StringVar(value="60")
            
            entry_frame = ttk.Frame(input_frame)
            entry_frame.grid(row=0, column=1, sticky='w', padx=10)
            
            ttk.Entry(entry_frame, textvariable=r_var, width=6).pack(side='left', padx=2)
            ttk.Label(entry_frame, text=",").pack(side='left')
            ttk.Entry(entry_frame, textvariable=g_var, width=6).pack(side='left', padx=2)
            ttk.Label(entry_frame, text=",").pack(side='left')
            ttk.Entry(entry_frame, textvariable=b_var, width=6).pack(side='left', padx=2)
            
            ttk.Label(input_frame, text="环境温度 (℃):").grid(row=1, column=0, sticky='w', pady=5)
            temp_var = tk.StringVar(value="25")
            ttk.Entry(input_frame, textvariable=temp_var, width=10).grid(row=1, column=1, sticky='w', padx=10)
            
            ttk.Label(input_frame, text="环境湿度 (%):").grid(row=2, column=0, sticky='w', pady=5)
            hum_var = tk.StringVar(value="60")
            ttk.Entry(input_frame, textvariable=hum_var, width=10).grid(row=2, column=1, sticky='w', padx=10)
            
            # 结果区
            result_text = tk.Text(frame, height=15, font=('Courier', 10), bg='#f8f9fa')
            result_text.pack(fill='both', expand=True, pady=10)
            
            def calculate():
                try:
                    r = int(r_var.get())
                    g = int(g_var.get())
                    b = int(b_var.get())
                    temp = float(temp_var.get())
                    hum = float(hum_var.get())
                    
                    calculator = DyeFormulaCalculator()
                    result = calculator.calculate_dye_formula([r, g, b], temp, hum)
                    
                    result_text.delete(1.0, tk.END)
                    
                    if 'error' in result:
                        result_text.insert(tk.END, f"❌ 错误: {result['error']}\n")
                    else:
                        result_text.insert(tk.END, "✅ 染色配方计算结果\n")
                        result_text.insert(tk.END, "=" * 50 + "\n\n")
                        
                        result_text.insert(tk.END, f"目标颜色: RGB({r}, {g}, {b})\n")
                        result_text.insert(tk.END, f"LAB值: {result['target_color']['lab']}\n\n")
                        
                        result_text.insert(tk.END, "染料配比:\n")
                        for dye, ratio in result['dye_ratio'].items():
                            result_text.insert(tk.END, f"  • {dye}: {ratio:.3f}\n")
                        
                        result_text.insert(tk.END, f"\n浸泡时间: {result['soak_time']}分钟")
                        result_text.insert(tk.END, f"\n固色时长: {result['fix_time']}分钟\n")
                        
                        result_text.insert(tk.END, f"\n环境条件:\n")
                        result_text.insert(tk.END, f"  温度: {temp}℃ (修正因子: {result['environmental_conditions']['temp_correction_factor']})\n")
                        result_text.insert(tk.END, f"  湿度: {hum}% (修正因子: {result['environmental_conditions']['humidity_correction_factor']})\n")
                        
                except Exception as e:
                    result_text.delete(1.0, tk.END)
                    result_text.insert(tk.END, f"❌ 计算错误: {str(e)}")
            
            calc_btn = tk.Button(frame, text="🔬 计算配方",
                                font=('微软雅黑', 12, 'bold'),
                                bg='#e74c3c', fg='white',
                                relief='flat', padx=30, pady=10,
                                cursor='hand2',
                                command=calculate)
            calc_btn.pack(pady=10)
            
        except Exception as e:
            messagebox.showerror("错误", f"无法启动染色配方计算器: {str(e)}")
    
    def open_quality_inspection(self):
        """打开品质检测模块"""
        try:
            from quality_inspection import QualityInspectionApp
            
            # 创建新窗口
            inspection_window = tk.Toplevel(self.root)
            app = QualityInspectionApp(inspection_window)
            
        except Exception as e:
            messagebox.showerror("错误", f"无法启动品质检测模块: {str(e)}")
    
    def open_pattern_design(self):
        """打开纹样设计模块"""
        try:
            from pattern_design_u1 import SilkPatternDesignApp
            
            # 创建新窗口
            design_window = tk.Toplevel(self.root)
            app = SilkPatternDesignApp(design_window)
            
        except Exception as e:
            messagebox.showerror("错误", f"无法启动纹样设计模块: {str(e)}")


def main():
    """主函数"""
    root = tk.Tk()
    app = MainApplication(root)
    root.mainloop()


if __name__ == "__main__":
    main()
