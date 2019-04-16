# -*- coding: utf-8 -*- #
#
# wrapping/box_extension.py
#
#
# MIT License
#
# Copyright (c) 2019 Brandon Gomes
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#

"""
Wrapping Library: Box Extension.
"""

# ------------------------ Standard Library ------------------------ #

from collections.abc import Mapping

# ------------------------ External Library ------------------------ #

import wrapt

# ------------------------ Wrapping Library ------------------------ #

from .wrappers import value_or


__extensions__ = ("Box", "FrozenBox", "subset_box")


try:
    import box

    __extensions__ += ("BoxObject",)
    __all__ = __extensions__
    _Box = box.Box
except ImportError:
    box = None
    _Box = object
    __all__ = ()


class Box(_Box):
    """
    Box Extension Object.

    """

    defaults = {}
    frozen_defaults = False

    def __init_subclass__(cls, defaults=None, frozen_defaults=False, **kwargs):
        """
        :param defaults:
        :param frozen_defaults:
        :param kwargs:
        :return:
        """
        super().__init_subclass__(**kwargs)
        cls.defaults = value_or(defaults, {})
        cls.frozen_defaults = frozen_defaults

    def __init__(self, *args, **kwargs):
        """
        Initialize Box with custom Defaults
        :param args:
        :param kwargs:
        """
        defaults = type(self).defaults
        if type(self).frozen_defaults:
            for k, v in self.defaults.items():
                if k in kwargs:
                    if v != kwargs[k]:
                        raise TypeError(
                            "Box default {key}={value} is permanent.".format(
                                key=k, value=v
                            )
                        )
                    kwargs.pop(k)
        else:
            defaults.update(**kwargs)
        super().__init__(*args, **defaults)


class _BoxObject(wrapt.ObjectProxy):
    """
    Wrapper for any Python object with a Box as __dict__.

    Simple Usage:
    import requests
    url = 'https://raw.githubusercontent.com/cdgriffith/Box/master/box.py'
    session = BoxObject(requests.Session())
    session.source_code = session.get(url).text

    :param wrapped: Wrapped Object.
    :param box_class: Custom internal Box class
    :param args: Arguments to fill Box
    :param kwargs: Keyword arguments to fill Box
    """

    def __init__(self, wrapped=None, *args, **kwargs):
        """Initialize Box Object with __dict__ as a Box."""
        super().__init__(wrapped)
        box_class = kwargs.pop("box_class", Box)
        try:
            base_dict = super().__getattr__("__dict__")
            if args:
                raise TypeError(
                    "Cannot pass dictionary arguments when "
                    "internal object has __dict__ attributes. "
                    "Pass arguments by keyword instead."
                )
            internal_box = box_class(base_dict, **kwargs)
        except AttributeError:
            internal_box = box_class(*args, **kwargs)
        super().__setattr__("__dict__", internal_box)

    def __call__(self, *args, **kwargs):
        """
        Call Method for Callable Objects.
        :param args:
        :param kwargs:
        :return:
        """
        return self.__wrapped__(*args, **kwargs)

    def __getattr__(self, name):
        """
        Get Attribute from Wrapped Object or from Box.
        :param name:
        :return:
        """
        try:
            return super().__getattr__(name)
        except AttributeError as error:
            try:
                return self.__dict__[name]
            except KeyError:
                raise error

    def __setattr__(self, name, value):
        """
        Set Attribute in Wrapped Object or Box.
        :param name:
        :param value:
        :return:
        """
        if name == "__dict__":
            raise TypeError("cannot set __dict__")
        elif hasattr(self.__wrapped__, name):
            setattr(self.__wrapped__, name, value)
        else:
            self.__dict__[name] = value

    def __delattr__(self, name):
        """
        Delete Attribute in Wrapped Object or Box.
        :param name:
        :return:
        """
        if name == "__dict__":
            super().__setattr__("__dict__", getattr(self.__wrapped__, "__dict__", {}))
        else:
            try:
                delattr(self.__wrapped__, name)
            except AttributeError as error:
                try:
                    del self.__dict__[name]
                except KeyError:
                    raise error


class FrozenBox(
    Box,
    defaults={"frozen_box": True, "default_box": True, "default_box_attr": None},
    frozen_defaults=True,
):
    """
    FrozenBox.

    """


def subset_box(total, key=lambda x: x, *, name_for_original=None, box_class=Box):
    """
    Get subset of mapping type as a Box or BoxObject.
    :param total:
    :param key:
    :param name_for_original:
    :param box_class:
    :return:
    """
    subset = key(total)
    kwargs = box_class({name_for_original: total}) if name_for_original else box_class()
    if isinstance(subset, Mapping):
        return box_class(subset, **kwargs)
    return BoxObject(subset, box_class=box_class, **kwargs)


if box is None:
    BoxObject = NotImplemented
else:
    BoxObject = _BoxObject
