from typing import Any, Dict, List

import requests


class BaseAPIESawErrorResponse(Exception):
    def __init__(
        self,
        status_code: int,
        service_url: str,
        method_name: str,
        request_data: Dict[str, Any],
        response: requests.Response,
        *args,
        **kwargs,
    ) -> None:
        """BaseAPIESawErrorResponse."""
        super().__init__(*args, **kwargs)
        self.status_code = status_code
        self.service_url = service_url
        self.method_name = method_name
        self.response = response
        self.request_data = request_data
        self.response_headers = dict(response.headers)
        try:
            self.response_data = response.json()
        except Exception:
            try:
                self.response_data = (
                    response.content.decode()
                    if isinstance(response.content, bytes)
                    else response.content
                )
            except Exception:
                try:
                    self.response_data = response.text
                except Exception:
                    self.response_data = "Unable to get response data"

    def __str__(self):
        return f"Status Code: {self.status_code}"

    def __repr__(self):
        return f"Status Code: {self.status_code}"

    def __reduce__(self):
        return (
            self.__class__,
            (
                self.status_code,
                self.service_url,
                self.method_name,
                self.request_data,
                self.response,
            ),
        )


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
            f"Unexpected Response from url {self.service_url}\n"
            f"status_code : {self.status_code}\n"
            f"method_name : {self.method_name}\n"
            f"response_data : {str(self.response_data)}\n"
            f"request_data : {str(self.request_data)}\n"
            f"response_headers : {str(self.response_headers)}\n"
        )


class ESawErrorResponse(BaseAPIESawErrorResponse):
    def __str__(self):
        return (
            f"Error Response from url {self.service_url}\n"
            f"status_code : {self.status_code}\n"
            f"method_name: {self.method_name}\n"
            f"response_data : {str(self.response_data)}\n"
            f"request_data : {str(self.request_data)}\n"
            f"response_headers : {str(self.response_headers)}\n"
        )
