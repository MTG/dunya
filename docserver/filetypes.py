
class FileType(object):
    extension = ""
    converters = {}

class MP3FileType(FileType):
    extension = "mp3"

    def convert_to_wav(self, incoming):
        return incoming

class CSVFileType(FileType):
    extension = "csv"
