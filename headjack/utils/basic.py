def strip_whole(string: str, pattern: str, beginning: bool = False, end: bool =True):
    if beginning and string.startswith(pattern):
        string = string[len(pattern):]
    if end and string.endswith(pattern):
        string = string[:-len(pattern)]
    return string