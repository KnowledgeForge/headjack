def strip_whole(string: str, pattern: str, beginning: bool = False, end: bool = True):
    if beginning and string.startswith(pattern):
        string = string[len(pattern) :]  # noqa: E203
    if end and string.endswith(pattern):
        string = string[: -len(pattern)]
    return string


def list_dedup(lst: list):
    check_set = []
    ret = []
    for item in lst:
        if item not in check_set:
            ret.append(item)
            check_set.append(item)
    return ret
