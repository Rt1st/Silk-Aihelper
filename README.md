# 艾德莱斯绸智能生产系统

**Adelis Silk AI Production System**

> AI 赋能千年非遗，以计算机视觉与智能算法续写丝绸之路上的艾德莱斯绸传奇。

## 项目简介

艾德莱斯绸智能生产系统是一个面向新疆非遗工艺——艾德莱斯绸织造的智能化辅助平台。系统深度融合机器视觉、色彩科学与人工智能技术，覆盖从**染色配方计算**、**纹样智能生成**到**成品品质检测**的全链路生产环节，帮助传统工匠以数字化手段提升染色精度、创新纹样设计并实现标准化质量管控，推动非遗工艺的现代振兴。

---

## 三大核心功能

| 功能模块 | 说明 |
|---------|------|
| **染色配方智能计算** | 基于 RGB→LAB 色彩空间转换与天然染料数据库匹配，结合线性回归模型和温湿度环境因子修正，自动计算红花、板蓝根、黄刺叶等 8 种本土天然染料的精准配比、浸泡时间和固色时长。 |
| **AI 纹样生成** | 内置传统经典、国潮现代、旅拍简约三大风格，支持 12 种经典艾德莱斯配色。通过风格编码器融合用户偏好与传统工艺约束（线条宽度、对称度、图案重复），生成可织造的纹样方案。提供 3 组方案同时预览对比。 |
| **智能品质检测** | 对成品绸缎进行图像预处理后，检测染色均匀度（颜色方差分析）、纹样对齐度（ORB 特征点 + 角度分析）、三类瑕疵（破洞 / 污渍 / 线头错误），自动判定精品级、合格级、待返工三级标准，并生成唯一溯源码。 |

---

## 技术栈

- **语言**：Python 3.8+
- **GUI 框架**：Tkinter
- **计算机视觉**：OpenCV（图像预处理、ORB 特征检测）
- **图像处理**：Pillow（PIL）
- **数值计算**：NumPy
- **机器学习**：scikit-learn（K-Means 聚类、线性回归）
- **可视化**：Matplotlib
- **Web 界面**：HTML5 + CSS3 + JavaScript（`1.html`）
- **外部 API**：SiliconFlow（Tongyi-MAI/Z-Image-Turbo 纹样生成）、DeepSeek（染色配方 AI 咨询）

---

## 项目结构

```
SILK/
├── system_main.py            # 统一主入口
├── main.py                   # 颜色识别 GUI 模块
├── color_recognizer.py       # 颜色识别 + 染色配方计算 ⭐
├── quality_inspection.py     # 品质检测模块 ⭐
├── pattern_design_u1.py      # 纹样设计/生成模块 ⭐
├── preprocessor.py           # 图像预处理工具
├── test_algorithms.py        # 算法单元测试
├── generate_patterns.py      # 自动生成纹样图案
├── import_patterns.py        # 导入外部纹样
├── modern_ui.py              # 现代化 UI 组件
├── modern_ui_complete.py     # 完整 UI 实现
├── create_sample.py          # 样本数据创建
├── 1.html                    # Web 前端界面
├── requirements.txt          # Python 依赖
├── .gitignore                # Git 忽略规则
├── 算法说明.md               # 详细算法文档
├── 项目交付说明.md           # 项目交付说明
├── 快速参考.md               # 快速参考卡
├── 使用指南.txt              # 使用指南
├── 启动程序.bat              # Windows 一键启动
└── patterns/                 # 纹样模板图片（24 张）
```

---

## 快速开始

### 1. 克隆仓库

```bash
git clone <your-repo-url>
cd SILK
```

### 2. 创建虚拟环境（推荐）

```bash
python -m venv venv
venv\Scripts\activate   # Windows
# source venv/bin/activate  # macOS/Linux
```

### 3. 安装依赖

```bash
pip install -r requirements.txt
```

### 4. 运行系统

```bash
python system_main.py
```

或者双击 `启动程序.bat` 一键启动。

---

## 使用说明

| 入口 | 功能 | 启动方式 |
|------|------|---------|
| `system_main.py` | 统一主菜单，选择进入任意模块 | `python system_main.py` |
| `main.py` | 颜色识别：加载布料图片 → 提取主色 → 生成调色板 | `python main.py` |
| `pattern_design_u1.py` | 纹样设计：选择风格/配色 → 生成纹样 → 三方案对比 | `python pattern_design_u1.py` |
| `quality_inspection.py` | 品质检测：拍照/上传 → 自动检测 → 评级 + 溯源码 | `python quality_inspection.py` |
| `test_algorithms.py` | 运行所有算法的单元测试 | `python test_algorithms.py` |
| `1.html` | Web 版界面：纹样生成 + AI 调色 + 质检（浏览器打开） | 双击文件 |

### 染色配方命令行调用示例

```python
from color_recognizer import DyeFormulaCalculator

calc = DyeFormulaCalculator()
result = calc.calculate_dye_formula(
    target_color_rgb=[220, 20, 60],  # 中国红
    ambient_temp=28,
    ambient_humidity=55
)
print(result['dye_ratio'])   # 染料比例
print(result['soak_time'])   # 浸泡时间（分钟）
print(result['fix_time'])    # 固色时长（分钟）
```

---

## 重要安全提醒

> **`1.html` 中硬编码了 API 密钥，上传 GitHub 前务必处理！**

`1.html` 文件第 396-398 行包含以下明文密钥：

- SiliconFlow API Key（用于纹样生成）
- DeepSeek API Key（用于染色配方咨询）

### 处理建议

1. **立即前往对应平台重置这些已泄露的密钥**（SiliconFlow 控制台 / DeepSeek 控制台）
2. **不要将含密钥的 `1.html` 上传到 GitHub**。推荐方案：
   - 创建 `.env` 文件存储密钥，并在 `1.html` 中通过环境变量 / 后端代理方式获取
   - 将 `.env` 加入 `.gitignore`（本项目已配置）
   - 提供 `1.example.html` 模板文件，密钥位置用占位符标记
3. **如需保留 Web 界面上传**，建议改为后端中转方案：启动一个简单的 Python HTTP 服务，前端通过 `/api/*` 接口调用，密钥仅存于服务端

---

## 许可证

本项目采用 [MIT License](https://opensource.org/licenses/MIT) 开源。

---

## 项目背景

艾德莱斯绸（Atlas / Adelis Silk）是新疆维吾尔自治区国家级非物质文化遗产，以其独特的扎经染色工艺和绚丽多彩的几何纹样闻名于世，被誉为"丝绸之路上的活化石"。

然而，传统艾德莱斯绸生产面临三大挑战：

- **染色依赖经验**：天然染料配比全凭匠人手感，难以标准化复现
- **纹样创新乏力**：传统纹样传承以师徒口授为主，设计周期长、创新空间受限
- **质检效率低下**：成品质量评估依赖肉眼逐匹检验，主观性强且效率低

本项目以 AI 技术为核心驱动力，将计算机视觉、色彩科学与传统工艺深度融合，旨在：

- 降低传统工艺的学习门槛，吸引年轻一代传承人
- 提升染色配方精度与纹样设计效率
- 实现从经验驱动到数据驱动的生产升级
- 以数字化手段助力非遗工艺的活态传承与国际化推广

---

**贡献与反馈**：欢迎通过 Issue / Pull Request 参与项目改进。
