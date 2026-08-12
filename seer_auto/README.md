# seer_auto —— 赛尔号可视化自动键鼠操作研究框架

基于 Python 的屏幕自动化研究项目，通过「视觉反馈」驱动鼠标操作，实现赛尔号的自动化玩法研究（点击按钮、战斗、刷精灵等）。

## 架构分层

```
seer_auto/
├── main.py               # 入口：只调用顶层应用方法
├── requirements.txt      # 依赖
├── core/                 # 分层核心包
│   ├── base.py           # 底层实现：截图 / 鼠标原语 / 单帧模板匹配
│   └── actions.py        # 顶层应用方法：供 main 直接使用的完整动作
├── config/               # 命名映射表
│   ├── positions.py      # pos_xxx 坐标映射
│   └── images.py         # img_xxx 图片映射
└── assets/               # 图片资源（图标模板 .png）
```

| 层 | 文件 | 内容 |
| -- | ---- | ---- |
| 顶层应用方法 | `core/actions.py` | `click_pos` / `click_img` / `click_all_img` / `wait_img` |
| 底层实现 | `core/base.py` | `grab_screen` / `click_position` / `find_template` 等原语 |

## 顶层方法（main 中直接使用）

| 方法 | 作用 | 示例 |
| ---- | ---- | ---- |
| `click_pos(pos)` | 模式一：点击固定位置，可传元组或 x,y | `click_pos(pos_bag)` |
| `click_img(img)` | 模式二：检测图标并点击一次，检测时间可配置 | `click_img(img_bag, timeout=3.0, interval=0.5)` |
| `click_all_img(img)` | 检测并点击屏幕上所有匹配图标 | `click_all_img(img_battle)` |
| `wait_img(img)` | 等待图标出现后点击一次 | `wait_img(img_bag)` |

## 命名映射（推荐用法）

把常用位置和图标命名后集中管理，脚本里按名字引用，改坐标/换图标时只需改一处：

```python
# config/positions.py —— 坐标映射
pos_bag = (1, 1)          # 背包按钮坐标

# config/images.py —— 图片映射（文件名相对 assets/ 目录）
img_bag = "bag.png"       # 背包图标
```

```python
from core.actions import click_pos, click_img
from config.positions import pos_bag
from config.images import img_bag

click_pos(pos_bag)   # 模式一：点击背包坐标，等价于 click_pos(1, 1)
click_img(img_bag)   # 模式二：检测背包图标并点击
```

### 图片检测阶段的时间配置

`click_img` 只接收三个参数：图片映射名（必填）、最大检测时间、单次检测失败后的等待时间：

```python
click_img(img_bag)                       # 默认:最多检测 10 秒,失败后等 0.5 秒重试
click_img(img_bag, timeout=3.0)          # 最多检测 3 秒
click_img(img_bag, timeout=0)            # 立即检测一次,找不到就返回
click_img(img_bag, timeout=3.0, interval=1.0)   # 失败后等 1 秒再检测
```

匹配阈值内部固定为 0.85，检测到图标后点击一次并返回。

## 安装

```bash
cd seer_auto
pip install -r requirements.txt
```

> macOS 注意：首次运行需在「系统设置 → 隐私与安全性 → 辅助功能」中授权当前终端，否则 pyautogui 无法控制鼠标；图标检测还需要「屏幕录制」权限。

## 使用流程

1. **准备坐标**：把真实坐标填进 `config/positions.py`。
2. **准备图标**：截屏裁剪目标图标，保存到 `assets/` 目录（如 `assets/bag.png`），然后在 `config/images.py` 中登记名字。
3. **编写动作**：在 `main.py` 中用顶层方法组合你的流程。
4. **运行**：`python3 main.py`。

## 安全提示

- 脚本默认开启 pyautogui 的 FailSafe：操作过程中把鼠标快速甩到屏幕左上角可紧急终止。
- `click_img` 匹配阈值固定为 0.85；若经常匹配不到，重新裁剪更清晰的图标模板。
- 图标模板必须与游戏内实际显示一致（尺寸、颜色），不同分辨率下需重新裁剪。
