# -*- coding: utf-8 -*-
"""任务二：传统视觉基础 —— 读图/显示/灰度 + HSV 颜色提取。

====================================================================
【这是骨架文件】需要你写 TODO 1~5。做完一处跑一次。
====================================================================

两个小题：
(1) 用 OpenCV 读一张图，在窗口里显示，再转成灰度图，两张同时显示；
(2) 转到 HSV 颜色空间，把「蓝色」和「黄色」的区域抠出来，用矩形框标出来。

为什么要用 HSV 而不是直接卡 RGB？想清楚这个问题再动手（文档里要写）。
提示：同一个蓝色在太阳底下和在阴影里，RGB 三个数都变了；
      但「它是什么颜色」这件事其实没变。
      H 色相 / S 饱和度 / V 明度 分别管什么？去查文档，别背。

运行：python task2_basic_vision.py
运行后鼠标点一下窗口里的像素，终端会打印那个点的 BGR 和 HSV，
这就是调 inRange 范围最实用的办法。
"""

import argparse

import cv2
import numpy as np

from utils import (gray_to_bgr, hstack_same_height, imread_unicode,
                   imwrite_unicode, show, wait_and_close, with_title)

# ---------------------------------------------------------------------------
# HSV 阈值，格式是 (H下限, S下限, V下限), (H上限, S上限, V上限)
# 下面这组只卡了 H（色相），叫「宽松版」。先按这个跑通，再想办法收紧。
# ---------------------------------------------------------------------------
BLUE_LOWER = np.array([100, 120, 70])
BLUE_UPPER = np.array([130, 255, 255])
YELLOW_LOWER = np.array([20, 120, 120])
YELLOW_UPPER = np.array([35, 255, 255])

MIN_AREA = 300      # 小于这个面积的色块当噪声丢掉


def clean_mask(mask, ksize=5):
    """形态学清理：先开运算去掉小白点，再闭运算补掉小黑洞。已经写好了。"""
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (ksize, ksize))
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
    return mask


def extract_color(img_bgr, hsv, lower, upper, name, color):
    """按 HSV 范围取出一类颜色，返回 (掩膜, 画好框的图, 框列表)。

    【TODO 4】+【TODO 5】都写在这个函数里：
      TODO 4  inRange 得到掩膜 → 调 clean_mask() 清理
      TODO 5  在掩膜上 findContours，对每个轮廓：
                - cv2.contourArea 小于 MIN_AREA 的丢掉
                - cv2.boundingRect 求出最贴合的矩形 (x, y, w, h)
                - cv2.rectangle 画框，cv2.putText 写字
            最后画完的图返回，框的列表也返回（main 里要拼总图）。
    提示：findContours 在 OpenCV 4.x 返回两个值 (contours, hierarchy)，
          不是三个，网上老教程里的三个返回值是 3.x 的写法。
    """
    raise NotImplementedError("TODO 4 + 5: inRange、形态学、找轮廓、画框")


def main():
    parser = argparse.ArgumentParser(description="任务二：读图显示 + HSV 颜色提取")
    parser.add_argument("--image", default="images/chart.png")
    parser.add_argument("--no-show", action="store_true")
    args = parser.parse_args()
    show_window = not args.no_show

    # ---------- 小题 (1)：读图、显示、转灰度 ----------
    img = imread_unicode(args.image)
    print(f"读入图片：{args.image}  尺寸 {img.shape[1]}x{img.shape[0]}  通道数 {img.shape[2]}")

    # 【TODO 1】转灰度。查一下 cv2.cvtColor 的颜色转换码叫什么。
    gray = None
    raise NotImplementedError("TODO 1: 把 img 转成灰度图存到 gray")

    imwrite_unicode("results/task2_gray.png", gray)

    # 【TODO 2】把原图和灰度图并排拼起来，两张同时显示。
    # 已经给你两个工具函数：gray_to_bgr(灰度图) 把灰度转回三通道，
    # with_title(图, "英文标题") 在图上加一条标题，hstack_same_height([图1, 图2]) 横向拼。
    original_and_gray = None
    raise NotImplementedError("TODO 2: 拼出「原图 + 灰度」的对照图")
    imwrite_unicode("results/task2_original_and_gray.png", original_and_gray)

    # ---------- 小题 (2)：HSV 颜色提取 ----------
    # 【TODO 3】转 HSV。注意转换码是 cv2.COLOR_BGR2HSV（不是 RGB2HSV，OpenCV 读进来就是 BGR）。
    hsv = None
    raise NotImplementedError("TODO 3: 转成 HSV")

    mask_blue, res_blue, boxes_blue = extract_color(
        img, hsv, BLUE_LOWER, BLUE_UPPER, "Blue", (0, 255, 0))
    mask_yellow, res_yellow, boxes_yellow = extract_color(
        img, hsv, YELLOW_LOWER, YELLOW_UPPER, "Yellow", (0, 255, 0))

    imwrite_unicode("results/task2_mask_blue.png", mask_blue)
    imwrite_unicode("results/task2_mask_yellow.png", mask_yellow)

    # 两张掩膜叠起来 = 「蓝 + 黄」的总掩膜
    mask_all = cv2.bitwise_or(mask_blue, mask_yellow)
    imwrite_unicode("results/task2_mask_all.png", mask_all)

    # 最终结果：把所有框画到原图上
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
        cv2.setMouseCallback("Task 02 - Original & Gray", on_mouse,
                             {"img": img, "hsv": hsv})
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


# ===========================================================================
# 分级提示
# ===========================================================================
# 提示 1  转灰度：cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
#          转 HSV：cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
#
# 提示 2  inRange 的用法：cv2.inRange(hsv, lower, upper)
#          返回一张黑白图，落在范围内的像素是 255，其余是 0。
#
# 提示 3  只卡 H 会框多——同一色系里偏暗的那块（深蓝、橄榄）H 只差 2~3，
#          光靠 H 分不开。想一想 S 和 V 的下限各能排除什么：
#          S 小 = 发白/发灰，V 小 = 发黑。
#          自己试着把 S、V 下限往上抬，看框的数量怎么变。
#
# 提示 4  收紧阈值之后，你会发现 Indoor 那半边整组都丢了。
#          为什么？去看两半边同一块颜色的 V 值差多少。
#          这个现象就是传统颜色阈值最典型的坑，文档里一定要写。
