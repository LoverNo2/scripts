"""星球导航子动作:从星图进入指定星系/星球(可下第二层)。"""

import time

from core.actions import click_pos, detect
from core.mouse import click_left, drag_rel, move_to
from config.plane import GALAXIES, pos_map_btn, pos_map_center, pos_map_back


def enter_planet(galaxy_name, planet_name, layer=1):
    galaxy = GALAXIES[galaxy_name]
    planet = galaxy["planets"][planet_name]
    click_pos(pos_map_btn)
    click_pos(pos_map_back)
    click_pos(galaxy["pos"])
    click_pos(planet["pos_enter"], sleep=5)
    click_left()
    time.sleep(3)
    if planet["drag"] != (0, 0):
        move_to(pos_map_center)
        time.sleep(2)
        drag_rel(*planet["drag"])
        time.sleep(2)
    if layer >= 2:
        click_pos(planet["pos_layer2"])
        if not detect(planet["layer2_img"], timeout=10.0, interval=0.5):
            print("未检测到第二层图片")
            return False
    return True
