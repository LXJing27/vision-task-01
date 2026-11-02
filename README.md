# 视觉算法组 · 入门任务 01（霍夫圆检测 + 传统视觉基础）

OpenCV 入门练习：用霍夫圆检测找出盘子和饼干，用 HSV 颜色空间提取色卡上的蓝色和黄色。
语言用 Python，环境用 venv + VS Code。

**当前状态：骨架阶段。** 脚本里标了 `TODO 1~5` 的地方还没写，
每个 TODO 上面都写了要点提示，文件末尾还有「分级提示」。

## 怎么推进

1. 打开 `task1_hough_circle.py`，从 TODO 1 开始写。
2. **每完成一处，先把那行 `raise NotImplementedError(...)` 删掉**，再跑一次看结果。
3. 结果是错的也别急着改代码，先想「错在哪一步」：灰度图对不对？边缘图对不对？再往下。
4. 每完成一个 TODO 就 `git commit` 一次，历史里能看出你是怎么推进的。

## TODO 清单

| 文件 | TODO | 要做的事 |
|---|---|---|
| `task1_hough_circle.py` | 1 | 封装 `cv2.HoughCircles`，处理返回 None 和多余的维度 |
| | 2 | 画圆 + 圆心 + 英文标签 |
| | 3 | 第一遍：找盘子（半径范围和阈值都和饼干不一样） |
| | 4 | 第二遍：找饼干 |
| | 5 | 画到图上、存结果、拼三步对照图 |
| `task1_param_sweep.py` | 1 | 循环里调一次 HoughCircles（九宫格拼图已写好） |
| `task1_other_methods.py` | 1 | 方法 A：边缘 → 轮廓 → 最小外接圆 → 圆度筛选 → 去重 |
| | 2、3 | 方法 B / C（选做一个） |
| `task2_basic_vision.py` | 1 | 转灰度 |
| | 2 | 原图和灰度并排显示 |
| | 3 | 转 HSV |
| | 4 | `inRange` 得到掩膜 + 形态学清理 |
| | 5 | 找轮廓、算外接矩形、画框写字 |

## 目录结构

```
vision-task-01/
├── images/                      测试图片（plate.png 盘子饼干、chart.png 色卡）
├── results/                     程序输出的结果图（现在只有 .gitkeep）
├── docs/学习过程.md              提交用的学习过程文档（待按你的实现核对）
├── utils.py                     公共小工具（中文路径读写图、显示窗口、拼图）—— 已给好
├── make_demo_images.py          生成替代测试图 —— 已给好，拿到作业原图后不用它
├── task1_hough_circle.py        任务一(1)：霍夫圆检测
├── task1_param_sweep.py         任务一(1)：参数扫描九宫格
├── task1_other_methods.py       任务一(2)：轮廓法 / 连通域法 / ALT 版本
├── task2_basic_vision.py        任务二：读图显示 + 灰度 + HSV 蓝黄提取
├── requirements.txt             依赖
└── README.md
```

## 环境准备

```bash
# 1. 建虚拟环境（用你自己装的 Python 3.13）
python -m venv .venv

# 2. 激活（Windows / Git Bash）
source .venv/Scripts/activate
# PowerShell 用： .venv\Scripts\Activate.ps1
# CMD 用：        .venv\Scripts\activate.bat

# 3. 装依赖
pip install -r requirements.txt
```

> 注意：直接 `pip install opencv-python` 现在可能装到 5.x 预览版，
> 那个版本的 `HoughCircles` 行为不稳定（实测一个圆都检不出来），
> 所以 `requirements.txt` 里锁定了 `opencv-python==4.11.0.86`。

VS Code 里记得选解释器：`Ctrl+Shift+P` → `Python: Select Interpreter` → 选 `./.venv/Scripts/python.exe`。

## 怎么跑

```bash
python task1_hough_circle.py          # 任务一(1)：出 results/task1_result.png
python task1_param_sweep.py           # 任务一(1)：出九宫格调参图
python task1_other_methods.py         # 任务一(2)：出对比图
python task2_basic_vision.py          # 任务二：出灰度图、掩膜、标注图
```

窗口跑完按任意键结束。不想弹窗口（比如批量跑）加 `--no-show`。

## 换成本次作业的原图

把原图覆盖到 `images/plate.png` 和 `images/chart.png`，直接重跑，代码不用改。
如果原图是 jpg：

```bash
python task1_hough_circle.py --image images/plate.jpg
python task2_basic_vision.py --image images/chart.jpg
```

半径范围是按「图片短边的比例」算的，所以大图小图都能用。
检不出来时先跑 `task1_param_sweep.py`，看阈值该往哪边调。

## 预期的输出

| 文件 | 内容 |
|---|---|
| `results/task1_result.png` | 蓝圈标盘子、绿圈标饼干，带半径标注 |
| `results/task1_steps.png` | 灰度 → Canny 边缘 → 检测结果 三步对照 |
| `results/task1_param_sweep.png` | param1 从 20 扫到 130 的九宫格 |
| `results/task1_methods_compare.png` | 原图 / 轮廓法 / 连通域法 / ALT 法 |
| `results/task2_gray.png` | 灰度图 |
| `results/task2_original_and_gray.png` | 原图和灰度并排 |
| `results/task2_mask_blue.png`、`task2_mask_yellow.png` | 蓝、黄的二值掩膜 |
| `results/task2_compare.png` | 原图 / 灰度 / 标注框 / 掩膜 四联图 |

## 两个已经帮你绕过的坑

1. **中文路径**：`cv2.imread` 碰到中文路径不报错、直接返回 `None`
   （后面会报 `'NoneType' object has no attribute 'shape'`）。
   `utils.py` 里已经用 `np.fromfile` + `cv2.imdecode` 绕过去了，直接用 `imread_unicode`。
2. **`cv2.putText` 写不了中文**：OpenCV 自带字体只支持 ASCII，中文会变问号。
   所以图上标签一律用英文（Plate / Cookie / Blue / Yellow）。

## 提交前自查

- [ ] 四个脚本都能直接跑通，`results/` 里有一整套图
- [ ] `git log` 里能看出「骨架 → 逐步填完」的过程，不是一次性一个大提交
- [ ] `docs/学习过程.md` 里的数字和截图都是你自己跑出来的
- [ ] 仓库里有 `requirements.txt`，别人 clone 下来能直接装
- [ ] `.venv/` 没有被提交上去（`.gitignore` 已经排除了）
