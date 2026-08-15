
import time

from core.actions import click_img, click_pos
from core.mouse import move_to
from config.images import img_reload


CLOSE_BTN = (1766, -12)
START_BTN = (1083, 728)
GAME_SCREEN = (200, 200)
HOME_BTN = (900, 960)
LOGIN_BTN = (842, 572)
SERVER_BTN = (591, 363)
NOPLAYER_BTN = (1741, 947)
NONO_BTN = (1712, 827)
NONO_2_BTN = (1480, 834)


STAR_MAP_BTN = (93, 969)

PORTAL_BTN = (370, 777)
NONO_POS = (951, 623)
FLY_MODE = (868, 632)
SECOND_FORM = (806, 629)


def relogin():
    click_pos(CLOSE_BTN, sleep=1)
    click_pos(START_BTN, sleep=6)
    click_pos(GAME_SCREEN, sleep=2)
    click_pos(HOME_BTN, sleep=1)
    click_pos(LOGIN_BTN, sleep=4)
    click_pos(SERVER_BTN, sleep=0)

    click_img(img_reload, timeout=3)
    click_pos(NOPLAYER_BTN, sleep=0)
    click_img(img_reload, timeout=1)
    click_pos(NONO_BTN, sleep=0)
    click_pos(NONO_BTN, sleep=0)
    click_img(img_reload, timeout=2)
    click_pos(NONO_2_BTN, sleep=0)

    click_img(img_reload, timeout=2)
    recall_nono()


def recall_nono():
    click_pos(STAR_MAP_BTN, sleep=1)
    click_pos(PORTAL_BTN, sleep=1)

    move_to(NONO_POS)
    time.sleep(1)
    click_pos(FLY_MODE, sleep=1)
    click_pos(SECOND_FORM, sleep=1)
