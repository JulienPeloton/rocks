#!/usr/bin/env python
"""Implement the Rock class and other core rocks functionality.
"""
from functools import singledispatch
import json
import keyword
import os
from types import SimpleNamespace
import warnings

import numpy as np
import pandas as pd
from rich.progress import track

import rocks

# Read ssoCard template
path_cache = os.path.join(os.path.expanduser("~"), ".cache/rocks")
path_template = os.path.join(path_cache, "ssoCard_template.json")

if not os.path.isfile(path_template):
    print("Missing ssoCard template, retrieving..")
    rocks.utils.create_ssocard_template()

with open(path_template, "r") as file_:
    TEMPLATE = json.load(file_)


class Rock:
    "For space rocks."

    def __init__(self, identifier, ssoCard=None, datacloud=[], skip_id_check=False):
        """Identify a minor body  and retrieve its properties from SsODNet.

        Parameters
        ==========
        identifier : str, int, float
            Identifying asteroid name, designation, or number
        ssoCard : dict
            Optional previously acquired ssoCard.
        datacloud : list of str
            List of additional catalogues to retrieve from datacloud.
            Default is no additional catalogues.

        Returns
        =======
        rocks.core.Rock
            An asteroid class instance, with its properties as attributes.

        Notes
        =====
        If the asteroid could not be identified, the name and number are None
        and no further attributes are set.

        Example
        =======
        >>> from rocks.core import Rock
        >>> ceres = Rock('ceres')
        >>> ceres.taxonomy.class_
        'C'
        >>> ceres.taxonomy.shortbib
        'DeMeo+2009'
        >>> ceres.diameter
        848.4
        >>> ceres.diameter.unit
        'km'
        """

        # Identify minor body
        if not skip_id_check:
            self.name, self.number, self.id = rocks.resolver.identify(
                identifier, return_id=True, progress=False
            )
        else:
            self.id = identifier

        if not isinstance(self.id, str):
            return

        # Fill attributes from argument, cache, or query
        ssoCard = ssoCard if ssoCard is not None else rocks.utils.get_ssoCard(self.id)
        # No ssoCard exists
        if ssoCard is None:
            return

        # Initialize from template
        attributes = TEMPLATE
        attributes = rocks.utils.update_ssoCard(TEMPLATE, ssoCard)
        attributes = rocks.utils.sanitize_keys(attributes)

        # Add JSON keys as attributes, mapping to the appropriate type
        for attribute in attributes.keys():
            setattr(
                self,
                attribute,
                cast_types(attributes[attribute]),
            )

        # Set uncertainties and values
        self.__add_metadata()

        # Add datacloud list attributes
        for catalogue in datacloud:
            self.__add_datacloud_catalogue(catalogue)

    def __hash__(self):
        return hash(self.name)

    def __repr__(self):
        return (
            self.__class__.__qualname__
            + f"(number={self.number!r}, name={self.name!r})"
        )

    def __str__(self):
        return f"({self.number}) {self.name}"

    def __eq__(self, other):
        if self.__class__ is other.__class__:
            return self.name == other.name
        return NotImplemented

    def __lt__(self, other):
        if self.__class__ is other.__class__:
            return (self.number, self.name) < (other.number, other.name)
        return NotImplemented  # pragma: no cover

    def __le__(self, other):
        if self.__class__ is other.__class__:
            return (self.number, self.name) <= (other.number, other.name)
        return NotImplemented  # pragma: no cover

    def __gt__(self, other):
        if self.__class__ is other.__class__:
            return (self.number, self.name) > (other.number, other.name)
        return NotImplemented  # pragma: no cover

    def __ge__(self, other):
        if self.__class__ is other.__class__:
            return (self.number, self.name) >= (other.number, other.name)
        return NotImplemented  # pragma: no cover

    def __getattr__(self, name):
        """Implement attribute shortcuts.
        Only gets called if getattribute fails.
        """
        # Implements shortcuts: omission of parameters.physical/dynamical
        if hasattr(self.parameters.physical, name):
            return getattr(self.parameters.physical, name)
        elif hasattr(self.parameters.dynamical, name):
            return getattr(self.parameters.dynamical, name)
        else:
            raise AttributeError(f"Unknown attribute {name}")

    def __add_metadata(self):
        """docstring for __add_metadata"""
        # TODO slow, replace by dict mapping
        for meta in ["unit", "uncertainty"]:
            for path in pd.json_normalize(TEMPLATE).columns:
                if meta in path:
                    quantity = path.replace(f".{meta}", "")
                    try:
                        setattr(
                            rocks.utils.rgetattr(self, quantity),
                            meta,
                            rocks.utils.rgetattr(self, path),
                        )
                    except AttributeError:
                        pass  # some unit paths are ill-defined

    def __add_datacloud_catalogue(self, catalogue):
        """docstring for __add_datacloud_catalogue"""
        if not hasattr(getattr(self, "datacloud"), catalogue):
            warnings.warn(f"Unknown datacloud catalogue requested: {catalogue}")
            return

        catalogue_dict = rocks.utils.retrieve_catalogue(
            getattr(getattr(self, "datacloud"), catalogue)
        )

        if catalogue_dict[self.id]["datacloud"] is None:
            setattr(
                self,
                rocks.utils.DATACLOUD_META[catalogue]["attr_name"],
                None,
            )
            return

        catalogue_list = catalogue_dict[self.id]["datacloud"][catalogue]
        catalogue_list = [rocks.utils.sanitize_keys(dict_) for dict_ in catalogue_list]

        setattr(
            self,
            rocks.utils.DATACLOUD_META[catalogue]["attr_name"],
            cast_types(catalogue_list),
        )


