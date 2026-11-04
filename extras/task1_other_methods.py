# -*- coding: utf-8 -*-
"""任务一（2）：除了霍夫圆检测，还有哪些办法能把圆找出来？

三条路子的思路：

A. 边缘 -> 轮廓 -> 最小二乘拟合圆 -> 偏差筛选
   把边缘连成一条条曲线（轮廓），对每条轮廓拟合一个圆，
   再用「轮廓点到这个圆的相对偏差」判断它像不像圆。
   一开始我用的是圆度（4πA/P²）筛选，结果一个都筛不出来——
   因为真实照片里盘子的边是断断续续的，开口曲线算不出面积，圆度恒接近 0。
   换成拟合圆 + 偏差判断才行。

B. Otsu 二值化 -> 连通域 -> 外接矩形 -> 筛选
   不找边，直接把「比背景暗的整块东西」抠出来。盘子是白的，跳不出来。

C. HOUGH_GRADIENT_ALT
   还是霍夫，但换了更严的判据：边缘的梯度方向要和半径方向一致。

运行：python task1_other_methods.py
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import argparse

import cv2
import numpy as np

from utils import (hstack_same_height, imread_unicode, imwrite_unicode,
                   show, wait_and_close, with_title)


def circularity(contour):
    """圆度：4πA/P²。已经写好了，直接调用。"""
    area = cv2.contourArea(contour)
    peri = cv2.arcLength(contour, True)
    if peri <= 0:
        return 0.0
    return 4 * np.pi * area / (peri ** 2)


def fit_circle(pts):
    """最小二乘拟合圆，返回 (cx, cy, r, 相对偏差)。

    比 cv2.minEnclosingCircle 准：外接圆只要有一段弧最远就把半径撑大，
    而拟合圆用上所有点，断开的弧也能拟合出正确的圆心和半径。
    """
    x, y = pts[:, 0], pts[:, 1]
    A = np.c_[x, y, np.ones(len(x))]
    b = -(x * x + y * y)
    (D, E, F), *_ = np.linalg.lstsq(A, b, rcond=None)
    cx, cy = -D / 2, -E / 2
    r = np.sqrt(cx * cx + cy * cy - F)
    d = np.hypot(x - cx, y - cy)
    return cx, cy, r, np.std(d) / max(r, 1.0)


def method_a_contour(img, min_peri=600, max_err=0.10):
    """A：边缘 -> 轮廓 -> 最小二乘拟合圆 + 偏差筛选。"""
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (9, 9), 2.0)

    # 阈值必须压得低：盘沿和桌面只差十来个灰阶，用 40/120 边会碎成小段
    edges = cv2.Canny(blur, 20, 60)
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (9, 9))
    edges = cv2.morphologyEx(edges, cv2.MORPH_CLOSE, kernel)   # 补断口

    contours, _ = cv2.findContours(edges, cv2.RETR_LIST, cv2.CHAIN_APPROX_NONE)

    cands = []
    for c in contours:
        # 开口曲线的面积算不出来，所以这里用周长当尺子，不能用 contourArea
        if cv2.arcLength(c, True) < min_peri:
            continue
        pts = c.reshape(-1, 2).astype(float)
        cx, cy, r, err = fit_circle(pts)
        if r < 30 or err > max_err:
            continue
        cands.append((err, int(cx), int(cy), int(r)))

    # 去重：同一个圆的里外两条边会各拟合出一个，偏差小的留
    cands.sort()
    kept = []
    for err, x, y, r in cands:
        if any(np.hypot(x - kx, y - ky) < 0.20 * r and abs(r - kr) < 0.30 * r
               for kx, ky, kr in kept):
            continue
        kept.append((x, y, r))

    out = img.copy()
    for x, y, r in kept:
        cv2.circle(out, (x, y), r, (0, 140, 255), 2, cv2.LINE_AA)
        cv2.circle(out, (x, y), 3, (0, 140, 255), -1, cv2.LINE_AA)
    return out, kept


def method_b_connected(img, min_area=20000):
    """B：Otsu 二值化 -> 连通域 -> 外接矩形 -> 筛选。"""
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (9, 9), 2.0)

    # INV：让「比背景暗的物体」变成白色前景
    t, binary = cv2.threshold(blur, 0, 255,
                              cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    print(f"    Otsu 选出的阈值 = {t:.0f}")

    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (7, 7))
    binary = cv2.morphologyEx(binary, cv2.MORPH_OPEN, kernel)

    num, labels, stats, cents = cv2.connectedComponentsWithStats(binary)
    out = img.copy()
    found = []
    for i in range(1, num):
        x, y, w, h, area = stats[i]
        if area < min_area:
            continue
        if not (0.7 <= w / float(h) <= 1.3):      # 只留接近方形的
            continue
        found.append((int(cents[i][0]), int(cents[i][1]), int(max(w, h) / 2)))
        cv2.rectangle(out, (x, y), (x + w, y + h), (0, 255, 0), 2)
    return out, found


def method_c_alt(img, param1=50, param2=0.3):
    """C：HOUGH_GRADIENT_ALT（判据更严，param2 是 0~1 的小数）。"""
    short = min(img.shape[:2])
    blur = cv2.GaussianBlur(cv2.cvtColor(img, cv2.COLOR_BGR2GRAY), (9, 9), 2.0)

    found = cv2.HoughCircles(
        blur, cv2.HOUGH_GRADIENT_ALT,
        dp=1.5, minDist=short * 0.08,
        param1=param1, param2=param2,
        minRadius=int(short * 0.05), maxRadius=int(short * 0.60),
    )
    circles = [] if found is None else np.round(found[0]).astype(int).tolist()

    out = img.copy()
    for x, y, r in circles:
        cv2.circle(out, (x, y), r, (0, 255, 255), 2, cv2.LINE_AA)
        cv2.circle(out, (x, y), 3, (0, 255, 255), -1, cv2.LINE_AA)
    return out, circles


def main():
    parser = argparse.ArgumentParser(description="任务一(2)：其他识别圆的方法")
    parser.add_argument("--image", default="images/plate_real.png")
    parser.add_argument("--no-show", action="store_true")
    args = parser.parse_args()

    img = imread_unicode(args.image)
    print(f"读入图片：{args.image}  尺寸 {img.shape[1]}x{img.shape[0]}")

    res_a, circles_a = method_a_contour(img)
    print(f"[A 轮廓法] 得到 {len(circles_a)} 个圆：{circles_a}")

    res_b, circles_b = method_b_connected(img)
    print(f"[B 连通域] 得到 {len(circles_b)} 块区域：{circles_b}")

    res_c, circles_c = method_c_alt(img)
    print(f"[C ALT   ] 得到 {len(circles_c)} 个圆：{circles_c}")

    compare = hstack_same_height([
        with_title(img, "Original"),
        with_title(res_a, "A: Contour + circle fit"),
        with_title(res_b, "B: Otsu + connectedComponents"),
        with_title(res_c, "C: HOUGH_GRADIENT_ALT"),
    ])
    imwrite_unicode("results/task1_methods_compare.png", compare)

    show("Task 01 - Other Methods", compare, not args.no_show)
    wait_and_close(not args.no_show)


if __name__ == "__main__":
    main()


# ===========================================================================
# 分级提示
# ===========================================================================
# 提示 1  findContours 在 OpenCV 4.x 返回两个值：contours, hierarchy。
#          网上很多老教程写三个返回值，那是 3.x 的写法，会报
#          "too many values to unpack"。
#
# 提示 2  去重不用写太复杂：按半径从大到小排个序，逐个和你已经留下的比，
#          圆心距离 < 0.15 * 半径 且 半径差 < 0.25 * 半径，就当成重复跳过。
#          这个思路和深度学习里的 NMS 是一回事。
#
# 提示 3  B 方法跑出来你会发现盘子没检到——这不是你写错了，
#          是 Otsu 分不开「白盘子」和「浅色桌面」。把这个现象写进文档，
#          正好说明「找边缘」和「找区域」两类方法的区别。
