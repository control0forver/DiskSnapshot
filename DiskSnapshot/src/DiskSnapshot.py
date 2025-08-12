import os
import logging
import shlex
import argparse
import config
from pathlib import Path
from Snapshot import SnapshotWriter, SnapshotReader

def _on_snap_not_found(file):
    print(f'Snapshot file not found: {shlex.quote(str(file))}')
    exit(-1)

# Generate snapshot
def generate(src_path, ignore_hidden = False, ignore_symlinks = False, max_rec_depth = -1, output_name = None, output_dir = None, show = False, human = False):
    # Compute output file path
    src_path = Path(src_path).resolve()
    if not output_name or output_name is None:
        __tmp = 1
        while os.path.exists(output_name := f"{src_path.name}{f' ({__tmp})' if __tmp > 1 else ''}.snap"): __tmp += 1
    if not  output_dir: output_dir  = Path.cwd()
    output_dir.mkdir(parents=True, exist_ok=True)
    dest_path = output_dir / output_name
        
    logging.info(f'Generate: Source = "{shlex.quote(str(src_path))}"')
    logging.info(f'Generate: Snapshot = "{shlex.quote(str(dest_path))}"')

    if not src_path.exists():
        print(f'Source path does not exist: {shlex.quote(str(src_path.absolute()))}')
        exit(-1)
        
    print(f'Taking snapshot from source: {shlex.quote(str(src_path.absolute()))}')
    print()
    
    writer = SnapshotWriter(src_path, dest_path, ignore_hidden, ignore_symlinks, max_rec_depth)
    writer.write_snapshot()
    logging.info(f"Generate: Snapshot written to {shlex.quote(str(dest_path))}")
    
    print(f'Snapshot Saved in: {shlex.quote(str(dest_path.absolute()))}')
    print()
    
    if show:
        reader = SnapshotReader(dest_path)
        reader.print_snapshot(False, human)
        
# View snapshot
def view(snapshot_file, human = False):
    snapshot_file = Path(snapshot_file).resolve()
    
    logging.info(f'View: Snapshot = "{shlex.quote(str(snapshot_file))}"')
    
    if not snapshot_file.exists():
        _on_snap_not_found(snapshot_file.absolute())

    print(f'Viewing Snapshot: {shlex.quote(str(snapshot_file.absolute()))}')
    
    reader = SnapshotReader(snapshot_file)
    reader.print_snapshot(False, human)

# Compare snapshots
def compare(snap_a, snap_b, human = False):
    snap_a = Path(snap_a).resolve()
    snap_b = Path(snap_b).resolve()
    
    if not snap_a.exists():
        _on_snap_not_found(snap_a.absolute())
    if not snap_b.exists():
        _on_snap_not_found(snap_b.absolute())
        
    
    print(f'Comparing Snapshots:\n  1. {shlex.quote(str(snap_a.absolute()))}\n  2. {shlex.quote(str(snap_b.absolute()))}')
    print()
        
    added, removed, modified = SnapshotReader.compare_snapshots(snap_a, snap_b)
    
    if not added and not removed and not modified:
        print('Compare: No differences found!')
        return
    
    print(f'[Added: {len(added)}, Removed: {len(removed)}, Modified: {len(modified)}]')
    SnapshotReader.print_snapshot_comparisons(added, removed, modified, human)


