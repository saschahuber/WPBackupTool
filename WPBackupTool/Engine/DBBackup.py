#!/usr/bin/python
# -*- coding: utf-8 -*-

###########################################################
#
# This python script is used for mysql database backup
# using mysqldump and tar utility.
#
# Written by : Rahul Kumar
# Website: http://tecadmin.net
# Created date: Dec 03, 2013
# Last modified: Aug 17, 2018
# Tested with : Python 2.7.15 & Python 3.5
# Script Revision: 1.4
#
##########################################################

# Import required python libraries

import os
import pipes
import time

from WPBackupTool.Utils.Logger import Logger


class DBBackup():
    def __init__(self, db_host, db_user, db_name, db_password, path, backup_name):
        self.db_host = db_host
        self.db_user = db_user
        self.db_name = db_name
        self.db_password = db_password
        self.path = path
        self.backup_name = backup_name

    def databaseBackup(self):
        # Getting current DateTime to create the separate backup folder like "20180817-123433".
        DATETIME = time.strftime('%Y-%m-%d')
        TODAYBACKUPPATH = os.path.join(self.path, self.backup_name+"-"+DATETIME)+".sql"

        # Checking if backup folder already exists or not. If not exists will create it.
        try:
            os.stat(self.path)
        except:
            os.makedirs(self.path)

        # Code for checking if you want to take single database backup or assinged multiple backups in db_name.
        if os.path.exists(self.db_user):
            multi = 1
            Logger.log("Starting backup of all dbs listed in file " + self.db_name, "DB_BACKUP_"+self.backup_name)
        else:
            Logger.log("Starting backup of database " + self.db_name, "DB_BACKUP_"+self.backup_name)
            multi = 0

        # Starting actual database backup process.
        if multi:
            in_file = open(self.db_name, "r")
            flength = len(in_file.readlines())
            in_file.close()
            p = 1
            dbfile = open(self.db_name, "r")

            while p <= flength:
                db = dbfile.readline()  # reading database name from file
                db = db[:-1]  # deletes extra line
                dumpcmd = "sudo mysqldump -h " + self.db_host + " -u " + self.db_user + " -p" + self.db_password + " " + db + " > " + pipes.quote(
                    TODAYBACKUPPATH)
                os.system(dumpcmd)
                gzipcmd = "gzip " + pipes.quote(TODAYBACKUPPATH)
                os.system(gzipcmd)
                p = p + 1
            dbfile.close()
        else:
            dumpcmd = "sudo mysqldump -h " + self.db_host + " -u " + self.db_user + " -p" + self.db_password + " " + self.db_name + " > " + pipes.quote(
                TODAYBACKUPPATH)

            Logger.log(dumpcmd, "DB_BACKUP_"+self.backup_name)

            os.system(dumpcmd)
            #gzipcmd = "gzip " + pipes.quote(TODAYBACKUPPATH) + "/" + db + ".sql"
            #os.system(gzipcmd)

        success = False

        #Erfolg des Backups prüfen: datei existiert & dateigröße > 0
        if(os.path.isfile(TODAYBACKUPPATH)):
            if(os.path.getsize(TODAYBACKUPPATH) > 0):
                success = True

        return success