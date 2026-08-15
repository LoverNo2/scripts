import pyautogui

from config.view import VIEW_SIZE, view_left, view_top, view_width

pyautogui.FAILSAFE = False
pyautogui.PAUSE = 0.05


def viewport_to_screen(x, y):
    scale = view_width / VIEW_SIZE[0]
    return int(view_left + x * scale), int(view_top + y * scale)


def click_position(x, y, clicks=1, interval=0.0, button="left", duration=0.0):
    pyautogui.click(
        x, y, clicks=clicks, interval=interval, button=button, duration=duration
    )


def click_left():
    pyautogui.click()


def move_to(x, y=None, duration=0.1):
    if y is None:
        x, y = x
    x, y = viewport_to_screen(x, y)
    pyautogui.moveTo(x, y, duration=duration)


def drag_rel(dx, dy, duration=0.3):
    pyautogui.dragRel(int(dx), int(dy), duration=duration)
