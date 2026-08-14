"""鼠标操作与视口坐标换算原语。"""
import pyautogui

from config.view import VIEW_SIZE, view_left, view_top, view_width

pyautogui.FAILSAFE = True
pyautogui.PAUSE = 0.05


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


def move_to(x, y=None, duration=0.1):
    """移动到视口内配置坐标(支持元组或 x,y 传参)。"""
    if y is None:
        x, y = x
    x, y = viewport_to_screen(x, y)
    pyautogui.moveTo(x, y, duration=duration)


def drag_rel(dx, dy, duration=0.3):
    pyautogui.dragRel(int(dx), int(dy), duration=duration)
