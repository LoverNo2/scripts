import time

from core.actions import click_img, click_pos
from core.base import find_template, grab_screen, load_template
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
    if not detect(img_battle_start, timeout=10):
        print("未出现战斗开始标志,点击精灵消失确认,结束本次战斗")
        click_pos(pos_battle_miss_confirm)
        return "missed"
    print("战斗开始标志已出现")
    if not detect(target["img_pet_avatar"], timeout=2):
        print("未检测到目标精灵头像,触发逃跑流程")
        flee()
        return "fled"
    print("目标精灵已确认,进入正式战斗")
    return "fighting"


# 结算战斗胜利
def settle_win():
    print("战斗胜利,进入胜利结算")

    print("结算:点击战斗结束确认")
    click_pos(pos_battle_end_confirm)

    print("结算:点击经验获取确认")
    click_pos(pos_exp_confirm)

    if detect(img_drop, timeout=2):
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
