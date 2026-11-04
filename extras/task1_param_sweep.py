# -*- coding: utf-8 -*-
"""参数扫描：把盘子的 Canny 阈值 param1 从低到高扫一遍，看抓到的圆怎么变。

为什么值得写这个：调参不要靠猜。固定其它参数，只动一个，
把每一档的结果并排画出来，分界点一眼就能看到。
这张图放进文档里，比写十句「我反复调试」有说服力。

运行：python task1_param_sweep.py
输出：results/task1_param_sweep.png（3x3 九宫格）
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import argparse

import cv2
import numpy as np

from utils import imread_unicode, imwrite_unicode, with_title

PARAM1_LIST = [20, 30, 40, 50, 60, 70, 85, 100, 130]
PLATE_PARAM2 = 20
PLATE_R_MIN_RATIO = 0.35
PLATE_R_MAX_RATIO = 0.55


def main():
    parser = argparse.ArgumentParser(description="盘子检测的 param1 扫描")
    parser.add_argument("--image", default="images/plate_real.png")
    args = parser.parse_args()

    img = imread_unicode(args.image)
    short = min(img.shape[:2])
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (9, 9), 2.0)

    tiles = []
    for p1 in PARAM1_LIST:
        found = cv2.HoughCircles(
            blur, cv2.HOUGH_GRADIENT,
            dp=1.0, minDist=short * 0.5,
            param1=p1, param2=PLATE_PARAM2,
            minRadius=int(short * PLATE_R_MIN_RATIO),
            maxRadius=int(short * PLATE_R_MAX_RATIO),
        )
        circles = [] if found is None else np.round(found[0]).astype(int)

        tile = img.copy()
        for x, y, r in circles:
            cv2.circle(tile, (x, y), r, (255, 0, 0), 2, cv2.LINE_AA)
            cv2.putText(tile, f"R={r} ({x},{y})", (x - 180, y - r + 40),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 0), 2, cv2.LINE_AA)

        desc = "none" if len(circles) == 0 else f"R={circles[0][2]}"
        tiles.append(with_title(tile, f"param1={p1}, {desc}"))
        print(f"param1={p1:3d} -> {'没检出' if len(circles) == 0 else circles.tolist()}")

    rows = [np.hstack(tiles[i:i + 3]) for i in range(0, 9, 3)]
    grid = np.vstack(rows)
    imwrite_unicode("results/task1_param_sweep.png", grid)


if __name__ == "__main__":
    main()