def add_commands(parser: argparse.ArgumentParser, dest='command', required=True, title='commands', description='valid commands'):
    subparsers = parser.add_subparsers(dest = dest, required = required, title = title, description = description, metavar='{generate, view, compare}')
    
    # Generate command
    gen_parser = subparsers.add_parser('generate', aliases=['g', 'w'], 
                                      help='Generate snapshot')
    gen_parser.add_argument('src_path', help='Source directory path')
    gen_parser.add_argument('--output', help='Snapshot output file name (optional)')
    gen_parser.add_argument('--output-dir', help='Snapshot output directory (optional)')
    gen_parser.add_argument('--show', action='store_true', default=True,
                          help='Show snapshot content after generation (enabled by default)')
    gen_parser.add_argument('--no-show', action='store_false', dest='show',
                          help='Do not show snapshot content after generation')
    gen_parser.add_argument('--ignore-hidden', action='store_true',
                          help='Ignore hidden files and directories')
    gen_parser.add_argument('--ignore-symlinks', action='store_true',
                          help='Ignore symlinks')
    gen_parser.add_argument('--max-recursion-depth', type=int, default=-1,
                          help='Maximum recursion depth (default: unlimited)')
    gen_parser.add_argument('-H', '--human', action='store_true', default=False,
                        help='Use human friendly units for output')
    
    # View command
    view_parser = subparsers.add_parser('view', aliases=['v', 'r'],
                                      help='View snapshot file content')
    view_parser.add_argument('snapshot_file', metavar='SNAPSHOT_FILE',
                           help='Snapshot file to view')
    view_parser.add_argument('-H', '--human', action='store_true', default=False,
                        help='Use human friendly units for output')
    
    # Compare command
    compare_parser = subparsers.add_parser('compare', aliases=['c'],
                                         help='Compare two snapshot files')
    compare_parser.add_argument('snap_a', metavar='SNAP_A',
                              help='First snapshot file to compare')
    compare_parser.add_argument('snap_b', metavar='SNAP_B',
                              help='Second snapshot file to compare')
    compare_parser.add_argument('-H', '--human', action='store_true', default=False,
                        help='Use human friendly units for output')
    
    
    parser.add_argument('-H', '--human', action='store_true', default=False,
                        help='Use human friendly units for output')
    
    return subparsers

_COMMAND_ARG_GENERATE = ('generate', 'g', 'w')
_COMMAND_ARG_VIEW = ('view', 'v', 'r')
_COMMAND_ARG_COMPARE = ('compare', 'c')

