# 星图全局位置(相对视口 1440x840)
pos_map_btn = (100, 970)  # 打开星图按钮
pos_map_center = (740, 507)  # 星图中心(拖拽起点)
pos_map_back = (1460, 260)
# 四大星系 -> 星球 -> {drag: 星图中需拖拽的距离, pos_enter: 点击星球进入第一层,
#                      pos_layer2: 第二层点击位置, pos_layer3: 第三层点击位置}
GALAXIES = {
    "pano": {
        "pos": (412, 338),
        "planets": {
            "klose": {
                "drag": (0, 0),
                "pos_enter": (344, 415),
                "pos_layer2": (37, 743),
            },
            "volcano": {
                "drag": (0, 0),
                "pos_enter": (709, 419),
                "pos_layer2": (1622, 234),
                "layer2_img": "planets/volcano_2.png",
            },
        },
    }
}
