"""seer_auto —— 赛尔号可视化自动键鼠操作研究框架。"""

from core.clicker import click_position, double_click, drag, move_to, right_click, scroll, wait
from core.matcher import find_and_click, find_and_click_all, find_template, wait_until_found

__all__ = [
    # 模式一：固定位置点击
    "click_position",
    "double_click",
    "right_click",
    "move_to",
    "drag",
    "scroll",
    "wait",
    # 模式二：图标检测点击
    "find_and_click",
    "find_and_click_all",
    "find_template",
    "wait_until_found",
]
