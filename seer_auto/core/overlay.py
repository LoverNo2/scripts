"""core/overlay.py —— 屏幕左上角日志字幕,保留最近 5 条。

macOS 上 Tk 窗口只能由主线程创建,因此本模块无后台线程:
start_overlay() 在主线程初始化窗口,log() 同步刷新字幕。
"""

import tkinter as tk
from collections import deque

_lines = deque(maxlen=5)
_root = None
_label = None


def start_overlay():
    """在主线程创建字幕窗口:无边框、置顶、半透明,固定在屏幕左上角。"""
    global _root, _label
    if _root is not None:
        try:
            if _root.winfo_exists():
                return
        except tk.TclError:
            pass
        _root = None
        _label = None
    try:
        _root = tk.Tk()
    except Exception:
        return
    _root.overrideredirect(True)
    _root.attributes("-topmost", True)
    _root.attributes("-alpha", 0.85)
    _root.geometry("+10+10")
    _label = tk.Label(
        _root,
        text="",
        justify="left",
        anchor="nw",
        font=("Menlo", 12),
        fg="white",
        bg="black",
        padx=8,
        pady=4,
    )
    _label.pack()
    _root.update()


def log(msg):
    """记录一条信息:打印到终端,并显示在字幕中(保留最近 5 条)。"""
    print(msg)
    if _root is None:
        return
    _lines.append(str(msg))
    try:
        _label.config(text="\n".join(_lines))
        _root.update()
    except tk.TclError:
        pass
