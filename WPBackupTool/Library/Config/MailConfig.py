from WPBackupTool.Library.Config.SMPTConfig import SMPTConfig


class MailConfig:
    def __init__(self, smpt_config, sender_name, sender_mail, receiver_name, receiver_mail):
        self.smpt_config = smpt_config
        self.sender_name = sender_name
        self.sender_mail = sender_mail
        self.receiver_name = receiver_name
        self.receiver_mail = receiver_mail

    @staticmethod
    def from_config(config):
        smpt_config = SMPTConfig.from_config(config["smpt"])

        sender_name = config["sender"]["name"]
        sender_mail = config["sender"]["mail"]
        receiver_name = config["receiver"]["name"]
        receiver_mail = config["receiver"]["mail"]

        if sender_name is None or sender_mail is None or receiver_name is None or receiver_mail is None:
            raise AttributeError()

        return MailConfig(smpt_config, sender_name, sender_mail, receiver_name, receiver_mail)