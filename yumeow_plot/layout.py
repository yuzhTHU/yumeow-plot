from typing import Optional, Literal, Tuple
from .utils import cm_to_inch, pt_to_inch


def calculate_size(RN, CN, FW, FH, AW, AH, A_ratio, LM, RM, TM, BM, HS, VS, fontsize):
    """
    初始化一个具有精确物理尺寸控制的 Matplotlib Figure。

    该函数通过自动求解器处理画布大小(FW/FH)、子图大小(AW/AH)及比例(A_ratio)之间的约束。
    内置学术论文常用的样式规范，并使用局部 rc_context 避免全局样式污染。

    Args:
    RN, CN : int
        画布的行数 (Rows) 和列数 (Columns)。
    FW, FH : float, optional
        画布的总宽度和总高度，单位为厘米 (cm)。
    AW, AH : float, optional
        单个子图 (Axes) 的宽度和高度，单位为厘米 (cm)。
    A_ratio : float, default 1.0
        子图的宽高比 (Width / Height)。当 AW 或 AH 缺失时，将根据此比例自动推算。
    LM, RM, TM, BM : float, default 3
        画布的左、右、上、下边距。数值基于 fontsize 缩放，通常 3 代表约 3 个字符宽度。
    HS, VS : float, optional
        子图之间的水平间距 (Horizontal Spacing) 和垂直间距 (Vertical Spacing)。
        默认与 LM/TM 保持一致。
    fontsize : float, default 7
        基础字体大小 (pt)，学术论文（如 Nature/IEEE）通常建议在 5-9pt 之间。

    Returns:
    解算后的尺寸参数 (RN, CN, FW, FH, AW, AH, A_ratio, LM, RM, TM, BM, HS, VS)
    """    
    # 转换单位：cm -> inch (只针对外部输入的物理尺寸)
    FW, FH, AW, AH = map(cm_to_inch, [FW, FH, AW, AH])

    # 边距换算：pt -> inch
    LM = pt_to_inch(LM, fontsize)
    RM = pt_to_inch(RM, fontsize)
    TM = pt_to_inch(TM, fontsize)
    BM = pt_to_inch(BM, fontsize)
    HS = pt_to_inch(HS, fontsize) if HS is not None else LM
    VS = pt_to_inch(VS, fontsize) if VS is not None else TM

    # 1. 水平方向独立求解 (Solve Horizontal)
    if AW is not None:
        FW = LM + CN * AW + (CN - 1) * HS + RM
    elif FW is not None:
        AW = (FW - LM - RM - (CN - 1) * HS) / CN

    # 2. 垂直方向独立求解 (Solve Vertical)
    if AH is not None:
        FH = TM + RN * AH + (RN - 1) * VS + BM
    elif FH is not None:
        AH = (FH - TM - BM - (RN - 1) * VS) / RN

    # 3. 跨维度桥接 (Bridge via A_ratio)
    # 情况 A: 只有水平信息 -> 算垂直
    if AW is not None and AH is None:
        AH = AW / A_ratio
        FH = TM + RN * AH + (RN - 1) * VS + BM
    # 情况 B: 只有垂直信息 -> 算水平
    elif AH is not None and AW is None:
        AW = AH * A_ratio
        FW = LM + CN * AW + (CN - 1) * HS + RM
    # 情况 C: 两者都有 -> 更新 A_ratio 以防冲突
    elif AW is not None and AH is not None:
        A_ratio = AW / AH
    # 情况 D: 什么都没有 -> 给个默认值 (比如子图宽 4cm)
    elif AW is None and AH is None:
        AW = cm_to_inch(4)  # 默认子图宽度 4cm
        AH = AW / A_ratio
        FW = LM + CN * AW + (CN - 1) * HS + RM
        FH = TM + RN * AH + (RN - 1) * VS + BM

    return RN, CN, FW, FH, AW, AH, A_ratio, LM, RM, TM, BM, HS, VS


