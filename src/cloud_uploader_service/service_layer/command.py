from enum import Enum, unique


@unique
class Command(str, Enum):
    CREATE_UPLOAD_CASE = 'create_upload_case'
    COMPLETE_UPLOAD_CASE = 'complete_upload_case'
    DELETE_UPLOAD_CASE = 'delete_upload_case'
