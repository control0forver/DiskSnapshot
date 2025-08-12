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
    DiskSnapshot.add_commands(parser, required=False)
    
    return parser.parse_args()

def main():
    args = resolve_args()
    DiskSnapshot.gui(args)
        
    return
if __name__ == "__main__":
    main()
