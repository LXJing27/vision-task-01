# -*- coding: utf-8 -*-
"""生成两张「替代测试图」，让代码在拿到作业原图之前也能先跑通。

为什么需要这个脚本：
作业原作里的两张图（盘子+饼干、两块色卡）在邮件附件里，
手上暂时没有原图时，先用合成的图调试算法。
**拿到原图后，直接用原图覆盖 images/plate.png 和 images/chart.png 即可**，
两个任务脚本都不用改。

运行：python make_demo_images.py
"""

import cv2
import numpy as np

from utils import imwrite_unicode

RNG = np.random.default_rng(20261102)


def make_plate(path="images/plate.png", size=900):
    """画一个俯拍的盘子：浅色桌面 + 白色圆盘 + 盘子里 3 块圆饼干。"""
    img = np.full((size, size, 3), (244, 243, 240), np.uint8)

    center = (size // 2, size // 2)

    # 盘子：外圈阴影 -> 盘面 -> 盘沿
    cv2.circle(img, (center[0] + 8, center[1] + 10), 400, (225, 224, 221), -1, cv2.LINE_AA)
    cv2.circle(img, center, 400, (238, 238, 235), -1, cv2.LINE_AA)
    cv2.circle(img, center, 396, (200, 199, 196), 6, cv2.LINE_AA)
    cv2.circle(img, center, 330, (246, 246, 243), -1, cv2.LINE_AA)
    cv2.circle(img, center, 330, (215, 214, 211), 2, cv2.LINE_AA)

    # 三块饼干的位置和半径（真值，方便后面验证检测精度）
    cookies = [(430, 330, 100), (300, 570, 100), (565, 570, 100)]
    for cx, cy, r in cookies:
        # 阴影
        shadow = img.copy()
        cv2.circle(shadow, (cx + 6, cy + 8), r, (200, 198, 194), -1, cv2.LINE_AA)
        img = cv2.addWeighted(shadow, 0.45, img, 0.55, 0)
        # 饼干本体：中心亮、边缘暗，模拟烘烤的渐变
        for rr in range(r, 0, -1):
            t = rr / r
            color = (int(40 + 30 * t), int(120 + 45 * t), int(200 + 35 * t))
            cv2.circle(img, (cx, cy), rr, color, -1, cv2.LINE_AA)
        # 饼干边缘一圈稍深的烤色
        cv2.circle(img, (cx, cy), r - 2, (35, 105, 190), 4, cv2.LINE_AA)
        # 表面的小孔
        for _ in range(46):
            ang = RNG.uniform(0, 2 * np.pi)
            dist = r * np.sqrt(RNG.uniform(0, 0.75))
            px = int(cx + dist * np.cos(ang))
            py = int(cy + dist * np.sin(ang))
            cv2.circle(img, (px, py), int(RNG.integers(2, 4)), (30, 90, 165), -1, cv2.LINE_AA)

    # 轻微模糊 + 噪声，让它更接近真实拍摄的照片
    img = cv2.GaussianBlur(img, (3, 3), 0)
    noise = RNG.normal(0, 4, img.shape).astype(np.int16)
    img = np.clip(img.astype(np.int16) + noise, 0, 255).astype(np.uint8)

    imwrite_unicode(path, img)
    print("  盘中三块饼干的真实半径都是 100 px，圆心分别：", [(x, y) for x, y, _ in cookies])


def make_chart(path="images/chart.png"):
    """画两块色卡（Outdoor / Indoor），每块 3 行 3 列，用来练 HSV 颜色提取。"""
    patch, gap, margin = 120, 12, 46
    panel_w = 3 * patch + 2 * gap
    panel_h = 3 * patch + 2 * gap
    W = margin * 2 + panel_w * 2 + 90
    H = margin * 2 + panel_h + 44
    img = np.full((H, W, 3), (252, 252, 252), np.uint8)

    # 颜色用 BGR 写：蓝色、黄色是这次要提取的目标
    outdoor = [
        [(232, 231, 230), (38, 141, 236), (189, 101, 32)],    # 白、橙、蓝
        [(48, 40, 200), (75, 170, 45), (120, 55, 25)],        # 红、绿、深蓝
        [(34, 128, 220), (40, 150, 150), (35, 232, 250)],     # 橙、橄榄、黄
    ]
    # Indoor 就是同一套颜色调暗，模拟室内弱光
    indoor = [[tuple(int(c * 0.62) for c in color) for color in row] for row in outdoor]

    for idx, (title, colors) in enumerate([("Outdoor", outdoor), ("Indoor", indoor)]):
        x0 = margin + idx * (panel_w + 90)
        cv2.putText(img, title, (x0, margin - 12), cv2.FONT_HERSHEY_SIMPLEX,
                    0.7, (30, 30, 30), 2, cv2.LINE_AA)
        for r, row in enumerate(colors):
            for c, color in enumerate(row):
                x = x0 + c * (patch + gap)
                y = margin + r * (patch + gap)
                cv2.rectangle(img, (x, y), (x + patch, y + patch), color, -1)
                cv2.rectangle(img, (x, y), (x + patch, y + patch), (200, 200, 200), 1)

    imwrite_unicode(path, img)


if __name__ == "__main__":
    print("生成替代测试图（作业原图到位后直接覆盖同名文件即可）")
    make_plate()
    make_chart()
    print("完成。")
