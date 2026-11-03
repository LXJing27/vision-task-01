# -*- coding: utf-8 -*-
"""任务一：用霍夫圆检测找出盘子和饼干，并标注出来。要写的地方标了 TODO 1~5。"""

import argparse

import cv2
import numpy as np

from utils import (gray_to_bgr, hstack_same_height, imread_unicode,
                   imwrite_unicode, show, wait_and_close, with_title)

# 参数起点：这些数字只是能跑起来的初值，不是答案，你要自己扫出合适的一档。
BLUR_KSIZE = (9, 9)
BLUR_SIGMA = 2.0
CANNY_HIGH = 120           # 饼干：深褐压白盘，对比强，可以给高
PLATE_CANNY_HIGH = 70      # 盘子：白盘压浅桌面，对比弱，必须给低
PLATE_R_MIN_RATIO = 0.30   # 半径按「图片短边的比例」算，换分辨率不用改
PLATE_R_MAX_RATIO = 0.50
PLATE_PARAM2 = 60          # 盘子的投票门槛，要高一点压掉假圆
COOKIE_R_MIN_RATIO = 0.08
COOKIE_R_MAX_RATIO = 0.17
COOKIE_PARAM2 = 32         # 饼干的投票门槛，小圆票本来就少，得低


def hough_circles(gray, dp, min_dist, param1, param2, r_min, r_max):
    """封装 cv2.HoughCircles，统一返回 [[x, y, r], ...] 的 int 数组。"""
    # TODO 1：调 cv2.HoughCircles，检测方法用 cv2.HOUGH_GRADIENT。
    #   没找到圆时它返回 None，直接 found[0] 会 TypeError → 要先判断，
    #   没找到就 return np.empty((0, 3), dtype=int)。
    #   找到时返回 [[[x, y, r], ...]]，比我们要的多一层，取 found[0]。
    #   坐标是小数，用 np.round(...).astype(int) 转整数。
    raise NotImplementedError("TODO 1: 实现 hough_circles()")


def draw_circles(img, circles, color, label, thickness=2):
    """在图上画圆 + 圆心 + 标签。颜色是 BGR。"""
    # TODO 2：cv2.circle(img, 圆心, 半径, 颜色, 线宽)，线宽给 -1 是实心点；
    #   cv2.putText(img, 文字, 左下角坐标, 字体, 字号, 颜色, 线宽)。
    #   字号 0.7、位置 (x - r, y - 10)。putText 写不了中文，标签用 Plate / Cookie。
    raise NotImplementedError("TODO 2: 实现 draw_circles()")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--image", default="images/plate.png")
    parser.add_argument("--no-show", action="store_true")
    args = parser.parse_args()

    img = imread_unicode(args.image)
    h, w = img.shape[:2]
    short = min(h, w)
    print(f"读入图片：{args.image}  尺寸 {w}x{h}（短边 {short}）")

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, BLUR_KSIZE, BLUR_SIGMA)

    # TODO 3：调 hough_circles() 找盘子。
    #   半径上下限 = PLATE_R_*_RATIO * short。
    #   param1 该传 PLATE_CANNY_HIGH 还是 CANNY_HIGH？想想两张图的边缘对比度。
    #   调不通时先把 param2 往小调，先让它检出东西，再往大调压假圆。
    plates = None
    raise NotImplementedError("TODO 3: 调用 hough_circles() 找盘子（要先做完 TODO 1）")

    # TODO 4：再调一次，半径范围只覆盖饼干。想一想为什么 minDist 和盘子那遍不一样。
    cookies = None
    raise NotImplementedError("TODO 4: 调用 hough_circles() 找饼干（TODO 3 做完再动这里）")

    print(f"检测到盘子 {len(plates)} 个：{plates.tolist()}")
    print(f"检测到饼干 {len(cookies)} 个：{cookies.tolist()}")

    # TODO 5：result = img.copy()，蓝圈标 Plate、绿圈标 Cookie，
    #   存 results/task1_result.png。
    #   再拼一张三步对照图（灰度 / 边缘 / 结果），
    #   边缘用 cv2.Canny(blur, CANNY_HIGH // 2, CANNY_HIGH)。
    raise NotImplementedError("TODO 5: 把圆画到图上并保存结果")

    # TODO 5 做完后取消下面两行的注释就能弹窗
    # show("Task 01 Result", result, not args.no_show)
    # wait_and_close(not args.no_show)


if __name__ == "__main__":
    main()
