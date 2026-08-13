# 星图全局位置(相对视口 1440x840)
pos_map_btn = (100,970)      # 打开星图按钮
pos_map_center = (900, 580)  # 星图中心(拖拽起点)
pos_map_back = (1460,260)
# 四大星系 -> 星球 -> {drag: 星图中需拖拽的距离, pos_enter: 点击星球进入第一层,
#                      pos_layer2: 第二层点击位置, pos_layer3: 第三层点击位置}
GALAXIES = {
    "pano": {
        "pos": (412, 338),
        "planets": {
            "klose": {
                "drag": (890, 580),
                "pos_enter": (200, 200),
                "pos_layer2": (200, 300),
                "pos_layer3": (200, 400),
            },
        },
    }
}
