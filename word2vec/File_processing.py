import os


class File_processing:
    def __init__(self, file_path):
        self.file_path = file_path
        self.remove()

    def write(self, content):
        with open(self.file_path, "a", encoding="utf-8") as f:
            f.write(content + "\n")

    def remove(self):
        if os.path.isfile(self.file_path):
            os.remove(self.file_path)
