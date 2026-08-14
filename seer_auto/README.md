# seer_auto —— 赛尔号可视化自动键鼠操作研究框架

基于 Python 的屏幕自动化研究项目，通过「视觉反馈」驱动鼠标操作，实现赛尔号的自动化玩法研究（点击按钮、战斗、刷精灵等）。

## 架构分层

```
seer_auto/
├── main.py               # 入口：只调用顶层应用方法
├── requirements.txt      # 依赖
├── core/                 # 基础设施层（无业务逻辑，只依赖 config）
│   ├── screen.py         # 屏幕捕获与图像处理原语：grab_screen / to_bgr 等
│   ├── mouse.py          # 鼠标操作与视口换算：click_position / move_to 等
│   ├── vision.py         # 模板匹配：load_template / find_template 等
│   └── actions.py        # 组合动作：供 main / battle 直接使用的完整操作
├── battle/               # 业务层（编排 + 平行子动作）
│   ├── battle.py         # 战斗编排：进入 / 防疲劳 / 战斗循环 / 被传送回位
│   ├── ops.py            # 子动作：逃跑 / 治疗 / 胜负结算
│   └── plane_nav.py      # 子动作：星球导航
├── config/               # 配置层（全部命名映射与常量）
│   ├── view.py           # 游戏视口配置（原 env.py）
│   ├── targets.py        # 精灵目标配置（原 targets.py）
│   ├── positions.py      # pos_xxx 坐标映射
│   ├── images.py         # img_xxx 图片映射
│   └── plane.py          # 星图配置
└── assets/               # 图片资源，按领域分类（battle/ pets/ avatars/ planets/）
```

| 层 | 文件 | 内容 |
| -- | ---- | ---- |
| 组合动作 | `core/actions.py` | `click_pos` / `click_img` / `click_all_img` / `wait_img` / `detect` |
| 底层原语 | `core/screen.py` `core/mouse.py` `core/vision.py` | `grab_screen` / `click_position` / `find_template` 等 |

依赖方向：`main → battle → core → config`，禁止反向引用。

## 顶层方法（main 中直接使用）

| 方法 | 作用 | 示例 |
| ---- | ---- | ---- |
| `click_pos(pos)` | 模式一：点击固定位置，可传元组或 x,y | `click_pos(pos_skill_1)` |
| `click_img(img)` | 模式二：检测图标并点击一次，检测时间可配置 | `click_img(img_battle_start, timeout=3.0, interval=0.5)` |
| `click_all_img(img)` | 检测并点击屏幕上所有匹配图标 | `click_all_img(img_battle_start)` |
| `wait_img(img)` | 等待图标出现，返回坐标（不点击） | `wait_img(img_battle_start)` |
| `detect(img)` | 等待图标出现，返回是否出现（带日志） | `detect(img_tire, timeout=2)` |

## 命名映射（推荐用法）

把常用位置和图标命名后集中管理，脚本里按名字引用，改坐标/换图标时只需改一处：

```python
# config/positions.py —— 坐标映射
pos_skill_1 = (900, 875)      # 技能1按钮坐标

# config/images.py —— 图片映射（文件名相对 assets/ 目录）
img_battle_start = "battle/battle_start.png"   # 战斗开始图标
```

```python
from core.actions import click_pos, click_img
from config.positions import pos_skill_1
from config.images import img_battle_start

click_pos(pos_skill_1)          # 模式一：点击技能1坐标，等价于 click_pos(900, 875)
click_img(img_battle_start)     # 模式二：检测战斗开始图标并点击
```

### 图片检测阶段的时间配置

`click_img` 只接收三个参数：图片映射名（必填）、最大检测时间、单次检测失败后的等待时间：

```python
click_img(img_battle_start)                       # 默认:最多检测 10 秒,失败后等 0.5 秒重试
click_img(img_battle_start, timeout=3.0)          # 最多检测 3 秒
click_img(img_battle_start, timeout=0)            # 立即检测一次,找不到就返回
click_img(img_battle_start, timeout=3.0, interval=1.0)   # 失败后等 1 秒再检测
```

匹配阈值：`click_img` 默认 0.9，`detect` / `wait_img` 默认 0.85，均可通过 `threshold` 参数调整。检测到图标后点击一次并返回。

图标识别在 1440 基准分辨率上进行：窗口宽度变化时（见 `config/view.py` 的 `view_width`），脚本先把截图缩小回 1440 基准再与原始模板匹配，模板无需为不同窗口宽度重新裁剪。

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
- `click_img` 默认匹配阈值 0.9；若经常匹配不到，运行 `python debug_match.py` 查看每个模板的实际匹配分数，再决定调整模板或阈值。
- 图标模板基于 1440 宽视口裁剪；窗口宽度变化时脚本自动在基准分辨率匹配，无需为不同分辨率重新裁剪。
