import os
import shutil
import time
import traceback
from threading import Thread

from WPBackupTool.Utils import Helper
from WPBackupTool.Engine.DBBackup import DBBackup
from WPBackupTool.Engine.FTPBackup import FTPBackup
from WPBackupTool.Utils.Logger import Logger
from WPBackupTool.Engine.SFTPBackup import SFTPBackup
from WPBackupTool.Utils.ZipCompression import ZipCompression


class WPBackupTool():
    def __init__(self, configs, skip_db=False, skip_ftp=False, multithreading=False):
        self.configs = configs
        self.multithreading = multithreading
        self.skip_db = skip_db
        self.skip_ftp = skip_ftp

        Logger.log("Skipping db backup: "+str(self.skip_db))
        Logger.log("Skipping ftp backup: "+str(self.skip_ftp))

    def do_website_backups(self):
        threads = []

        for website_config in self.configs:
            if(self.multithreading):
                thread = Thread(target=self.do_website_backup, args=(website_config,))

                threads.append(thread)

                thread.start()
            else:
                self.do_website_backup(website_config)

        #Wait for all threads to finish
        for thread in threads:
            thread.join()


    def do_website_backup(self, website_config):
        backup_path = website_config.backup_path
        backup_name = website_config.backup_name

        ftp_config = None
        if website_config.ftp_config is not None:
            ftp_config = website_config.ftp_config

        db_configs = None
        if website_config.db_configs is not None:
            db_configs = website_config.db_configs

        if not os.path.isdir(backup_path):
            Helper.mkdir_p(backup_path)

        if not os.path.isdir(os.path.join(backup_path, backup_name)):
            Helper.mkdir_p(os.path.join(backup_path, backup_name))

        db_success = False
        ftp_success = False

        backupChildDir = backup_name + "_" + time.strftime('%Y-%m-%d')
        total_backup_path = os.path.join(backup_path, backup_name, backupChildDir)

        ftp_backup_path = os.path.join(total_backup_path, backup_name)
        db_backup_path = os.path.join(total_backup_path, "db")

        try:
            #Create backup directories
            Helper.mkdir_p(ftp_backup_path)
            Helper.mkdir_p(db_backup_path)

            Logger.log("saving sql-files to " + db_backup_path)
            db_fails = self.do_db_backups(db_configs, db_backup_path, backup_name)

            db_success = db_fails==""

            ftp_success_log, ftp_errors, ftp_success = self.do_ftp_backup(ftp_config, backup_name, ftp_backup_path)

            backup_path_done = os.path.join(backup_path, backup_name, backupChildDir + "_done")

            Logger.log(total_backup_path+" ==> "+backup_path_done)

            shutil.move(total_backup_path, backup_path_done)

            log_item = backup_name + ":\n" + db_fails + ftp_success_log + ftp_errors
        except Exception as e:
            traceback.print_exc()
            log_item = backup_name + ":\n" + str(e)
            backup_path_done = None

        # log_datei erstellen
        log_path = os.path.join(backup_path, backup_name, backup_name + "_log_" + time.strftime('%Y-%m-%d') + ".txt")
        open(log_path, 'a').close()
        log_file = open(log_path, "w")
        log_file.write(log_item)
        log_file.close()

        if backup_path_done is not None:
            Logger.log("backup path done: " + backup_path_done)

            shutil.move(log_path, backup_path_done)

            if db_success and ftp_success:
                ZipCompression(backup_path_done).compress(delete_source=True)
            else:
                backup_path_error = os.path.join(backup_path, backup_name, backupChildDir + "_error")
                shutil.move(backup_path_done, backup_path_error)

    def do_db_backups(self, db_configs, backup_path, backup_name):
        db_fails = ""
        if not self.skip_db and db_configs is not None:
            for db in db_configs:
                db_backup_name = backup_name

                db_backup = DBBackup(db.host, db.user, db.name, db.password, backup_path, db_backup_name)
                db_backup_success = db_backup.databaseBackup()

                if (db_backup_success is False):
                    if (db_fails == ""):
                        db_fails = "\t-db backup errors:\n"

                    db_fails += "\t\t-" + db_backup_name + "\n"

        return db_fails

    def do_ftp_backup(self, ftp_config, backup_name, backup_path):
        ftp_success_log = ""
        ftp_errors = ""
        error_filenames = []

        if not self.skip_ftp and ftp_config is not None:
            ignore_dirs = None
            if ftp_config.ignore_dirs is not None:
                ignore_dirs = ftp_config.ignore_dirs

            Logger.log("saving ftp-files to " + backup_path)

            if ftp_config.use_sftp:
                print("Using SFTP...")
                ftp_backup = SFTPBackup(backup_name)
            else:
                print("Using FTP...")
                ftp_backup = FTPBackup(backup_name)

            successful, errors, error_filenames = ftp_backup.startBackup(ftp_config.host, ftp_config.username,
                                                                        ftp_config.password, ftp_config.server_dir,
                                                                        backup_path, ignore_dirs, interval=0.01)

            if (successful + errors) > 0:
                success_rate = (float(successful) / (successful + errors)) * 100
            else:
                success_rate = 0

            ftp_success_log = "\t-ftp backup result:\n\t\t-" + str(successful) + \
                              " successful transmissions\n\t\t-" + str(errors) + \
                              " errors\n\t\t-success_rate: " + str(success_rate) + "%"

            ftp_errors = "\t-ftp errors:"
            for name in error_filenames:
                ftp_errors += "\n\t\t" + name

            Logger.log("ftp-backup for " + backup_name + " complete. " + str(successful) + \
                  " successful transmissions, " + str(errors) + " errors")

        return ftp_success_log, ftp_errors, len(error_filenames)==0
