import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from typing import List, Dict, Tuple, Literal

__all__ = ['plotOD', 'EqualizeNormalize']

class EqualizeNormalize(mcolors.Normalize):
    """ 按分布而非值进行归一化 """
    def __init__(self, samples, clip=False):
        super().__init__(vmin=samples.min(), vmax=samples.max(), clip=clip)
        hist, bin_edges = np.histogram(samples.flatten(), bins=256, range=(self.vmin, self.vmax), density=True)
        cdf = hist.cumsum()
        cdf = (cdf - cdf.min()) / (cdf.max() - cdf.min())
        self.bin_edges = bin_edges
        self.cdf = cdf
    def __call__(self, value, clip=False):
        value = np.array(value)
        return np.ma.masked_array(np.interp(value.flatten(), self.bin_edges[:-1], self.cdf).reshape(value.shape))
    def inverse(self, value):
        value = np.array(value)
        return np.ma.masked_array(np.interp(value.flatten(), self.cdf, self.bin_edges[:-1]).reshape(value.shape))


def plotOD(ax, source:List[str], destination:List[str], flow:List[float], location:Dict[str, Tuple[float, float]],
           linetype:Literal['straight', 'parabola', 'rotated_parabola', 'projected_parabola']='straight', N=100, zorder=10,
           **kwargs):
    """ 绘制OD流量 """
    cmap = mcolors.LinearSegmentedColormap.from_list('cmap', ['#0308F8', '#FD0B1B', '#ffff00'], gamma=5.0)
    norm = EqualizeNormalize(flow.values)
    t = np.linspace(0, 1, N)
    ignored = set(list(source) + list(destination)) - set(location.keys())
    if ignored: print(f'\033[33mWarning: {ignored} are not in location\033[0m')
    for (s, d, f) in zip(source, destination, flow):
        if s not in location or d not in location: continue
        p1 = np.array(location[s])[:, np.newaxis] # (2, 1)
        p2 = np.array(location[d])[:, np.newaxis] # (2, 1)
        if linetype == 'straight':
            ax.plot(*(p1 * (1 - t) + p2 * t), lw=0.05+0.1*norm(f), alpha=0.4+0.4*norm(f), color=cmap(norm(f)), zorder=zorder+norm(f), rasterized=kwargs.get('rasterized', False))
        elif linetype == 'parabola':
            y_scale = locals().get('y_scale', np.diff(ax.get_ylim())[0])
            xy = p1 * (1-t) + p2 * t + np.array([[0], [1]]) * 4 * t * (1-t) * norm(f) * y_scale * kwargs.get('scale', 0.1)
            ax.plot(*xy, lw=0.05+0.1*norm(f), alpha=0.4+0.4*norm(f), color=cmap(norm(f)), zorder=zorder+norm(f), rasterized=kwargs.get('rasterized', False))
        elif linetype == 'rotated_parabola':
            height = 0.5 * norm(f)
            C, S = (p2 - p1)[:, 0]
            A = np.array([[C, -S], [S, C]]) / 2
            if kwargs.get('adjust_up', None) and (C < 0): A = -A
            if kwargs.get('adjust_down', None) and (C > 0): A = -A
            xy = A @ np.array([2 * t - 1, height * 4 * t * (1 - t)]) + 0.5 * (p1 + p2)
            ax.plot(*xy, lw=0.05+0.1*norm(f), alpha=0.4+0.4*norm(f), color=cmap(norm(f)), zorder=zorder+norm(f), rasterized=kwargs.get('rasterized', False))
        elif linetype == 'projected_parabola':
            p0 = locals().get('p0', np.array(kwargs.get('p0', [np.mean(ax.get_xlim()), np.mean(ax.get_ylim())]))[:, np.newaxis])
            D = kwargs.get('D', 10)
            xy = p0 + D * (p1 * (1-t) + p2 * t - p0) / (D - 4*t*(1 - t)*(norm(f) + 1))
            ax.plot(*xy, lw=0.05+0.1*norm(f), alpha=0.4+0.4*norm(f), color=cmap(norm(f)), zorder=zorder+norm(f), rasterized=kwargs.get('rasterized', False))
        else:
            raise ValueError(f'Invalid linetype: {linetype}')
    return ax
