import os
import matplotlib.pyplot as plt
from typing import Dict, Any

def get_my_rc(fontsize: float = 7, lw: float = 0.5, font_family: str = "Arial") -> Dict[str, Any]:
    """返回个人习惯风格的 rc 配置字典"""
    return {
        "font.family": font_family,
        "font.size": fontsize,
        "axes.labelsize": fontsize,
        "axes.titlesize": fontsize,
        "xtick.labelsize": fontsize * (5/7),
        "ytick.labelsize": fontsize * (5/7),
        "legend.fontsize": fontsize * (5/7),
        "figure.titlesize": fontsize,
        "lines.linewidth": lw,
        "axes.linewidth": lw,
        "xtick.major.width": lw,
        "ytick.major.width": lw,
        "xtick.minor.width": lw,
        "ytick.minor.width": lw,
        "grid.linewidth": lw,
        "patch.linewidth": lw,
        "pdf.fonttype": 42,
        "svg.fonttype": "none",
    }

def cm_to_inch(x): 
    return x / 2.54 if x is not None else None

def pt_to_inch(x, fontsize):
    return x * fontsize / 72 if x is not None else None

def load_zh_font(
    font_path="/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
    font_url="https://ghp.ci/https://github.com/notofonts/noto-cjk/blob/main/Sans/SubsetOTF/SC/NotoSansSC-Regular.otf",
):
    """
    加载中文字体并设置为 Matplotlib 默认字体。
    - font_path: 本地字体文件路径，优先使用。
    - font_url: 字体文件在线下载链接，备用。
    - save_path: 字体文件下载后保存的本地路径。

    使用示例：
        font = load_zh_font()
        plt.title("示例图表：数字平方", fontproperties=font, size=15)
        plt.xlabel("数字", fontproperties=font, size=12)
        plt.ylabel("平方", fontproperties=font, size=12)
    """
    from matplotlib.font_manager import FontProperties

    if not os.path.exists(font_path):
        import requests
        font_path="/tmp/SimHei.otf"
        if not os.path.exists(font_path):
            response = requests.get(font_url)
            response.raise_for_status()  # 确保请求成功
            with open(font_path, "wb") as f:
                f.write(response.content)
        
    font = FontProperties(fname=font_path)
    plt.rcParams["font.family"] = "sans-serif"
    plt.rcParams["font.sans-serif"] = [font_path]  # 这里指定.otf文件路径
    plt.rcParams["axes.unicode_minus"] = False  # 正确显示负号
    return font
