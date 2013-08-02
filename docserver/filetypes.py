
class FileType(object):
    extension = ""
    converters = {}

#class WavFileType(FileType):
#    extension = "wav"
#
#    def convert_to_mp3(self, incoming):
#        pass

class MP3FileType(FileType):
    extension = "mp3"

    def convert_to_wav(self, incoming):
        return incoming

class CSVFileType(FileType):
    extension = "csv"
