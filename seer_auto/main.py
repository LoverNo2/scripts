import time

from battle.battle import battle
from battle.capture import capture
from battle.plane_nav import enter_planet
from battle.relogin import relogin
from battle.train import train

if __name__ == "__main__":
    time.sleep(2)
    # capture("eye")
    train(times=1)
