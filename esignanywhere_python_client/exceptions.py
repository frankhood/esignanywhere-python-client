import json
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
        self.status_code = status_code  # type: ignore
        self.service_url = service_url  # type: ignore
        self.method_name = method_name  # type: ignore
        self.request_data = json.dumps(request_data)  # type: ignore
        self.response_headers = dict(response.headers)  # type: ignore
        try:
            self.response_data = response.json()  # type: ignore
        except Exception:
            try:
                self.response_data = (  # type: ignore
                    response.content.decode()  # type: ignore
                    if isinstance(response.content, bytes)  # type: ignore
                    else response.content  # type: ignore
                )
            except Exception:
                try:
                    self.response_data = response.text  # type: ignore
                except Exception:
                    self.response_data = "Unable to get response data"  # type: ignore

    def __str__(self):
        return f"Status Code: {self.status_code}"

    def __repr__(self):
        return f"Status Code: {self.status_code}"


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
            f"request_data : {str(self.request_data)}\n"
            f"response_data : {str(self.response_data)}\n"
            f"response_headers : {str(self.response_headers)}\n"
        )


class ESawErrorResponse(BaseAPIESawErrorResponse):
    def __str__(self):
        return (
            f"Error Response from url {self.service_url}\n"
            f"status_code : {self.status_code}\n"
            f"method_name: {self.method_name}\n"
            f"request_data : {str(self.request_data)}\n"
            f"response_data : {str(self.response_data)}\n"
            f"response_headers : {str(self.response_headers)}\n"
        )
