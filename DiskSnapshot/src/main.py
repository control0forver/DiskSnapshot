#!/usr/bin/python3 -u
import logging
import argparse
import config
import DiskSnapshot

logging.basicConfig(format='%(asctime)s %(levelname)-8s [%(filename)s:%(lineno)d] %(message)s', datefmt='%Y-%m-%d:%H:%M:%S', level=logging.NOTSET)

def resolve_args():
    parser = argparse.ArgumentParser(
        description = config.GetAppDescription(),
        epilog = config.GetAppLicenseDescription()
    )
    subparsers = DiskSnapshot.add_commands(parser)
    
    # Gui
    gui_parser = subparsers.add_parser('gui',
                                      help=f'Launch {config.APP_NAME} graphical')
    gui_parser
    
    return parser.parse_args()

def main():
    args = resolve_args()
    
    if args.command == 'gui':
        DiskSnapshot.gui(args)
    else:  # 'generate', 'view', 'compare', etc.
        DiskSnapshot.cli(args)
        
    return
if __name__ == "__main__":
    main()
