import os
from pathlib import Path
import stat

def file_size_to_string_human(num_bytes):
    units = ["bytes", "KiB", "MiB", "GiB", "TiB"]
    multiplier = 1024
    ans, i = num_bytes, 0
    while ans > multiplier and i < len(units) - 1:
        ans /= multiplier
        i += 1
    return f"{f'{ans:.2f}'.rstrip('0').rstrip('.')} {units[i]}"

def time_to_string_human(time):
    import datetime
    return datetime.datetime.fromtimestamp(time).strftime('%Y-%m-%d %H:%M:%S')

def is_hidden(path):
    path = Path(path)
    if path.name.startswith('.') and path.name not in ('.', '..'):
        return True
    # Windows
    if path.name.startswith('.') or \
       (path.exists() and bool(os.stat(path).st_file_attributes & stat.FILE_ATTRIBUTE_HIDDEN)):
        return True
    return False
