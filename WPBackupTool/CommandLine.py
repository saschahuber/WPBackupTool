#!/usr/bin/env python
# -*- coding: utf-8 -*-
import argparse
import json

from WPBackupTool import WPBackupTool
from WPBackupTool.Utils import Logger
from WPBackupTool.Utils.Config import Config


def main():
    # parse args
    parser = argparse.ArgumentParser(description='Create a backup of your wordpress site!')
    parser.add_argument('--config', required=True, type=str, help='Path to the json-config-file')
    parser.add_argument('--skip_db', action='store_true', help='Skip db-backup?')
    parser.add_argument('--skip_ftp', action='store_true', help='Skip ftp-backup?')
    parser.add_argument('--multithreading', action='store_true', help='Do all Backups in parrallel?')
    parser.add_argument('--logging', action='store_true', help='Write logs?')

    args = parser.parse_args()

    config_file = args.config

    configs = Config.from_config_file(config_file)

    Logger.LOGGING = args.logging

    wordpressBackup = WPBackupTool(configs, args.skip_db, args.skip_ftp, args.multithreading)

    wordpressBackup.do_website_backups()


if __name__ == "__main__":
    main()
