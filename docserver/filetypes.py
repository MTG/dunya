
class FileType(object):
    extension = ""
    converters = {}

class MusicXmlType(FileType):
    extension = "mxz"

class EssentiaAnalysisType(FileType):
    extension = ""

class WavFileType(FileType):
    extension = "wav"

    def convert_to_mp3(self, incoming):
        pass

    def convert_to_ogg(self, incoming):
        pass

class MP3FileType(FileType):
    extension = "mp3"

    def __init__(self):
        self.converters = {"opus": self.convert_to_opus}

    def convert_to_wav(self, incoming):
        return incoming
