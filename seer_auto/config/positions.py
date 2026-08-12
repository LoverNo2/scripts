"""坐标映射表 —— 为常用的屏幕固定位置命名。

坐标 = (x, y)，原点为屏幕左上角，单位：像素。
把示例值替换成你的真实坐标后，脚本里通过名字引用，避免到处写魔法数字。

用法:
    from config.positions import pos_bag
    click_position(*pos_bag)          # 等价于 click_position(1, 1)
"""

# ---- 演示 ----
pos_click = (900, 300)   # 测试点：单击一次

# ---- 赛尔号常用界面（示例值，请替换为真实坐标） ----
pos_bag = (1, 1)         # 背包按钮
pos_battle = (2, 2)      # 战斗按钮
pos_map = (3, 3)         # 地图按钮
