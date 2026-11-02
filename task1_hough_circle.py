# -*- coding: utf-8 -*-
"""任务一（1）：用霍夫圆检测找出盘子和盘中的饼干，并把圆标注出来。

====================================================================
【这是骨架文件】
已经给好的：读图、转灰度、高斯模糊、命令行参数、显示与保存。
需要你自己写的：标了 TODO 1~5 的五处。做完一处就跑一次，看结果变没变。
卡住了先看文件末尾的「分级提示」，还不行再来问。
====================================================================

原理提示（先自己想，别急着找现成代码）
--------------------------------------
霍夫圆不是「去找一个圆」，而是「让每个边缘点投票」：
边缘上每个点都在猜「如果圆心在我附近这个位置、半径是 r，那这个圆成立」，
每猜一次就给那个圆投一票。所有点投完，票数超过门槛的就是真的圆。
参数 param2 就是这个「票数门槛」。

需要想清楚的三件事
------------------
1. 盘子半径 400 左右、饼干半径 100 左右，差 4 倍。
   只调用一次、只给一组参数，能不能同时照顾这两种大小的圆？先试，会出问题。
2. 盘子的边是「白盘子压在浅色桌面上」，明暗差很小；
   饼干和盘子对比很强。这两种边，用同一个边缘阈值合适吗？
3. 半径要不要写死成像素值？换一张 4000x3000 的照片会怎么样？

运行：python task1_hough_circle.py
"""

import argparse

import cv2
import numpy as np

from utils import (gray_to_bgr, hstack_same_height, imread_unicode,
                   imwrite_unicode, show, wait_and_close, with_title)

# ---------------------------------------------------------------------------
# 参数区：TODO 3 / TODO 4 会用到。
# 下面这些数字是「起点」，不是答案，你要自己扫出合适的那一档。
# ---------------------------------------------------------------------------
BLUR_KSIZE = (9, 9)       # 高斯模糊核大小，1~21 都可以试试，看圆心准不准
BLUR_SIGMA = 2.0

CANNY_HIGH = 120          # 饼干的边缘阈值（对比强，可以给高）
PLATE_CANNY_HIGH = 70     # 盘子的边缘阈值（对比弱，得给低）

PLATE_R_MIN_RATIO = 0.30  # 盘子最小半径 = 图片短边 * 这个数
PLATE_R_MAX_RATIO = 0.50
PLATE_PARAM2 = 60         # 盘子的投票门槛

COOKIE_R_MIN_RATIO = 0.08  # 饼干半径范围
COOKIE_R_MAX_RATIO = 0.17
COOKIE_PARAM2 = 32        # 饼干的投票门槛，比盘子低（小圆的票本来就少）


def hough_circles(gray, dp, min_dist, param1, param2, r_min, r_max):
    """把 cv2.HoughCircles 包一层，统一返回 [[x, y, r], ...] 这样的数组。

    【TODO 1】实现这个函数。注意这几件事：
      - cv2.HoughCircles 的参数名和这里的参数名不完全一样，自己对应；
      - 检测方法用 cv2.HOUGH_GRADIENT；
      - 它没找到圆时返回 None，直接 found[0] 会 TypeError，先判断，
        没找到就返回 np.empty((0, 3), dtype=int)；
      - 它返回 [[[x, y, r], ...]]，比我们要的多一层，记得取 found[0]；
      - 坐标是小数，用 np.round(...).astype(int) 转整数，画图方便。
    """
    raise NotImplementedError("TODO 1: 实现 hough_circles()")


def draw_circles(img, circles, color, label, thickness=2):
    """在图上画圆 + 圆心 + 文字标签。颜色是 BGR，蓝色写 (255, 0, 0)。

    【TODO 2】实现这个函数。会用到的两个函数：
      - cv2.circle(img, 圆心, 半径, 颜色, 线宽)  线宽给 -1 是实心，适合画圆心那一点
      - cv2.putText(img, 文字, 左下角坐标, 字体, 字号, 颜色, 线宽)
    字号 0.7、线宽 2、位置放 (x - r, y - 10) 附近比较好看。
    注意：cv2.putText 写不了中文，标签只用英文（Plate / Cookie）。
    """
    raise NotImplementedError("TODO 2: 实现 draw_circles()")


