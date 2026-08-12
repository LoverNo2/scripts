"""seer_auto —— 入口:启动左上角日志字幕,按精灵名称调用战斗脚本。"""

from battle.battle import battle
from core.overlay import start_overlay

if __name__ == "__main__":
    start_overlay()
    battle("nail")
