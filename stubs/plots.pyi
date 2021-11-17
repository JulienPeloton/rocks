"""
This type stub file was generated by pyright.
"""

""" Plotting utilities for rocks."""
def plot(catalogue, parameter, nbins=..., show=..., save_to=...): # -> None:
    """Create a scatter/histogram figure for asteroid parameters in datacloud
    catalogues.

    Parameters
    ==========
    catalogue : rocks.datacloud.Catalog
        A datacloud catalogue ingested in Rock instance.
    parameter : str
        The parameter name, referring to a column in the datacloud catalogue.
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
    ...

PLOTTING = ...
