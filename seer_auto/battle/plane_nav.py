from core.actions import click_pos
from core.base import drag_rel, move_to, viewport_to_screen, click_left
from config.plane import GALAXIES, pos_map_btn, pos_map_center, pos_map_back
from battle.battle import detect
import time


def enter_planet(_galaxy, _planet, layer=1):
    galaxy = GALAXIES[_galaxy]
    planet = galaxy["planets"][_planet]
    click_pos(pos_map_btn)
    click_pos(pos_map_back)
    click_pos(galaxy["pos"])
    click_pos(planet["pos_enter"], sleep=4)
    click_left()
    time.sleep(3)
    if planet["drag"] != (0, 0):
        move_to(pos_map_center)
        time.sleep(2)
        drag_rel(planet["drag"][0], planet["drag"][1])
        time.sleep(2)
    if layer >= 2:
        click_pos(planet["pos_layer2"])
        if not detect(planet["layer2_img"], timeout=10.0, interval=0.5):
            print("未检测到第二层图片")
            return False
    # if layer >= 3:
    #     click_pos(p["pos_layer3"])
    return True
