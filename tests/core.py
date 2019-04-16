# -*- coding: utf-8 -*- #
#
# tests/core.py
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
Wrapping Test Suite.
"""

# ------------------------ External Library ------------------------ #

from hypothesis import strategies as st

# ------------------------ Wrapping Library ------------------------ #

anything = st.one_of(
    st.none(),
    st.integers(),
    st.floats(),
    st.booleans(),
    st.complex_numbers(),
    st.characters(),
    st.binary(),
    st.decimals(),
    st.dictionaries(st.text(), st.integers()),
    st.emails(),
    st.fractions(),
    st.text(),
    st.sets(st.integers() | st.floats()),
    st.lists(st.integers() | st.floats()),
    st.lists(st.integers() | st.floats()).map(tuple),
)
