
from enum import Enum

class ResponseSignal(Enum):
    FILE_VALIDATED_SUCCESS = "File validated successfully."
    FILE_VALIDATION_FAILED = "File validation failed."
    FILE_TYPE_NOT_ALLOWED = "File type is not allowed."
    FILE_SIZE_EXCEEDED = "File size exceeds the maximum limit."
    FILE_UPLOAD_SUCCESS = "File uploaded successfully."
    FILE_UPLOAD_FAILED = "File upload failed."