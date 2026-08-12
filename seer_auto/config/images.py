"""图片映射表 —— 为游戏内图标命名。

值是图标模板文件名（相对 assets/ 目录）。
先把目标图标裁剪保存到 assets/ 下，再通过名字传给图标检测点击功能。

用法:
    from config.images import img_bag
    find_and_click(img_bag)           # 检测背包图标并点击
"""

# ---- 赛尔号常用图标（示例，请把真实图标裁剪保存到 assets/ 下） ----
img_bag = "bag.png"        # 背包图标
img_battle = "battle.png"  # 战斗图标
img_nail = "nail.png"      # 钉子图标