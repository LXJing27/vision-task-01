# -*- coding: utf-8 -*-
"""用鼠标拖一个框，直接把 x y w h 打出来。

用法：
    python pick_rect.py
    python pick_rect.py --image images/chart.png

操作：
    弹出窗口后按住鼠标左键拖一个矩形，松开
    然后按 空格 或 回车 确认（按 c 取消）
    终端会打印出 x y w h，以及可以直接复制的 probe_hsv 命令
"""

import argparse

import cv2

from utils import imread_unicode


def main():
    parser = argparse.ArgumentParser(description="拖框取坐标")
    parser.add_argument("--image", default="images/chart.png")
    args = parser.parse_args()

    img = imread_unicode(args.image)
    print(f"图片：{args.image}  尺寸 {img.shape[1]}x{img.shape[0]}")
    print("在弹出的窗口里按住左键拖一个矩形，松开后按 空格 确认，按 c 取消。")

    # selectROI 会开一个窗口让你拖框，返回的就是 (x, y, w, h)
    x, y, w, h = cv2.selectROI("drag a box, then press SPACE", img,
                               showCrosshair=True, fromCenter=False)
    cv2.destroyAllWindows()

    if w == 0 or h == 0:
        print("没有选中区域，重新跑一次吧。")
        return

    print(f"\n左上角 x={x}  y={y}  宽 w={w}  高 h={h}")
    print(f"切片写法：hsv[{y}:{y + h}, {x}:{x + w}]")
    print("\n复制这一行去量 HSV：")
    print(f"  python probe_hsv.py --image {args.image} --rect {x} {y} {w} {h}")


if __name__ == "__main__":
    main()
