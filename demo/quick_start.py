import numpy as np
import matplotlib.pyplot as plt
import yumeow_plot as ym

# 1. 初始化一个 1x2 的布局
# 设定每个子图宽度 (Axis Width, AW) 为 5cm，子图宽高比 (A_ratio) 为 1:1
# 子图横向间距 (Horizontal Spacing, HS) 为 3 字符高度
# 图像的左右边距 (Left Margin, LM 和 Right Margin, RM) 都设为 5 字符宽度
# 设置图像的上边距 (Top Margin, TM) 为 3 字符高度，以便放置标题
fig, axes = ym.get_fig(RN=1, CN=2, AW=5, A_ratio=1.0, TM=3, HS=3, LM=5, RM=5)

# 第一个图画一个简单的正弦波，展示子图尺寸控制能力
ax = axes[0]
x = np.linspace(0, 10, 100)
y = np.sin(x)
ax.plot(x, y, label='Sine Wave')
ax.set_title("Subplot A: Sizing Control")
ax.set_xlabel("Time (s)")
ax.set_ylabel("Amplitude")

# 第二个图画一个带有 colorbar 的 Heatmap，展示空间探测能力
ax = axes[1]
x = np.linspace(-10, 10, 100)
y = np.linspace(-10, 10, 100)
xx, yy = np.meshgrid(x, y)
r = np.sqrt(xx**2 + yy**2)
data = np.sin(r) / r
im = ax.imshow(data, cmap='viridis', extent=(-10, 10, -10, 10))
ax.set_title("Subplot B: Colorbar Alignment")

# 在 axes[1] 的右侧，距离 0.2cm 处，创建一个宽度为 0.3cm 的 cax
cax = fig.add_axes(ax.get_side_rect(side='right', fixed_cm=0.3, pad_cm=0.2))
fig.colorbar(im, cax=cax)

# 在顶部边距区域添加一个通栏标题
fig.suptitle("Demonstration of yumeow-plot Capabilities")

# 保存图片（记得学术论文通常要求 300+ DPI）
fig.savefig("./assets/demo_result.png", dpi=300)
# plt.show()