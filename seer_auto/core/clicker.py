"""固定位置点击模块 —— 模式一：点击屏幕的固定坐标。

底层使用 pyautogui 控制鼠标，跨平台（macOS / Windows / Linux）。
macOS 上首次运行需在「系统设置 → 隐私与安全性 → 辅助功能」中授权终端。
"""

import time

import pyautogui

# 鼠标移到屏幕左上角 (0,0) 立即触发 FailSafe 异常，用于紧急停止脚本
pyautogui.FAILSAFE = True
# 每次 pyautogui 调用之间的间隔（秒），避免动作过快
pyautogui.PAUSE = 0.05


def click_position(x, y, clicks=1, interval=0.0, button="left", duration=0.0):
    """在屏幕固定坐标 (x, y) 处点击。

    Args:
        x, y: 屏幕像素坐标（主屏幕左上角为原点）
        clicks: 点击次数（1 单击，2 双击）
        interval: 多次点击之间的间隔秒数
        button: "left" | "right" | "middle"
        duration: 鼠标移动到目标点的耗时（秒），0 表示瞬间移动
    """
    pyautogui.click(x, y, clicks=clicks, interval=interval, button=button, duration=duration)


def double_click(x, y, interval=0.1, duration=0.0):
    """双击固定坐标（常用于打开背包、精灵等界面）。"""
    click_position(x, y, clicks=2, interval=interval, button="left", duration=duration)


def right_click(x, y, duration=0.0):
    """右键点击固定坐标。"""
    click_position(x, y, clicks=1, button="right", duration=duration)


def move_to(x, y, duration=0.1):
    """仅移动鼠标到固定坐标，不点击。"""
    pyautogui.moveTo(x, y, duration=duration)


def drag(x1, y1, x2, y2, duration=0.3):
    """从 (x1, y1) 按住左键拖拽到 (x2, y2)，用于拖动物品/滑动界面。"""
    pyautogui.moveTo(x1, y1, duration=duration / 2)
    pyautogui.dragTo(x2, y2, duration=duration / 2, button="left")


def scroll(clicks, x=None, y=None):
    """在固定坐标处滚动滚轮（clicks > 0 向上，< 0 向下）。"""
    pyautogui.scroll(clicks, x=x, y=y)


def wait(seconds):
    """等待指定秒数（常用在两次操作之间）。"""
    time.sleep(seconds)
