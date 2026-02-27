import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors

__all__ = ['plot_resilience']

def plot_resilience(f:callable, extent=(0, 1, 0, 1), gridnum=(1000, 1000), cmap=None, norm=None, ax=None, reset_xylim=True, lw=1):
    """
    绘制二维函数的韧性
    - f: 二维函数，如 lambda x, y: y - 3*y**2 - y**3 + x*y**3
    - extent: 函数定义域 (xmin, xmax, ymin, ymax)
    - gridnum: 网格数量 (xnum, ynum)
    ---
    Example:
    >>> f = lambda x, y: y - 3*y**2 - y**3 + x*y**3
    >>> plot_resilience(f, ax=axes[0], extent=(0, 5, 0, 5))
    >>> f = lambda x, y: np.sin(np.sqrt(x**2 + y ** 2))
    >>> plot_resilience(f, ax=axes[1], extent=(-4*np.pi, 4*np.pi, -4*np.pi, 4*np.pi))
    >>> f = lambda x, y: np.sin(np.sqrt(x ** 2 + y ** 2)) * x - y * np.cos(np.sqrt(x ** 2 + y ** 2))
    >>> plot_resilience(f, ax=axes[2], extent=(-4*np.pi, 4*np.pi, -4*np.pi, 4*np.pi))
    """
    if cmap is None: cmap = mcolors.LinearSegmentedColormap.from_list('my_bwr', ['#74b9ff', 'white', '#ff7675'])
    if norm is None: norm = mcolors.SymLogNorm(linthresh=0.01, linscale=0.01, vmin=-1, vmax=1)
    if ax is None: ax = plt.gca()

    def plot1(x, y):
        ax.plot(x, y, 'black', linewidth=lw, linestyle='-', solid_capstyle='round')

    def plot2(x, y):
        ax.plot(x, y, 'gray', linewidth=lw, linestyle=(3, (3, 1)), solid_capstyle='round')

    xmin, xmax, ymin, ymax = extent
    xnum, ynum = gridnum
    x = np.linspace(xmin, xmax, xnum)
    y = np.linspace(ymin, ymax, ynum)
    x, y = np.meshgrid(x, y)
    z = f(x, y)

    ax.imshow(z, origin='lower', aspect='auto', cmap=cmap, norm=norm, zorder=0, extent=(xmin, xmax, ymin, ymax))

    contours = ax.contour(x, y, z, levels=[0], linewidths=0)
    for coll in contours.collections: coll.remove()

    dzdy = np.gradient(z)[0]
    for coll in contours.collections:
        for path in coll.get_paths():
            saved = []
            sign = None
            for (x0, y0) in path.vertices:
                saved.append((x0, y0))
                x_idx = int(np.floor((x0-xmin) / (xmax-xmin) * (xnum - 1)))
                y_idx = int(np.floor((y0-ymin) / (ymax-ymin) * (ynum - 1)))
                if sign is None: sign = np.sign(dzdy[y_idx, x_idx])
                if np.sign(dzdy[y_idx, x_idx] * sign) < 0:
                    if sign < 0: plot1(*np.array(saved).T)
                    else: plot2(*np.array(saved).T)
                    sign *= -1
                    saved = []
                else:
                    pass
            if saved:
                if sign < 0: plot1(*np.array(saved).T)
                else: plot2(*np.array(saved).T)

    if reset_xylim:
        scale = lambda min, max, ratio=0.1: (min - (max - min) * ratio / 2, max + (max - min) * ratio / 2)
        ax.set_xlim(*scale(xmin, xmax))
        ax.set_ylim(*scale(ymin, ymax))

