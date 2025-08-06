###################################################################################
#
# Assortment of plot functions for various representations of data.
#
# Siddharth Maddali
# siddharth@liminalinsights.com
# May 2025
#
###################################################################################

import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.axes_grid1.inset_locator import inset_axes
from matplotlib.colors import ListedColormap, BoundaryNorm


def PlotGraduatedData(
    x,
    ylist_ordered,
    value_range,
    figsize=None,
    default_ax=None,
    cmap='cividis',
    loc='lower right',
    title='Generic title',
    llabel='Least',
    rlabel='Most'
):
    """
    plot_graduated_data:
    Plots a set of 1-D line plots and colors them according to a graduated scalar field.
    In addition, plots a labeled color legend within the graphing area.

    Inputs:

    x:          Nx1 array
    ylist_ordered: List of size N, each element of which is an array of the same dimension as x.
                   Each element corresponds to a uniformly increasing scalar field value.
    value_range: Doublet [a, b]. Describes range of scalar field values
    figsize:    Custom figure size if default axis has not been provided.
    default_ax: User-defined axis object within which to plot. If None (default), creates new axis object.
    cmap:       Color map (string) for coloring each line plot.
                Default 'cividis' chosen for optimal viewing with color-blindness.
    loc:        Where to plot the color legend within the graphing area. Default: 'lower right'.
    title:      Title of the color legend.
    llabel:     String label for the smallest scalar field value.
    rlabel:     String label for the largest scalar field value.

    Returns:
    default_ax: The axis object in which the data was plotted.

    """
    my_cmap = plt.get_cmap(cmap)
    scaled_index = np.linspace(0.0, 1.0, len(ylist_ordered))
    colors = my_cmap(scaled_index)

    if default_ax is None:
        default_ax = plt.figure(figsize=figsize).subplots()

    for n, y in enumerate(ylist_ordered):
        default_ax.plot(x, y, color=colors[n])
    default_ax.grid()
    ax_ins = inset_axes(default_ax, width='30%', height='7%', loc=loc)
    scaled_index = np.linspace(value_range[0], value_range[1], 100)
    x_mesh, _ = np.meshgrid(scaled_index, np.arange(3))
    ax_ins.imshow(x_mesh, cmap=cmap)
    ax_ins.set_yticks([])
    ax_ins.set_xticks([0, len(scaled_index) - 1])
    ax_ins.set_xticklabels([llabel, rlabel])
    ax_ins.set_title(title, fontsize=12, fontweight='bold')
    return default_ax


def PlotLabeledSegmentsImage(
    img,
    segment_dictionary,
    x_grid=None,
    y_grid=None,
    alpha=1.0,
    default_ax=None,
    figsize=None,
    color_map='tab10'
):
    """
    plot_labeled_segments_image:
    Plots a segmented image with integer (>=0) labels in a color scale suitable for a schematic,
    along with a color bar labeled with the various segments taken from the user-provided dictionary.
    Useful to avoid the hassle of colorbar details while plotting segmented images.
    This routine is extremely useful for rendering wave simulations against a semi-transparent backdrop.

    Inputs:

    img:                    Image of size MxN
    segment_dictionary:     Dict of the form {0: 'class 0', 1: 'class 1', ...}
    x_grid:                 A linspace array describing the uniform spacing along the image X-axis. Defaults to matrix coordinates.
    y_grid:                 A linspace array describing the uniform spacing along the image Y-axis. Defaults to matrix coordinates.
    alpha:                  Transparency of plotted image. Default 1.
    default_ax:             User-defined axis object within which to plot. If None (default), creates new axis object.
    figsize:                Custom figure size if default axis has not been provided.
    color_map:              Possible values are 'tab10', 'tab20', 'tab20b', 'tab20c'.

    Returns:
    default_ax: The axis object in which the data was plotted.

    """
    allowed_cmaps = ['tab10', 'tab20', 'tab20b', 'tab20c']
    assert color_map in allowed_cmaps, (
        f'Incompatible color map. Allowed values are {allowed_cmaps}.'
    )
    seg_idx = []
    segments = []
    for key, val in segment_dictionary.items():
        seg_idx.append(key)
        segments.append(val)
    assert list(np.unique(img)) == seg_idx, 'Incompatible segment indices.'

    x_grid = x_grid if x_grid is not None else np.arange(img.shape[1])
    y_grid = y_grid if y_grid is not None else np.arange(img.shape[0])

    num_categories = len(segments)
    colors = plt.get_cmap(color_map, num_categories).colors
    cmap = ListedColormap(colors)
    bounds = -0.5 + np.arange(len(segments) + 1)
    norm = BoundaryNorm(bounds, cmap.N)

    if default_ax is None:
        default_ax = plt.figure(figsize=figsize).subplots()

    im = default_ax.pcolormesh(
        x_grid, y_grid, img, cmap=cmap, norm=norm, alpha=alpha
    )
    cbar = plt.colorbar(
        im, ax=default_ax, fraction=0.046, pad=0.05, ticks=np.arange(len(segments))
    )
    cbar.ax.set_yticklabels(segments)
    return default_ax
