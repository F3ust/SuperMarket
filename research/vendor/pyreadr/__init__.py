"""""" # start delvewheel patch
def _delvewheel_patch_1_13_2():
    import os
    if os.path.isdir(libs_dir := os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, 'pyreadr.libs'))):
        os.add_dll_directory(libs_dir)


_delvewheel_patch_1_13_2()
del _delvewheel_patch_1_13_2
# end delvewheel patch

_has_pandas = False
_has_polars = False
try:
    import pandas
    _has_pandas = True
except ImportError:
    pass
try:
    import polars
    _has_polars = True
except ImportError:
    pass

if not _has_pandas and not _has_polars:
    raise ImportError("pyreadr requires either pandas or polars to be installed. "
                      "Please install at least one of them.")

from .pyreadr import read_r, list_objects, read_metadata, write_rds, write_rdata, download_file
from .custom_errors import PyreadrError, LibrdataError

__version__ = "0.5.9"

