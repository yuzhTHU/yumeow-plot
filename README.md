# 🐾 yumeow-plot

**YuMeow's personal matplotlib wrappers for academic and daily use.**

`yumeow-plot` 是一套专为科研绘图设计的 Matplotlib 封装库。它专注于解决论文投稿中常见的**物理尺寸对齐**、**空间布局分配**等痛点。

---

## ✨ 核心特性

* 📏 **精确尺寸求解 (Sizing Solver)**：直接使用厘米 (cm) 定义画布或子图大小，自动计算间距，完美适配不同期刊会议的分栏要求。
* 🧠 **空间感应轴 (Space-aware Axes)**：通过 `ax.get_side_rect()` 探测子图周边区域，实现 Colorbar 或标注区域的毫米级对齐。
* 🧩 **智能合并布局 (Smart Merging)**：告别复杂的 GridSpec，通过 `merge_axes` 像 Excel 合并单元格一样调整布局。
* 🛡️ **局部样式隔离**：使用局部 `rc_context` 应用学术风配置，绝不污染全局绘图设置。
* 📈 **高阶可视化补丁**：内置 `plot_resilience` (相平面韧性分析) 和 `plotOD` (地理流向图) 等高级功能。

---

## 🚀 快速开始

### 安装

```bash
pip install yumeow-plot

```

### 基础用法：精确控制子图尺寸

```python
import yumeow_plot as ym
import matplotlib.pyplot as plt

# 创建一个 1x2 布局，强制每个子图宽度为 4cm，高度按比例自动计算
fig, axes = ym.get_fig(1, 2, AW=4, A_ratio=1.2)

axes[0].plot([1, 2, 3], [4, 5, 6])
axes[1].scatter([1, 2, 3], [6, 5, 4])

# 在子图右侧自动分配一个 0.2cm 宽的区域放置 Colorbar
cax_rect = axes[1].get_side_rect(side='right', fixed_cm=0.2, pad_cm=0.1)
cax = fig.add_axes(cax_rect)

```

### 进阶：合并子图

```python
# 生成 3x3 网格
fig, axes = ym.get_fig(3, 3, AW=3, AH=3)

# 将左上角 2x2 的子图合并为一个大图
big_ax = ym.merge_axes(axes.reshape(3,3)[:2, :2])

# 大图依然保留空间探测能力
title_rect = big_ax.get_side_rect(side='top', fixed_cm=0.5)

```

---

## 🎨 高级可视化

### 韧性分析图 (Resilience Plot)

针对二维系统动态特性的快速可视化工具。

```python
from yumeow_plot import plot_resilience

f = lambda x, y: y - 3*y**2 - y**3 + x*y**3
plot_resilience(f, extent=(0, 5, 0, 5))

```

### 地理流向图 (OD Flow)

支持多种曲线样式的起终点流量可视化。

```python
from yumeow_plot import plotOD

# 支持 'straight', 'parabola', 'rotated_parabola' 等多种轨迹
plotOD(ax, source, destination, flow, location, linetype='parabola')

```

---

## 📂 项目结构

```text
yumeow-plot/
├── yumeow_plot/
│   ├── figure.py      # get_fig, merge_axes (物理布局)
│   ├── layout.py      # get_side_rect, get_margin_rect (空间探测)
│   ├── utils.py       # 字体加载与底层转换
│   └── advanced_viz/  # 高级绘图函数 (OD, Resilience)
├── demo/              # 示例代码目录
├── pyproject.toml     # 项目元数据
└── LICENSE            # MIT License

```

---

## ⚖️ License

本项目采用 **MIT License**。

Copyright (c) 2026 **YuMeow**。
