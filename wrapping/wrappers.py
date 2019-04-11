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

# -------------- External Library -------------- #

from wrapt.wrappers import (
    ObjectProxy,
    CallableObjectProxy,
    FunctionWrapper,
    BoundFunctionWrapper,
    WeakFunctionProxy,
    PartialCallableObjectProxy,
    resolve_path,
    apply_patch,
    wrap_object,
    wrap_object_attribute,
    function_wrapper,
    wrap_function_wrapper,
    patch_function_wrapper,
    transient_function_wrapper,
)

# -------------- Wrapping Library -------------- #

from .util import partial


__extensions__ = ("FullObjectProxy", "Bounded")

__all__ = (
    "ObjectProxy",
    "CallableObjectProxy",
    "FunctionWrapper",
    "BoundFunctionWrapper",
    "WeakFunctionProxy",
    "PartialCallableObjectProxy",
    "resolve_path",
    "apply_patch",
    "wrap_object",
    "wrap_object_attribute",
    "function_wrapper",
    "wrap_function_wrapper",
    "patch_function_wrapper",
    "transient_function_wrapper",
) + __extensions__


class FullObjectProxy(ObjectProxy):
    """Fully Implemented Object Proxy."""

    def __call__(self, *args, **kwargs):
        """Call Implementation."""
        return self.__wrapped__(*args, **kwargs)

    def __copy__(self):
        """Default Copy Implementation."""
        return type(self)(self.__wrapped__.__copy__())

    def __deepcopy__(self, memo):
        """Default Deepcopy Implementation."""
        return type(self)(self.__wrapped__.__deepcopy__(memo))

    def __reduce__(self):
        """Default Reduce Implementation."""
        reduce_value = self.__wrapped__.__reduce__()
        if isinstance(reduce_value, str):
            return reduce_value
        if isinstance(reduce_value, tuple):
            caller, arguments, *rest = reduce_value
            return (lambda *args: type(self)(caller(*args)), arguments, *rest)
        else:
            raise TypeError("__reduce__ must return a string or tuple")

    def __reduce_ex__(self, protocol):
        """Default Reduce Ex Implementation."""
        reduce_value = self.__wrapped__.__reduce_ex__(protocol)
        if isinstance(reduce_value, str):
            return reduce_value
        if isinstance(reduce_value, tuple):
            caller, arguments, *rest = reduce_value
            return (lambda *args: type(self)(caller(*args)), arguments, *rest)
        else:
            raise TypeError("__reduce__ must return a string or tuple")


class Bounded(FullObjectProxy):
    """
    Bounded Object Proxy.

    """

    def _default_clamp_function(self, minimum=None, maximum=None):
        """Clamp Object Between Minimum and Maximum."""
        if self._self_minimum is not None:
            if minimum is not None:
                self._self_minimum = minimum
            self.__wrapped__ = max(self._self_minimum, self.__wrapped__)
        if self._self_maximum is not None:
            if maximum is not None:
                self._self_maximum = maximum
            self.__wrapped__ = min(self._self_maximum, self.__wrapped__)

    def __init__(self, wrapped, *, minimum=None, maximum=None, clamp_function=None):
        """Initialized Wrapped Bounded Object."""
        super().__init__(wrapped)
        self._self_minimum = minimum
        self._self_maximum = maximum
        if clamp_function is not None:
            self._self_clamp_function = partial(clamp_function, self.__wrapped__)
            delattr(self, "minimum")
            delattr(self, "maximum")
            delattr(self, "is_unbounded")
            delattr(self, "is_bounded")
            delattr(self, "is_equal_as_bounded")
        else:
            self._self_clamp_function = self._default_clamp_function
        self.clamp()

    @property
    def minimum(self):
        """Get Minimum."""
        return self._self_minimum

    @minimum.setter
    def minimum(self, new_minimum):
        """Clamp at Minimum"""
        self.clamp(minimum=new_minimum)

    @property
    def maximum(self):
        """Get Maximum."""
        return self._self_maximum

    @maximum.setter
    def maximum(self, new_maximum):
        """Clamp at Maximum"""
        self.clamp(maximum=new_maximum)

    def clamp(self, *args, **kwargs):
        """Clamp Object Between Minimum and Maximum."""
        return self._self_clamp_function(*args, **kwargs)

    def _clamp_after(self, operation, other):
        """"""
        getattr(super(), operation)(other)
        self.clamp()

    @property
    def is_unbounded(self):
        """Check if Object is Unbounded."""
        return self.minimum is None and self.maximum is None

    @property
    def is_bounded(self):
        """Check if Object is Bounded."""
        return not self.is_unbounded

    def is_equal_as_bounded(self, other):
        """Check that Bounded Types are Equal and Bounded Equally."""
        if not isinstance(other, type(self)):
            return NotImplemented
        return (
            super().__eq__(other)
            and self.minimum == other.minimum
            and self.maximum == other.maximum
        )

    def __iadd__(self, other):
        self._clamp_after("__iadd__", other)

    def __isub__(self, other):
        self._clamp_after("__isub__", other)

    def __imul__(self, other):
        self._clamp_after("__imul__", other)

    def __imatmul__(self, other):
        self._clamp_after("__imatmul__", other)

    def __itruediv__(self, other):
        self._clamp_after("__itruediv__", other)

    def __ifloordiv__(self, other):
        self._clamp_after("__ifloordiv__", other)

    def __imod__(self, other):
        self._clamp_after("__imod__", other)

    def __ipow__(self, other):
        self._clamp_after("__ipow__", other)

    def __ilshift__(self, other):
        self._clamp_after("__ilshift__", other)

    def __irshift__(self, other):
        self._clamp_after("__irshift__", other)

    def __iand__(self, other):
        self._clamp_after("__iand__", other)

    def __ixor__(self, other):
        self._clamp_after("__ixor__", other)

    def __ior__(self, other):
        self._clamp_after("__ior__", other)
