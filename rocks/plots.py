#!/usr/bin/env python
""" Plotting utilities for rocks.
"""
import sys

import numpy as np
import matplotlib.pyplot as plt

import rocks

# Define colors/markers for all methods in ssodnet
s = {
    "avg": {"color": "black"},
    "std": {"color": "darkgrey"},
    # -Space mission
    "SPACE": {"color": "gold", "marker": "X"},
    # -3d shape modeling
    "ADAM": {"color": "navy", "marker": "v"},
    "SAGE": {"color": "mediumblue", "marker": "^"},
    "KOALA": {"color": "slateblue", "marker": "<"},
    "Radar": {"color": "cornflowerblue", "marker": ">"},
    # -LC with scaling
    "LC+OCC": {"color": "lightgreen", "marker": "v"},
    "LC+AO": {"color": "forestgreen", "marker": "^"},  # deprecated =LC+IM
    "LC+IM": {"color": "forestgreen", "marker": "^"},
    "LC+TPM": {"color": "darkgreen", "marker": "<"},
    "LC-TPM": {"color": "green", "marker": ">"},
    # -Thermal models
    "STM": {"color": "grey", "marker": "D"},
    "NEATM": {"color": "grey", "marker": "o"},
    "TPM": {"color": "darkgrey", "marker": "s"},
    # -triaxial ellipsoid
    "TE-IM": {"color": "blue", "marker": "o"},
    # -2d on sky
    "OCC": {"color": "brown", "marker": "P"},
    "IM": {"color": "oranged", "marker": "p"},
    "IM-PSF": {"color": "tomato", "marker": "H"},
    # -Mass from binary
    "Bin-IM": {"color": "navy", "marker": "v"},
    "Bin-Genoid": {"color": "mediumblue", "marker": "^"},
    "Bin-PheMu": {"color": "slateblue", "marker": "<"},
    "Bin-Radar": {"color": "cornflowerblue", "marker": ">"},
    # -Mass from deflection
    "DEFLECT": {"color": "brown", "marker": "D"},
    "EPHEM": {"color": "red", "marker": "o"},
    # -Taxonomy
    "Phot": {"color": "red", "marker": "s"},
    "Spec": {"color": "red", "marker": "s"},
}

ylabels = {"diameter": "Diameter (km)", "mass": "Mass (kg)", "albedo": "Albedo"}


def show_scatter_hist(info, par, figname):

    # translate input
    n = len(info[1])
    x = np.linspace(1, n, n)

    val = info[1].get(par).values
    unc = info[1].get("err_" + par).values
    avg = info[0][0]
    std = info[0][1]

    # Define figure layout
    fig = plt.figure(figsize=(12, 8))
    gs = fig.add_gridspec(
        1,
        2,
        width_ratios=(7, 2),
        wspace=0.05,
        left=0.07,
        right=0.97,
        bottom=0.05,
        top=0.87,
    )
    ax = fig.add_subplot(gs[0])
    ax_histy = fig.add_subplot(gs[1], sharey=ax)

    # the scatter plot:
    # mean and std
    lavg = ax.axhline(avg, label="Average", color=s["avg"]["color"])
    lstd = ax.axhline(
        avg + std,
        label="1$\sigma$ deviation",
        color=s["std"]["color"],
        linestyle="dashed",
    )
    lstd = ax.axhline(avg - std, color=s["std"]["color"], linestyle="dashed")

    # all methods
    for i in np.unique(info[1].method):
        p = np.where(info[1].method == i)
        if True in info[1].selected.values[p]:
            fcol = s[i]["color"]
        else:
            fcol = "none"
        ax.scatter(
            x[p],
            val[p],
            marker=s[i]["marker"],
            s=80,
            label=i,
            facecolors=fcol,
            edgecolors=s[i]["color"],
        )
        ax.errorbar(x[p], val[p], yerr=unc[p], c=s[i]["color"], linestyle="")

    # axes
    ax.set_ylabel(ylabels[par])
    ax.set_xticks(x)

    # Legend
    ax.legend(loc="best", ncol=2)

    # place shortbib on top for quick identification
    axtop = ax.twiny()
    axtop.set_xticks(x)
    axtop.set_xticklabels(info[1].shortbib, rotation=25, ha="left")

    # Histogram
    range_ = ax.get_ylim()
    nbins = 10
    ax_histy.tick_params(axis="y", labelleft=False)
    sel = np.where(info[1].selected)

    na, ba, pa = ax_histy.hist(
        val,
        bins=nbins,
        range=range_,
        orientation="horizontal",
        color="grey",
        label="All",
    )
    ns, bs, ps = ax_histy.hist(
        val[sel],
        bins=nbins,
        range_=range_,
        orientation="horizontal",
        color="gold",
        label="Selected",
    )

    ax_histy.legend(loc="lower right")

    plt.savefig(figname)
    plt.close()


