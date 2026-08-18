import time

from core.actions import click_img, click_pos, detect
from core.mouse import move_to
from config.images import (
    img_login_btn,
    img_login_page,
    img_reload,
    img_save,
    img_server_btn,
)


CLOSE_BTN = (1766, -12)
START_BTN = (1083, 728)
GAME_SCREEN = (200, 200)
HOME_BTN = (900, 960)
LOGIN_BTN = (842, 572)
SERVER_BTN = (591, 363)
SAVE_CONFIRM_BTN = (844, 613)
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
    click_pos(START_BTN, sleep=7)
    click_pos(GAME_SCREEN, sleep=2)
    click_pos(GAME_SCREEN, sleep=2)
    if detect(img_login_page, timeout=5):
        click_pos(HOME_BTN, sleep=1)
    if detect(img_login_btn, timeout=5):
        while True:
            click_pos(LOGIN_BTN)
            if not detect(img_save, timeout=1):
                break
            click_pos(SAVE_CONFIRM_BTN, sleep=1)
            if not detect(img_login_btn, timeout=5):
                break
    if detect(img_server_btn, timeout=5):
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
