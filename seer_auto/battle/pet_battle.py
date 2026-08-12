import time

from core.actions import click_img, click_pos
from core.base import find_template, grab_screen, load_template

pos_flee_btn = (100, 100)
pos_flee_confirm_btn = (100, 200)
pos_flee_success_btn = (100, 300)

pos_heal_bag = (200, 100)
pos_heal_first_pet = (200, 200)
pos_heal_btn = (200, 300)
pos_heal_confirm_btn = (200, 400)
pos_heal_success_btn = (200, 500)

pos_battle_miss_confirm = (300, 100)

pos_skill_1 = (400, 100)
pos_skill_2 = (400, 200)
pos_skill_3 = (400, 300)
pos_skill_4 = (400, 400)

pos_map_safe = (500, 500)

img_pet = "pet.png"
img_pet_avatar = "pet_avatar.png"
img_battle_start = "battle_start.png"
img_battle_win = "battle_win.png"
img_battle_lose = "battle_lose.png"
img_battle_win_confirm = "battle_win_confirm.png"
img_exp_confirm = "exp_confirm.png"
img_drop_confirm = "drop_confirm.png"

# 检测精灵是否出现
def detect(template, timeout=3.0, interval=0.5):
    tpl = load_template(template)
    deadline = time.time() + timeout
    while time.time() < deadline:
        loc, _score = find_template(grab_screen(), tpl, 0.85)
        if loc is not None:
            return True
        time.sleep(interval)
    return False

# 逃跑
def flee():
    click_pos(pos_flee_btn)
    click_pos(pos_flee_confirm_btn)
    click_pos(pos_flee_success_btn)

# 治疗
def heal():
    click_pos(pos_heal_bag)
    click_pos(pos_heal_first_pet)
    click_pos(pos_heal_btn)
    click_pos(pos_heal_confirm_btn)
    click_pos(pos_heal_success_btn)

# 进入战斗
def enter_battle():
    if not click_img(img_pet):
        return "no_pet"
    time.sleep(3)
    if not detect(img_battle_start, timeout=3):
        click_pos(pos_battle_miss_confirm)
        return "missed"
    if not detect(img_pet_avatar, timeout=3):
        flee()
        return "fled"
    return "fighting"

# 战斗
def battle():
    while True:
        click_pos(pos_skill_1)
        deadline = time.time() + 5
        while time.time() < deadline:
            if click_img(img_battle_win, timeout=0):
                return "win"
            if click_img(img_battle_lose, timeout=0):
                return "lose"
            time.sleep(0.5)

# 结算战斗
def settle():
    click_img(img_battle_win_confirm)
    click_img(img_exp_confirm)
    click_img(img_drop_confirm)
    click_pos(pos_map_safe)

# 运行战斗
def run(times=10, heal_every=0):
    for i in range(times):
        result = enter_battle()
        if result in ("no_pet", "missed", "fled"):
            continue
        battle()
        settle()
        if heal_every > 0 and (i + 1) % heal_every == 0:
            heal()


if __name__ == "__main__":
    run()
