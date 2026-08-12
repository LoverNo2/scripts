import time

from core.base import (
    click_position,
    find_all_templates,
    find_template,
    grab_screen,
    load_template,
    to_screen_coords,
)


def click_pos(x, y=None,sleep=1.0, clicks=1, button="left", duration=0.0):
    if y is None:
        x, y = x
    click_position(x, y, clicks=clicks, button=button, duration=duration)
    time.sleep(sleep)


def click_img(template, timeout=10.0, interval=0.5):
    tpl = load_template(template)
    deadline = time.time() + timeout
    while True:
        screen = grab_screen()
        loc, score = find_template(screen, tpl, 0.85)
        if loc is not None:
            x, y = to_screen_coords(screen, *loc)
            print(f"点击 {template} 位置 {(x, y)} 评分 {score}")
            click_position(x, y)
            return (x, y), score
        if time.time() >= deadline:
            return None, None
        if interval > 0:
            time.sleep(interval)


def click_all_img(template, threshold=0.85, region=None, max_matches=5):
    tpl = load_template(template)
    screen = grab_screen(region)
    matches = find_all_templates(screen, tpl, threshold, max_matches)
    for (x, y), _score in matches:
        sx, sy = to_screen_coords(screen, x, y)
        click_position(sx, sy)
    return [(to_screen_coords(screen, x, y), s) for (x, y), s in matches]


def wait_img(template, timeout=10.0, interval=0.5):
    return click_img(template, timeout=timeout, interval=interval)
