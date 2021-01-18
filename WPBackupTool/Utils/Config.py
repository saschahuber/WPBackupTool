import json

from WPBackupTool.Utils import Helper


class DBConfig:
    def __init__(self, host, name, user, password):
        self.host = host
        self.name = name
        self.user = user
        self.password = password

    @staticmethod
    def from_config(config):
        try:
            db_configs = []

            for config in config['db_data']:
                host = config['host']
                name = config['db_name']
                user = config['user']
                password = config['password']

                if host is None or name is None or user is None or password is None:
                    raise AttributeError()

                db_configs.append(DBConfig(host, name, user, password))
            return db_configs
        except:
            raise AttributeError("No DB credentials in config file")

class FTPConfig:
    def __init__(self, host, username, password, use_sftp, server_dir, ignore_dirs):
        self.host = host
        self.username = username
        self.password = password
        self.use_sftp = use_sftp
        self.server_dir = server_dir
        self.ignore_dirs = ignore_dirs

    @staticmethod
    def from_config(config):
        try:
            host = config['ftp_data']['host']
            username = config['ftp_data']['user']
            password = config['ftp_data']['password']
            use_sftp = config['ftp_data']['use_sftp']
            server_dir = config['ftp_data']['server_dir']
            ignore_dirs = config['ftp_data']['ignore_dirs']

            if host is None or username is None or password is None or server_dir is None:
                raise AttributeError()

            return FTPConfig(host, username, password, use_sftp, server_dir, ignore_dirs)
        except:
            raise AttributeError("No DB credentials in config file")

class Config:
    def __init__(self, backup_name, backup_path, db_configs, ftp_config):
        self.backup_name = backup_name
        self.backup_path = backup_path
        self.db_configs = db_configs
        self.ftp_config = ftp_config

    @staticmethod
    def from_config(config):
        configs = []
        try:
            for config_item in config:
                backup_name = config_item['backup_name']
                if backup_name is None:
                    raise AttributeError()

                backup_path = config_item['backup_path']
                if backup_path is None:
                    raise AttributeError()

                db_configs = DBConfig.from_config(config_item)
                ftp_config = FTPConfig.from_config(config_item)

                configs.append(Config(backup_name, backup_path, db_configs, ftp_config))
        except:
            raise AttributeError("Incorrect formatted config-file")

        return configs

    @staticmethod
    def from_config_file(path):
        with open(path) as json_file:
            config_data = json.load(json_file)
            return Config.from_config(config_data)