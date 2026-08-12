"""seer_auto —— 启动后点击屏幕固定位置一次。

坐标来自 config/positions.py 映射表,通过名字引用:
    click_position(*pos_click) 等价于 click_position(900, 300)
"""

from core import click_position
from config.positions import pos_click
from config.images import img_nail
from core import find_and_click



if __name__ == "__main__":
    click_position(*pos_click)
    find_and_click(img_nail, timeout=30, interval=1)
    print("已点击钉子图标")
