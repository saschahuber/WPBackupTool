import json

from WPBackupTool.Library.Config.MailConfig import MailConfig
from WPBackupTool.Library.Config.BackupConfig import BackupConfig
from WPBackupTool.Library.Config.SMPTConfig import SMPTConfig


class Config:
    def __init__(self, mail_config, backup_configs):
        self.mail_config = mail_config
        self.backup_configs = backup_configs

    @staticmethod
    def from_config_file(path):
        with open(path) as json_file:
            config_data = json.load(json_file)
            mail_config = MailConfig.from_config(config_data['mail'])
            backup_configs = BackupConfig.from_config(config_data['backups'])
            return Config(mail_config, backup_configs)