class LogItem:
    def __init__(self, backup_name, db_log, ftp_log):
        self.backup_name = backup_name
        self.db_log = db_log
        self.ftp_log = ftp_log

    @staticmethod
    def many_to_string(log_items, html=False):
        data = ""

        for log_item in log_items:
            data += log_item.to_string(html)+"\n\n"

        return data

    def to_string(self, html=False):
        new_line = "\n"
        if html:
            new_line = "<br>"

        complete_log = "Log von Backup (" + self.backup_name + "):"

        if self.db_log is not None:
            complete_log += new_line+" - DB: " + self.db_log.to_string(html)

        if self.ftp_log is not None:
            complete_log += new_line+" - FTP: " + self.ftp_log.to_string(html)

        return complete_log

    def was_success(self):
        if self.db_log is not None:
            if not self.db_log.was_success:
                return False

        if self.ftp_log is not None:
            if not self.ftp_log.was_success:
                return False

        return True