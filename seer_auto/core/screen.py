"""屏幕捕获与图像处理原语。"""
import cv2
import numpy as np
import pyautogui

try:
    from mss import mss

    HAS_MSS = True
except ImportError:
    HAS_MSS = False

MAIN_MONITOR = 1


def to_bgr(frame):
    """统一转为 BGR 三通道 uint8 图像。"""
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
    """抓取屏幕(或指定区域),返回 BGR 图像。"""
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


def to_screen_coords(screen, x, y):
    """把截图内的图像坐标换算为屏幕逻辑坐标。

    macOS 高分屏截图是物理像素(如 2880x1800),而 pyautogui 点击用
    逻辑坐标(1440x900),不换算会点击到错误位置(约差 2 倍)。
    """
    sw, sh = pyautogui.size()
    return int(x * sw / screen.shape[1]), int(y * sh / screen.shape[0])
