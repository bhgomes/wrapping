# -*- coding: utf-8 -*- #
#
# wrapping/importer.py
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
Wrapping Library: Importer.
"""

# ------------------------ Standard Library ------------------------ #

from typing import Any, AnyStr, Union, Sequence, Tuple, List, Callable, Iterable
from importlib import import_module

# ------------------------ External Library ------------------------ #

from wrapt.importer import (
    register_post_import_hook,
    when_imported,
    notify_module_loaded,
    discover_post_import_hooks,
)

# ------------------------ Wrapping Library ------------------------ #

__extensions__ = ("fallback_import", "try_import")

__all__ = (
    "register_post_import_hook",
    "when_imported",
    "notify_module_loaded",
    "discover_post_import_hooks",
) + __extensions__


def fallback_import(name: AnyStr, package: AnyStr, fallback_package: AnyStr) -> Any:
    """
    Fallback importer.
    :param name: Name of package.
    :param package: Package Anchor.
    :param fallback_package: Fallback Package Anchor.
    :return: Imported Package.
    """
    try:
        return import_module(name, package)
    except ImportError:
        return import_module(name, fallback_package)


def _recurse_try_import(
    names: Sequence[AnyStr],
    package: AnyStr,
    exceptions: Iterable[Exception],
    log_error: Callable[[Any], None],
    log_success: Callable[[Any], None],
    default: Any,
) -> Tuple[List[Any], List[bool]]:
    """
    Recurse Try-Import Mechanism.
    :param names: Names to import
    :param package: Anchor Package
    :param exceptions: Exceptions to catch during import
    :param log_error: Log function for errors
    :param log_success: Log function for successes
    :param default: Default value for missing names
    :return: Pair of resulting objects and success/failure flags
    """
    return tuple(
        zip(
            *[
                try_import(
                    name,
                    package,
                    *exceptions,
                    log_error=log_error,
                    log_success=log_success,
                    default=default
                )
                for name in names
            ]
        )
    )


def try_import(
    names: Union[AnyStr, Sequence[AnyStr]],
    package: AnyStr = None,
    *exceptions: Exception,
    log_error: Callable[[Any], None] = lambda s: None,
    log_success: Callable[[Any], None] = lambda s: None,
    default: Any = None
) -> Union[Tuple[Any, bool], Tuple[List[Any], List[bool]]]:
    """
    Attempt Package Import With Automatic Exception Handling.
    :param names: Names to import. Input as one string or a list of strings.
    :param package: Anchor Package for relative imports.
    :param exceptions: Exception types to catch on import.
    :param log_error: Log function for logging errors.
    :param log_success: Log function for logging successes.
    :param default: Default value for missing names.
    :return: Pair of result and success/failure flag
    """
    if not exceptions:
        exceptions = (ImportError, ModuleNotFoundError)
    if not isinstance(names, str) and isinstance(names, Sequence):
        return _recurse_try_import(
            names, package, exceptions, log_error, log_success, default
        )
    elif names.startswith(".") and package is None:
        raise TypeError("Relative Packages must be imported with an anchor package.")
    try:
        module = import_module(names, package=package)
        log_success(module)
        return module, True
    except exceptions as error:
        try:
            module = import_module(package)
            resource = getattr(module, names)
            log_success(resource)
            return resource, True
        except exceptions as import_error:
            log_error(import_error)
        except AttributeError as attribute_error:
            log_error(attribute_error)
        log_error(error)
    return default, False
