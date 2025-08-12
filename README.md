# DiskSnapshot
[![license-gpl 3](https://img.shields.io/badge/license-GPL%203-blue.svg?style=flat-square)](https://www.gnu.org/licenses/gpl-3.0.html)
[![python-3.7+](https://img.shields.io/badge/python-3.7+-brightgreen.svg?style=flat-square)](https://www.python.org/downloads/release/python-370/)

DiskSnapshot is a utility for creating, analyzing, and comparing disk metadata snapshots.  
These lightweight snapshots capture file system metadata (paths, sizes, timestamps) without file contents,  
making them perfect for change monitoring, audit trails, and version tracking.

**IMPORTANT: This tool does not perform file backups - snapshots only contain metadata, not file contents!**


## Requirements
 - Python 3.7+

### Usage
 - for gui
    ``` bash
    > python main_gui.py
    ```

 - for cli
    ``` bash
    > python main.py g folder --output folder_old.snap

    something changed...

    > python main.py g folder --output folder_new.snap
    > python main.py c folder_old.snap folder_new.snap
    ```

## To-Do
 - Use other GUI libraries.
 - Parallel processing.
 - Add hash code records for the snapshot entries.
 - Progress bar in cli.
 - Publish to pypi.