def scatter(catalogue, nbins=10, show=False, savefig=""):
    """Create scatter/histogram figure for float parameters.

    Parameters
    ==========
    catalogue : rocks.core.propertyCollection
        A datacloud catalogue ingested in Rock instance.
    nbins : int
        Number of bins in histogram. Default is 10
    show : bool
        Show plot. Default is False.
    save_to : str
        Save figure to path. Default is no saving.

    Returns
    =======
    matplotlib.figures.Figure instance, matplotib.axes.Axis instance
    """
    prop, errors, prop_name = _property_errors(catalogue)

    # ------
    # Build figure
    fig = plt.figure(figsize=(12, 8))
    gs = fig.add_gridspec(
        1,
        2,
        width_ratios=(7, 2),
        wspace=0.05,
        left=0.07,
        right=0.97,
        bottom=0.05,
        top=0.87,
    )

    ax = fig.add_subplot(gs[0])
    ax_histy = fig.add_subplot(gs[1], sharey=ax)

    avg, std = prop.weighted_average(errors)
    ax.axhline(avg, label="Average", color=rocks.utils.METHODS["avg"]["color"])
    ax.axhline(
        avg + std,
        label=fr"1$\sigma$ deviation",
        linestyle="dashed",
        color=rocks.utils.METHODS["std"]["color"],
    )
    ax.axhline(avg - std, linestyle="dashed", color=rocks.utils.METHODS["std"]["color"])

    x = np.linspace(1, len(prop), len(prop))
    for i, m in enumerate(np.unique(catalogue.method)):
        cur = np.where(np.asarray(catalogue.method) == m)
    fcol = "none"
    ax.scatter(
        x[cur],
        np.asarray(prop)[cur],
        label=m,
        marker=rocks.utils.METHODS[m]["marker"],
        s=80,
        facecolors=fcol,
        edgecolors=rocks.utils.METHODS[m]["color"],
    )
    ax.errorbar(
        x[cur],
        np.asarray(prop)[cur],
        yerr=np.asarray(errors)[cur],
        c=rocks.utils.METHODS[m]["color"],
        linestyle="",
    )

    ax.set_xticks(x)
    axtop = ax.twiny()
    axtop.set_xticks(x)
    axtop.set_xticklabels(catalogue.shortbib, rotation=25, ha="left")
    ax.set_ylabel(rocks.utils.PLOTTING["LABELS"][prop_name])
    ax.legend(loc="best", ncol=2)

    range_ = ax.get_ylim()
    ax_histy.tick_params(axis="y", labelleft=False)
    ax_histy.hist(
        prop,
        bins=nbins,
        range=range_,
        orientation="horizontal",
        color="grey",
        label="All",
    )
    ax_histy.legend(loc="lower right")

    if savefig:
        fig.savefig(savefig)

    if show:
        plt.show()
        plt.close()

    return fig, ax


def hist(catalogue, nbins=10, show=False, save_to=""):
    """Create histogram figure for float parameters.

    Parameters
    ==========
    catalogue : rocks.core.propertyCollection
        A datacloud catalogue ingested in Rock instance.
    nbins : int
        Number of bins in histogram. Default is 10
    show : bool
        Show plot. Default is False.
    save_to : str
        Save figure to path. Default is no saving.

    Returns
    =======
    matplotlib.figures.Figure instance, matplotib.axes.Axis instance
    """

    # inferred from propertyCollection
    prop, errors, prop_name = _property_errors(catalogue)

    # ------
    # Build figure
    fig = plt.figure(figsize=(8, 6))

    plt.hist(prop, bins=nbins, label="Estimates")

    avg, std = prop.weighted_average(errors)

    plt.errorbar(avg, 0.5, xerr=std, label="Average", marker="o")

    plt.legend(loc="upper right")

    plt.xlabel(rocks.utils.PLOTTING["LABELS"][prop_name])
    plt.ylabel("Distribution")

    if save_to:
        fig.savefig(save_to)

    if show:
        plt.show()
        plt.close()

    return fig, plt.gca()


def _property_errors(catalogue):
    """Retrieve main property and its errors from a datacloud catalogue.
    masses -> mass, diamalbedo -> either albedos or diameters

    Parameters
    ==========
    catalogue : rocks.core.propertyCollection
        Datacloud catalogue ingested into Rock instance.

    Returns
    =======
    ndarray, ndarray
        The main property as defined in utils.DATACLOUD_META and its error.
    str
        The property name.
    """
    # ------
    # Data selection: if called from command line, get from arguments
    # TODO Fails if user renames executable. Should be
    if sys.argv[0].endswith("rocks"):
        prop = sys.argv[1]  # eg masses, diameters, albedos

        if prop in ["diameters", "albedos"]:
            cat_name = "diamalbedo"
        else:
            cat_name = prop

        # Actual attribute name is singular version
        prop_name = rocks.utils.DATACLOUD_META[cat_name]["prop_name"][prop]
        prop = getattr(catalogue, prop_name)  # listSameTypeParameter

    if hasattr(catalogue, f"err_{prop_name}"):
        errors = getattr(catalogue, f"err_{prop_name}")
    else:
        errors = np.ones(np.array(prop).shape)
    return prop, errors, prop_name
