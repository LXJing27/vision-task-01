# 视觉算法组 · 入门任务 01

两个 OpenCV 练习：霍夫圆检测（找盘子和饼干）、传统视觉基础（读图/灰度 + HSV 取色）。
Python 3.13 + OpenCV 4.11 + VS Code。

## 结果

**任务一** · `images/plate_real.png`（1333×886）

```
盘子 1 个：圆心 (622, 436)，半径 379
饼干 3 个：半径 148 / 155 / 148
```

**任务二** · `images/chart_real.png`（836×431）

```
蓝色 4 块（Outdoor 顶行+中行、Indoor 顶行+中行）
黄色 2 块（Outdoor 底行、Indoor 底行）
```

## 怎么跑

```bash
python task1_hough_circle.py          # 任务一，弹窗显示
python task2_basic_vision.py          # 任务二，弹三个窗口
python task1_hough_circle.py --no-show   # 不弹窗，只输出结果图
```

换图片：`--image images/xxx.png`，或在文件里改 `--image` 的默认值。
结果图都写在 `results/`。

## 参数是怎么定的

真实照片对比度弱，**不能用教科书上的默认值**。下面每个数都是实测扫出来的：

| 参数 | 值 | 为什么 |
|---|---|---|
| 盘子 `param1` | 60 | 白盘压浅背景，边缘弱，太高就描不出边 |
| 盘子 `param2` | 30 | 门槛给 50 就一个圆都检不到 |
| 饼干 `param1` | 50 | 金黄饼干压在米白盘上，灰度只差 11，必须低 |
| 饼干 `param2` | 25 | 小圆票少 |
| 盘子半径 | 0.35~0.55×短边 | 实测半径 379，短边 886，比值 0.43 |
| 饼干半径 | 0.09~0.20×短边 | 实测半径 148~155，比值 0.17 |
| 蓝色 `S` 下限 | 120 | Indoor 那半边偏暗，蓝块 S 只有 150，卡到 200 以上会漏 |
| 黄色 `S` 下限 | 120 | 黄块的 S 都 240 以上，给低点没有副作用 |

真实照片的对比度比想象中弱得多：饼干（灰度 213）和盘子（202）只差 11，
所以 `param1` 必须压到 50 才描得出边缘。换别的照片时这两个参数要重新扫。

## 目录

```
vision-task-01/
├── task1_hough_circle.py     任务一：分尺度两遍霍夫圆
├── task2_basic_vision.py     任务二：灰度 + HSV 取色画框
├── probe_hsv.py              小工具：量某块区域的 HSV 分布，定阈值用
├── pick_rect.py              小工具：鼠标拖框，打印 x y w h
├── utils.py                  读图/显示/拼图的小函数
├── images/                   作业原图（plate_real / chart_real）
├── results/                  程序输出
├── extras/                   参数扫描、三种替代方法（写文档时用）
├── docs/学习过程.md           提交用的文档
└── _reference/               参考实现，被 .gitignore 排除
```

## 环境

```bash
python -m venv .venv
.venv/Scripts/python.exe -m pip install -r requirements.txt
```

VS Code 打开这个文件夹，右下角显示 `.venv (Python 3.13.14)` 即可。

## 三个已经绕过的坑

1. **中文路径**：`cv2.imread` 遇中文名不报错、返回 `None`，然后报
   `'NoneType' object has no attribute 'shape'`，完全指不到原因。用 `imread_unicode`。
2. **`cv2.putText` 写不了中文**，标签统一英文。
3. **`HoughCircles` 检不到时返回 `None`**，直接 `found[0]` 会 `TypeError`，要先判断。
