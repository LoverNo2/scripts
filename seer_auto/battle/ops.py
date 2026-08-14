"""战斗子动作:逃跑 / 治疗 / 胜负结算,与 plane_nav 平行,由 battle 编排调用。"""

import time

from core.actions import click_img, click_pos, detect
from config.images import img_drop, img_heal_two
from config.positions import (
    pos_battle_end_confirm,
    pos_drop_confirm,
    pos_exp_confirm,
    pos_flee_btn,
    pos_flee_confirm_btn,
    pos_flee_success_btn,
    pos_heal_bag,
    pos_heal_btn,
    pos_heal_close_btn,
    pos_heal_confirm_btn,
    pos_heal_pet_1,
)


def _click(msg, pos):
    print(msg)
    click_pos(pos)


# 逃跑
def flee():
    _click("逃跑:点击逃跑按钮", pos_flee_btn)
    _click("逃跑:点击确认逃跑按钮", pos_flee_confirm_btn)
    time.sleep(2)
    _click("逃跑:点击逃跑成功按钮", pos_flee_success_btn)


# 治疗
def heal():
    _click("治疗:点击精灵背包", pos_heal_bag)
    _click("治疗:点击治疗按钮", pos_heal_btn)
    _click("治疗:点击确认治疗按钮", pos_heal_confirm_btn)
    _click("治疗:点击关闭治疗界面按钮", pos_heal_close_btn)


# 治疗一号位与二号位精灵
def heal_pets():
    """打开治疗界面,依次治疗一号位与二号位精灵后关闭。"""
    _click("治疗:点击精灵背包", pos_heal_bag)
    # 一号位:固定位置定位
    _click("治疗:选择一号位精灵", pos_heal_pet_1)
    _click("治疗:点击治疗按钮", pos_heal_btn)
    _click("治疗:点击确认治疗按钮", pos_heal_confirm_btn)
    # 二号位:检测 heal_two.png 定位
    if not click_img(img_heal_two):
        print("未检测到二号位精灵图片(heal_two.png),跳过二号位治疗")
    else:
        time.sleep(1)
        _click("治疗:点击治疗按钮", pos_heal_btn)
        _click("治疗:点击确认治疗按钮", pos_heal_confirm_btn)
    _click("治疗:点击关闭治疗界面按钮", pos_heal_close_btn)


# 结算战斗胜利
def settle_win():
    print("战斗胜利,进入胜利结算")
    _click("结算:点击战斗结束确认", pos_battle_end_confirm)
    _click("结算:点击经验获取确认", pos_exp_confirm)
    if detect(img_drop, timeout=1):
        _click("结算:检测到掉落物,点击掉落确认", pos_drop_confirm)
    _click("结算:累计经验确认", pos_drop_confirm)


# 结算战斗失败
def settle_lose():
    print("战斗失败,进入失败结算")
    _click("结算:点击战斗结束确认", pos_battle_end_confirm)
    heal()
