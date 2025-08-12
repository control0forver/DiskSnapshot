import io
import utils
import struct
import hashlib
import asyncio
from concurrent.futures import ThreadPoolExecutor
from typing import Optional
from pathlib import Path

SNAPSHOT_FILE_HEADER = b'DISK01SNAP'
ENTRY_TYPE_FILE = 1
ENTRY_TYPE_DIR = 2
ENTRY_TYPE_SYMLINK = 3

# Binary entry format: type(1) | path_len(2) | path(utf8) | size(8) | time(8) | hash(32)
ENTRY_HEADER_FORMAT = '<B H'
ENTRY_FILE_FORMAT = '<Q Q 32s'  # size, time, hash

class SnapshotWriter:
    def __init__(this, src_path, dest_file, ignore_hidden=False, ignore_symlinks=False, max_rec_depth=-1):
        this._src_path = Path(src_path)
        this._output_file = Path(dest_file)
        this._ignore_hidden = ignore_hidden
        this._ignore_symlinks = ignore_symlinks
        this._max_rec_depth = max_rec_depth
        this._write_lock = asyncio.Lock()

    def write_snapshot(this):
        with this._output_file.open('wb') as f:
            f.write(SNAPSHOT_FILE_HEADER)
            this._write_entry(f, this._src_path, 0)

    def _write_entry(this, f:io.BufferedWriter, path:Path, depth):
        if this._max_rec_depth != -1 and depth > this._max_rec_depth:
            return
        if this._ignore_hidden and utils.is_hidden(path):
            return
        
        rel_path = str(path.relative_to(this._src_path.parent)).encode('utf-8')
        path_len = len(rel_path)
        if path.is_file():
            entry_type = ENTRY_TYPE_FILE
            size = path.stat().st_size
            time = int(path.stat().st_mtime)
            hash_value = hashlib.sha256(path.read_bytes()).digest()
            header = struct.pack(ENTRY_HEADER_FORMAT, entry_type, path_len)
            f.write(header)
            f.write(rel_path)
            f.write(struct.pack(ENTRY_FILE_FORMAT, size, time, hash_value))
        elif path.is_symlink():
            if this._ignore_symlinks: 
                return
            entry_type = ENTRY_TYPE_SYMLINK
            header = struct.pack(ENTRY_HEADER_FORMAT, entry_type, path_len)
            f.write(header)
            f.write(rel_path)
            # symlink: size=0, time=0, hash=None
            f.write(struct.pack(ENTRY_FILE_FORMAT, 0, 0, b'\x00' * 32))
        elif path.is_dir():
            entry_type = ENTRY_TYPE_DIR
            header = struct.pack(ENTRY_HEADER_FORMAT, entry_type, path_len)
            f.write(header)
            f.write(rel_path)
            # dir: size=0, time=time, hash=None
            time = int(path.stat().st_mtime)
            f.write(struct.pack(ENTRY_FILE_FORMAT, 0, time, b'\x00' * 32))
            for entry in path.iterdir():
                this._write_entry(f, entry, depth+1)

    # async def _write_entry(this, f: io.BufferedWriter, path: Path, depth, executor: Optional[ThreadPoolExecutor] = None):
    #     if executor is None:
    #         executor = ThreadPoolExecutor()
    #     loop = asyncio.get_running_loop()
        
    #     if this._max_rec_depth != -1 and depth > this._max_rec_depth:
    #         return
    #     if this._ignore_hidden:
    #         is_hidden = await loop.run_in_executor(executor, utils.is_hidden, path)
    #         if is_hidden:
    #             return
        
    #     rel_path = str(path.relative_to(this._src_path.parent)).encode('utf-8')
    #     path_len = len(rel_path)
        
    #     stat = await loop.run_in_executor(executor, path.stat)
        
    #     if path.is_file():
    #         entry_type = ENTRY_TYPE_FILE
    #         size = stat.st_size
    #         time = int(stat.st_mtime)
            
    #         file_bytes = await loop.run_in_executor(executor, path.read_bytes)
    #         hash_value = hashlib.sha256(file_bytes).digest()
            
    #         header = struct.pack(ENTRY_HEADER_FORMAT, entry_type, path_len)
    #         async with this._write_lock:
    #             f.write(header)
    #             f.write(rel_path)
    #             f.write(struct.pack(ENTRY_FILE_FORMAT, size, time, hash_value))
                
    #     elif path.is_symlink():
    #         if this._ignore_symlinks:
    #             return
    #         entry_type = ENTRY_TYPE_SYMLINK
    #         header = struct.pack(ENTRY_HEADER_FORMAT, entry_type, path_len)
    #         async with this._write_lock:
    #             f.write(header)
    #             f.write(rel_path)
    #             f.write(struct.pack(ENTRY_FILE_FORMAT, 0, 0, b'\x00' * 32))
                
    #     elif path.is_dir():
    #         entry_type = ENTRY_TYPE_DIR
    #         header = struct.pack(ENTRY_HEADER_FORMAT, entry_type, path_len)
    #         time = int(stat.st_mtime)
    #         async with this._write_lock:
    #             f.write(header)
    #             f.write(rel_path)
    #             f.write(struct.pack(ENTRY_FILE_FORMAT, 0, time, b'\x00' * 32))
            
    #         entries = await loop.run_in_executor(executor, list, path.iterdir())
    #         await asyncio.gather(*[
    #             this._write_entry(f, entry, depth+1, executor)
    #             for entry in entries
    #         ])

