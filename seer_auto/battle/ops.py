import time

from core.actions import click_img, click_pos, detect
from config.images import (
    img_close_pet_bag,
    img_drop,
    img_heal,
    img_heal_two,
    img_pet_bag,
)
from config.positions import (
    pos_battle_end_confirm,
    pos_drop_confirm,
    pos_exp_confirm,
    pos_flee_btn,
    pos_flee_confirm_btn,
    pos_flee_success_btn,
    pos_bag_open,
    pos_heal_bag,
    pos_heal_btn,
    pos_heal_close_btn,
    pos_heal_confirm,
    pos_heal_confirm_btn,
    pos_heal_pet_1,
)


def _click(msg, pos):
    click_pos(pos)


def flee():
    _click("逃跑:点击逃跑按钮", pos_flee_btn)
    _click("逃跑:点击确认逃跑按钮", pos_flee_confirm_btn)
    time.sleep(2)
    _click("逃跑:点击逃跑成功按钮", pos_flee_success_btn)


def heal():
    _click("治疗:点击精灵背包", pos_heal_bag)
    _click("治疗:点击治疗按钮", pos_heal_btn)
    _click("治疗:点击确认治疗按钮", pos_heal_confirm_btn)
    _click("治疗:点击关闭治疗界面按钮", pos_heal_close_btn)


def heal_pets():
    _click("治疗:点击精灵背包", pos_heal_bag)

    _click("治疗:选择一号位精灵", pos_heal_pet_1)
    _click("治疗:点击治疗按钮", pos_heal_btn)
    _click("治疗:点击确认治疗按钮", pos_heal_confirm_btn)

    if click_img(img_heal_two):
        time.sleep(1)
        _click("治疗:点击治疗按钮", pos_heal_btn)
        _click("治疗:点击确认治疗按钮", pos_heal_confirm_btn)
    _click("治疗:点击关闭治疗界面按钮", pos_heal_close_btn)


def heal_pets_train():
    """训练室专用恢复:持续点击打开背包直到界面出现,治疗并关闭"""
    while not detect(img_pet_bag, timeout=0.5):
        click_pos(pos_bag_open)
    click_img(img_heal)
    time.sleep(1)
    click_pos(pos_heal_confirm)
    click_img(img_close_pet_bag)


def settle_win():
    _click("结算:点击战斗结束确认", pos_battle_end_confirm)
    _click("结算:点击经验获取确认", pos_exp_confirm)
    if detect(img_drop, timeout=1):
        _click("结算:检测到掉落物,点击掉落确认", pos_drop_confirm)
    _click("结算:累计经验确认", pos_drop_confirm)


def settle_lose():
    _click("结算:点击战斗结束确认", pos_battle_end_confirm)
    heal()
