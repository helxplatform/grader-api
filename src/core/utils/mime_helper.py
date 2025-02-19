from pathlib import Path
from typing import IO
from mimetypes import guess_type

def guess_mimetype(path: str | Path) -> str | None:
    ext = Path(path).suffix.lstrip(".").lower()
    if ext == "ipynb":
        return "application/x-ipynb+json"
    if ext == "r" or ext == "rmd":
        # R does not define MIME types for their file extensions.
        # This is reiterated by extramime from Yihui Xie's R mime package.
        return "text/plain"
    return guess_type(path)[0]