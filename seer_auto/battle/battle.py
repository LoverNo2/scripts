import time

from core.actions import click_img, click_pos
from core.base import find_template, grab_screen, load_template
from core.overlay import log
from config.images import (
    img_battle_lose,
    img_battle_start,
    img_battle_win,
    img_drop,
)

from config.positions import (
    pos_battle_miss_confirm,
    pos_flee_btn,
    pos_flee_confirm_btn,
    pos_flee_success_btn,
    pos_heal_bag,
    pos_heal_btn,
    pos_heal_confirm_btn,
    pos_heal_close_btn,
    pos_skill_1,
    pos_drop_confirm,
    pos_exp_confirm,
    pos_battle_end_confirm
)
from targets import TARGETS


# 检测图片是否出现
def detect(template, timeout=10.0, interval=0.5):
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
    click_pos(pos_heal_btn)
    click_pos(pos_heal_confirm_btn)
    click_pos(pos_heal_close_btn)


# 进入战斗
def enter_battle(target):
    if not click_img(target["img_pet"]):
        return "no_pet"
    if not detect(img_battle_start, timeout=10):
        click_pos(pos_battle_miss_confirm)
        return "missed"
    if not detect(target["img_pet_avatar"], timeout=2):
        flee()
        return "fled"
    return "fighting"


# 结算战斗胜利
def settle_win():
    log("战斗胜利")
    click_pos(pos_battle_end_confirm)
    click_pos(pos_exp_confirm)
    if detect(img_drop):
        click_pos(pos_drop_confirm)


# 结算战斗失败
def settle_lose():
    log("战斗失败")
    click_pos(pos_battle_end_confirm)
    heal()


# 战斗
def battling():
    while True:
        click_pos(pos_skill_1)
        deadline = time.time() + 5
        while time.time() < deadline:
            if detect(img_battle_win, timeout=1):
                settle_win()
                return "win"
            if detect(img_battle_lose, timeout=1):
                settle_lose()
                return "lose"


# 运行战斗:传入精灵名称,自动从 targets.py 配置读取该精灵的三个属性
def battle(name, times=10, heal_every=10):
    target = TARGETS[name]
    for i in range(times):
        log(f"-----开始第{i+1}次战斗,目标: {name}-----")
        result = enter_battle(target)
        if result in ("no_pet", "missed", "fled"):
            log(f"第{i+1}次战斗取消{result}")
            continue
        battling()
        if heal_every > 0 and (i + 1) % heal_every == 0:
            heal()
