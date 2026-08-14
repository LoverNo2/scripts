"""组合动作:面向业务流程的高层操作。"""

import time

from core.mouse import click_position, viewport_to_screen
from core.screen import grab_screen, to_screen_coords
from core.vision import find_all_templates, find_template, load_template


def click_pos(x, y=None, sleep=1.0, clicks=1, button="left", duration=0.0):
    """点击视口内配置坐标(支持元组或 x,y 传参),点击后按 sleep 秒等待。"""
    if y is None:
        x, y = x
    x, y = viewport_to_screen(x, y)
    click_position(x, y, clicks=clicks, button=button, duration=duration)
    time.sleep(sleep)


def wait_img(template, timeout=10.0, interval=0.5, threshold=0.85):
    """轮询检测图标,出现则返回 (屏幕坐标, 分数),超时返回 None。"""
    tpl = load_template(template)
    deadline = time.time() + timeout
    while True:
        screen = grab_screen()
        loc, score = find_template(screen, tpl, threshold)
        if loc is not None:
            return to_screen_coords(screen, *loc), score
        if time.time() >= deadline:
            return None
        if interval > 0:
            time.sleep(interval)


def click_img(template, timeout=10.0, interval=0.1, threshold=0.9):
    """检测图标并点击一次,返回 (屏幕坐标, 分数);超时返回 None。"""
    found = wait_img(template, timeout, interval, threshold)
    if found is None:
        return None
    (x, y), score = found
    click_position(x, y)
    return (x, y), score


def detect(template, timeout=10.0, interval=0.5, threshold=0.85):
    """轮询检测图标是否出现(不点击),带日志输出。"""
    found = wait_img(template, timeout, interval, threshold)
    print(f"{'检测到' if found else '未检测到'}图片: {template}")
    return found is not None


def click_all_img(template, timeout=10.0, interval=0.5, threshold=0.85):
    """检测并点击屏幕上所有匹配图标。"""
    tpl = load_template(template)
    deadline = time.time() + timeout
    while True:
        screen = grab_screen()
        matches = find_all_templates(screen, tpl, threshold)
        if matches:
            for (x, y), score in matches:
                click_position(*to_screen_coords(screen, x, y))
            return matches
        if time.time() >= deadline:
            return None
        if interval > 0:
            time.sleep(interval)
