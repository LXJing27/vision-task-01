# -*- coding: utf-8 -*-
"""任务二：读图/显示/灰度 + HSV 颜色提取。"""

import argparse

import cv2
import numpy as np

from utils import (gray_to_bgr, hstack_same_height, imread_unicode,
                   imwrite_unicode, show, wait_and_close, with_title)

# HSV 阈值：(H下限, S下限, V下限), (H上限, S上限, V上限)
# H 管"是不是这个颜色"，S/V 下限只负责排除"发白/发灰"和"发黑"的像素。
# 注意 S 不能卡太高：真实照片里 Indoor 那半边偏暗，蓝色块的 S 只有 150 左右。
BLUE_LOWER = np.array([100, 120, 70])
BLUE_UPPER = np.array([130, 255, 255])
YELLOW_LOWER = np.array([20, 120, 90])
YELLOW_UPPER = np.array([35, 255, 255])

MIN_AREA = 300      # 小于这个面积的色块当噪声丢掉


def clean_mask(mask, ksize=5):
    """开运算去小白点，闭运算补小黑洞。"""
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (ksize, ksize))
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
    return mask


def extract_color(img_bgr, hsv, lower, upper, name, color):
    """按 HSV 范围取出一类颜色，返回 (掩膜, 画好框的图, 框列表)。"""
    mask = cv2.inRange(hsv, lower, upper)
    mask = clean_mask(mask)

    out = img_bgr.copy()
    boxes = []
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    for c in contours:
        if cv2.contourArea(c) < MIN_AREA:       # 小块当噪声跳过
            continue
        x, y, w, h = cv2.boundingRect(c)
        boxes.append((x, y, w, h))
        cv2.rectangle(out, (x, y), (x + w, y + h), color, 2)
        cv2.putText(out, name, (x, y - 6), cv2.FONT_HERSHEY_SIMPLEX,
                    0.6, color, 2, cv2.LINE_AA)

    print(f"{name}: 找到 {len(boxes)} 块 {boxes}")
    return mask, out, boxes


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--image", default="images/chart_real.png")
    parser.add_argument("--no-show", action="store_true")
    args = parser.parse_args()
    show_window = not args.no_show

    # ---------- 小题 (1)：读图、显示、转灰度 ----------
    img = imread_unicode(args.image)
    print(f"读入图片：{args.image}  尺寸 {img.shape[1]}x{img.shape[0]}  通道数 {img.shape[2]}")

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    imwrite_unicode("results/task2_gray.png", gray)

    original_and_gray = hstack_same_height([
        with_title(img, "1. Original"),
        with_title(gray_to_bgr(gray), "2. Gray"),
    ])
    imwrite_unicode("results/task2_original_and_gray.png", original_and_gray)

    # ---------- 小题 (2)：HSV 颜色提取 ----------
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

    mask_blue, res_blue, boxes_blue = extract_color(
        img, hsv, BLUE_LOWER, BLUE_UPPER, "Blue", (255, 0, 0))
    mask_yellow, res_yellow, boxes_yellow = extract_color(
        img, hsv, YELLOW_LOWER, YELLOW_UPPER, "Yellow", (0, 255, 255))

    imwrite_unicode("results/task2_mask_blue.png", mask_blue)
    imwrite_unicode("results/task2_mask_yellow.png", mask_yellow)

    mask_all = cv2.bitwise_or(mask_blue, mask_yellow)
    imwrite_unicode("results/task2_mask_all.png", mask_all)

    # 最终结果：把所有框画到同一张原图上
    result = img.copy()
    for x, y, w, h in boxes_blue + boxes_yellow:
        cv2.rectangle(result, (x, y), (x + w, y + h), (0, 255, 0), 2)
    imwrite_unicode("results/task2_result.png", result)

    compare = hstack_same_height([
        with_title(img, "1. Original"),
        with_title(gray_to_bgr(gray), "2. Gray"),
        with_title(result, "3. Blue+Yellow boxes"),
        with_title(gray_to_bgr(mask_all), "4. Mask"),
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
