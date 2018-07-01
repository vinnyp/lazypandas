"""lazypandas - A collection of data wrangling helper methods for pandas."""

from __future__ import absolute_import
from . import io
from .io import Export
import logging

logging.getLogger(__name__).addHandler(logging.NullHandler())

_export = Export()
path_out = _export.path_out
timestamp_label = _export.timestamp_label

def export_df(*args, **kwargs):
    _export.path_out = path_out
    return _export.export_df(*args, **kwargs)


__version__ = '0.1.0'
__author__ = 'Vinny Pasceri <vinnypasceri@gmail.com>'
__all__ = []
