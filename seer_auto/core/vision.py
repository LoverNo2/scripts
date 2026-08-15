from pathlib import Path

import cv2

from config.view import VIEW_SIZE, view_width
from core.screen import to_bgr

TEMPLATES_DIR = Path(__file__).resolve().parent.parent / "assets"

DEFAULT_THRESHOLD = 0.85


def load_template(template_path):
    path = Path(template_path)
    if not path.is_absolute():
        path = TEMPLATES_DIR / path
    img = cv2.imread(str(path), cv2.IMREAD_UNCHANGED)
    if img is None:
        raise FileNotFoundError(f"无法读取图标模板: {path}")
    tpl = to_bgr(img)
    scale = view_width / VIEW_SIZE[0]
    if abs(scale - 1) > 0.01:
        tpl = cv2.resize(tpl, None, fx=scale, fy=scale, interpolation=cv2.INTER_LINEAR)
    return tpl


def find_template(screen, template, threshold=DEFAULT_THRESHOLD):
    screen = to_bgr(screen)
    template = to_bgr(template)
    result = cv2.matchTemplate(screen, template, cv2.TM_CCOEFF_NORMED)
    _min_val, max_val, _min_loc, max_loc = cv2.minMaxLoc(result)
    if max_val >= threshold:
        h, w = template.shape[:2]
        center_x = max_loc[0] + w // 2
        center_y = max_loc[1] + h // 2
        return (center_x, center_y), max_val
    return None, max_val


def find_all_templates(
    screen, template, threshold=DEFAULT_THRESHOLD, max_matches=5, min_distance=20
):
    h, w = template.shape[:2]
    work = to_bgr(screen).copy()
    template = to_bgr(template)
    matches = []
    for _ in range(max_matches):
        loc, score = find_template(work, template, threshold)
        if loc is None:
            break
        matches.append((loc, score))
        x, y = loc[0] - w // 2, loc[1] - h // 2
        pad = max(min_distance, 1)
        y0, y1 = max(0, y - pad), min(work.shape[0], y + h + pad)
        x0, x1 = max(0, x - pad), min(work.shape[1], x + w + pad)
        work[y0:y1, x0:x1] = 0
    return matches
