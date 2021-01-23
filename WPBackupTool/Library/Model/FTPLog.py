class FTPLog:
    def __init__(self):
        self.successful = 0
        self.errors = 0
        self.error_filenames = []

    def success(self, num):
        self.successful += num

    def error(self, num):
        self.errors += num

    def error_files(self, files):
        self.error_filenames.extend(files)

    def was_success(self):
        return self.errors is 0

    def to_string(self, html=False):
        new_line = "\n"
        if html:
            new_line = "<br>"

        return "FTPLog"