def get_side_rect(
    ax,
    side: Literal['left', 'right', 'top', 'bottom'] = 'right',
    fill_to: Optional[float] = None, # 延伸至特定的比例坐标 (0-1)
    fixed_cm: Optional[float] = None, # 固定物理长度 (cm)
    pad_cm: float = 0.1,
    figinfo: dict = None
) -> Tuple[float, float, float, float]:
    """
    获取 ax 侧边的矩形区域坐标。
    
    逻辑优先级：
    1. 如果指定了 fixed_cm：使用固定物理尺寸。
    2. 如果指定了 fill_to：延伸至该比例坐标。
    3. 如果两者都为 None：默认延伸至图像边缘。
    """
    if figinfo is None:
        raise ValueError("调用 get_side_rect 必须提供 figinfo")

    pos = ax.get_position()
    FW, FH = figinfo['FW'], figinfo['FH']
    pw, ph = cm_to_inch(pad_cm)/FW, cm_to_inch(pad_cm)/FH
    
    # 核心逻辑：确定目标的“边界坐标”或“物理跨度”
    if side == 'right':
        x0, y0 = pos.x1 + pw, pos.y0
        if fixed_cm is not None:
            w = cm_to_inch(fixed_cm) / FW
        else:
            target = fill_to if fill_to is not None else 1.0
            w = target - x0
        h = pos.height

    elif side == 'left':
        x1, y0 = pos.x0 - pw, pos.y0
        if fixed_cm is not None:
            w = cm_to_inch(fixed_cm) / FW
        else:
            target = fill_to if fill_to is not None else 0.0
            w = x1 - target
        x0, h = x1 - w, pos.height

    elif side == 'top':
        x0, y0_start = pos.x0, pos.y1 + ph
        if fixed_cm is not None:
            h = cm_to_inch(fixed_cm) / FH
        else:
            target = fill_to if fill_to is not None else 1.0
            h = target - y0_start
        y0, w = y0_start, pos.width

    elif side == 'bottom':
        x0, y1_start = pos.x0, pos.y0 - ph
        if fixed_cm is not None:
            h = cm_to_inch(fixed_cm) / FH
        else:
            target = fill_to if fill_to is not None else 0.0
            h = y1_start - target
        y0, w = y1_start - h, pos.width

    return (x0, y0, w, h)


def get_margin_rect(
    side: Literal['left', 'right', 'top', 'bottom'],
    full_span: bool = False, # 是否横跨整个画布边缘
    figinfo: dict = None
):
    """
    获取画布边缘（边距区域）的矩形坐标。
    
    full_span = False: 限制在对侧边距之间（例如 top_box 在 LM 和 RM 之间）
    full_span = True: 延伸到画布物理边缘（例如 top_box 宽度为 1.0）
    """
    if figinfo is None:
        raise ValueError("需要提供 figinfo")

    r_LM, r_RM = figinfo['LM'] / figinfo['FW'], figinfo['RM'] / figinfo['FW']
    r_TM, r_BM = figinfo['TM'] / figinfo['FH'], figinfo['BM'] / figinfo['FH']

    if side == 'top':
        x0 = 0 if full_span else r_LM
        w = 1 if full_span else (1 - r_LM - r_RM)
        y0, h = 1 - r_TM, r_TM
    elif side == 'bottom':
        x0 = 0 if full_span else r_LM
        w = 1 if full_span else (1 - r_LM - r_RM)
        y0, h = 0, r_BM
    elif side == 'left':
        y0 = 0 if full_span else r_BM
        h = 1 if full_span else (1 - r_TM - r_BM)
        x0, w = 0, r_LM
    elif side == 'right':
        y0 = 0 if full_span else r_BM
        h = 1 if full_span else (1 - r_TM - r_BM)
        x0, w = 1 - r_RM, r_RM
    
    return (x0, y0, w, h)