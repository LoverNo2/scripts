from core.actions import click_pos
from core.base import drag_rel, move_to, viewport_to_screen
from config.plane import GALAXIES, pos_map_btn, pos_map_center, pos_map_back


def enter_planet(_galaxy, _planet, layer=1):
    galaxy = GALAXIES[_galaxy]
    planet = galaxy["planets"][_planet]
    click_pos(pos_map_btn)
    click_pos(pos_map_back)                        
    click_pos(galaxy["pos"])
    move_to(pos_map_center)
    drag_rel(planet["drag"][0], planet["drag"][1])
    # click_pos(planet["pos_enter"])                    
    # if layer >= 2:
    #     click_pos(p["pos_layer2"])              
    # if layer >= 3:
    #     click_pos(p["pos_layer3"])              
