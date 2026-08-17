import time

from battle.ops import flee, heal_pets
from battle.plane_nav import enter_planet
from battle.relogin import relogin
from core.actions import click_img, click_pos, detect
from core.screen import grab_screen
from core.vision import find_template, load_template
from config.images import (
    img_battle_start,
    img_capture_item,
    img_capture_success,
    img_my_turn,
    img_not_my_turn,
    img_pet_2,
)
from config.positions import (
    pos_battle_pos,
    pos_capture_btn,
    pos_capture_confirm,
    pos_skill_1,
    pos_skill_2,
    pos_skill_3,
    pos_switch_btn,
)
from config.targets import TARGETS


MAX_CAPTURE_ATTEMPTS = 15

TARGET_DETECT_TIMEOUT = 60

TURN_WAIT_TIMEOUT = 20

RELOGIN_INTERVAL = 60 * 60

LOGIN_START = time.time()
_last_turn_state = None


class BattleRefreshed(Exception):
    pass


def _check_relogin(target):
    global LOGIN_START
    if time.time() - LOGIN_START >= RELOGIN_INTERVAL:
        print(f"本次登录已超过 {RELOGIN_INTERVAL // 60} 分钟,触发重新登录")
        _relogin_and_back(target)
        return True
    return False


def _relogin_and_back(target):
    global LOGIN_START
    relogin()
    LOGIN_START = time.time()
    enter_planet(target["galaxy"], target["planets"], layer=1)
    time.sleep(3)
    click_pos(target["safe_pos"])


def click_pet(target):
    detect_start = time.time()
    while True:
        if not click_img(target["img_pet"], timeout=TARGET_DETECT_TIMEOUT):
            print(f"检测目标精灵中,已检测{int(time.time() - detect_start)/60}分钟")
            if _check_relogin(target):
                detect_start = time.time()
            continue
        print("检测到目标精灵,点击进入战斗")
        if detect(img_battle_start, timeout=10):
            print("战斗开始标志已出现,正式进入战斗")
            return True
        print("点击精灵后长时间未进入战斗,刷新页面")
        _relogin_and_back(target)
        return None


_tpl_my_turn = None
_tpl_not_my_turn = None


def _init_templates():
    global _tpl_my_turn, _tpl_not_my_turn
    if _tpl_my_turn is None:
        _tpl_my_turn = load_template(img_my_turn)
        _tpl_not_my_turn = load_template(img_not_my_turn)


def _probe_turn():
    """双模板分数对比判定回合状态,返回 'my_turn' / 'not_my_turn' / None。
    两态按钮形状相同仅颜色不同时,TM_CCOEFF 会对两者都高分,
    比较分数差而非绝对阈值可彻底区分。"""
    _init_templates()
    screen = grab_screen()
    _, score_m = find_template(screen, _tpl_my_turn, 0.5)
    _, score_n = find_template(screen, _tpl_not_my_turn, 0.5)
    if score_m > 0.6 or score_n > 0.6:
        return "my_turn" if score_m >= score_n else "not_my_turn"
    return None


def wait_for_turn(timeout=10.0, expect=None):
    """快速轮询检测回合状态,返回 'my_turn' 或 'not_my_turn'。
    若指定 expect, 则只在状态等于 expect 时返回,其余状态继续等待。"""
    global _last_turn_state
    deadline = time.time() + timeout
    while time.time() < deadline:
        state = _probe_turn()
        if state is not None:
            if state != _last_turn_state:
                print(f"回合切换: {state}")
                _last_turn_state = state
            if expect is None or state == expect:
                return state
        time.sleep(0.2)
    return None


def _wait_my_turn(target, timeout=TURN_WAIT_TIMEOUT):
    turn = wait_for_turn(timeout=timeout, expect="my_turn")
    if turn == "my_turn":
        time.sleep(1)
        return
    print(f"等待我的回合超时({timeout}秒),刷新页面")
    _relogin_and_back(target)
    raise BattleRefreshed


def _turn(pos_skill, target):
    _wait_my_turn(target)
    click_pos(pos_skill)
    # print(f"已释放技能,位置 {pos_skill}")


def _switch_pet(target):
    _wait_my_turn(target)
    # print("开始切换精灵")
    click_pos(pos_switch_btn)
    if not click_img(img_pet_2):
        return False
    time.sleep(1)
    click_pos(pos_battle_pos)
    time.sleep(1)
    return True


def _try_capture(target):
    _wait_my_turn(target)
    click_pos(pos_capture_btn)
    click_img(img_capture_item)
    return detect(img_capture_success, timeout=5)


def _settle_captured():
    click_pos(pos_capture_confirm)


def _battle_capture(target):
    global _last_turn_state
    _last_turn_state = None

    # 启动自检:确认回合检测模板可用
    state = _probe_turn()
    if state is None:
        print("⚠️  回合检测模板未匹配,回合检测可能不工作,将使用固定延时兜底")
    else:
        print(f"回合检测就绪,当前状态: {state}")

    _turn(pos_skill_2, target)
    if not _switch_pet(target):
        return "failed"
    _turn(pos_skill_3, target)
    _turn(pos_skill_3, target)
    _turn(pos_skill_1, target)
    for attempt in range(MAX_CAPTURE_ATTEMPTS):
        if _try_capture(target):
            _settle_captured()
            return "captured"
        _turn(pos_skill_3, target)
        _turn(pos_skill_1, target)
    heal_pets()
    return "failed"


def capture_once(target):
    if click_pet(target):
        return _battle_capture(target)
    return None


def capture(name):
    global LOGIN_START
    LOGIN_START = time.time()
    target = TARGETS[name]

    while True:
        try:
            result = capture_once(target)
        except BattleRefreshed:
            print("回合等待超时已刷新页面,重新开始捕捉")
            continue
        if result is None:
            continue
        time.sleep(1)
        click_pos(target["safe_pos"])
        heal_pets()
