import time

from core.actions import click_img, click_pos
from core.base import find_template, grab_screen, load_template
from config.images import (
    img_battle_lose,
    img_battle_start,
    img_battle_win,
    img_drop,
    img_tire,
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
    pos_battle_end_confirm,
    pos_tire_1,
)
from targets import TARGETS


# 检测图片是否出现
def detect(template, timeout=10.0, interval=0.5):
    tpl = load_template(template)
    deadline = time.time() + timeout
    while time.time() < deadline:
        loc, _score = find_template(grab_screen(), tpl, 0.85)
        if loc is not None:
            print(f"检测到图片: {template}")
            return True
        time.sleep(interval)
    print(f"未检测到图片: {template}")
    return False


# 逃跑
def flee():
    print("逃跑:点击逃跑按钮")
    click_pos(pos_flee_btn)
    print("逃跑:点击确认逃跑按钮")
    click_pos(pos_flee_confirm_btn)
    print("逃跑:点击逃跑成功按钮")
    time.sleep(2)
    click_pos(pos_flee_success_btn)
    print("逃跑完成")


# 治疗
def heal():
    print("治疗:点击精灵背包")
    click_pos(pos_heal_bag)
    print("治疗:点击治疗按钮")
    click_pos(pos_heal_btn)
    print("治疗:点击确认治疗按钮")
    click_pos(pos_heal_confirm_btn)
    print("治疗:点击关闭治疗界面按钮")
    click_pos(pos_heal_close_btn)
    print("治疗完成")


# 进入战斗
def enter_battle(target):
    print(f"进入战斗:检测并点击精灵图像 {target['img_pet']}")
    if not click_img(target["img_pet"]):
        print("未发现精灵图像,本次战斗取消")
        return "no_pet"
    print("已点击精灵图像")

    # 点击精灵后先等战斗开始标志(防疲劳弹窗出现时它不会出现)
    if detect(img_battle_start, timeout=10):
        return _after_battle_start(target)

    # 长时间未出现战斗开始:检查是否弹出了防疲劳弹窗
    if detect(img_tire, timeout=2):
        print("检测到防疲劳弹窗,执行跳过流程")
        return _skip_anti_fatigue(target)

    print("未出现战斗开始标志,点击精灵消失确认,结束本次战斗")
    click_pos(pos_battle_miss_confirm)
    return "missed"


def _after_battle_start(target):
    """战斗开始标志已出现:确认目标精灵头像后进入正式战斗。"""
    print("战斗开始标志已出现")
    if not detect(target["img_pet_avatar"], timeout=2):
        print("未检测到目标精灵头像,触发逃跑流程")
        flee()
        return "fled"
    print("目标精灵已确认,进入正式战斗")
    return "fighting"


def _skip_anti_fatigue(target):
    """跳过防疲劳弹窗:最多两次选择机会,两次都未进入战斗则视为被传送。"""
    # 第一次选择
    print("防疲劳:第一次选择,点击 pos_tire_1")
    click_pos(pos_tire_1)
    if detect(img_battle_start, timeout=3):
        print("防疲劳:选择成功进入战斗,直接逃跑,进入下一次")
        flee()
        return "fled"

    # 弹窗仍在 -> 选错了,还有一次机会
    if detect(img_tire, timeout=1):
        print("防疲劳:第一次选择失败,第二次点击 pos_tire_1")
        click_pos(pos_tire_1)
        if detect(img_battle_start, timeout=3):
            print("防疲劳:第二次选择成功进入战斗,直接逃跑,进入下一次")
            flee()
            return "fled"

    # 弹窗消失且未进入战斗(或第二次也未成功):判定被传送出去
    print("防疲劳:两次选择均未进入战斗,判定被传送")
    return _teleport_back(target)


def _teleport_back(target):
    """被传送后调用 enter_planet 回到原位置,然后继续战斗流程。"""
    if "galaxy" not in target or "planets" not in target:
        print("目标未配置 galaxy/planets,无法传送回原位置,取消本次战斗")
        return "no_pet"

    # 延迟导入,避免与 battle.plane_nav(其顶部 import battle.battle.detect)循环导入
    from battle.plane_nav import enter_planet

    print(
        f"被传送:调用 enter_planet 回到 "
        f"{target['galaxy']}/{target['planets']} (layer={target.get('layer', 1)})"
    )
    ok = enter_planet(
        target["galaxy"], target["planets"], layer=target.get("layer", 1)
    )
    if not ok:
        print("传送回原位置失败,取消本次战斗")
        return "no_pet"
    print("已回到原位置,继续战斗流程")
    return enter_battle(target)


# 结算战斗胜利
def settle_win():
    print("战斗胜利,进入胜利结算")

    print("结算:点击战斗结束确认")
    click_pos(pos_battle_end_confirm)

    print("结算:点击经验获取确认")
    click_pos(pos_exp_confirm)

    if detect(img_drop, timeout=1):
        print("结算:检测到掉落物,点击掉落确认")
        click_pos(pos_drop_confirm)

    print("结算:累计经验确认")
    click_pos(pos_drop_confirm)
    print("胜利结算完成")


# 结算战斗失败
def settle_lose():
    print("战斗失败,进入失败结算")
    print("结算:点击战斗结束确认")
    click_pos(pos_battle_end_confirm)
    print("结算:触发精灵恢复流程")
    heal()
    print("失败结算完成")


# 战斗
def battling():
    time.sleep(1)
    while True:
        print("战斗:点击技能1")
        click_pos(pos_skill_1)
        deadline = time.time() + 5
        while time.time() < deadline:
            if detect(img_battle_win, timeout=1):
                settle_win()
                return "win"
            if detect(img_battle_lose, timeout=1):
                settle_lose()
                return "lose"
        print("5秒内未检测到战斗结果,再次点击技能1")


# 运行战斗:传入精灵名称,自动从 targets.py 配置读取该精灵的三个属性
def battle(name, times=10, heal_every=10):
    target = TARGETS[name]
    for i in range(times):
        print(f"-----开始第{i+1}次战斗,目标: {name}-----")
        result = enter_battle(target)
        if result in ("no_pet", "missed", "fled"):
            print(f"第{i+1}次战斗取消{result}")
            continue
        battling()
        if heal_every > 0 and (i + 1) % heal_every == 0:
            print(f"已战斗 {i+1} 场,执行精灵恢复")
            heal()
