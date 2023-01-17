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
