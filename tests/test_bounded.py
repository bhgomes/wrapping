# -*- coding: utf-8 -*- #
#
# tests/test_bounded.py
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
Wrapping: Bounded Test.
"""

# ------------------------ External Library ------------------------ #

import pytest
from hypothesis import given, assume
from hypothesis import strategies as st
from hypothesis.stateful import RuleBasedStateMachine, rule, invariant, initialize

# ------------------------ Wrapping Library ------------------------ #

from wrapping import Bounded
from .core import anything


@given(anything)
def test_initialization(obj):
    Bounded(obj)


def build_strategy(strategy, *args, **kwargs):
    """
    Build Compound Strategy for Bounded.
    :param strategy:
    :return:
    """
    return st.builds(
        Bounded,
        strategy(*args, **kwargs),
        minimum=st.none() | strategy(*args, **kwargs),
        maximum=st.none() | strategy(*args, **kwargs),
    )


bounded_strategy = st.one_of(
    build_strategy(st.integers),
    build_strategy(st.floats, allow_nan=False, allow_infinity=False),
    build_strategy(st.characters),
)


@given(bounded_strategy)
def test_clamp(bounded):
    value = bounded.__wrapped__
    minimum = bounded.minimum
    maximum = bounded.maximum
    clamped = bounded.clamped()
    if minimum is not None and value <= minimum:
        assert clamped == minimum
    elif maximum is not None and value >= maximum:
        assert clamped == maximum
    else:
        assert clamped == value
    assert bounded == value
    bounded.clamp()
    if minimum is not None and value <= minimum:
        assert bounded == minimum
    elif maximum is not None and value >= maximum:
        assert bounded == maximum
    else:
        assert bounded == value


@given(bounded_strategy)
def test_boundedness_consistency(bounded):
    if bounded.is_unbounded:
        assert not bounded.is_bounded
    elif bounded.is_bounded:
        assert not bounded.is_unbounded
    if bounded.is_unbounded_from_above:
        assert not bounded.is_bounded_from_above
    elif bounded.is_bounded_from_above:
        assert not bounded.is_unbounded_from_above
    if bounded.is_unbounded_from_below:
        assert not bounded.is_bounded_from_below
    elif bounded.is_bounded_from_below:
        assert not bounded.is_unbounded_from_below


@given(bounded_strategy)
def test_width(bounded):
    if bounded.is_unbounded:
        assert bounded.width is None
    elif bounded.is_bounded_from_above and bounded.is_bounded_from_below:
        try:
            width = bounded.maximum - bounded.minimum
            assert bounded.width == width
        except TypeError:
            assert bounded.width is None


class BoundedMachine(RuleBasedStateMachine):
    @initialize(bounded=bounded_strategy)
    def make_bounded(self, bounded):
        self.bounded = bounded
        if isinstance(self.bounded, int):
            self.strategy = st.integers()
        elif isinstance(self.bounded, float):
            self.strategy = st.floats(allow_infinity=False, allow_nan=False)
        elif isinstance(self.bounded, str):
            self.strategy = st.characters()
        else:
            pytest.fail("Strategy Creation Failed.")

    @rule(data=st.data())
    def change_max(self, data):
        self.bounded.maximum = data.draw(self.strategy)

    @rule(data=st.data())
    def change_min(self, data):
        self.bounded.minimum = data.draw(self.strategy)

    @rule(data=st.data())
    def change_value(self, data):
        self.bounded.clamp_at(data.draw(self.strategy))

    @invariant()
    def always_clamped(self):
        if hasattr(self, "bounded") and self.bounded.is_bounded:
            if self.bounded.minimum is not None:
                assert self.bounded.minimum <= self.bounded.__wrapped__
            if self.bounded.maximum is not None:
                assert self.bounded.__wrapped__ <= self.bounded.maximum

    @invariant()
    def always_self_equal(self):
        if hasattr(self, "bounded"):
            assert self.bounded == self.bounded.__wrapped__
            assert self.bounded.is_equal_as_bounded(self.bounded.clamped())
            assert self.bounded.clamped().is_equal_as_bounded(self.bounded)
            assert (
                self.bounded.is_equal_as_bounded(self.bounded.__wrapped__)
                is NotImplemented
            )

    @invariant()
    def always_represented(self):
        if hasattr(self, "bounded"):
            repr_string = repr(self.bounded)
            assert repr_string == self.bounded.__repr__()
            assert str(self.bounded) in repr_string
            assert self.bounded.__class__.__name__ in repr_string
            if self.bounded.is_bounded:
                assert str(self.bounded.minimum) in repr_string
                assert str(self.bounded.maximum) in repr_string


TestBoundedMachine = BoundedMachine.TestCase
