import json
from typing import Any, Dict, List

import requests


class BaseAPIESawErrorResponse(Exception):
    def __init__(
        self,
        status_code: int | None = None,
        service_url: str | None = None,
        method_name: str | None = None,
        request_data: Dict[str, Any] | None = None,
        response: requests.Response | None = None,
        *args,
        **kwargs,
    ) -> None:
        """BaseAPIESawErrorResponse."""
        super().__init__(*args, **kwargs)
        self.status_code = None
        self.service_url = None
        self.method_name = None
        self.request_data = None
        self.response_data = None
        if all([status_code, service_url, method_name, request_data, response]):
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

    def __reduce__(self):
        """Metodo speciale per il pickling che specifica come ricostruire l'oggetto."""
        return (self.__class__, (), self.__getstate__())

    def __getstate__(self):
        """Metodo chiamato durante la serializzazione."""
        return {
            "status_code": self.status_code,
            "service_url": self.service_url,
            "method_name": self.method_name,
            "request_data": self.request_data,
            "response_data": self.response_data,
            "args": self.args,
        }

    def __setstate__(self, state):
        """Metodo chiamato durante la deserializzazione."""
        # Non chiamare __init__, assegna direttamente gli attributi
        self.__dict__.update(state)
        # Inizializza anche la classe base Exception
        super().__init__()

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
