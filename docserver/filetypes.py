
class FileType(object):
    extension = ""
    converters = {}

class MP3FileType(FileType):
    extension = "mp3"

class CSVFileType(FileType):
    extension = "csv"
