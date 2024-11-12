# SPDX-FileCopyrightText: 2016 Ole Martin Bjorndalen <ombdalen@gmail.com>
# SPDX-FileCopyrightText: 2023 Raphaël Doursenaud <rdoursenaud@gmail.com>
#
# SPDX-License-Identifier: MIT

"""
MIDO Library Version Management
"""

import importlib.metadata
import warnings

import packaging.version

__version__ = "0.0.0.dev0"

try:
    __version__ = importlib.metadata.version("mido")
except importlib.metadata.PackageNotFoundError:
    # Package is not installed
    warnings.warn("mido is not installed, can't determine its version.",
                  stacklevel=2)
    pass

version_info = packaging.version.Version(__version__)
