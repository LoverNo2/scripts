import time

from battle.battle import battle
from battle.plane_nav import enter_planet

if __name__ == "__main__":
    time.sleep(1)  # 等待游戏窗口就绪
    # battle("nail", times=40, heal_every=10)
    # battle("fire", times=255, heal_every=19)
    battle("jier", times=255, heal_every=19)
    # enter_planet("pano", "volcano", layer=2)
