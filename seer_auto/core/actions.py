import time

from core.base import (
    click_position,
    find_all_templates,
    find_template,
    grab_screen,
    load_template,
)


def click_pos(x, y=None, clicks=1, button="left", duration=0.0):
    if y is None:
        x, y = x
    click_position(x, y, clicks=clicks, button=button, duration=duration)


def click_img(template, timeout=10.0, interval=0.5):
    tpl = load_template(template)
    deadline = time.time() + timeout
    while True:
        loc, score = find_template(grab_screen(), tpl, 0.85)
        if loc is not None:
            click_position(*loc)
            return loc, score
        if time.time() >= deadline:
            return None, None
        if interval > 0:
            time.sleep(interval)
