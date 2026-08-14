import time

from battle.battle import battle
from battle.capture import capture
from battle.plane_nav import enter_planet

if __name__ == "__main__":
    time.sleep(1)  # 等待游戏窗口就绪
    # battle("nail", times=40, heal_every=10)
    # battle("fire", times=255, heal_every=19)
    # battle("jier", times=255, heal_every=19)
    capture("spipi")  # 每次捕捉结束自动治疗一二号位
    # enter_planet("pano", "volcano", layer=2)
