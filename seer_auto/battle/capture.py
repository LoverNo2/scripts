"""精灵捕捉子流程:复用战斗的进入/防疲劳/结算,执行换宠、耗血、捕捉循环。"""

import time

from battle.ops import flee, heal_pets
from battle.plane_nav import enter_planet
from battle.relogin import relogin
from core.actions import click_img, click_pos, detect, wait_img
from config.images import (
    img_battle_start,
    img_capture_success,
    img_klose_layer_2,
    img_pet_2,
)
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
ROUND_WAIT = 8.0
# 单次捕捉的最大尝试次数,超限后逃跑结束
MAX_CAPTURE_ATTEMPTS = 30
# 回到一层后等待精灵刷出的时长(秒)
REFRESH_WAIT = 2.0
# 进入二层后,单次检测标志图的时长(秒),未出现则持续检测
LAYER2_DETECT_TIMEOUT = 3.0
# 一层与二层之间的切换位置(视口坐标,待实测补充)
POS_ENTER_LAYER2 = (24, 810)  # 在一层点击此处进入二层
POS_BACK_LAYER1 = (1700, 553)  # 在二层点击此处回到一层
# 登录超过该时长(秒)触发重新登录
RELOGIN_INTERVAL = 10 * 60
# 本次登录开始时间,以 capture() 入口为准
LOGIN_START = time.time()


# 每次回到一层时检查登录时长,超时则重新登录并回到目标星球一层
def _check_relogin(target):
    global LOGIN_START
    if time.time() - LOGIN_START < RELOGIN_INTERVAL:
        return
    print(f"本次登录已超过 {RELOGIN_INTERVAL // 60} 分钟,触发重新登录")
    _relogin_and_back(target)


def _relogin_and_back(target):
    """重新登录(刷新页面)并回到目标星球一层。"""
    global LOGIN_START
    relogin()  # relogin 内部自动刷新登录计时器
    LOGIN_START = time.time()  # 重置登录计时
    if "galaxy" in target and "planets" in target:
        print(f"重新登录完成,返回 {target['galaxy']}/{target['planets']} 一层")
        enter_planet(target["galaxy"], target["planets"], layer=1)


def _refresh_until_target(target):
    """一/二层来回切换,直接点击目标精灵直到正式进入战斗。

    一层点击 POS_ENTER_LAYER2 进二层,持续检查二层标志图后回一层,
    直接点击目标精灵:点击成功且战斗标志出现才返回 True;
    点击后 10 秒未进入战斗则刷新页面(重新登录)继续。
    """
    while True:
        click_pos(POS_ENTER_LAYER2, sleep=1)  # 一层 -> 二层
        # 持续检查二层标志图,检测到前不返回一层
        while wait_img(img_klose_layer_2, timeout=LAYER2_DETECT_TIMEOUT) is None:
            print("二层标志图未出现,持续检测中")
        click_pos(POS_BACK_LAYER1, sleep=1)  # 检测到,立刻回到一层
        _check_relogin(target)  # 每次回到一层判断登录时长,超时重新登录
        time.sleep(REFRESH_WAIT)  # 等待三只精灵刷出
        # 直接点击目标精灵,不再先检测图片
        if not click_img(target["img_pet"], timeout=5):
            print("未点击到目标精灵,继续来回切换")
            continue
        print("已点击目标精灵,检测战斗开始标志")
        if detect(img_battle_start, timeout=10):
            print("战斗开始标志已出现,正式进入战斗")
            return True
        # 点击成功但未进入战斗:刷新页面后继续
        print("点击精灵后 10 秒未进入战斗,刷新页面")
        _relogin_and_back(target)


def _turn(pos_skill, sleep=1, round_wait=ROUND_WAIT):
    """点击技能并等待本回合结束。"""
    time.sleep(sleep)
    click_pos(pos_skill)
    time.sleep(round_wait)


def _switch_pet():
    """切换二号精灵出战:切换 -> 识别并点击二号精灵 -> 确认出战。"""
    time.sleep(2)
    click_pos(pos_switch_btn)
    if not click_img(img_pet_2):
        print("未识别到二号精灵图片(two.png),放弃本次切换")
        return False
    time.sleep(1)
    click_pos(pos_battle_pos)
    time.sleep(3)
    return True


def _try_capture():
    """打开捕捉界面并用二号道具捕捉,返回是否成功。"""
    click_pos(pos_capture_btn)
    click_pos(pos_capture_item_2)
    return detect(img_capture_success, timeout=5)


def _settle_captured(target):
    """捕捉成功结算:点击确认成功,回到目标精灵的地图安全位置。"""
    click_pos(pos_capture_confirm, sleep=2)  # 确认捕捉成功弹窗
    # click_pos(target["safe_pos"])


def capture_once(target):
    """单次捕捉:切层刷新并确认进入战斗后,换宠耗血循环捕捉。"""
    _refresh_until_target(target)  # 无限循环直到正式进入战斗

    time.sleep(2)
    _turn(pos_skill_2)  # 首发精灵使用二技能
    if not _switch_pet():  # 换二号精灵出战
        return "failed"
    time.sleep(1)
    _turn(pos_skill_3)  # 第一回合:三技能
    _turn(pos_skill_3)  # 第二回合:三技能
    _turn(pos_skill_1, round_wait=4)  # 第三回合:一技能
    for attempt in range(MAX_CAPTURE_ATTEMPTS):
        if _try_capture():
            _settle_captured(target)
            return "captured"
        print(f"捕捉未成功(第{attempt + 1}次),用三技能重新进入状态")
        _turn(pos_skill_1, round_wait=4)  # 第四回合:三技能
    print("捕捉尝试次数已达上限,逃跑结束本次捕捉")
    flee()
    return "failed"


def capture(name, times=10):
    """连续捕捉入口:每次成功捕捉后治疗一号位与二号位精灵。"""
    global LOGIN_START
    LOGIN_START = time.time()  # 以本轮捕捉开始作为登录起点
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
