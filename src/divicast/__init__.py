from importlib.metadata import PackageNotFoundError, version

try:
    __version__ = version("divicast")
except PackageNotFoundError:
    __version__ = "0+unknown"

from .sixline.divinatory_symbol import DivinatorySymbol

__all__ = [
    "DivinatorySymbol",
    "__version__",
]
