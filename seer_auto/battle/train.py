"""训练室战斗模块

train() 流程:
1. 判断是否已在训练室: 在则直接开始, 否则重新登录(复用 relogin)并导航
   —— 点击星图 -> 点击训练室; 随后点击训练师并选择训练类型(默认第一种)
2. 点击战斗擂台, 持续监测进入战斗图标: 检测到即已进入战斗, 直接进入战斗处理;
   未检测到(超时)则刷新页面(重新登录导航)重来
3. 正式战斗: 回合检测复用 capture.wait_for_turn, 自己的回合使用技能1,
   每次使用技能后检测 2 秒战斗结束标记, 未检测到则继续等自己的回合, 直到战斗结束
4. 战斗结算: 胜利确认/经验确认/升级确认/技能替换确认(默认不替换)/累计经验确认,
   确认后回到战斗擂台, 治疗目标精灵, 进入下一轮
"""

import time

from battle.capture import wait_for_turn
from battle.ops import heal_pets_train
from battle.relogin import relogin
from config.images import (
    img_train_arena,
    img_train_cancel_skill,
    img_train_enter_battle,
    img_train_exp_confirm,
    img_train_room,
    img_train_room_enter,
    img_train_type_1,
    img_train_type_2,
    img_train_type_3,
    img_train_type_4,
    img_train_type_5,
    img_train_type_6,
    img_train_upgrade_confirm,
    img_train_win,
    img_train_win_confirm,
    img_trainer,
    img_store_exp_confirm,
)
from config.positions import (
    pos_drop_confirm,
    pos_skill_3,
    pos_star_map,
    pos_train_arena,
    pos_train_cancel_skill,
    pos_train_exp_confirm,
    pos_train_upgrade_confirm,
    pos_train_win_confirm,
    pos_store_exp_confirm,
)
from core.actions import click_img, click_pos, detect


# 训练类型 1-6 对应的选择图标
TRAIN_TYPES = {
    1: img_train_type_1,
    2: img_train_type_2,
    3: img_train_type_3,
    4: img_train_type_4,
    5: img_train_type_5,
    6: img_train_type_6,
}


# 点击战斗擂台后, 持续监测进入战斗图标的时间上限(秒)
ENTER_BATTLE_TIMEOUT = 3
# 等回合的探测窗口(秒), 与胜利检测交替轮询, 避免错过任意时刻的胜利
TURN_PROBE_TIMEOUT = 2.0


def _is_in_train_room():
    """判断当前是否已在训练室"""
    return detect(img_train_arena, timeout=1)


# ---------- 1. 登录/导航 + 点击训练师并选择训练类型 ----------


def refresh(train_type=1):
    relogin()
    click_pos(pos_star_map, sleep=1.5)
    click_img(img_train_room_enter, timeout=2)
    click_img(img_trainer)
    click_img(TRAIN_TYPES[train_type])
    time.sleep(5)


def _enter_train_room(train_type=1):
    if _is_in_train_room():
        print("已在训练室, 直接开始")
    else:
        refresh(train_type)


# ---------- 2. 点击战斗擂台, 持续监测进入战斗图标 ----------


def _enter_train():
    click_pos(pos_train_arena, sleep=1)
    print("持续监测进入战斗图标...")
    entered = detect(img_train_enter_battle, timeout=ENTER_BATTLE_TIMEOUT, interval=0.3)
    if entered:
        print("检测到进入战斗图标, 已进入战斗")
        return True
    return False


# ---------- 3. 正式战斗 ----------


def _check_battle_end(timeout=5):
    return detect(img_train_win, timeout=timeout)


def _fight():
    """胜利检测与等回合交替轮询: 胜利可能出现在任意时刻(如对方先手后的后手击杀),
    不能只在我方出招后检测一次, 否则胜利界面无回合按钮会永远等不到我的回合"""
    while True:
        if _check_battle_end(timeout=1):
            print("战斗结束")
            return
        if wait_for_turn(timeout=TURN_PROBE_TIMEOUT, expect="my_turn") == "my_turn":
            click_pos(pos_skill_3)


# ---------- 4. 战斗结算 ----------


def _settle():
    if detect(img_train_win_confirm, timeout=0.5):
        print("胜利确认")
        click_pos(pos_train_win_confirm)
    if detect(img_train_upgrade_confirm, timeout=0.5):
        print("升级确认")
        click_pos(pos_train_upgrade_confirm)
    if detect(img_train_exp_confirm, timeout=0.5):
        print("经验确认")
        click_pos(pos_train_exp_confirm)
    if detect(img_train_cancel_skill, timeout=0.5):
        print("技能替换确认")
        click_pos(pos_train_cancel_skill)
    if detect(img_store_exp_confirm, timeout=0.5):
        print("累计经验确认")
        click_pos(pos_store_exp_confirm)
    print("战斗结算完成")


# ---------- 主入口 ----------


def train(times=10, train_type=6, refresh_every=0, heal_every=1):
    if train_type not in TRAIN_TYPES:
        raise ValueError(f"不支持的训练类型: {train_type}, 可选 {sorted(TRAIN_TYPES)}")
    for i in range(times):
        print(f"第 {i + 1}/{times} 轮")
        if refresh_every and i > 0 and i % refresh_every == 0:
            print(f"已进行 {i} 轮,刷新页面重新执行")
            refresh(train_type)
        _enter_train_room(train_type)
        if not _enter_train():
            print("未检测到进入战斗按钮, 刷新页面")
            refresh(train_type)
            continue
        _fight()
        _settle()
        if heal_every and i % heal_every == 0:
            heal_pets_train()
        time.sleep(1)


def train_plan(plans, refresh_every=0, heal_every=1):
    """按顺序执行多个训练计划, 每个计划为 (train_type, times)。

    例: train_plan([(6, 5), (3, 3), (1, 2)])  # 类型6跑5轮 -> 类型3跑3轮 -> 类型1跑2轮
    切换训练类型时先刷新页面重新进入训练室选择新类型, 否则已在训练室会直接开始不换类型。
    """
    for idx, (times, train_type) in enumerate(plans):
        print(f"执行计划: 训练类型 {train_type} x {times} 轮")
        if idx > 0:
            print("切换训练类型, 刷新页面重新进入训练室")
            refresh(train_type)
        train(
            times=times,
            train_type=train_type,
            refresh_every=refresh_every,
            heal_every=heal_every,
        )
