import os
from pathlib import Path
from typing import Sequence, Tuple, Union

AddressType = Tuple[int, str]
PathLikeType = Union[str, Path, os.PathLike]
PathListType = Sequence[PathLikeType]
