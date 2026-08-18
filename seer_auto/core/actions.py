import time

from core.mouse import click_position, viewport_to_screen
from core.screen import grab_screen, to_screen_coords
from core.vision import find_all_templates, find_template, load_template


def click_pos(x, y=None, sleep=1.0, clicks=1, button="left", duration=0.0):
    if y is None:
        x, y = x
    x, y = viewport_to_screen(x, y)
    click_position(x, y, clicks=clicks, button=button, duration=duration)
    time.sleep(sleep)


def wait_img(template, timeout=10.0, interval=0.5, threshold=0.85):
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
    found = wait_img(template, timeout, interval, threshold)
    if found is None:
        return None
    (x, y), score = found
    click_position(x, y)
    return (x, y), score


def detect(template, timeout=10.0, interval=0.1, threshold=0.85):
    found = wait_img(template, timeout, interval, threshold)
    return found is not None


def click_all_img(template, timeout=10.0, interval=0.5, threshold=0.85):
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
