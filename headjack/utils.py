import inspect
import re
from functools import lru_cache
from itertools import chain

import chromadb

@lru_cache(1)
def get_chroma():
    return chromadb.Client()


SOURCE_PATCH = {}

try:
    getsourcelines
except NameError:
    getsourcelines = inspect.getsourcelines


def monkey_patch_getsourcelines(object):
    if object in SOURCE_PATCH:
        return SOURCE_PATCH[object].splitlines(keepends=True), 0
    return getsourcelines(object)


inspect.getsourcelines = monkey_patch_getsourcelines


def window_document(file_name: str, document_text: str, window_size: int = 100, overlap: int = 25):
    """
    Splits a document into overlapping windows of fixed size.

    Args:
        document (str): The document to split.
        window_size (int): The word size of each window.
        overlap (int): The amount of word overlap between adjacent windows.

    Returns:
        List[str]: A list of overlapping windows.
    """

    document = re.split(r"\s+", document_text)
    title = re.split(r"[._-]+", file_name) + re.split(r"\s+", document_text.split("\n")[0])[:10]
    windows = []
    start = 0
    end = window_size
    while end <= len(document):
        windows.append(" ".join((title if start != 0 else []) + document[start:end]))
        start += window_size - overlap
        end += window_size - overlap
    if end > len(document) and start < len(document):
        windows.append(" ".join(title + document[start:]))
    return windows
