"""屏幕截图模块 —— 为图标检测提供屏幕帧。

优先使用 mss 抓屏（跨平台且比 pyautogui.screenshot 快很多）；
若 mss 未安装，自动回退到 pyautogui.screenshot。
返回 OpenCV 的 BGR 格式 numpy 数组，可直接用于模板匹配。
"""

import numpy as np

try:
    from mss import mss

    HAS_MSS = True
except ImportError:
    HAS_MSS = False

# mss 的 monitor 编号：1 = 主屏幕，0 = 所有屏幕合并
MAIN_MONITOR = 1


def grab_screen(region=None):
    """抓取屏幕指定区域，返回 BGR 格式的 numpy 数组 (H, W, 3)。

    Args:
        region: 可选 (left, top, width, height) 四元组；
                为 None 时抓取整个主屏幕。
    """
    if HAS_MSS:
        with mss() as sct:
            if region is None:
                monitor = sct.monitors[MAIN_MONITOR]
            else:
                left, top, width, height = region
                monitor = {"left": left, "top": top, "width": width, "height": height}
            shot = sct.grab(monitor)
        # mss 返回 BGRA，丢弃 alpha 通道得到 BGR；
        # 切片会产生非连续数组，matchTemplate 会报 dims 错，需转连续
        return np.ascontiguousarray(np.array(shot)[:, :, :3])

    # 回退方案：pyautogui 截屏（返回 RGB，需转为 BGR）
    import pyautogui

    try:
        img = pyautogui.screenshot(region=region)
    except Exception as exc:
        raise RuntimeError(
            "屏幕截图失败。macOS 请在「系统设置 → 隐私与安全性 → 屏幕录制」"
            "中授权当前终端，然后重启终端重试。"
        ) from exc
    # 反转通道产生非连续数组，转连续后再返回
    return np.ascontiguousarray(np.array(img)[:, :, ::-1])


def screen_size():
    """返回主屏幕 (宽, 高)。"""
    if HAS_MSS:
        with mss() as sct:
            m = sct.monitors[MAIN_MONITOR]
        return m["width"], m["height"]
    import pyautogui

    return pyautogui.size()
