# -*- coding: utf-8 -*- #
#
# wrapping/wrappers.py
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
Wrapping Library: Wrappers.
"""

# ------------------------ Standard Library ------------------------ #

from copy import copy
from typing import Any, Union, TypeVar

# ------------------------ External Library ------------------------ #

from wrapt.wrappers import (
    ObjectProxy,
    CallableObjectProxy,
    FunctionWrapper,
    BoundFunctionWrapper,
    WeakFunctionProxy,
    resolve_path,
    apply_patch,
    wrap_object,
    wrap_object_attribute,
    function_wrapper,
    wrap_function_wrapper,
    patch_function_wrapper,
    transient_function_wrapper,
)

# ------------------------ Wrapping Library ------------------------ #


__extensions__ = ("value_or", "FullObjectProxy", "Restricted", "Bounded")

__all__ = (
    "ObjectProxy",
    "CallableObjectProxy",
    "FunctionWrapper",
    "BoundFunctionWrapper",
    "WeakFunctionProxy",
    "resolve_path",
    "apply_patch",
    "wrap_object",
    "wrap_object_attribute",
    "function_wrapper",
    "wrap_function_wrapper",
    "patch_function_wrapper",
    "transient_function_wrapper",
) + __extensions__


A = TypeVar("A")

B = TypeVar("B")


def value_or(value: A, default: B) -> Union[A, B]:
    """Get Value or the Default if the Value is None.Like a Maybe Monad.
    :param value: Value to test.
    :param default: Default result.
    :return: Value or default.
    """
    return value if value is not None else default


class FullObjectProxy(ObjectProxy):
    """Fully Implemented Object Proxy."""

    def __call__(self, *args, **kwargs):
        """Call Implementation.
        :param args:
        :param kwargs:
        :return:
        """
        return self.__wrapped__(*args, **kwargs)

    def __copy__(self):
        """Default Copy Implementation.
        :return:
        """
        return type(self)(self.__wrapped__.__copy__())

    def __deepcopy__(self, memo):
        """Default Deepcopy Implementation.
        :param memo:
        :return:
        """
        return type(self)(self.__wrapped__.__deepcopy__(memo))

    def __reduce__(self):
        """Default Reduce Implementation.
        :return:
        """
        reduce_value = self.__wrapped__.__reduce__()
        if isinstance(reduce_value, str):
            return reduce_value
        if isinstance(reduce_value, tuple):
            caller, arguments, *rest = reduce_value
            return (lambda *args: type(self)(caller(*args)), arguments, *rest)
        else:
            raise TypeError("__reduce__ must return a string or tuple")

    def __reduce_ex__(self, protocol):
        """Default Reduce Ex Implementation.
        :param protocol:
        :return:
        """
        reduce_value = self.__wrapped__.__reduce_ex__(protocol)
        if isinstance(reduce_value, str):
            return reduce_value
        if isinstance(reduce_value, tuple):
            caller, arguments, *rest = reduce_value
            return (lambda *args: type(self)(caller(*args)), arguments, *rest)
        else:
            raise TypeError("__reduce__ must return a string or tuple")


class Restricted(FullObjectProxy):
    """
    Restricted-Object Wrapper.
    """

    def __init__(self, value, *, clamp=None, auto_clamp=True):
        """Initialize Restricted Object.
        :param value: Internal Value.
        :param clamp: Clamp function.
        :param auto_clamp: Set to always clamp.
        """
        super().__init__(value)
        self._self_clamp = clamp
        self._self_auto_clamp = auto_clamp
        if auto_clamp:
            self.clamp()

    @property
    def auto_clamp(self):
        """
        :return: Auto Clamp Flag.
        """
        return self._self_auto_clamp

    @auto_clamp.setter
    def auto_clamp(self, auto):
        """Set the Auto Clamp flag.
        :param auto: New auto clamping flag.
        """
        self._self_auto_clamp = auto

    @property
    def clamp_function(self):
        """
        :return: Get the internal Clamp Function.
        """
        return self._self_clamp

    @clamp_function.setter
    def clamp_function(self, function):
        """Set the Clamp Function.
        :param function: New clamp function.
        """
        self._self_clamp = function

    def clamp(self, *args, **kwargs):
        """Restrict the internal value with the clamp function.
        :param args: Positional Arguments to the clamp function.
        :param kwargs: Keyword Arguments to the clamp function.
        :return: Internal value after clamping.
        """
        value_or(self._self_clamp, lambda s, *a, **k: s)(self, *args, **kwargs)
        return self

    def clamped(self, *args, **kwargs):
        """Get Clamped Copy of the internal value.
        :param args: Positional arguments to clamp function.
        :param kwargs: Keyword arguments to clamp function.
        :return: Copy of Internal Value after clamping.
        """
        try:
            return copy(self).clamp(*args, **kwargs)
        except AttributeError:
            value = type(self)(
                self.__wrapped__, clamp=self._self_clamp, auto_clamp=False
            )
            return value.clamp(*args, **kwargs)

    def clamp_at(self, new_value, *args, **kwargs):
        """Clamp Internal Object at New Value..
        :param new_value: New value of wrapped object.
        :param args: Positional Arguments to Clamp.
        :param kwargs: Keyword Arguments to Clamp.
        :return: Clamped Value.
        """
        self.__wrapped__ = new_value
        return self.clamp(*args, **kwargs)

    @property
    def on_boundary(self):
        """
        :return: True if Object is on the Boundary.
        """
        return self == self.clamped

    @property
    def is_unrestricted(self):
        """
        :return: True if Object is Unrestricted.
        """
        return self._self_clamp is None

    @property
    def is_restricted(self):
        """
        :return: True if Object is Restricted.
        """
        return not self.is_unrestricted

    def _clamp_after(self, operation, other):
        """
        :param operation:
        :param other:
        :return:
        """
        getattr(super(), operation)(other)
        if self.auto_clamp:
            self.clamp()

    def __iadd__(self, other):
        """
        :param other:
        :return:
        """
        self._clamp_after("__iadd__", other)

    def __isub__(self, other):
        """
        :param other:
        :return:
        """
        self._clamp_after("__isub__", other)

    def __imul__(self, other):
        """
        :param other:
        :return:
        """
        self._clamp_after("__imul__", other)

    def __imatmul__(self, other):
        """
        :param other:
        :return:
        """
        self._clamp_after("__imatmul__", other)

    def __itruediv__(self, other):
        """
        :param other:
        :return:
        """
        self._clamp_after("__itruediv__", other)

    def __ifloordiv__(self, other):
        """
        :param other:
        :return:
        """
        self._clamp_after("__ifloordiv__", other)

    def __imod__(self, other):
        """
        :param other:
        :return:
        """
        self._clamp_after("__imod__", other)

    def __ipow__(self, other):
        """
        :param other:
        :return:
        """
        self._clamp_after("__ipow__", other)

    def __ilshift__(self, other):
        """
        :param other:
        :return:
        """
        self._clamp_after("__ilshift__", other)

    def __irshift__(self, other):
        """
        :param other:
        :return:
        """
        self._clamp_after("__irshift__", other)

    def __iand__(self, other):
        """
        :param other:
        :return:
        """
        self._clamp_after("__iand__", other)

    def __ixor__(self, other):
        """
        :param other:
        :return:
        """
        self._clamp_after("__ixor__", other)

    def __ior__(self, other):
        """
        :param other:
        :return:
        """
        self._clamp_after("__ior__", other)


class Bounded(Restricted):
    """
    Bounded Object Proxy.

    """

    @classmethod
    def _fix_boundary_ordering(cls, minimum, maximum):
        """
        :param minimum:
        :param maximum:
        :return:
        """
        if minimum is not None and maximum is not None:
            if minimum >= maximum:
                return maximum, maximum
            if maximum <= minimum:
                return minimum, minimum
        return minimum, maximum

    @classmethod
    def _clamp_function(cls, obj, minimum=None, maximum=None):
        """Clamp Object Between Minimum and Maximum.
        :param obj: 
        :param minimum: 
        :param maximum: 
        :return: 
        """
        minimum, maximum = cls._fix_boundary_ordering(
            value_or(minimum, obj._self_min), value_or(maximum, obj._self_max)
        )
        if minimum is not None:
            obj._self_min = minimum
        if obj._self_min is not None:
            obj.__wrapped__ = max(obj._self_min, obj.__wrapped__)
        if maximum is not None:
            obj._self_max = maximum
        if obj._self_max is not None:
            obj.__wrapped__ = min(obj._self_max, obj.__wrapped__)
        return obj.__wrapped__

    def __init__(self, value, *, minimum=None, maximum=None, auto_clamp=True):
        """Initialized Wrapped Bounded Object.
        :param value:
        :param minimum:
        :param maximum:
        """
        super().__init__(value, clamp=type(self)._clamp_function, auto_clamp=False)
        minimum, maximum = type(self)._fix_boundary_ordering(minimum, maximum)
        self._self_min = minimum
        self._self_max = maximum
        self.auto_clamp = auto_clamp
        if auto_clamp:
            self.clamp()

    def __repr__(self):
        """
        :return: Representation of Bounded Class Object.
        """
        prefix = "{}[{}]({}".format(
            type(self).__name__, self.__class__.__name__, self.__wrapped__
        )
        if self.is_unbounded:
            return prefix + ")"
        return (prefix + ", minimum={}, maximum={})").format(self.minimum, self.maximum)

    def clamped(self, *args, **kwargs):
        """Get Clamped Copy of the internal value.
        :param args: Positional arguments to clamp function.
        :param kwargs: Keyword arguments to clamp function.
        :return: Copy of Internal Value after clamping.
        """
        try:
            return copy(self).clamp(*args, **kwargs)
        except AttributeError:
            value = type(self)(
                self.__wrapped__,
                minimum=self.minimum,
                maximum=self.maximum,
                auto_clamp=False,
            )
            return value.clamp(*args, **kwargs)

    @property
    def minimum(self):
        """Get Minimum."""
        return self._self_min

    @minimum.setter
    def minimum(self, new_minimum):
        """Clamp at Minimum"""
        self.clamp(minimum=new_minimum)

    @property
    def maximum(self):
        """Get Maximum."""
        return self._self_max

    @maximum.setter
    def maximum(self, new_maximum):
        """Clamp at Maximum"""
        self.clamp(maximum=new_maximum)

    @property
    def is_unbounded(self):
        """
        :return: True if Object is Unbounded.
        """
        return self.is_unrestricted

    @property
    def is_bounded(self):
        """
        :return: True if Object is Bounded.
        """
        return not self.is_unbounded

    @property
    def is_unbounded_from_above(self):
        """
        :return: True if Object is not bounded from above.
        """
        return self.maximum is None

    @property
    def is_bounded_from_above(self):
        """
        :return: True if Object is bounded from above.
        """
        return self.maximum is not None

    @property
    def is_unbounded_from_below(self):
        """
        :return: True if Object is not bounded from below.
        """
        return self.minimum is None

    @property
    def is_bounded_from_below(self):
        """
        :return: True if Object is bounded from below.
        """
        return self.minimum is not None

    @property
    def width(self):
        """
        :return: Interval containing the internal value.
        """
        try:
            return self.maximum - self.minimum
        except TypeError:
            return None

    def is_equal_as_bounded(self, other):
        """Check that Bounded Types are Equal and Bounded Equally.
        :param other: Other Bounded object.
        :return: Whether or not the objects are equal as internal values and
        as bounded objects.
        """
        if not isinstance(other, type(self)):
            return NotImplemented
        return (
            super().__eq__(other)
            and self.minimum == other.minimum
            and self.maximum == other.maximum
        )
