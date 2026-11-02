# -*- coding: utf-8 -*-
"""公共小工具：中文路径读写图片、显示窗口、拼图对照。

为什么单独放一个文件？
因为读图、存图、开窗口这几件事每个脚本都要做，
写一遍之后调用，主程序里就只剩下和算法相关的代码，看得更清楚。
"""

import os

import cv2
import numpy as np


def imread_unicode(path, flags=cv2.IMREAD_COLOR):
    """读取图片，支持中文路径。

    cv2.imread 在 Windows 上遇到中文路径会「不报错、直接返回 None」，
    所以这里先用 numpy 把文件读成字节流，再交给 cv2.imdecode 解码。
    """
    if not os.path.exists(path):
        raise FileNotFoundError(f"找不到图片：{os.path.abspath(path)}")
    data = np.fromfile(path, dtype=np.uint8)
    img = cv2.imdecode(data, flags)
    if img is None:
        raise ValueError(f"图片解码失败，可能不是有效的图片文件：{path}")
    return img


def imwrite_unicode(path, img):
    """保存图片，同样支持中文路径。"""
    folder = os.path.dirname(os.path.abspath(path))
    os.makedirs(folder, exist_ok=True)
    ext = os.path.splitext(path)[1]
    ok, buf = cv2.imencode(ext, img)
    if not ok:
        raise IOError(f"图片编码失败：{path}")
    buf.tofile(path)
    print(f"[已保存] {path}")


def show(title, img, enabled=True):
    """弹出一个窗口显示图片。

    enabled=False 时只跳过显示，不影响存图（在没有图形界面的环境里跑代码时用）。
    """
    if not enabled:
        return
    cv2.imshow(title, img)


def wait_and_close(enabled=True):
    """等任意键，然后关掉所有窗口。"""
    if not enabled:
        return
    print(">>> 在弹出的窗口里按任意键继续（关闭窗口后程序会自动往下走）")
    cv2.waitKey(0)
    cv2.destroyAllWindows()


def gray_to_bgr(gray):
    """把灰度图转成三通道，方便和彩色图并排放。"""
    return cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR)


def hstack_same_height(images, gap=10, bg=255):
    """把几张高度不同的图并排拼在一起（高度统一到最高的那张）。"""
    h = max(im.shape[0] for im in images)
    padded = []
    for im in images:
        if im.shape[0] != h:
            scale = h / im.shape[0]
            im = cv2.resize(im, (int(im.shape[1] * scale), h))
        padded.append(im)
        padded.append(np.full((h, gap, 3), bg, np.uint8))
    return np.hstack(padded[:-1])


def title_bar(text, width, height=28, bg=40, fg=255):
    """生成一条带英文标题的深色横条，用来给对照图做标注。

    cv2.putText 只能写英文，中文会变成问号，所以标题一律用英文。
    """
    bar = np.full((height, width, 3), bg, np.uint8)
    cv2.putText(bar, text, (8, height - 9), cv2.FONT_HERSHEY_SIMPLEX,
                0.6, (fg, fg, fg), 1, cv2.LINE_AA)
    return bar


def with_title(img, text):
    """给图片顶部加一条标题条。"""
    bar = title_bar(text, img.shape[1])
    return np.vstack([bar, img])
