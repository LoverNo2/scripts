import time
from pathlib import Path

import cv2
import numpy as np
import pyautogui

pyautogui.FAILSAFE = True
pyautogui.PAUSE = 0.05

from env import VIEW_SIZE, view_left, view_top, view_width

try:
    from mss import mss

    HAS_MSS = True
except ImportError:
    HAS_MSS = False

MAIN_MONITOR = 1


def to_bgr(frame):
    if frame.ndim == 2:
        frame = cv2.cvtColor(frame, cv2.COLOR_GRAY2BGR)
    elif frame.shape[2] == 4:
        frame = cv2.cvtColor(frame, cv2.COLOR_BGRA2BGR)
    elif frame.shape[2] != 3:
        raise ValueError(f"不支持的图像形状: {frame.shape}")
    if frame.dtype != np.uint8:
        frame = frame.astype(np.uint8)
    return np.ascontiguousarray(frame)


def grab_screen(region=None):
    if HAS_MSS:
        with mss() as sct:
            if region is None:
                monitor = sct.monitors[MAIN_MONITOR]
            else:
                left, top, width, height = region
                monitor = {"left": left, "top": top, "width": width, "height": height}
            shot = sct.grab(monitor)
        return to_bgr(np.array(shot))

    try:
        img = pyautogui.screenshot(region=region)
    except Exception as exc:
        raise RuntimeError(
            "屏幕截图失败。macOS 请在「系统设置 → 隐私与安全性 → 屏幕录制」"
            "中授权当前终端，然后重启终端重试。"
        ) from exc
    arr = np.array(img)
    if arr.ndim == 3 and arr.shape[2] == 4:
        arr = cv2.cvtColor(arr, cv2.COLOR_RGBA2BGR)
    elif arr.ndim == 3:
        arr = arr[:, :, ::-1]
    return to_bgr(arr)


def screen_size():
    if HAS_MSS:
        with mss() as sct:
            m = sct.monitors[MAIN_MONITOR]
        return m["width"], m["height"]
    return pyautogui.size()


def to_screen_coords(screen, x, y):
    """把截图内的图像坐标换算为屏幕逻辑坐标。

    macOS 高分屏截图是物理像素(如 2880x1800),而 pyautogui 点击用
    逻辑坐标(1440x900),不换算会点击到错误位置(约差 2 倍)。
    """
    sw, sh = pyautogui.size()
    return int(x * sw / screen.shape[1]), int(y * sh / screen.shape[0])


def viewport_to_screen(x, y):
    """把相对游戏视口左上角的配置坐标换算为屏幕坐标。

    视口固有比例 VIEW_SIZE(1440x840),运行时按 view_width 等比缩放:
    scale = view_width / 1440, 屏幕坐标 = 视口左上角 + 配置坐标 * scale。
    """
    scale = view_width / VIEW_SIZE[0]
    return int(view_left + x * scale), int(view_top + y * scale)


def click_position(x, y, clicks=1, interval=0.0, button="left", duration=0.0):
    pyautogui.click(
        x, y, clicks=clicks, interval=interval, button=button, duration=duration
    )


def click_left():
    pyautogui.click()


def double_click(x, y, interval=0.1, duration=0.0):
    click_position(x, y, clicks=2, interval=interval, button="left", duration=duration)


def right_click(x, y, duration=0.0):
    click_position(x, y, clicks=1, button="right", duration=duration)


def move_to(x, y=None, duration=0.1):
    if y is None:
        x, y = x
    x, y = viewport_to_screen(x, y)
    pyautogui.moveTo(x, y, duration=duration)


def drag(x1, y1, x2, y2, duration=0.3):
    pyautogui.moveTo(x1, y1, duration=duration / 2)
    pyautogui.dragTo(x2, y2, duration=duration / 2, button="left")


def drag_rel(dx, dy, duration=0.3):
    pyautogui.dragRel(int(dx), int(dy), duration=duration)


def scroll(clicks, x=None, y=None):
    pyautogui.scroll(clicks, x=x, y=y)


def wait(seconds):
    time.sleep(seconds)


PROJECT_ROOT = Path(__file__).resolve().parent.parent
TEMPLATES_DIR = PROJECT_ROOT / "assets"


def load_template(template_path):
    """读取图标模板,并按当前视口缩放比例等比缩放后返回。

    约定:assets/ 下的模板基于 VIEW_SIZE(1440 宽)视口裁剪;
    视口宽度调整后,图标实际尺寸变为 原尺寸 * view_width / 1440,
    这里自动缩放,保证旧模板在新视口下仍能匹配。
    """
    path = Path(template_path)
    if not path.is_absolute():
        path = TEMPLATES_DIR / path
    img = cv2.imread(str(path), cv2.IMREAD_UNCHANGED)
    if img is None:
        raise FileNotFoundError(f"无法读取图标模板: {path}")
    tpl = to_bgr(img)
    scale = view_width / VIEW_SIZE[0]
    if abs(scale - 1) > 0.01:
        tpl = cv2.resize(tpl, None, fx=scale, fy=scale, interpolation=cv2.INTER_LINEAR)
    return tpl


def find_template(screen, template, threshold=0.85):
    screen = to_bgr(screen)
    template = to_bgr(template)
    result = cv2.matchTemplate(screen, template, cv2.TM_CCOEFF_NORMED)
    _min_val, max_val, _min_loc, max_loc = cv2.minMaxLoc(result)
    if max_val >= threshold:
        h, w = template.shape[:2]
        center_x = max_loc[0] + w // 2
        center_y = max_loc[1] + h // 2
        return (center_x, center_y), max_val
    return None, max_val


def find_all_templates(
    screen, template, threshold=0.85, max_matches=5, min_distance=20
):
    h, w = template.shape[:2]
    work = to_bgr(screen).copy()
    template = to_bgr(template)
    matches = []
    for _ in range(max_matches):
        loc, score = find_template(work, template, threshold)
        if loc is None:
            break
        matches.append((loc, score))
        x, y = loc[0] - w // 2, loc[1] - h // 2
        pad = max(min_distance, 1)
        y0, y1 = max(0, y - pad), min(work.shape[0], y + h + pad)
        x0, x1 = max(0, x - pad), min(work.shape[1], x + w + pad)
        work[y0:y1, x0:x1] = 0
    return matches
