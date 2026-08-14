"""重新登录子动作:关闭游戏客户端,重新启动并完成登录。"""

import time

from core.actions import click_pos
from core.mouse import move_to

# 重新登录各步骤的点击位置(视口坐标,模拟数据,待实测替换)
CLOSE_BTN = (1766, -12)  # 游戏关闭按钮
START_BTN = (1083, 728)  # 开始游戏按钮
GAME_SCREEN = (200, 200)  # 游戏画面(启动后点击进入)
HOME_BTN = (900, 960)  # 开始位置
LOGIN_BTN = (842, 572)  # 登录按钮
SERVER_BTN = (591, 363)  # 服务器按钮
NOPLAYER_BTN = (1741, 947)  # 无玩家按钮
NONO_BTN = (1712, 827)  # nono按钮
NONO_2_BTN = (1480, 834)  # nono2按钮

# 星图
STAR_MAP_BTN = (93, 969)  # 星图按钮
# 传送室
PORTAL_BTN = (370, 777)  # 传送室按钮
NONO_POS = (951, 623)  # nono位置
FLY_MODE = (868, 632)  # 飞行模式
SECOND_FORM = (806, 629)  # 第二形态


def relogin():
    """重新登录:关闭游戏 -> 开始游戏 -> 点击画面 -> 开始位置 -> 登录 -> 选服务器。"""
    print("重新登录:关闭游戏")
    click_pos(CLOSE_BTN, sleep=1)
    print("重新登录:点击开始游戏")
    click_pos(START_BTN, sleep=7)
    print("重新登录:点击游戏画面")
    click_pos(GAME_SCREEN, sleep=2)
    print("重新登录:点击开始位置")
    click_pos(HOME_BTN, sleep=1)
    print("重新登录:点击登录")
    click_pos(LOGIN_BTN, sleep=5)
    print("重新登录:点击服务器")
    click_pos(SERVER_BTN, sleep=3)
    print("重新登录完成")
    click_pos(NOPLAYER_BTN, sleep=1)
    print("重新登录:点击无玩家")
    click_pos(NONO_BTN, sleep=1)
    print("重新登录:点击nono")
    click_pos(NONO_2_BTN, sleep=1)
    print("重新登录:点击nono2")
    recall_nono()


def recall_nono():
    """召回nono"""
    click_pos(STAR_MAP_BTN, sleep=1)
    print("召回nono")
    click_pos(PORTAL_BTN, sleep=1)
    print("召回nono2")
    # 鼠标移动到此，不点击nono
    move_to(NONO_POS)
    time.sleep(1)
    print("召回nono")
    click_pos(FLY_MODE, sleep=1)
    print("召回nono")
    click_pos(SECOND_FORM, sleep=1)
    print("召回nono")
