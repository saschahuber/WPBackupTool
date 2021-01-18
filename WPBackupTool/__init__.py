import os
import shutil
import time
import traceback
from threading import Thread

from WPBackupTool.Utils import Helper
from WPBackupTool.Utils.DBBackup import DBBackup
from WPBackupTool.Utils.FTPBackup import FTPBackup
from WPBackupTool.Utils.Logger import Logger
from WPBackupTool.Utils.SFTPBackup import SFTPBackup
from WPBackupTool.Utils.ZipCompression import ZipCompression


class WPBackupTool():
    def __init__(self, config, skipDb=False, skipFtp=False, multithreading=False):
        self.config = config
        self.skipDb = skipDb
        self.skipFtp = skipFtp
        self.multithreading = multithreading

        Logger.log("Skipping db backup: "+str(self.skipDb))
        Logger.log("Skipping ftp backup: "+str(self.skipFtp))

    def doWebsiteBackups(self):
        threads = []

        for website_config in self.config:
            if(self.multithreading):
                thread = Thread(target=self.doWebsiteBackup, args=(website_config,))

                threads.append(thread)

                thread.start()
            else:
                self.doWebsiteBackup(website_config)

        #Wait for all threads to finish
        for thread in threads:
            thread.join()


    def doWebsiteBackup(self, website_config):
        use_sftp = False
        backup_path = website_config['backup_path']
        backup_name = website_config['backup_name']

        ftp_data = None
        if 'ftp_data' in website_config and website_config['ftp_data'] is not None:
                ftp_data = website_config['ftp_data']
                if 'use_sftp' in ftp_data and ftp_data['use_sftp']:
                    use_sftp = ftp_data['use_sftp']

        db_data = None
        if 'db_data' in website_config and website_config['db_data'] is not None:
            db_data = website_config['db_data']

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
            db_fails = self.doDbBackups(db_data, db_backup_path, backup_name)

            db_success = db_fails==""

            ftp_success_log, ftp_errors, ftp_success = self.doFtpBackup(ftp_data, use_sftp, backup_name, ftp_backup_path)

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

    def doDbBackups(self, db_data, backup_path, backup_name):
        db_fails = ""
        if not self.skipDb and db_data is not None:
            for db in db_data:
                if 'backup_name' in db and db['backup_name'] is not None:
                    db_backup_name = db['backup_name']
                else:
                    db_backup_name = backup_name

                dbBackup = DBBackup(db['host'], db['user'],
                                    db['db_name'], db['password'], backup_path, db_backup_name)
                db_backup_success = dbBackup.databaseBackup()

                if (db_backup_success is False):
                    if (db_fails == ""):
                        db_fails = "\t-db backup errors:\n"

                    db_fails += "\t\t-" + db_backup_name + "\n"

        return db_fails

    def doFtpBackup(self, ftp_data, use_sftp, backup_name, backup_path):
        ftp_success_log = ""
        ftp_errors = ""
        error_filenames = []

        if (not self.skipFtp and ftp_data is not None):
            ignore_dirs = None
            if ('ignore_dirs' in ftp_data):
                ignore_dirs = ftp_data['ignore_dirs']

            Logger.log("saving ftp-files to " + backup_path)

            if (use_sftp):
                print("Using SFTP...")
                ftpBackup = SFTPBackup(backup_name)
            else:
                print("Using FTP...")
                ftpBackup = FTPBackup(backup_name)

            successful, errors, error_filenames = ftpBackup.startBackup(ftp_data['host'], ftp_data['user'],
                                                                         ftp_data['password'],
                                                                         ftp_data['server_dir'],
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
