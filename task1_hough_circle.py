# -*- coding: utf-8 -*-

import argparse

import cv2
import numpy as np

from utils import (gray_to_bgr, hstack_same_height, imread_unicode,
                   imwrite_unicode, show, wait_and_close, with_title)

BLUR_KSIZE = (9, 9)
BLUR_SIGMA = 2.0
CANNY_HIGH = 50
PLATE_CANNY_HIGH = 60
PLATE_R_MIN_RATIO = 0.35
PLATE_R_MAX_RATIO = 0.55
PLATE_PARAM2 = 20
COOKIE_R_MIN_RATIO = 0.09
COOKIE_R_MAX_RATIO = 0.20
COOKIE_PARAM2 = 25


def hough_circles(gray, dp, min_dist, param1, param2, r_min, r_max):
    found = cv2.HoughCircles(
        gray, cv2.HOUGH_GRADIENT,
        dp=dp, minDist=min_dist,
        param1=param1, param2=param2,
        minRadius=int(r_min), maxRadius=int(r_max),
    )
    # 一个都没检到时返回的是 None，不是空数组，直接取下标会 TypeError
    if found is None:
        return np.empty((0, 3), dtype=int)
    return np.round(found[0]).astype(int)


def draw_circles(img, circles, color, label, thickness=2):
    for x, y, r in circles:
        x, y, r = int(x), int(y), int(r)
        cv2.circle(img, (x, y), r, color, thickness, cv2.LINE_AA)
        cv2.circle(img, (x, y), 3, color, -1, cv2.LINE_AA)
        cv2.putText(img, label, (x - r, y - 10), cv2.FONT_HERSHEY_SIMPLEX,
                    0.7, color, 2, cv2.LINE_AA)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--image", default="images/plate_real.png")
    parser.add_argument("--no-show", action="store_true")
    args = parser.parse_args()

    img = imread_unicode(args.image)
    h, w = img.shape[:2]
    short = min(h, w)
    print(f"读入图片：{args.image}  尺寸 {w}x{h}（短边 {short}）")

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, BLUR_KSIZE, BLUR_SIGMA)

    # 盘子和饼干的尺寸差 4 倍、边缘强弱也不同，一组参数只能折中，所以分两遍
    plates = hough_circles(
        blur, dp=1.0, min_dist=short * 0.5, param1=PLATE_CANNY_HIGH,
        param2=PLATE_PARAM2,
        r_min=short * PLATE_R_MIN_RATIO, r_max=short * PLATE_R_MAX_RATIO,
    )
    cookies = hough_circles(
        blur, dp=1.0, min_dist=short * 0.16, param1=CANNY_HIGH,
        param2=COOKIE_PARAM2,
        r_min=short * COOKIE_R_MIN_RATIO, r_max=short * COOKIE_R_MAX_RATIO,
    )

    print(f"检测到盘子 {len(plates)} 个：{plates.tolist()}")
    print(f"检测到饼干 {len(cookies)} 个：{cookies.tolist()}")

    result = img.copy()
    draw_circles(result, plates, (255, 0, 0), "Plate")
    draw_circles(result, cookies, (0, 255, 0), "Cookie")
    imwrite_unicode("results/task1_result.png", result)

    edges = cv2.Canny(blur, CANNY_HIGH // 2, CANNY_HIGH)
    steps = hstack_same_height([
        with_title(gray_to_bgr(gray), "1. Gray"),
        with_title(gray_to_bgr(edges), "2. Canny"),
        with_title(result, "3. Result"),
    ])
    imwrite_unicode("results/task1_steps.png", steps)

    show("Task 01 Result", result, not args.no_show)
    wait_and_close(not args.no_show)


if __name__ == "__main__":
    main()
