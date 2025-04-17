import logging
from requests.exceptions import HTTPError
from voyager_sdk.file_repository import FileRepository, File
from exceptions.file_exceptions import FileNotFoundException, FileHelperException


class FileProcessor(object):

    logger = logging.getLogger(__name__)

    @staticmethod
    def get_sample(file):
        return file.sample

    @staticmethod
    def get_file_id(uri):
        file_obj = FileProcessor.get_file_obj(uri)
        return str(file_obj.id)

    @staticmethod
    def get_file_path(uri):
        file_obj = FileProcessor.get_file_obj(uri)
        return file_obj.path

    @staticmethod
    def get_juno_uri_from_file(file):
        return "juno://%s" % file.path

    @staticmethod
    def get_file_size(file):
        return file.size

    @staticmethod
    def get_file_checksum(file):
        return file.checksum

    @staticmethod
    def get_bid_from_file(file):
        return "bid://%s" % str(file.id)

    @staticmethod
    def parse_path_from_uri(uri):
        if uri.startswith("bid://"):
            raise FileHelperException("Can't parse path from uri %s." % uri)
        elif uri.startswith("juno://"):
            return uri.replace("juno://", "")
        elif uri.startswith("file://"):
            return uri.replace("file://", "")
        else:
            raise FileHelperException("Unknown uri schema %s" % uri)

    @staticmethod
    def get_file_obj(uri):
        """
        :param uri:
        :return: File model. Throws UriParserException if File doesn't exist
        """
        if uri.startswith("bid://"):
            beagle_id = uri.replace("bid://", "")
            try:
                file_obj = FileRepository.get_by_id(id=beagle_id)
            except HTTPError as e:
                raise FileNotFoundException("File with uri %s doesn't exist" % uri)
            return file_obj
        elif uri.startswith("juno://"):
            juno_path = uri.replace("juno://", "")
            file_obj = FileRepository.filter(path=juno_path).first()
            if not file_obj:
                raise FileHelperException("File with uri %s doesn't exist" % uri)
            return file_obj
        elif uri.startswith("file://"):
            juno_path = uri.replace("file://", "")
            file_obj = File.objects.filter(path=juno_path).first()
            if not file_obj:
                raise FileHelperException("File with uri %s doesn't exist" % uri)
            return file_obj
        else:
            raise FileHelperException("Unknown uri schema %s" % uri)
