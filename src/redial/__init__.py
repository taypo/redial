# -*- coding: utf-8 -*-
try:
    from importlib.metadata import version, PackageNotFoundError
    try:
        __version__ = version("redial")
    except PackageNotFoundError:
        __version__ = 'unknown'
except ImportError:
    # Fallback for Python < 3.8
    from pkg_resources import get_distribution, DistributionNotFound
    try:
        __version__ = get_distribution("redial").version
    except DistributionNotFound:
        __version__ = 'unknown'
