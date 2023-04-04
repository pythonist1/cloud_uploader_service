from cloud_uploader_service.base_exception import BaseCloudUploaderException


class UploadCaseNotFound(BaseCloudUploaderException):
    pass


class UploadPartStatusNotFound(BaseCloudUploaderException):
    pass
