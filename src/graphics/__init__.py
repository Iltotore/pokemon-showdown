import sys


def fit(original_size, final_size):
    scale = max(final_size[0] / original_size[0], final_size[1] / original_size[1])
    return original_size[0] * scale, original_size[1] * scale


def fit_text(size, length, max_hint=0.65):
    return min(size[0] / length * 2, size[0] * max_hint, size[1] * max_hint)


def center_pos(size, window_size, offset=(0, 0), hint=(0.5, 0.5)):
    diffX, diffY = size[0] - window_size[0], size[1] - window_size[1]
    return offset[0] - diffX * hint[0], offset[1] - diffY * hint[1]


def screen_size():
    if sys.platform in ["linux2", "darwin", "win32", "macOS"]:
        import pyautogui
        return pyautogui.size()
