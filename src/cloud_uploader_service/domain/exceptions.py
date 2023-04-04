from cloud_uploader_service.base_exception import BaseCloudUploaderException


class BaseUploadCaseException(BaseCloudUploaderException):
    pass


class FileAlreadyFullUploaded(BaseUploadCaseException):
    pass


class FilePartAlreadyUploaded(BaseUploadCaseException):
    pass


class FileNotFullUploaded(BaseUploadCaseException):
    pass
