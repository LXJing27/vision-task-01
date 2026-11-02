# -*- coding: utf-8 -*-
"""HSV 定值助手：帮你从图片里「问出」目标的 HSV 范围，而不是瞎试。

两种用法：

1) 你已经知道目标大概在哪个矩形里 —— 直接量那一块：
       python probe_hsv.py --image images/chart.png --rect 311 47 119 119
   输出这块区域 H/S/V 的 5%~95% 分位数，并给出一组建议阈值。

2) 还不知道目标在哪 —— 先看整张图里哪些色相最多：
       python probe_hsv.py --image images/chart.png
   输出 H 通道的直方图峰值，也就是「这张图的主色调是哪几个」。

为什么要用分位数而不是平均值：
   一块色块上有高光、有边框、有阴影，平均值会被这些极端像素拉偏。
   取 5%~95% 之间的范围，正好扔掉两头的异常值，留下「主体颜色大概是什么」。

想手点也行：task2_basic_vision.py 运行后，在窗口里点像素会在终端打印 HSV。
"""

import argparse

import cv2
import numpy as np

from utils import imread_unicode, imwrite_unicode


def rect_stats(hsv, x, y, w, h):
    """统计一个矩形区域内 H/S/V 的分位数。"""
    roi = hsv[y:y + h, x:x + w]
    h_ch = roi[:, :, 0].ravel()
    s_ch = roi[:, :, 1].ravel()
    v_ch = roi[:, :, 2].ravel()

    def p(ch):
        return (int(np.percentile(ch, 5)), int(np.median(ch)), int(np.percentile(ch, 95)))

    return p(h_ch), p(s_ch), p(v_ch), roi.shape[0] * roi.shape[1]


def suggest_range(h_p, s_p, v_p, h_margin=8, s_margin=40, v_margin=50):
    """按分位数给一组建议阈值。H 加小余量，S/V 只往下放（上限给 255）。"""
    lower = (max(0, h_p[0] - h_margin), max(0, s_p[0] - s_margin), max(0, v_p[0] - v_margin))
    upper = (min(179, h_p[2] + h_margin), 255, 255)
    return lower, upper


def hue_peaks(hsv, top_n=4):
    """整张图的 H 直方图峰值，用来找「图里主要有哪些颜色」。"""
    h_ch = hsv[:, :, 0]
    s_ch = hsv[:, :, 1]
    # 只统计有颜色的像素，灰白黑的 S 很小，会把直方图抬高
    valid = h_ch[s_ch > 60]
    if valid.size == 0:
        return []
    hist = cv2.calcHist([hsv], [0], (s_ch > 60).astype(np.uint8) * 255, [180], [0, 180]).ravel()
    # 简单找局部峰值：比左右邻居都大
    peaks = []
    for i in range(1, 179):
        if hist[i] > hist[i - 1] and hist[i] >= hist[i + 1] and hist[i] > valid.size * 0.01:
            peaks.append((i, int(hist[i])))
    peaks.sort(key=lambda t: -t[1])
    return peaks[:top_n]


def main():
    parser = argparse.ArgumentParser(description="HSV 定值助手")
    parser.add_argument("--image", default="images/chart.png")
    parser.add_argument("--rect", nargs=4, type=int, metavar=("X", "Y", "W", "H"),
                        help="目标所在的矩形，例如 --rect 311 47 119 119")
    args = parser.parse_args()

    img = imread_unicode(args.image)
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    print(f"图片：{args.image}  尺寸 {img.shape[1]}x{img.shape[0]}")

    if args.rect:
        x, y, w, h = args.rect
        h_p, s_p, v_p, n = rect_stats(hsv, x, y, w, h)
        print(f"\n区域 ({x},{y}) 宽{w} 高{h}，共 {n} 像素")
        print(f"  H 色相  ：5%={h_p[0]:3d}  中位数={h_p[1]:3d}  95%={h_p[2]:3d}")
        print(f"  S 饱和度：5%={s_p[0]:3d}  中位数={s_p[1]:3d}  95%={s_p[2]:3d}")
        print(f"  V 明度  ：5%={v_p[0]:3d}  中位数={v_p[1]:3d}  95%={v_p[2]:3d}")

        lower, upper = suggest_range(h_p, s_p, v_p)
        print(f"\n  建议阈值：lower={lower}  upper={upper}")
        print(f"  也就是：cv2.inRange(hsv, {lower}, {upper})")

        # 顺手把这块区域框出来存一张图，方便确认你没量错地方
        mark = img.copy()
        cv2.rectangle(mark, (x, y), (x + w, y + h), (0, 255, 255), 2)
        imwrite_unicode("results/probe_rect.png", mark)
    else:
        print("\n没给 --rect，先看看整张图里哪些色相最多：")
        peaks = hue_peaks(hsv)
        if not peaks:
            print("  图里几乎没有彩色像素（S 都太低）")
        for hue, count in peaks:
            print(f"  H≈{hue:3d}  像素数 {count}")
        print("\n拿到峰值后，用 --rect 量一块具体的区域，才知道 S/V 该卡到多少。")


if __name__ == "__main__":
    main()
