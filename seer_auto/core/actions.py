import time

from core.base import (
    click_position,
    find_template,
    grab_screen,
    load_template,
    to_screen_coords,
    viewport_to_screen,
)
from config.images import (
    info,
)


def click_pos(x, y=None, sleep=1.0, clicks=1, button="left", duration=0.0):
    if y is None:
        x, y = x
    x, y = viewport_to_screen(x, y)
    click_position(x, y, clicks=clicks, button=button, duration=duration)
    time.sleep(sleep)


def click_img(template, timeout=10.0, interval=0.5):
    tpl = load_template(template)
    deadline = time.time() + timeout
    while True:
        screen = grab_screen()
        loc, score = find_template(screen, tpl, 0.9)
        if loc is not None:
            x, y = to_screen_coords(screen, *loc)
            click_position(x, y)
            return (x, y), score
        if time.time() >= deadline:
            return None
        if interval > 0:
            time.sleep(interval)
