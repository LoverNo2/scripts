import time

from battle.ops import flee, heal, settle_lose, settle_win
from battle.plane_nav import enter_planet
from core.actions import click_img, click_pos, detect
from config.images import (
    img_battle_lose,
    img_battle_start,
    img_battle_win,
    img_tire,
    img_tire_3,
)
from config.positions import (
    pos_battle_miss_confirm,
    pos_skill_1,
    pos_tire_1,
    pos_tire_3,
)
from config.targets import TARGETS


def enter_battle(target):
    if not click_img(target["img_pet"], timeout=10, interval=0.2):
        return "no_pet"


    if detect(img_battle_start, timeout=10):
        return _after_battle_start(target)


    if detect(img_tire, timeout=2):
        return _skip_anti_fatigue(target)

    click_pos(pos_battle_miss_confirm)
    return "missed"


def _after_battle_start(target):
    if not detect(target["img_pet_avatar"], timeout=2):
        flee()
        return "fled"
    return "fighting"


def _skip_anti_fatigue(target):
    for attempt in (1, 2):
        click_pos(pos_tire_1, sleep=1)
        if detect(img_tire_3, timeout=2):
            click_pos(pos_tire_3, sleep=1)
            return "fled"
        if detect(img_battle_start, timeout=3):
            flee()
            return "fled"
        if not detect(img_tire, timeout=1):
            break


    return _teleport_back(target)


def _teleport_back(target):
    if "galaxy" not in target or "planets" not in target:
        return "no_pet"

    layer = target.get("layer", 1)
    if not enter_planet(target["galaxy"], target["planets"], layer=layer):
        return "no_pet"
    return enter_battle(target)


def battling():
    time.sleep(1)
    while True:
        click_pos(pos_skill_1)
        deadline = time.time() + 5
        while time.time() < deadline:
            for result, img, settle in (
                ("win", img_battle_win, settle_win),
                ("lose", img_battle_lose, settle_lose),
            ):
                if detect(img, timeout=1):
                    settle()
                    return result


def battle(name, times=10, heal_every=10):
    target = TARGETS[name]
    for i in range(times):
        result = enter_battle(target)
        if result in ("no_pet", "missed", "fled"):
            continue
        battling()
        if heal_every > 0 and (i + 1) % heal_every == 0:
            heal()
