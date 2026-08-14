import time

from battle.ops import flee, heal, settle_lose, settle_win
from battle.plane_nav import enter_planet
from core.actions import click_img, click_pos, detect
from config.images import (
    img_battle_lose,
    img_battle_start,
    img_battle_win,
    img_tire,
    img_tire_3,
)
from config.positions import (
    pos_battle_miss_confirm,
    pos_skill_1,
    pos_tire_1,
    pos_tire_3,
)
from config.targets import TARGETS


# 进入战斗
def enter_battle(target):
    print(f"进入战斗:检测并点击精灵图像 {target['img_pet']}")
    if not click_img(target["img_pet"], timeout=10, interval=0.2):
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
    for attempt in (1, 2):
        print(f"防疲劳:第{attempt}次选择,点击 pos_tire_1")
        click_pos(pos_tire_1, sleep=1)
        if detect(img_tire_3, timeout=2):
            click_pos(pos_tire_3, sleep=1)
            return "fled"
        if detect(img_battle_start, timeout=3):
            print(f"防疲劳:第{attempt}次选择成功进入战斗,直接逃跑,进入下一次")
            flee()
            return "fled"
        if not detect(img_tire, timeout=1):
            break

    # 弹窗消失且未进入战斗(或两次均未成功):判定被传送出去
    print("防疲劳:两次选择均未进入战斗,判定被传送")
    return _teleport_back(target)


def _teleport_back(target):
    """被传送后调用 enter_planet 回到原位置,然后继续战斗流程。"""
    if "galaxy" not in target or "planets" not in target:
        print("目标未配置 galaxy/planets,无法传送回原位置,取消本次战斗")
        return "no_pet"

    layer = target.get("layer", 1)
    print(
        f"被传送:调用 enter_planet 回到 "
        f"{target['galaxy']}/{target['planets']} (layer={layer})"
    )
    if not enter_planet(target["galaxy"], target["planets"], layer=layer):
        print("传送回原位置失败,取消本次战斗")
        return "no_pet"
    print("已回到原位置,继续战斗流程")
    return enter_battle(target)


# 战斗
def battling():
    """循环点击技能1直到出现胜负结算,返回 "win" / "lose"。"""
    time.sleep(1)
    while True:
        print("战斗:点击技能1")
        click_pos(pos_skill_1)
        deadline = time.time() + 5
        while time.time() < deadline:
            for result, img, settle in (
                ("win", img_battle_win, settle_win),
                ("lose", img_battle_lose, settle_lose),
            ):
                if detect(img, timeout=1):
                    settle()
                    return result
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
