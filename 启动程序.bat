@echo off
chcp 65001 >nul
echo ════════════════════════════════════════════════════
echo    艾德莱斯绸智能生产系统 - 启动程序
echo ════════════════════════════════════════════════════
echo.
echo [1/3] 检查依赖...
python -c "import cv2, numpy, PIL, sklearn" 2>nul
if errorlevel 1 (
    echo [!] 正在安装依赖包...
    pip install opencv-python numpy Pillow scikit-learn matplotlib --quiet
) else (
    echo [✓] 依赖已安装
)
echo.
echo [2/3] 运行算法测试...
python test_algorithms.py
echo.
echo [3/3] 启动主程序...
echo 提示：可选择染色配方、品质检测或纹样设计功能
echo.
pause
python system_main.py
