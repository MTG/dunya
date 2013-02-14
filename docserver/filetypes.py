
class FileType(object):
    extension = ""
    converters = {}

class MusicXmlType(FileType):
    extension = "mxz"

class EssentiaAnalysisType(FileType):
    extension = ""

class WavFileType(FileType):
    extension = "mp3"

class MP3FileType(FileType):
    extension = "mp3"

    def __init__(self):
        self.converters = {"opus": self.convert_to_opus}

    def convert_to_opus(self, incoming):
        return incoming