class SnapshotReader:
    @staticmethod
    def _get_size_string(size, human = False):
        return str(size) if not human else utils.file_size_to_string_human(size)
    
    @staticmethod
    def _get_time_string(time, human = False):
        return str(time) if not human else utils.time_to_string_human(time) 
    
    @staticmethod
    def _get_entry_type_string(entry):
        return {ENTRY_TYPE_FILE: 'FILE', ENTRY_TYPE_DIR: 'DIR', ENTRY_TYPE_SYMLINK: 'SYMLINK'}.get(entry['type'], 'UNKNOWN')
    
    @staticmethod
    def _get_entry_string(entry, human=False):
        parts = [
            f"{SnapshotReader._get_entry_type_string(entry)}: {entry['path']}"
        ]
        if entry['type'] not in (ENTRY_TYPE_DIR, ENTRY_TYPE_SYMLINK):
            parts.append(f"hash=\"{entry['hash'].hex()}\"")
            parts.append(f"size=\"{SnapshotReader._get_size_string(entry['size'], human)}\"")
        parts.append(f"time=\"{SnapshotReader._get_time_string(entry['time'], human)}\"")
        return ' '.join(parts)

    @staticmethod
    def _get_diff_entry_string(entry1, entry2, human=False):
        parts = [
            f"{SnapshotReader._get_entry_type_string(entry1)}: {entry1['path']}"
        ]
        if entry1['type'] not in (ENTRY_TYPE_DIR, ENTRY_TYPE_SYMLINK):
            parts.append(
                f"hash=\"{entry1['hash'].hex()} -> {entry2['hash'].hex()}\""
            )
            parts.append(
                f"size=\"{SnapshotReader._get_size_string(entry1['size'], human)} "
                f"-> {SnapshotReader._get_size_string(entry2['size'], human)}\""
            )
        parts.append(
            f"time=\"{SnapshotReader._get_time_string(entry1['time'], human)} "
            f"-> {SnapshotReader._get_time_string(entry2['time'], human)}\""
        )
        return ' '.join(parts)
    
    
    def __init__(this, snap_file):
        this._snap_file = Path(snap_file)

    def read_snapshot(this):
        entries = []
        with this._snap_file.open('rb') as f:
            magic = f.read(len(SNAPSHOT_FILE_HEADER))
            if magic != SNAPSHOT_FILE_HEADER:
                raise ValueError('Invalid snapshot file')
            while True:
                header = f.read(struct.calcsize(ENTRY_HEADER_FORMAT))
                if not header:
                    break
                entry_type, path_len = struct.unpack(ENTRY_HEADER_FORMAT, header)
                rel_path = f.read(path_len).decode('utf-8')
                size, time, hash_value = struct.unpack(ENTRY_FILE_FORMAT, f.read(struct.calcsize(ENTRY_FILE_FORMAT)))
                entries.append({'type': entry_type, 'path': rel_path, 'size': size, 'time': time, 'hash': hash_value})
        return entries

    def print_snapshot(this, easy = False, human = False):
        entries = this.read_snapshot()
        
        entry_strings = []
        _files_count = 0
        _dirs_count = 0
        _unknown_count = 0
        
        for e in entries:
            if e['type'] == ENTRY_TYPE_FILE:
                _files_count += 1
            elif e['type'] == ENTRY_TYPE_DIR:
                _dirs_count += 1
            else:
                _unknown_count += 1
            
            if not easy:
                entry_strings.append(SnapshotReader._get_entry_string(e, human))
            
        print(f"Snapshot Summary:")
        print(f"Contains: {_files_count:,} Files, {_dirs_count:,} Directories, {_unknown_count:,} Others")
        if easy:
            return
        
        print()
        for entry_string in entry_strings:
            print(entry_string)
    
    
    @staticmethod
    def compare_snapshots(snap_file_a, snap_file_b):
        """
        Compare two snapshot files and print added, removed, and modified entries.
        """
        reader_a = SnapshotReader(snap_file_a)
        reader_b = SnapshotReader(snap_file_b)
        entries_a = reader_a.read_snapshot()
        entries_b = reader_b.read_snapshot()

        def entry_key(e):
            return (e['type'], e['path'])

        dict_a = {entry_key(e): e for e in entries_a}
        dict_b = {entry_key(e): e for e in entries_b}

        added = [e for k, e in dict_b.items() if k not in dict_a]
        removed = [e for k, e in dict_a.items() if k not in dict_b]
        modified = []
        for k in dict_a.keys() & dict_b.keys():
            ea, eb = dict_a[k], dict_b[k]
            if ea['hash'] != eb['hash'] or ea['size'] != eb['size'] or ea['time'] != eb['time']:
                modified.append((ea, eb))
        
        return added, removed, modified
        
    @staticmethod
    def print_snapshot_comparisons(added = None, removed = None, modified = None, human = False):
        if added:
            print('--- Added ---')
            for e in added:
                print(f"+ {SnapshotReader._get_entry_string(e, human)}")
            print()
        if removed:
            print('--- Removed ---')
            for e in removed:
                print(f"- {SnapshotReader._get_entry_string(e, human)}")
            print()
        if modified:
            print('--- Modified ---')
            for ea, eb in modified:
                print(f"* {SnapshotReader._get_diff_entry_string(ea, eb, human)}")
            print()
