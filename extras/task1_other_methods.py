# -*- coding: utf-8 -*-
"""任务一（2）：除了霍夫圆检测，还有哪些办法能把圆找出来？

====================================================================
【这是骨架文件】方法 A 必须自己写（TODO 1），B、C 选做一个就够。
方法 A 写通了，B 和 C 你自然就知道怎么改。
====================================================================

三条路子的思路（先想清楚原理再写代码）：

A. 边缘 -> 轮廓 -> 最小外接圆 -> 圆度筛选
   把边缘连成一条条闭合曲线（轮廓），给每条轮廓套一个最小的圆，
   再用「圆度」判断它像不像圆。圆度 = 4π*面积 / 周长²，正圆是 1，
   方形约 0.785，细长条趋近 0。
   **先想一个问题**：一个圆，它的「外边」和「里边」是不是两条轮廓？
   那会不会被数成两个圆？怎么去重？

B. Otsu 二值化 -> 连通域 -> 外接矩形 -> 筛选
   不找边，直接把「比背景暗的整块东西」抠出来。
   Otsu 是自动找阈值的办法：遍历所有阈值，选让前景背景差别最大的那个。
   想一想：白盘子和浅色桌面差得很少，这个方法能不能把盘子分出来？

C. HOUGH_GRADIENT_ALT
   还是霍夫，但换了更严的判据：边缘的梯度方向要和半径方向一致。

运行：python task1_other_methods.py
"""

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


def method_a_contour(img, min_circ=0.80):
    """A：边缘 -> 轮廓 -> 最小外接圆 + 圆度筛选。

    【TODO 1】步骤提示：
      1) 转灰度、高斯模糊（和任务一一样）
      2) cv2.Canny 求边缘
      3) 用 cv2.morphologyEx(..., cv2.MORPH_CLOSE, kernel) 把断开的边连起来
         —— 不做这一步，轮廓不闭合，面积就不准
      4) cv2.findContours 拿到所有轮廓（用 cv2.RETR_LIST，里外两条都要）
      5) 对每条轮廓：circularity(c) 大于 min_circ 才留；
         面积太小（比如 < 500）的直接丢
      6) cv2.minEnclosingCircle 求出圆心和半径，画出来
      7) 去重：圆心离得近、半径又差不多的是同一个圆，只留一个
    返回：(画好的图, [(x, y, r), ...])
    """
    raise NotImplementedError("TODO 1: 实现轮廓法")


def method_b_connected(img):
    """B：Otsu 二值化 -> 连通域 -> 外接矩形 -> 筛选。（选做）

    【TODO 2】提示：
      cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
      注意要用 INV，这样「暗的物体」才会变成白色前景。
      然后 cv2.connectedComponentsWithStats 拿到每个连通域的中心、外接框、面积。
    """
    raise NotImplementedError("TODO 2（选做）: 实现连通域法")


def method_c_alt(img):
    """C：HOUGH_GRADIENT_ALT。（选做）

    【TODO 3】提示：还是 cv2.HoughCircles，但第二个参数换成 cv2.HOUGH_GRADIENT_ALT，
    dp 给 1.5 左右，param1 给 300 左右，param2 这次是 0~1 的小数（0.8~0.9）。
    """
    raise NotImplementedError("TODO 3（选做）: 实现 ALT 版本")


def main():
    parser = argparse.ArgumentParser(description="任务一(2)：其他识别圆的方法")
    parser.add_argument("--image", default="images/plate_real.png")
    parser.add_argument("--no-show", action="store_true")
    args = parser.parse_args()

    img = imread_unicode(args.image)
    print(f"读入图片：{args.image}  尺寸 {img.shape[1]}x{img.shape[0]}")

    res_a, circles_a = method_a_contour(img)
    print(f"[A 轮廓法] 得到 {len(circles_a)} 个圆：{circles_a}")

    # B、C 做完后把下面两行取消注释，并加进对比图
    # res_b, circles_b = method_b_connected(img)
    # res_c, circles_c = method_c_alt(img)

    compare = hstack_same_height([
        with_title(img, "Original"),
        with_title(res_a, "A: Contour + minEnclosingCircle"),
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
