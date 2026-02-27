import types
import numpy as np
import matplotlib.pyplot as plt
from typing import Optional
from functools import partial
from .layout import calculate_size, get_side_rect, get_margin_rect
from .utils import get_my_rc, cm_to_inch, pt_to_inch

def get_my_fig(
    RN: int,
    CN: int,
    FW: Optional[float] = None,
    FH: Optional[float] = None,
    AW: Optional[float] = None,
    AH: Optional[float] = None,
    A_ratio: Optional[float] = None,
    LM: float = 3.0,
    RM: float = 3.0,
    TM: float = 3.0,
    BM: float = 3.0,
    HS: float = 3.0,
    VS: float = 3.0,
    dpi: int = 300,
    fontsize: float = 7,
    lw: float = 0.5,
    font_family: str = 'Arial',
    **kwargs
):
    """
    初始化具有精确物理尺寸控制的 Matplotlib Figure。

    参数
    ----------
    RN, CN : int
        行数和列数。
    FW, FH : float, optional (cm)
        画布总宽高。
    AW, AH : float, optional (cm)
        子图宽高。
    A_ratio : float, default 1.0
        子图宽高比 (W/H)。
    LM, RM, TM, BM : float, default 3
        边距系数，实际 inch 为 val * fontsize / 72。
    HS, VS : float, optional
        子图水平/垂直间距。
    dpi : int, default 300
        分辨率。
    fontsize : float, default 7
        基础字号 (pt)。
    lw : float, default 0.5
        基础线宽 (pt)。
    """
    # 样式配置准备
    rc_params = get_my_rc(fontsize, lw, font_family)

    # 尺寸解算
    RN, CN, FW, FH, AW, AH, A_ratio, LM, RM, TM, BM, HS, VS = calculate_size(
        RN, CN, FW, FH, AW, AH, A_ratio, LM, RM, TM, BM, HS, VS, fontsize
    )

    # 封装 figinfo
    figinfo = dict(
        RN=RN, CN=CN, FW=FW, FH=FH, AW=AW, AH=AH,
        LM=LM, RM=RM, TM=TM, BM=BM, HS=HS, VS=VS,
        r_AW=AW/FW, r_AH=AH/FH, r_HS=HS/FW, r_VS=VS/FH,
        r_LM=LM/FW, r_RM=RM/FW, r_TM=TM/FH, r_BM=BM/FH,
        fontsize=fontsize, lw=lw,
        top_box=(LM/FW, 1-TM/FH, 1-(LM+RM)/FW, TM/FH),
        bottom_box=(LM/FW, 0, 1-(LM+RM)/FW, BM/FH),
        right_box=(1-RM/FW, BM/FH, RM/FW, 1-(TM+BM)/FH),
        left_box=(0, BM/FH, LM/FW, 1-(TM+BM)/FH),
    )

    fig.get_margin_rect = partial(get_margin_rect, figinfo=figinfo)

    for ax in axes:
        ax.get_side_rect = partial(get_side_rect, ax, figinfo=figinfo)

    # 使用 rc_context 局部应用样式，防止污染全局 plt.rcParams
    with plt.rc_context(rc_params):
        fig, axes = plt.subplots(RN, CN, figsize=(FW, FH), dpi=dpi, **kwargs)
        fig.subplots_adjust(
            left=LM/FW, right=1-RM/FW, 
            top=1-TM/FH, bottom=BM/FH, 
            wspace=HS/AW, hspace=VS/AH
        )
        axes = axes.ravel() if RN * CN > 1 else [axes]
        fig.figinfo = figinfo  # 附加尺寸信息到 fig 对象
    
    return fig, axes


def merge_axes(axes, fig=None, label=None):
    """
    合并一组 axes 为一个大的 axis。
    支持传入 Axes 列表或 NumPy 矩阵。
    """
    if not axes: return None
    
    # 确保 axes 是扁平化的数组，兼容 list 和 np.ndarray
    axes = np.asarray(axes).ravel()
    if fig is None: fig = axes[0].figure

    # 1. 动态获取所有轴的比例坐标 (0-1)
    bboxes = [ax.get_position() for ax in axes]
    
    # 2. 计算并集包围盒
    x0 = min(b.x0 for b in bboxes)
    y0 = min(b.y0 for b in bboxes)
    x1 = max(b.x1 for b in bboxes)
    y1 = max(b.y1 for b in bboxes)

    # 3. 创建新轴
    merged_ax = fig.add_axes([x0, y0, x1 - x0, y1 - y0], label=label)
    
    # 4. 清理旧轴
    for ax in axes:
        ax.remove()
        
    # 5. 自动注入空间感应方法
    if hasattr(axes[0], 'get_side_rect'):
        old_partial = axes[0].get_side_rect
        # 重新创建一个 partial，把第一个参数替换为新的 merged_ax
        # old_partial.keywords 里存着之前的 figinfo=figinfo
        merged_ax.get_side_rect = partial(
            get_side_rect, 
            merged_ax,      # 关键：替换为新轴
            **old_partial.keywords
        )

    return merged_ax