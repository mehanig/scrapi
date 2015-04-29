"""Importing harvesters imports all file and folders contained in
the harvesters folder. All harvesters should be defined in here.
NOTE: Empty folders in will cause this to break
"""
import os

# Get a list of folders
_, __all__, files = next(os.walk(os.path.dirname(__file__)))

# Find all .py files that are not init
__all__.extend([
    name[:-3]
    for name in files
    if name[-3:] == '.py'
    and name != '__init__.py'
])
# .remove('__pycache__') doesn't work right after extend.
__all__.remove('__pycache__')
# Import everything in __all__
from . import *