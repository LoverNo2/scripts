# seer_auto —— 赛尔号可视化自动键鼠操作研究框架

基于 Python 的屏幕自动化研究项目，通过「视觉反馈」驱动鼠标操作，实现赛尔号的自动化玩法研究（点击按钮、战斗、刷精灵等）。

## 两种点击模式

| 模式 | 说明 | 核心函数 |
| ---- | ---- | -------- |
| 模式一：固定位置点击 | 直接点击屏幕上的固定坐标，适合布局不变的界面 | `click_position(x, y)` |
| 模式二：图标检测点击 | 实时截屏，用 OpenCV 模板匹配找到图标后点击其中心，适合图标位置会变的界面 | `find_and_click("bag.png")` |

## 目录结构

```
seer_auto/
├── main.py               # 入口（点击一次固定位置）
├── requirements.txt      # 依赖
├── core/                 # 核心功能（两种点击模式）
│   ├── __init__.py       # 统一导出
│   ├── clicker.py        # 模式一：固定位置点击（pyautogui）
│   ├── screen.py         # 屏幕截图（mss，缺失时回退 pyautogui）
│   └── matcher.py        # 模式二：图标检测（OpenCV 模板匹配）
├── config/               # 命名映射表
│   ├── positions.py      # pos_xxx 坐标映射
│   └── images.py         # img_xxx 图片映射
└── assets/               # 图片资源（图标模板 .png）
```

## 命名映射（推荐用法）

把常用位置和图标命名后集中管理，脚本里按名字引用，改坐标/换图标时只需改一处：

```python
# config/positions.py —— 坐标映射
pos_bag = (1, 1)          # 背包按钮坐标

# config/images.py —— 图片映射（文件名相对 assets/ 目录）
img_bag = "bag.png"       # 背包图标
```

```python
from core import click_position, find_and_click
from config.positions import pos_bag
from config.images import img_bag

click_position(*pos_bag)   # 模式一：点击背包坐标，等价于 click_position(1, 1)
find_and_click(img_bag)    # 模式二：检测背包图标并点击
```

### 图片检测阶段的时间配置

`find_and_click` 的检测阶段耗时由两个参数控制（均为秒）：

```python
find_and_click(img_bag, timeout=3.0, interval=0.5)
# timeout:  检测阶段总时间预算，超时未找到即放弃（默认 2 秒；0 = 只检测一次）
# interval: 每轮截图匹配之间的间隔（默认 0.5 秒，应对画面加载延迟）

find_and_click(img_bag, timeout=0)   # 立即检测一次，找不到就返回，不等待
```

## 安装

```bash
cd seer_auto
pip install -r requirements.txt
```

> macOS 注意：首次运行需在「系统设置 → 隐私与安全性 → 辅助功能」中授权当前终端，否则 pyautogui 无法控制鼠标；图标检测还需要「屏幕录制」权限。

## 使用流程

1. **准备坐标**：运行 `python3 main.py` 前，把真实坐标填进 `config/positions.py`。
2. **准备图标**：截屏裁剪目标图标，保存到 `assets/` 目录（如 `assets/bag.png`），然后在 `config/images.py` 中登记名字。
3. **运行**：`python3 main.py`（点击 `pos_click` 指向的坐标一次）。

## 安全提示

- 脚本默认开启 pyautogui 的 FailSafe：操作过程中把鼠标快速甩到屏幕左上角可紧急终止。
- 模板匹配阈值建议在 0.8~0.9 之间调试：过低会误点，过高会漏点。
- 图标模板必须与游戏内实际显示一致（尺寸、颜色），不同分辨率下需重新裁剪。
