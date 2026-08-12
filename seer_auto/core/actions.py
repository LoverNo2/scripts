import time

from core.base import (
    click_position,
    find_template,
    grab_screen,
    load_template,
)


def click_pos(x, y=None, clicks=1, button="left", duration=0.0):
    if y is None:
        x, y = x
    click_position(x, y, clicks=clicks, button=button, duration=duration)


def click_img(template, threshold=0.85, region=None, timeout=2.0, interval=0.5):
    tpl = load_template(template)
    deadline = time.time() + timeout
    while True:
        screen = grab_screen(region)
        loc, score = find_template(screen, tpl, threshold)
        if loc is not None:
            click_position(*loc)
            return loc, score
        if time.time() >= deadline:
            return None, None
        if interval > 0:
            time.sleep(interval)