class stringParameter(str):
    """For minor body parameters which are strings, e.g. taxonomy."""

    def __new__(self, value):
        return str.__new__(self, value)

    def __init__(self, value):
        str.__init__(value)


class floatParameter(float):
    """For minor body parameters which are floats, e.g. albedo.

    Allows to assign attributes.
    """

    def __new__(self, value):
        return float.__new__(self, value)

    def __init__(self, value):
        float.__init__(value)


class intParameter(int):
    """For minor body parameters which are floats, e.g. number.

    Allows to assign attributes.
    """

    def __new__(self, value):
        return int.__new__(self, value)

    def __init__(self, value):
        float.__init__(value)


class propertyCollection(SimpleNamespace):
    """For collections of data, e.g. taxonomy -> class, method, shortbib.

    Collections of float properties have plotting and averaging methods.
    """

    def __repr__(self):
        return self.__class__.__qualname__ + json.dumps(self.__dict__, indent=2)

    def __str__(self):
        return self.__class__.__qualname__ + json.dumps(self.__dict__, indent=2)

    def scatter(self, **kwargs):
        return rocks.plots.scatter(self, **kwargs)

    def hist(self, **kwargs):
        return rocks.plots.hist(self, **kwargs)


class listSameTypeParameter(list):
    """For several measurements of a single parameters of any type
    in datcloud catalogues.
    """

    def __init__(self, data):
        """Construct list which allows for assigning attributes.

        Parameters
        ==========
        data : iterable
            The minor body data from datacloud.
        """
        self.datatype = self.__get_type(data[-1])

        if self.datatype is not None:
            list.__init__(self, [self.datatype(d) for d in data])
        else:
            list.__init__(self, [None for d in data])

    def __get_type(self, string):
        """Infers type from str variable."""
        if not string:
            return None
        else:
            try:
                var = float(string)
                # scientific notation is not understood by int
                if var.is_integer() and "e" not in string and "E" not in string:
                    return float
                else:
                    return float
            except ValueError:
                return str

    def weighted_average(self, errors=False):
        """Compute weighted average of float-type parameters.

        Parameters
        ==========
        errors : list of floats, np.ndarraya of floats
            Optional list of associated uncertainties.  Default is unit
            unceratinty.

        Returns
        ======
        (float, float)
        Weighted average and its uncertainty.
        """
        if self.datatype is not float:
            raise TypeError("Property is not of type float.")

        observable = np.array(self)

        # Make uniform weights in case no errors are provided
        if not errors:
            warnings.warn("No error provided, using uniform weights.")
            errors = np.ones(len(self))
        else:
            # Remove measurements where the error is zero
            errors = np.array(errors)
        return rocks.utils.weighted_average(observable, errors)


def rocks_(identifier, datacloud=[]):
    """Create multiple Rock instances via POST request.

    Parameters
    ==========
    identifier : list of str, list of int, list of float, np.array, pd.Series
        An iterable containing minor body identifiers.
    datacloud : list of str
        List of additional catalogues to retrieve from datacloud. Default is
        [], no additional data.

    Returns
    =======
    list of rocks.core.Rock
        A list of Rock instances
    """
    if isinstance(identifier, pd.Series):
        identifier = identifier.values

    # Ensure we know these objects
    ids = [id_ for name, number, id_ in identify(identifier, return_id=True)]
    # Sent POST request
    ssoCards = rocks.utils.get_ssoCard(ids)
    # Build rocks
    rocks_ = []
    for id_, ssoCard in track(
        zip(ids, ssoCards), total=len(ids), description="Building rocks"
    ):
        rocks_.append(Rock(id_, ssoCard, datacloud, skip_id_check=True))

    return rocks_


@singledispatch
def cast_types(value):
    return value


@cast_types.register(dict)
def _cast_dict(value):
    return propertyCollection(
        **{
            k: cast_types(v) if isinstance(v, dict) else __TYPES[type(v)](v)
            for k, v in value.items()
        }
    )


@cast_types.register(list)
def _cast_list(li):
    """Turn lists of dicts into a dict of lists."""
    return propertyCollection(
        **{k: listSameTypeParameter([dic[k] for dic in li]) for k in li[0]}
    )


__TYPES = {
    None: lambda v: None,
    int: intParameter,
    str: stringParameter,
    float: floatParameter,
    dict: propertyCollection,
    list: _cast_list,
}
