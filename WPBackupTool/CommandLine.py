#!/usr/bin/env python
# -*- coding: utf-8 -*-
import argparse
import json

from WPBackupTool import WPBackupTool
from WPBackupTool.Utils import Logger


def main():
    # parse args
    parser = argparse.ArgumentParser(description='Create a backup of your wordpress site!')
    parser.add_argument('--config', required=True, type=str, help='Path to the json-config-file')
    parser.add_argument('--skipDb', action='store_true', help='Skip db-backup?')
    parser.add_argument('--skipFtp', action='store_true', help='Skip ftp-backup?')
    parser.add_argument('--multithreading', action='store_true', help='Do all Backups in parrallel?')
    parser.add_argument('--logging', action='store_true', help='Write logs?')

    args = parser.parse_args()

    config_file = args.config

    Logger.LOGGING = args.logging

    Logger.Logger.log(config_file)

    with open(config_file) as json_file:
        config = json.load(json_file)

    Logger.Logger.log(config)

    wordpressBackup = WPBackupTool(config, args.skipDb, args.skipFtp, args.multithreading)

    wordpressBackup.doWebsiteBackups()


if __name__ == "__main__":
    main()
