# -*- coding: utf-8 -*- #
#
# tests/test_module.py
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
Wrapping: Test that Wrapping is a Supermodule of Wrapt.
"""

# ------------------------ External Library ------------------------ #

import pytest
import wrapt

# ------------------------ Wrapping Library ------------------------ #

import wrapping


def test_import():
    import wrapping._version
    import wrapping.box_extension
    import wrapping.decorators
    import wrapping.importer
    import wrapping.wrappers


@pytest.mark.parametrize("name", wrapping.__all__)
def test_supermodule(name):
    try:
        getattr(wrapt, name)
    except AttributeError:
        assert name in wrapping.__extensions__
