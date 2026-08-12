"""图标检测与点击模块 —— 模式二：在屏幕中检测图标并点击。

实现方式：OpenCV 模板匹配（cv2.matchTemplate + TM_CCOEFF_NORMED），
将截图与预存的图标小图（assets/ 目录）比对，找到匹配位置后点击图标中心。

使用前需要先用截图工具把目标图标裁剪保存到 assets/ 目录，
例如 assets/bag.png。
"""

from pathlib import Path

import cv2
import numpy as np

from core.clicker import click_position
from core.screen import grab_screen

# 项目根目录（core/ 的上一级）
PROJECT_ROOT = Path(__file__).resolve().parent.parent
TEMPLATES_DIR = PROJECT_ROOT / "assets"


def load_template(template_path):
    """读取图标模板图片，返回 BGR 格式 numpy 数组（统一为 3 通道 uint8）。

    带 alpha 透明通道的 PNG 会被 cv2.imread 读成 4 通道（BGRA），
    与 3 通道的屏幕截图不匹配会导致 matchTemplate 报错，这里统一转回 3 通道。
    """
    path = Path(template_path)
    if not path.is_absolute():
        path = TEMPLATES_DIR / path
    img = cv2.imread(str(path))
    if img is None:
        raise FileNotFoundError(f"无法读取图标模板: {path}")
    if img.ndim == 3 and img.shape[2] == 4:
        img = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
    return img


def find_template(screen, template, threshold=0.85):
    """在屏幕帧中查找图标模板，返回 (中心坐标 (x, y), 匹配分数)。

    分数 >= threshold 视为匹配成功；未找到时返回 (None, 分数)。
    """
    # matchTemplate 要求连续内存的多通道数组，非连续时转为连续
    if not screen.flags["C_CONTIGUOUS"]:
        screen = np.ascontiguousarray(screen)
    if not template.flags["C_CONTIGUOUS"]:
        template = np.ascontiguousarray(template)
    result = cv2.matchTemplate(screen, template, cv2.TM_CCOEFF_NORMED)
    _min_val, max_val, _min_loc, max_loc = cv2.minMaxLoc(result)
    if max_val >= threshold:
        h, w = template.shape[:2]
        center_x = max_loc[0] + w // 2
        center_y = max_loc[1] + h // 2
        return (center_x, center_y), max_val
    return None, max_val


def find_all_templates(screen, template, threshold=0.85, max_matches=5, min_distance=20):
    """查找图标的所有匹配位置（用于屏幕上出现多个相同图标时）。

    通过逐次遮盖已匹配区域来避免重复匹配同一位置。

    Returns:
        [(中心坐标, 分数), ...] 按匹配分数从高到低排序
    """
    h, w = template.shape[:2]
    work = screen.copy()
    matches = []
    for _ in range(max_matches):
        loc, score = find_template(work, template, threshold)
        if loc is None:
            break
        matches.append((loc, score))
        # 将已匹配区域涂黑，继续找下一个
        x, y = loc[0] - w // 2, loc[1] - h // 2
        pad = max(min_distance, 1)
        y0, y1 = max(0, y - pad), min(work.shape[0], y + h + pad)
        x0, x1 = max(0, x - pad), min(work.shape[1], x + w + pad)
        work[y0:y1, x0:x1] = 0
    return matches


def find_and_click(template, threshold=0.85, region=None, timeout=2.0, interval=0.5):
    """【模式二】在屏幕中检测图标并点击其中心。

    图片检测阶段的时间可配置：timeout 为总时间预算，到点未找到即放弃；
    interval 为每轮截图匹配之间的间隔。

    Args:
        template: 模板文件名（相对 assets/ 目录）或绝对路径
        threshold: 匹配阈值 0~1，越高要求越严格（建议 0.8~0.9）
        region: 可选搜索区域 (left, top, width, height)，缩小范围可提速
        timeout: 图片检测阶段的总时间预算（秒），超时未找到则放弃；
                 0 表示只检测一次，不重试
        interval: 每轮检测之间的等待秒数（应对画面加载延迟）

    Returns:
        找到并点击时返回 (中心坐标, 匹配分数)；失败返回 (None, None)。
    """
    import time

    tpl = load_template(template)
    deadline = time.time() + timeout
    while True:
        screen = grab_screen(region)
        loc, score = find_template(screen, tpl, threshold)
        if loc is not None:
            click_position(*loc)
            return loc, score
        if time.time() >= deadline:
            return None, None
        if interval > 0:
            time.sleep(interval)


def find_and_click_all(template, threshold=0.85, region=None, max_matches=5):
    """检测屏幕上所有匹配的图标并依次点击（例如批量点击多个按钮）。"""
    tpl = load_template(template)
    screen = grab_screen(region)
    matches = find_all_templates(screen, tpl, threshold, max_matches)
    for (x, y), _score in matches:
        click_position(x, y)
    return matches


def wait_until_found(template, threshold=0.85, region=None, timeout=10.0, interval=0.5):
    """轮询等待图标出现，出现后立即点击。

    与 find_and_click 同一套检测逻辑，仅默认 timeout 更长，
    用于「等待某界面加载完成」的场景。

    Returns:
        成功点击返回 (中心坐标, 分数)；超时返回 (None, None)。
    """
    return find_and_click(template, threshold, region, timeout=timeout, interval=interval)
