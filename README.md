# 视觉算法组 · 入门任务 01

两个 OpenCV 练习：霍夫圆检测（找盘子和饼干）、传统视觉基础（读图/灰度 + HSV 取色）。
Python 3.13 + OpenCV 4.11 + VS Code。

## 状态

两个任务都还是骨架，算法部分自己写。需要填的地方一共 10 处：

| 文件 | TODO | 要写的东西 |
|---|---|---|
| `task1_hough_circle.py` | 1 | 封装 `cv2.HoughCircles`（处理 None 和多余维度） |
| | 2 | 画圆 + 圆心 + 英文标签 |
| | 3 | 第一遍检测：盘子 |
| | 4 | 第二遍检测：饼干 |
| | 5 | 画图、存结果、拼三步对照图 |
| `task2_basic_vision.py` | 1 | 转灰度 |
| | 2 | 原图和灰度并排显示 |
| | 3 | 转 HSV |
| | 4 | `inRange` 得掩膜 + 形态学清理 |
| | 5 | 找轮廓、算外接矩形、画框写字 |

每处上方都有要点提示，每处做完先把那行 `raise NotImplementedError(...)` 删掉再跑。

## 目录

```
vision-task-01/
├── task1_hough_circle.py     任务一（1），骨架
├── task2_basic_vision.py     任务二，骨架
├── probe_hsv.py              小工具：量某块区域的 HSV，帮你定阈值
├── utils.py                  读图/显示/拼图的小函数，直接用
├── make_demo_images.py       生成替代测试图（有原图后用不上）
├── images/                   测试图
├── results/                  程序输出的图
├── extras/                   选做：参数扫描、三种方法对比（写文档时才用）
├── docs/学习过程.md           提交用的文档，待按你的实现核对
└── _reference/               完整答案，被 .gitignore 排除，卡住了再看
```

## 环境

已经装好了。要重建：

```bash
python -m venv .venv
source .venv/Scripts/activate
pip install -r requirements.txt
```

VS Code 打开这个文件夹，右下角应显示 `.venv (Python 3.13.14)`。
不是就 `Ctrl+Shift+P` → `Python: Select Interpreter` → 选 `./.venv/Scripts/python.exe`。

## 怎么跑

```bash
python task1_hough_circle.py    # 任务一
python task2_basic_vision.py    # 任务二
python probe_hsv.py --image images/chart.png    # 量 HSV
```

加 `--no-show` 不弹窗只出图。窗口跑完按任意键结束。

## 卡住时的顺序

1. 看那个函数上面的提示，再看文件末尾的「分级提示」
2. 一次只改一个参数，跑一次看结果怎么变
3. 卡够 20 分钟再看 `_reference/`，而且只看一个函数，看完合上自己重写

## 两个已经绕过的坑

1. **中文路径**：`cv2.imread` 遇中文路径不报错、返回 `None`，
   之后报 `'NoneType' object has no attribute 'shape'`，完全指不到原因。
   用 `utils.py` 里的 `imread_unicode` 读图。
2. **`cv2.putText` 写不了中文**，标签统一用英文（Plate / Cookie / Blue / Yellow）。
