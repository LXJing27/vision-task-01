# -*- coding: utf-8 -*-
"""任务二：读图/显示/灰度 + HSV 颜色提取。要写的地方标了 TODO 1~5。"""

import argparse

import cv2
import numpy as np

from utils import (gray_to_bgr, hstack_same_height, imread_unicode,
                   imwrite_unicode, show, wait_and_close, with_title)

# HSV 阈值，格式是 (H下限, S下限, V下限), (H上限, S上限, V上限)
# 这组只卡了 H，叫「宽松版」，先按这个跑通，再想办法收紧。
BLUE_LOWER = np.array([100, 120, 70])
BLUE_UPPER = np.array([130, 255, 255])
YELLOW_LOWER = np.array([20, 120, 120])
YELLOW_UPPER = np.array([35, 255, 255])

MIN_AREA = 300      # 小于这个面积的色块当噪声丢掉


def clean_mask(mask, ksize=5):
    """形态学清理：先开运算去掉小白点，再闭运算补掉小黑洞。已写好。"""
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (ksize, ksize))
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
    return mask


def extract_color(img_bgr, hsv, lower, upper, name, color):
    """按 HSV 范围取出一类颜色，返回 (掩膜, 画好框的图, 框列表)。"""
    # TODO 4：mask = cv2.inRange(hsv, lower, upper)，再过一遍 clean_mask()。
    # TODO 5：在掩膜上 findContours，对每个轮廓：
    #   cv2.contourArea 小于 MIN_AREA 的丢掉 → cv2.boundingRect 求 (x, y, w, h)
    #   → cv2.rectangle 画框 + cv2.putText 写 name。
    #   注意 findContours 在 4.x 返回两个值 (contours, hierarchy)，不是三个。
    raise NotImplementedError("TODO 4 + 5: inRange、形态学、找轮廓、画框")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--image", default="images/chart.png")
    parser.add_argument("--no-show", action="store_true")
    args = parser.parse_args()
    show_window = not args.no_show

    # ---------- 小题 (1)：读图、显示、转灰度 ----------
    img = imread_unicode(args.image)
    print(f"读入图片：{args.image}  尺寸 {img.shape[1]}x{img.shape[0]}  通道数 {img.shape[2]}")

    # TODO 1：把 img 转成灰度图存到 gray。查一下 cvtColor 的转换码叫什么。
    gray = None
    raise NotImplementedError("TODO 1: 把 img 转成灰度图存到 gray")

    imwrite_unicode("results/task2_gray.png", gray)

    # TODO 2：把原图和灰度图并排拼起来，两张同时显示。
    #   现成的三个工具：gray_to_bgr(灰度图)、with_title(图, "英文标题")、
    #   hstack_same_height([图1, 图2])。
    original_and_gray = None
    raise NotImplementedError("TODO 2: 拼出「原图 + 灰度」的对照图")
    imwrite_unicode("results/task2_original_and_gray.png", original_and_gray)

    # ---------- 小题 (2)：HSV 颜色提取 ----------
    # TODO 3：转 HSV。转换码是 cv2.COLOR_BGR2HSV（OpenCV 读进来就是 BGR，不是 RGB）。
    hsv = None
    raise NotImplementedError("TODO 3: 转成 HSV")

    mask_blue, res_blue, boxes_blue = extract_color(
        img, hsv, BLUE_LOWER, BLUE_UPPER, "Blue", (0, 255, 0))
    mask_yellow, res_yellow, boxes_yellow = extract_color(
        img, hsv, YELLOW_LOWER, YELLOW_UPPER, "Yellow", (0, 255, 0))

    imwrite_unicode("results/task2_mask_blue.png", mask_blue)
    imwrite_unicode("results/task2_mask_yellow.png", mask_yellow)

    mask_all = cv2.bitwise_or(mask_blue, mask_yellow)
    imwrite_unicode("results/task2_mask_all.png", mask_all)

    result = img.copy()
    for x, y, w, h in boxes_blue + boxes_yellow:
        cv2.rectangle(result, (x, y), (x + w, y + h), (0, 255, 0), 2)
    imwrite_unicode("results/task2_result.png", result)

    compare = hstack_same_height([
        with_title(img, "1. Original"),
        with_title(gray_to_bgr(gray), "2. Gray"),
        with_title(result, "3. Blue+Yellow boxes"),
        with_title(gray_to_bgr(mask_all), "4. Mask (blue|yellow)"),
    ])
    imwrite_unicode("results/task2_compare.png", compare)

    # ---------- 显示 ----------
    if show_window:
        def on_mouse(event, x, y, flags, param):
            if event == cv2.EVENT_LBUTTONDOWN:
                b, g, r = img[y, x]
                h, s, v = hsv[y, x]
                print(f"  (x={x}, y={y})  BGR=({b},{g},{r})  HSV=({h},{s},{v})")

        show("Task 02 - Original & Gray", original_and_gray)
        cv2.setMouseCallback("Task 02 - Original & Gray", on_mouse)
        show("Task 02 - Result", result)
        show("Task 02 - Masks", hstack_same_height([
            with_title(gray_to_bgr(mask_blue), "Blue mask"),
            with_title(gray_to_bgr(mask_yellow), "Yellow mask"),
            with_title(gray_to_bgr(mask_all), "Blue | Yellow"),
        ]))
        print("\n小提示：在窗口里点像素能看到它的 HSV，照着改文件开头的阈值。")
        wait_and_close(True)


if __name__ == "__main__":
    main()
