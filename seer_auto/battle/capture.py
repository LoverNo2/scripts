"""精灵捕捉子流程:复用战斗的进入/防疲劳/结算,执行换宠、耗血、捕捉循环。"""

import time

from battle.battle import enter_battle
from battle.ops import flee, heal_pets
from core.actions import click_img, click_pos, detect
from config.images import img_capture_success, img_pet_2
from config.positions import (
    pos_battle_pos,
    pos_capture_btn,
    pos_capture_confirm,
    pos_capture_item_2,
    pos_skill_1,
    pos_skill_2,
    pos_skill_3,
    pos_switch_btn,
)
from config.targets import TARGETS

# 单回合等待时长(秒),按游戏实际回合节奏调整
ROUND_WAIT = 7.0
# 单次捕捉的最大尝试次数,超限后逃跑结束
MAX_CAPTURE_ATTEMPTS = 30


def _turn(pos_skill, sleep=1):
    """点击技能并等待本回合结束。"""
    time.sleep(sleep)
    click_pos(pos_skill)
    time.sleep(ROUND_WAIT)


def _switch_pet():
    """切换二号精灵出战:切换 -> 识别并点击二号精灵 -> 确认出战。"""
    click_pos(pos_switch_btn)
    if not click_img(img_pet_2):
        print("未识别到二号精灵图片(two.png),放弃本次切换")
        return False
    click_pos(pos_battle_pos)
    time.sleep(3)
    return True


def _try_capture():
    """打开捕捉界面并用二号道具捕捉,返回是否成功。"""
    click_pos(pos_capture_btn)
    click_pos(pos_capture_item_2)
    return detect(img_capture_success, timeout=3)


def _settle_captured(target):
    """捕捉成功结算:点击确认成功,回到目标精灵的地图安全位置。"""
    click_pos(pos_capture_confirm, sleep=2)  # 确认捕捉成功弹窗
    click_pos(target["safe_pos"])  # 回到地图安全位置


def capture_once(target):
    """单次捕捉:进入战斗(含防疲劳流程),换宠耗血后循环捕捉直到成功。"""
    result = enter_battle(target)
    if result != "fighting":
        print(f"进入战斗失败({result}),本次捕捉取消")
        return result

    time.sleep(1)
    _turn(pos_skill_2)  # 首发精灵使用二技能
    if not _switch_pet():  # 换二号精灵出战
        return "failed"
    _turn(pos_skill_3)  # 第一回合:三技能
    _turn(pos_skill_3)  # 第二回合:三技能
    _turn(pos_skill_1)  # 第三回合:一技能
    for attempt in range(MAX_CAPTURE_ATTEMPTS):
        if _try_capture():
            _settle_captured(target)
            return "captured"
        print(f"捕捉未成功(第{attempt + 1}次),用三技能重新进入状态")
        _turn(pos_skill_1)
    print("捕捉尝试次数已达上限,逃跑结束本次捕捉")
    flee()
    return "failed"


def capture(name, times=10):
    """连续捕捉入口:每次成功捕捉后治疗一号位与二号位精灵。"""
    target = TARGETS[name]
    # 无限次循环捕捉
    while True:
        print(f"-----开始捕捉,目标: {name}-----")
        result = capture_once(target)
        if result != "captured":
            print(f"捕捉未成功({result})")
            continue
        print(f"已捕捉,治疗一号位与二号位精灵")
        heal_pets()
