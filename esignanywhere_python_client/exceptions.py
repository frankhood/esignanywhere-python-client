from typing import List


class BaseAPIESawErrorResponse(Exception):
    def __init__(
        self,
        message,
        status_code=None,
        service_url=None,
        request_data=None,
        response_data=None,
    ):
        """BaseAPIESawErrorResponse."""
        self.message = message
        self.status_code = status_code
        self.service_url = service_url
        self.request_data = request_data
        self.response_data = response_data


class ESawInvalidVersionError(Exception):
    def __init__(
        self,
        version: str,
        supported_versions: List[str],
    ):
        self.version = version
        self.supported_versions = supported_versions

    def __str__(self):
        return (
            f"Invalid Version Error: Version {self.version} is not supported.\n"
            f"Supported Versions: {self.supported_versions}"
        )


class ESawUnauthorizedRequest(BaseAPIESawErrorResponse):
    pass


class ESawUnexpectedResponse(BaseAPIESawErrorResponse):
    def __str__(self):
        return (
            f"Unexpected Response from url {self.service_url}: {self.message}\n"
            f"status_code : {self.status_code}\n"
            f"response_data : {self.response_data}\n"
            f"request_data : {self.request_data}"
        )


class ESawErrorResponse(BaseAPIESawErrorResponse):
    def __str__(self):
        return (
            f"Error Response from url {self.service_url}: {self.message}\n"
            f"status_code : {self.status_code}\n"
            f"response_data : {self.response_data}\n"
            f"request_data : {self.request_data}"
        )
