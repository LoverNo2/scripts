import time

from battle.battle import battle
from battle.capture import capture
from battle.plane_nav import enter_planet
from battle.relogin import relogin
from battle.train import train, train_plan

if __name__ == "__main__":
    time.sleep(2)
    capture("eye")
    # train(times=148, train_type=2, refresh_every=100, heal_every=7)
    # 按顺序执行多个训练计划(切换类型时自动刷新页面重新选择):
    # train_plan([(247, 1), (255, 4)], heal_every=7)
