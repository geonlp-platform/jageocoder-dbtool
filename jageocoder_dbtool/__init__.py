from .convertor import ConvertorException, Convertor
from .data_manager import DataManager
from .metadata import Catalog

__all__ = [
    "ConvertorException",
    "Convertor",
    "DataManager",
    "Catalog",
]


def get_version():
    return Catalog.get_version()
