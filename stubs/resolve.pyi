"""
This type stub file was generated by pyright.
"""
from typing import List, Set, Tuple, Union

import pandas as pd
import numpy as np

"""Local and remote asteroid name resolution."""
def identify(
    id_: Union[str, int, float, List, range, Set, np.ndarray, pd.Series],
    return_id: bool = False,
    local: bool = True,
    progress: bool = False,
) -> Union[Tuple[str, int, str], List[Tuple]]:
    """Resolve names and numbers of one or more minor bodies using identifiers.

    Parameters
    ----------
    id_ : str, int, float, list, range, set, np.ndarray, pd.Series
        One or more identifying names or numbers to resolve.
    return_id : bool
        Return the SsODNet ID of the asteroid as third member of
        the tuple. Default is False.
    local : bool
        Try resolving the name locally first. Default is True.
    progress : bool
        Show progress bar. Default is False.

    Returns
    -------
    tuple, list of tuple : (str, int, str), (None, np.nan, None)
        List containing len(id_) tuples. Each tuple contains the asteroid's
        name, number, and the SsODNet ID if return_id=True. If the resolution
        failed, the values are None for name and SsODNet and np.nan for the
        number. If a single identifier is resolved, a tuple is returned.

    Notes
    -----
    Name resolution is first attempted locally, then remotely via quaero. If
    the asteroid is unnumbered, its number is np.nan.
    """
    ...

def _standardize_id(id_: Union[str, int, float]) -> Union[str, int]:
    """Try to infer id_ type and re-format if necessary to ensure
    successful remote lookup.

    Parameters
    ----------
    id_ : str, int, float
        The minor body's name, designation, or number.

    Returns
    -------
    str, int, float, None
        The standardized name, designation, or number. None if id_ is NaN or None.
    """
    ...