def gui(args = None):
    GUI_LANGUAGES = {
        'en': {
            'menu_preferences': 'Preferences',
            'menu_human_units': 'Human Friendly Units',
            'menu_language': 'Language',
            'menu_view_license': 'License',
            'menu_about': 'About',
            'menu_help': 'Help',
            'tab_viewer': 'Viewer',
            'tab_generator': 'Generator',
            'frame_view_snapshot': 'View Snapshot',
            'label_snapshot_file': 'Snapshot File:',
            'button_browse': 'Browse...',
            'button_view_snapshot': 'View Snapshot',
            'frame_compare_snapshots': 'Compare Snapshots',
            'label_snapshot_file_a': 'Snapshot File A:',
            'label_snapshot_file_b': 'Snapshot File B:',
            'button_compare_snapshots': 'Compare Snapshots',
            'label_source_directory': 'Source Directory:',
            'label_output_file': 'Output File Name:',
            'label_output_directory': 'Output Directory:',
            'check_ignore_hidden': 'Ignore Hidden Files',
            'check_ignore_symlinks': 'Ignore Symlinks',
            'label_max_depth': 'Max Recursion Depth (-1=unlimited):',
            'button_generate_snapshot': 'Generate Snapshot',
            'check_show_snapshot': 'Show Snapshot After Generation',
            'error_select_file': 'Please select a snapshot file.',
            'error_select_both_files': 'Please select both snapshot files.',
            'error_select_directory': 'Please select a source directory.',
            'title_license': f'License of {config.APP_NAME}',
            'title_about': f'About {config.APP_NAME}'
        },
        'zh': {
            'menu_preferences': '首选项',
            'menu_human_units': '使用人性化单位',
            'menu_language': '语言',
            'menu_view_license': '许可证',
            'menu_about': '关于',
            'menu_help': '帮助',
            'tab_viewer': '查看器',
            'tab_generator': '生成器',
            'frame_view_snapshot': '查看快照',
            'label_snapshot_file': '快照文件:',
            'button_browse': '浏览...',
            'button_view_snapshot': '查看快照',
            'frame_compare_snapshots': '比较快照',
            'label_snapshot_file_a': '快照文件 A:',
            'label_snapshot_file_b': '快照文件 B:',
            'button_compare_snapshots': '比较快照',
            'label_source_directory': '源目录:',
            'label_output_file': '输出文件名:',
            'label_output_directory': '输出目录:',
            'check_ignore_hidden': '忽略隐藏文件',
            'check_ignore_symlinks': '忽略符号链接',
            'label_max_depth': '最大递归深度 (-1=无限制):',
            'button_generate_snapshot': '生成快照',
            'check_show_snapshot': '生成后显示快照',
            'error_select_file': '请选择一个快照文件。',
            'error_select_both_files': '请选择两个快照文件。',
            'error_select_directory': '请选择一个源目录。',
            'title_license': f'{config.APP_NAME} 的许可证',
            'title_about': f'关于 {config.APP_NAME}'
        }
    }
    current_lang = 'en'
        
    def update_ui_texts():
        lang = GUI_LANGUAGES[current_lang]
        
        # Rebuild the menus with the new language
        menubar.delete(0, tk.END)  # Clear all menus
        
        # [Menu] Preferences
        preferences_menu = tk.Menu(menubar, tearoff=0)
        preferences_menu.add_checkbutton(label=lang['menu_human_units'], variable=human_units_var)
        preferences_menu.add_separator()
        
        language_menu = tk.Menu(preferences_menu, tearoff=0)
        language_menu.add_command(label='English', command=lambda: change_language('en'))
        language_menu.add_command(label='中文（简体）', command=lambda: change_language('zh'))
        preferences_menu.add_cascade(label=lang['menu_language'], menu=language_menu)
        
        menubar.add_cascade(label=lang['menu_preferences'], menu=preferences_menu)

        # [Menu] Help
        help_menu = tk.Menu(menubar, tearoff=0)
        help_menu.add_command(label=lang['menu_view_license'], command=show_license)
        help_menu.add_separator()
        help_menu.add_command(label=lang['menu_about'], command=show_about)
        menubar.add_cascade(label=lang['menu_help'], menu=help_menu)

        mainWnd.config(menu=menubar)
        
        # Update tab names
        tabControl.tab(0, text=lang['tab_viewer'])
        tabControl.tab(1, text=lang['tab_generator'])
        
        # Update viewer tab
        view_frame.config(text=lang['frame_view_snapshot'])
        for child in view_frame.winfo_children():
            if isinstance(child, tk.Label):
                child.config(text=lang['label_snapshot_file'])
                break
        browse_view_btn.config(text=lang['button_browse'])
        view_btn.config(text=lang['button_view_snapshot'])
        
        # Update comparison frame
        cmp_frame.config(text=lang['frame_compare_snapshots'])
        labels = [child for child in cmp_frame.winfo_children() if isinstance(child, tk.Label)]
        if len(labels) >= 2:
            labels[0].config(text=lang['label_snapshot_file_a'])
            labels[1].config(text=lang['label_snapshot_file_b'])
        browse_cmp_a_btn.config(text=lang['button_browse'])
        browse_cmp_b_btn.config(text=lang['button_browse'])
        cmp_btn.config(text=lang['button_compare_snapshots'])
        
        # Update generator tab
        gen_labels = [child for child in pageGenerate.winfo_children() if isinstance(child, tk.Label)]
        if len(gen_labels) >= 4:
            gen_labels[0].config(text=lang['label_source_directory'])
            gen_labels[1].config(text=lang['label_output_file'])
            gen_labels[2].config(text=lang['label_output_directory'])
            gen_labels[3].config(text=lang['label_max_depth'])
        
        browse_gen_btn.config(text=lang['button_browse'])
        browse_gen_output_btn.config(text=lang['button_browse'])
        
        checkbuttons = [child for child in pageGenerate.winfo_children() if isinstance(child, ttk.Checkbutton)]
        if len(checkbuttons) >= 3:
            checkbuttons[0].config(text=lang['check_ignore_hidden'])
            checkbuttons[1].config(text=lang['check_ignore_symlinks'])
            checkbuttons[2].config(text=lang['check_show_snapshot'])
        
        gen_btn.config(text=lang['button_generate_snapshot'])
    
    def change_language(lang):
        nonlocal current_lang
        current_lang = lang
        update_ui_texts()
    
    import tkinter as tk
    from tkinter import ttk, filedialog, messagebox

    mainWnd = tk.Tk()
    mainWnd.title(config.GetAppTitle())
    mainWnd.minsize(630, 520)
    mainWnd.resizable(True, True)

    # Config Vars
    human_units_var = tk.BooleanVar(value=True)
    
    # Menu
    menubar = tk.Menu(mainWnd)
    
    # [Menu] Preferences
    preferences_menu = tk.Menu(menubar, tearoff=0)
    preferences_menu.add_checkbutton(label='Human Friendly Units', variable=human_units_var)
    preferences_menu.add_separator()
    
    language_menu = tk.Menu(preferences_menu, tearoff=0)
    language_menu.add_command(label='English', command=lambda: change_language('en'))
    language_menu.add_command(label='中文（简体）', command=lambda: change_language('zh'))
    preferences_menu.add_cascade(label='Language', menu=language_menu)
    
    menubar.add_cascade(label='Preferences', menu=preferences_menu)

    # [Menu] Help
    help_menu = tk.Menu(menubar, tearoff=0)
    def show_license():
        messagebox.showinfo(
            GUI_LANGUAGES[current_lang]['title_license'].format(app_name=config.APP_NAME), 
            config.GetAppLicenseDescription()
        )
    def show_about():
        messagebox.showinfo(
            GUI_LANGUAGES[current_lang]['title_about'].format(app_name=config.APP_NAME), 
            config.GetAppDescription()
        )
    help_menu.add_command(label='License', command=show_license)
    help_menu.add_separator()
    help_menu.add_command(label='About', command=show_about)
    menubar.add_cascade(label='Help', menu=help_menu)

    mainWnd.config(menu=menubar)

    # TabControl
    tabControl = ttk.Notebook(mainWnd)
    style = ttk.Style()
    style.configure('TNotebook.Tab', padding=[10, 5], expand=1)

    # Viewer Tab
    pageViewer = ttk.Frame(tabControl)
    tabControl.add(pageViewer, text='Viewer')

    # --- Snapshot View ---
    view_frame = ttk.LabelFrame(pageViewer, text='View Snapshot')
    view_frame.pack(fill='both', expand=True, padx=8, pady=4)
    view_file_var = tk.StringVar()
    tk.Label(view_frame, text='Snapshot File:').pack(anchor='w', padx=8, pady=4)
    view_file_entry_frame = ttk.Frame(view_frame)
    view_file_entry_frame.pack(fill='x', padx=8)
    view_entry = ttk.Entry(view_file_entry_frame, textvariable=view_file_var)
    view_entry.grid(row=0, column=0, sticky='ew')
    def browse_view_file():
        f = filedialog.askopenfilename(title='Select Snapshot File', filetypes=[('Snapshot Files', '*.snap'), ('All Files', '*.*')])
        if f:
            view_file_var.set(f)
    browse_view_btn = ttk.Button(view_file_entry_frame, text='Browse...', command=browse_view_file)
    browse_view_btn.grid(row=0, column=1, padx=(4,0))
    view_file_entry_frame.columnconfigure(0, weight=1)
    view_btn_frame = ttk.Frame(view_frame)
    view_btn_frame.pack(fill='x', padx=8, pady=(8,0))
    def do_view():
        view_output.delete('1.0', tk.END)
        file = view_file_var.get()
        if not file:
            messagebox.showerror('Error', GUI_LANGUAGES[current_lang]['error_select_file'])
            return
        try:
            import io, sys
            buf = io.StringIO()
            sys_stdout = sys.stdout
            sys.stdout = buf
            view(file, human_units_var.get())
            sys.stdout = sys_stdout
            view_output.insert(tk.END, buf.getvalue())
        except Exception as e:
            sys.stdout = sys_stdout
            messagebox.showerror('Error', str(e))
    view_btn = ttk.Button(view_btn_frame, text='View Snapshot', command=do_view)
    view_btn.pack(fill='x')
    view_output = tk.Text(view_frame, height=10)
    view_output.pack(fill='both', expand=True, padx=8, pady=4)

    # --- Snapshot Comparison ---
    cmp_frame = ttk.LabelFrame(pageViewer, text='Compare Snapshots')
    cmp_frame.pack(fill='both', expand=True, padx=8, pady=4)
    cmp_a_var = tk.StringVar()
    cmp_b_var = tk.StringVar()
    tk.Label(cmp_frame, text='Snapshot File A:').pack(anchor='w', padx=8, pady=4)
    cmp_a_entry_frame = ttk.Frame(cmp_frame)
    cmp_a_entry_frame.pack(fill='x', padx=8)
    cmp_a_entry = ttk.Entry(cmp_a_entry_frame, textvariable=cmp_a_var)
    cmp_a_entry.grid(row=0, column=0, sticky='ew')
    def browse_cmp_a():
        f = filedialog.askopenfilename(title='Select Snapshot File A', filetypes=[('Snapshot Files', '*.snap'), ('All Files', '*.*')])
        if f:
            cmp_a_var.set(f)
    browse_cmp_a_btn = ttk.Button(cmp_a_entry_frame, text='Browse...', command=browse_cmp_a)
    browse_cmp_a_btn.grid(row=0, column=1, padx=(4,0))
    cmp_a_entry_frame.columnconfigure(0, weight=1)
    tk.Label(cmp_frame, text='Snapshot File B:').pack(anchor='w', padx=8, pady=4)
    cmp_b_entry_frame = ttk.Frame(cmp_frame)
    cmp_b_entry_frame.pack(fill='x', padx=8)
    cmp_b_entry = ttk.Entry(cmp_b_entry_frame, textvariable=cmp_b_var)
    cmp_b_entry.grid(row=0, column=0, sticky='ew')
    def browse_cmp_b():
        f = filedialog.askopenfilename(title='Select Snapshot File B', filetypes=[('Snapshot Files', '*.snap'), ('All Files', '*.*')])
        if f:
            cmp_b_var.set(f)
    browse_cmp_b_btn = ttk.Button(cmp_b_entry_frame, text='Browse...', command=browse_cmp_b)
    browse_cmp_b_btn.grid(row=0, column=1, padx=(4,0))
    cmp_b_entry_frame.columnconfigure(0, weight=1)
    cmp_btn_frame = ttk.Frame(cmp_frame)
    cmp_btn_frame.pack(fill='x', padx=8, pady=(8,0))
    def do_compare():
        cmp_output.delete('1.0', tk.END)
        a = cmp_a_var.get()
        b = cmp_b_var.get()
        if not a or not b:
            messagebox.showerror('Error', GUI_LANGUAGES[current_lang]['error_select_both_files'])
            return
        try:
            import io, sys
            buf = io.StringIO()
            sys_stdout = sys.stdout
            sys.stdout = buf
            compare(a, b, human_units_var.get())
            sys.stdout = sys_stdout
            cmp_output.insert(tk.END, buf.getvalue())
        except Exception as e:
            sys.stdout = sys_stdout
            messagebox.showerror('Error', str(e))
    cmp_btn = ttk.Button(cmp_btn_frame, text='Compare Snapshots', command=do_compare)
    cmp_btn.pack(fill='x')
    cmp_output = tk.Text(cmp_frame, height=10)
    cmp_output.pack(fill='both', expand=True, padx=8, pady=4)

    # Generator Tab
    pageGenerate = ttk.Frame(tabControl)
    tabControl.add(pageGenerate, text='Generator')
    gen_src_var = tk.StringVar(value='.')
    tk.Label(pageGenerate, text='Source Directory:').pack(anchor='w', padx=8, pady=4)
    gen_src_frame = ttk.Frame(pageGenerate)
    gen_src_frame.pack(fill='x', padx=8)
    gen_src_entry = ttk.Entry(gen_src_frame, textvariable=gen_src_var)
    gen_src_entry.grid(row=0, column=0, sticky='ew')
    def browse_gen_dir():
        d = filedialog.askdirectory(title='Select Source Directory')
        if d:
            gen_src_var.set(d)
    browse_gen_btn = ttk.Button(gen_src_frame, text='Browse...', command=browse_gen_dir)
    browse_gen_btn.grid(row=0, column=1, padx=(4,0))
    gen_src_frame.columnconfigure(0, weight=1)
    gen_output_var = tk.StringVar()
    tk.Label(pageGenerate, text='Output File Name:').pack(anchor='w', padx=8, pady=4)
    gen_output_frame = ttk.Frame(pageGenerate)
    gen_output_frame.pack(fill='x', padx=8)
    gen_output_entry = ttk.Entry(gen_output_frame, textvariable=gen_output_var)
    gen_output_entry.grid(row=0, column=0, sticky='ew')
    gen_output_frame.columnconfigure(0, weight=1)
    gen_output_dir_var = tk.StringVar()
    tk.Label(pageGenerate, text='Output Directory:').pack(anchor='w', padx=8, pady=4)
    gen_output_dir_frame = ttk.Frame(pageGenerate)
    gen_output_dir_frame.pack(fill='x', padx=8)
    gen_output_dir_entry = ttk.Entry(gen_output_dir_frame, textvariable=gen_output_dir_var)
    gen_output_dir_entry.grid(row=0, column=0, sticky='ew')
    def browse_gen_output_dir():
        d = filedialog.askdirectory(title='Select Output Directory')
        if d:
            gen_output_dir_var.set(d)
    browse_gen_output_btn = ttk.Button(gen_output_dir_frame, text='Browse...', command=browse_gen_output_dir)
    browse_gen_output_btn.grid(row=0, column=1, padx=(4,0))
    gen_output_dir_frame.columnconfigure(0, weight=1)
    gen_ignore_hidden_var = tk.BooleanVar()
    ttk.Checkbutton(pageGenerate, text='Ignore Hidden Files', variable=gen_ignore_hidden_var).pack(anchor='w', padx=8)
    gen_ignore_symlinks_var = tk.BooleanVar()
    ttk.Checkbutton(pageGenerate, text='Ignore Symlinks', variable=gen_ignore_symlinks_var).pack(anchor='w', padx=8)
    gen_max_depth_var = tk.StringVar(value='-1')
    tk.Label(pageGenerate, text='Max Recursion Depth (-1=unlimited):').pack(anchor='w', padx=8, pady=4)
    ttk.Entry(pageGenerate, textvariable=gen_max_depth_var, width=10).pack(anchor='w', padx=8)
    gen_show_var = tk.BooleanVar(value=True)
    gen_btn_frame = ttk.Frame(pageGenerate)
    gen_btn_frame.pack(fill='x', padx=8, pady=(8,0))
    def do_generate():
        gen_output.delete('1.0', tk.END)
        src = gen_src_var.get()
        if not src:
            messagebox.showerror('Error', GUI_LANGUAGES[current_lang]['error_select_directory'])
            return
        try:
            import io, sys
            buf = io.StringIO()
            sys_stdout = sys.stdout
            sys.stdout = buf
            generate(
                src,
                gen_ignore_hidden_var.get(),
                gen_ignore_symlinks_var.get(),
                int(gen_max_depth_var.get()),
                gen_output_var.get() or None,
                gen_output_dir_var.get() or None,
                gen_show_var.get(),
                human_units_var.get()
            )
            sys.stdout = sys_stdout
            gen_output.insert(tk.END, buf.getvalue())
        except Exception as e:
            sys.stdout = sys_stdout
            messagebox.showerror('Error', str(e))
    gen_btn = ttk.Button(gen_btn_frame, text='Generate Snapshot', command=do_generate)
    gen_btn.pack(fill='x')
    ttk.Checkbutton(pageGenerate, text='Show Snapshot After Generation', variable=gen_show_var).pack(anchor='w', padx=8)
    gen_output = tk.Text(pageGenerate, height=15)
    gen_output.pack(fill='both', expand=True, padx=8, pady=4)

    tabControl.pack(expand=True, fill='both')
    
    
    import locale
    try:
        current_lang = locale.getdefaultlocale()[0]
    except ValueError:
        pass
    if current_lang not in GUI_LANGUAGES:
        current_lang = 'en'
        
    #change_language(current_lang)

    # Tab selection based on command
    if args and hasattr(args, 'command'):
        if args.command in _COMMAND_ARG_GENERATE:
            tabControl.select(pageGenerate)
        elif args.command in _COMMAND_ARG_VIEW or args.command in _COMMAND_ARG_COMPARE:
            tabControl.select(pageViewer)

    mainWnd.mainloop()
    return
