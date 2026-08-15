
import time

from battle.ops import flee, heal_pets
from battle.plane_nav import enter_planet
from battle.relogin import relogin
from core.actions import click_img, click_pos, detect, wait_img
from config.images import (
    img_battle_start,
    img_capture_success,
    img_pet_2,
)
from config.positions import (
    pos_battle_pos,
    pos_capture_btn,
    pos_capture_confirm,
    pos_capture_item_2,
    pos_skill_1,
    pos_skill_2,
    pos_skill_3,
    pos_switch_btn,
)
from config.targets import TARGETS


ROUND_WAIT = 8.0

MAX_CAPTURE_ATTEMPTS = 15

REFRESH_DETECT_TIMEOUT = 5.0

RELOGIN_INTERVAL = 30

LOGIN_START = time.time()


def _check_relogin(target):
    global LOGIN_START
    if time.time() - LOGIN_START >= RELOGIN_INTERVAL:
        _relogin_and_back(target)


def _relogin_and_back(target):
    global LOGIN_START
    relogin()
    LOGIN_START = time.time()
    enter_planet(target["galaxy"], target["planets"], layer=1)


def _refresh_until_target(target):
    while True:
        _check_relogin(target)
        if (
            wait_img(target["img_pet"], timeout=REFRESH_DETECT_TIMEOUT, threshold=0.9)
            is None
        ):
            continue
        if not click_img(target["img_pet"]):
            continue
        if detect(img_battle_start, timeout=10):
            return True

        _relogin_and_back(target)
        return None


def _turn(pos_skill, sleep=1, round_wait=ROUND_WAIT):
    time.sleep(sleep)
    click_pos(pos_skill)
    time.sleep(round_wait)


def _switch_pet():
    click_pos(pos_switch_btn)
    if not click_img(img_pet_2):
        return False
    time.sleep(1)
    click_pos(pos_battle_pos)
    time.sleep(3)
    return True


def _try_capture():
    click_pos(pos_capture_btn)
    click_pos(pos_capture_item_2)
    return detect(img_capture_success, timeout=5)


def _settle_captured(target):
    click_pos(pos_capture_confirm, sleep=2)


def _battle_capture(target):
    time.sleep(2)
    _turn(pos_skill_2)
    if not _switch_pet():
        return "failed"
    time.sleep(1)
    _turn(pos_skill_3)
    _turn(pos_skill_3)
    _turn(pos_skill_1, round_wait=4)
    for attempt in range(MAX_CAPTURE_ATTEMPTS):
        if _try_capture():
            _settle_captured(target)
            return "captured"
        _turn(pos_skill_1, round_wait=4)
    flee()
    return "failed"


def capture_once(target):
    result = _refresh_until_target(target)
    if result is True:
        return _battle_capture(target)


def capture(name):
    global LOGIN_START
    LOGIN_START = time.time()
    target = TARGETS[name]

    while True:
        result = capture_once(target)
        if result is None:
            continue
        heal_pets()
