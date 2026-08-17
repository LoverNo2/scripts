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

训练室相关素材暂缺: 能复用的复用现有资源, 缺失的先模拟。
MOCK_ASSETS = True 时缺失步骤只打印并延时, 不做真实点击; 补齐素材后置 False。
两个模拟开关用于占位"在训练室"与"进入战斗按钮"的判断, 方便分别测试各分支。
"""

import time

from battle.capture import wait_for_turn
from battle.ops import heal_pets
from battle.relogin import relogin
from config.images import img_battle_lose, img_battle_win, img_train_enter_battle
from config.positions import (
    pos_battle_end_confirm,
    pos_drop_confirm,
    pos_exp_confirm,
    pos_skill_1,
    pos_skill_keep_btn,
    pos_star_map,
    pos_train_arena,
    pos_train_room,
    pos_train_type_1,
    pos_trainer,
    pos_upgrade_confirm,
)
from core.actions import click_pos, detect
from core.screen import grab_screen
from core.vision import find_template, load_template


# 训练室相关素材缺失, 置 True 时缺失步骤只打印+延时, 不做真实点击
MOCK_ASSETS = True
# 模拟开关: 是否认定已处于训练室(素材缺失时的占位判断)
MOCK_IS_IN_TRAIN_ROOM = False
# 模拟开关: 点击擂台后是否认定检测到进入战斗图标
MOCK_ENTER_DETECTED = True

# 点击战斗擂台后, 持续监测进入战斗图标的时间上限(秒)
ENTER_BATTLE_TIMEOUT = 10.0
# 每次使用技能后检测战斗结束标记的时长(秒)
BATTLE_END_TIMEOUT = 2.0
# 等待自己回合的超时(秒), 超时后继续等待
TURN_WAIT_TIMEOUT = 20.0


def _mock(desc, pos):
    """模拟缺失素材的步骤: 打印日志并延时; 关闭 MOCK_ASSETS 后改为真实点击"""
    if MOCK_ASSETS:
        print(f"[模拟] {desc} {pos}")
        time.sleep(0.5)
        return True
    click_pos(pos, sleep=1)
    return False


def _is_in_train_room():
    """判断当前是否已在训练室。素材缺失时按 MOCK_IS_IN_TRAIN_ROOM 占位。"""
    if MOCK_ASSETS:
        return MOCK_IS_IN_TRAIN_ROOM
    return detect(img_train_room, timeout=1)


# ---------- 1. 登录/导航 + 点击训练师并选择训练类型 ----------

def refresh():
    relogin()
    click_pos(pos_star_map, sleep=1.5)
    _mock("点击训练室", pos_train_room)
    time.sleep(2)
    _mock("点击训练师", pos_trainer)
    _mock("选择训练类型(默认第一种)", pos_train_type_1)

def _enter_train_room():
    if _is_in_train_room():
        print("已在训练室, 直接开始")
    else:
        refresh()


# ---------- 2. 点击战斗擂台, 持续监测进入战斗图标 ----------

def _enter_train():
    _mock("点击战斗擂台", pos_train_arena)
    if MOCK_ASSETS:
        entered = MOCK_ENTER_DETECTED
        time.sleep(0.5)
    else:
        print("持续监测进入战斗图标...")
        entered = detect(img_train_enter_battle, timeout=ENTER_BATTLE_TIMEOUT, interval=0.3)
    if entered:
        print("检测到进入战斗图标, 已进入战斗")
        return True
    return False


# ---------- 3. 正式战斗 ----------

_tpl_battle_win = None
_tpl_battle_lose = None


def _init_end_templates():
    global _tpl_battle_win, _tpl_battle_lose
    if _tpl_battle_win is None:
        _tpl_battle_win = load_template(img_battle_win)
        _tpl_battle_lose = load_template(img_battle_lose)


def _check_battle_end(timeout=BATTLE_END_TIMEOUT):
    """在 timeout 秒窗口内轮询战斗结束标记, 返回 'win' / 'lose' / None"""
    _init_end_templates()
    deadline = time.time() + timeout
    while time.time() < deadline:
        screen = grab_screen()
        _, score_win = find_template(screen, _tpl_battle_win, 0.5)
        _, score_lose = find_template(screen, _tpl_battle_lose, 0.5)
        if score_win > 0.85:
            return "win"
        if score_lose > 0.85:
            return "lose"
        time.sleep(0.2)
    return None


def _fight():
    """自己的回合使用技能1, 每次使用后检测 2 秒战斗结束标记, 直到战斗结束"""
    while True:
        if wait_for_turn(timeout=TURN_WAIT_TIMEOUT, expect="my_turn") != "my_turn":
            continue
        click_pos(pos_skill_1)
        result = _check_battle_end()
        if result:
            print(f"战斗结束: {result}")
            return result


# ---------- 4. 战斗结算 ----------

def _settle():
    click_pos(pos_battle_end_confirm, sleep=1)
    click_pos(pos_exp_confirm, sleep=1)
    _mock("升级确认", pos_upgrade_confirm)
    _mock("技能替换确认(默认不替换)", pos_skill_keep_btn)
    click_pos(pos_drop_confirm, sleep=1)
    print("战斗结算完成")


# ---------- 主入口 ----------

def train(times=10):
    for i in range(times):
        print(f"第 {i + 1}/{times} 轮")
        _enter_train_room()
        if not _enter_train():
            print("未检测到进入战斗按钮, 刷新页面")
            _enter_train_room()
            continue
        _fight()
        _settle()
        heal_pets()
        time.sleep(1)