def main():
    parser = argparse.ArgumentParser(description="任务一：霍夫圆检测")
    parser.add_argument("--image", default="images/plate.png", help="要检测的图片")
    parser.add_argument("--no-show", action="store_true", help="不弹出显示窗口")
    args = parser.parse_args()
    show_window = not args.no_show

    img = imread_unicode(args.image)
    h, w = img.shape[:2]
    short = min(h, w)
    print(f"读入图片：{args.image}  尺寸 {w}x{h}（短边 {short}）")

    # ---- 这两步已经写好了，先看懂它们在干什么再往下 ----
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)           # 转灰度
    blur = cv2.GaussianBlur(gray, BLUR_KSIZE, BLUR_SIGMA)   # 高斯模糊

    # ---- 【TODO 3】找盘子 ----
    # 调一次 hough_circles()，半径限制在「盘子那么大」的范围。
    # 想一想：param1 该传 PLATE_CANNY_HIGH 还是 CANNY_HIGH？为什么？
    #         半径上下限是 PLATE_R_MIN_RATIO / PLATE_R_MAX_RATIO 乘 short。
    #         调不通时先把 param2 往小调，让它先检出东西，再往大调压假圆。
    plates = None
    raise NotImplementedError("TODO 3: 调用 hough_circles() 找盘子（要先做完 TODO 1）")

    # ---- 【TODO 4】找饼干 ----
    # 再调一次，这次的半径范围只覆盖饼干。
    # 想一想：为什么两遍的 minDist 不一样？
    cookies = None
    raise NotImplementedError("TODO 4: 调用 hough_circles() 找饼干（TODO 3 做完再动这里）")

    print(f"检测到盘子 {len(plates)} 个：{plates.tolist()}")
    print(f"检测到饼干 {len(cookies)} 个：{cookies.tolist()}")

    # ---- 【TODO 5】画出来并保存 ----
    # 1) result = img.copy()
    # 2) draw_circles(result, plates, 蓝色, "Plate")
    # 3) draw_circles(result, cookies, 绿色, "Cookie")
    # 4) imwrite_unicode("results/task1_result.png", result)
    # 5) 再用 hstack_same_height + with_title 拼一张三步对照图：
    #    灰度 / 边缘 / 结果，边缘图用 cv2.Canny(blur, CANNY_HIGH // 2, CANNY_HIGH)
    raise NotImplementedError("TODO 5: 把圆画到图上并保存结果")

    # TODO 5 做完后，取消下面两行的注释就能弹窗看结果
    # show("Task 01 Result", result, show_window)
    # wait_and_close(show_window)


if __name__ == "__main__":
    main()


# ===========================================================================
# 分级提示：看一条想一会儿再往下，别一次全看完
# ===========================================================================
# 提示 1  霍夫圆的六个参数各管什么？
#          dp        累加器分辨率，1 就是和原图同精度，先用 1
#          minDist   两个圆心至少隔多远，防止同一个圆被重复检出
#          param1    Canny 边缘检测的高阈值
#          param2    投票门槛，越小越容易检出、也越容易误检
#          minRadius 只找这个半径以上的圆
#          maxRadius 只找这个半径以下的圆
#
# 提示 2  只调用一次、半径范围放到 0.05~0.55 会怎样？自己试：
#          param1=70、param2=30 时，除了 4 个真圆，还会多出半径 300 左右的假圆
#          （盘子内圈那圈阴影边凑够票了）。把 param2 抬到 60 就没了，
#          但这时门槛对半径 100 的饼干来说偏高，换张图容易漏。
#
# 提示 3  两遍检测的 minDist 不一样，是因为盘子只有一个、离边远；
#          饼干有三个、彼此挨得近，minDist 给大了会把相邻的饼干吞掉一个。
#
# 提示 4  还是卡住，就去打开 vision-task-01-reference/ 里的参考实现看一眼，
#          但看完要合上自己重敲。直接抄的话，文档里那些数据你解释不出来。
