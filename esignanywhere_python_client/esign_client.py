import logging
from io import BufferedReader
from typing import Union

import requests

from . import exceptions
from .models import models_v5, models_v6

logger = logging.getLogger(__name__)


class ESignAnyWhereClient:
    """Base class client for eSignAnyWhere V5."""

    def __init__(self, api_token, api_domain=None, is_test_env=True):
        """
        ESignAnyWhereClient.

        :param api_token: Token of the organization
        :param api_uri: Esign uri to append for each api
        """
        self.api_token = api_token
        self.api_domain = api_domain or self._get_api_domain(is_test_env=is_test_env)
        self.api_uri = f"{self.api_domain}/Api/"

    def _get_api_domain(self, is_test_env=True):
        if is_test_env:
            return "https://demo.esignanywhere.net"
        else:
            return "https://saas.esignanywhere.net"

    def _get_request_headers(self, is_json=True):
        _request_headers = {
            "apiToken": self.api_token,
        }
        if is_json:
            _request_headers.update({"Content-Type": "application/json"})
        return _request_headers

    def _handle_response_errors(self, service_url, response, request_data: dict):
        if response.status_code == 401:
            raise exceptions.ESawUnauthorizedRequest(
                message=response.text
                and response.json().get("Message")
                or f"Error with code {response.status_code}",
                status_code=response.status_code,
                service_url=service_url,
                request_data=request_data,
                response_data=response.text and response.json() or {},
            )
        else:
            error_message = f"Error with code {response.status_code}"
            if response.text:
                error_id = response.json().get("ErrorId", "")
                support_id = response.json().get("SupportId", "")
                if error_id:
                    error_message = (
                        f"{response.text} [ErrorId: {error_id} SupportID: {support_id}]"
                    )
            raise exceptions.ESawErrorResponse(
                message=error_message,
                status_code=response.status_code,
                service_url=service_url,
                request_data=request_data,
                response_data=response.text and response.json() or {},
            )

    def get_version(self, version="v4"):
        """
        Return the version of eSignAnyWhere.

        :param version: string for api version
        :return:
            {
                "Success": true,
                "Version": "string"
            }
        """
        service_url = self.api_uri + version + "/version"
        request_data = {}
        response = requests.get(
            url=service_url, data=request_data, headers=self._get_request_headers()
        )
        if response.status_code == 200:
            logger.debug(
                f"Response from service_url : {service_url}: {response.json()}"
            )
            return response.json()

    def test_authorization(self, version="v4"):
        """
        Test Authorization.

        :param: version: string
        :return: HTTP_200_OK
        """
        service_url = self.api_uri + version + "/authorization"
        response = requests.get(
            url=service_url, data={}, headers=self._get_request_headers()
        )
        if response.status_code == 200:
            logger.debug(f"Response from service_url : {service_url}: {response.text}")
            return response.text
        else:
            self._handle_response_errors(
                service_url, response=response, request_data={}
            )

    def upload_file(
        self,
        resource_to_upload: Union[str, BufferedReader],
        version="v6",
    ):
        """
        Upload a file for further processing/using. Content-Type must be multipart/form-data.

        :param file: file full_path
        :return: models_v6.FileUploadResponse
        """
        if version == "v6":
            service_url = self.api_uri + "v6/file/upload"
        else:
            raise exceptions.ESawInvalidVersionError(
                version=version, supported_versions=["v6"]
            )

        file_content = None
        try:
            if isinstance(resource_to_upload, str):
                file_content = open(resource_to_upload, "rb")
                request_data = {"File": file_content}
            else:

                request_data = {"File": resource_to_upload}

            response = requests.post(
                url=service_url,  # https://demo.esignanywhere.net
                files=request_data,
                headers=self._get_request_headers(is_json=False),
            )

            if response.status_code == 200:
                logger.info(
                    f"Response from service_url : {service_url}: {response.json()}"
                )
                response_data = response.json()
                return models_v6.FileUploadResponse(**response_data)
            else:
                self._handle_response_errors(
                    service_url, response=response, request_data=request_data
                )

        finally:
            try:
                if file_content:
                    file_content.close()
            except Exception:
                logger.exception(
                    "Unable to close file in upload_file method of Esign client"
                )

    def create_and_send_envelope(
        self,
        envelope_data: models_v6.EnvelopeSendRequest,
        version="v6",
    ):
        """
        Create and directly sends a new envelope.

        :param models_v6.EnvelopeSendRequest
        :param version: string for api version
        :return: models_v6.EnvelopeSendResponse
        """
        if version == "v6":
            service_url = self.api_uri + "v6/envelope/send"
        else:
            raise exceptions.ESawInvalidVersionError(
                version=version, supported_versions=["v6"]
            )

        request_data = envelope_data.json()
        response = requests.post(
            url=service_url, data=request_data, headers=self._get_request_headers()
        )
        logger.debug(f"create_and_send_envelope Request : {request_data}")
        if response.status_code == 200:
            logger.info(f"Response from service_url : {service_url}: {response.json()}")
            response_data = response.json()
            if "EnvelopeId" not in response_data.keys():
                raise exceptions.ESawUnexpectedResponse(
                    message='Response has no attribute "EnvelopeId"',
                    status_code=response.status_code,
                    service_url=service_url,
                    request_data=request_data,
                    response_data=response_data,
                )
            return models_v6.EnvelopeSendResponse(**response_data)
        else:
            self._handle_response_errors(
                service_url, response=response, request_data=request_data
            )

    def create_and_send_bulk_envelope(
        self,
        envelope_data: models_v6.EnvelopeBulkSendRequest,
        version="v6",
    ):
        """
        Create and directly sends a new envelope.

        :param models_v6.EnvelopeBulkSendRequest
        :param version: string for api version
        :return: models_v6.EnvelopeBulkSendResponse
        """
        if version == "v6":
            service_url = self.api_uri + "v6/envelopebulk/send"
        else:
            raise exceptions.ESawInvalidVersionError(
                version=version, supported_versions=["v6"]
            )

        request_data = envelope_data.json()
        response = requests.post(
            url=service_url, data=request_data, headers=self._get_request_headers()
        )
        logger.debug(f"create_and_send_envelope Request : {request_data}")
        if response.status_code == 200:
            logger.info(f"Response from service_url : {service_url}: {response.json()}")
            response_data = response.json()
            return models_v6.EnvelopeBulkSendResponse(**response_data)
        else:
            self._handle_response_errors(
                service_url, response=response, request_data=request_data
            )

    def get_envelope(
        self,
        envelope_id: str,
        version="v6",
    ):
        """
        Return an envelope for the given id.

        :param envelope_id: str
        :param version: string for api version
        :return: models_v6.EnvelopeGetResponse for v6 or models_v5.EnvelopeStatus for v5
        """
        if version == "v6":
            service_url = f"{self.api_uri}v6/envelope/{envelope_id}"
        elif version == "v5":
            service_url = f"{self.api_uri}v5/envelope/{envelope_id}"
        else:
            raise exceptions.ESawInvalidVersionError(
                version=version, supported_versions=["v6", "v5"]
            )

        request_data = {}  # type:ignore
        response = requests.get(
            url=service_url, data=request_data, headers=self._get_request_headers()
        )
        if response.status_code == 200:
            logger.info(f"Response from service_url : {service_url}: {response.json()}")
            response_data = response.json()
            if version == "v5":
                envelope_status = models_v5.EnvelopeStatus(**response_data)
            else:
                envelope_status = models_v6.EnvelopeGetResponse(**response_data)
            return envelope_status
        else:
            self._handle_response_errors(
                service_url, response=response, request_data=request_data
            )

    def get_envelope_configuration(
        self,
        envelope_id: str,
        version="v6",
    ):
        """
        Return an envelope configuration for the given id.

        :param envelope_id: str
        :param version: string for api version
        :return: models_v6.EnvelopeGetConfigurationResponse
        """
        if version == "v6":
            service_url = f"{self.api_uri}v6/envelope/{envelope_id}/configuration"
        else:
            raise exceptions.ESawInvalidVersionError(
                version=version, supported_versions=["v6"]
            )

        request_data = {}  # type:ignore
        response = requests.get(
            url=service_url, data=request_data, headers=self._get_request_headers()
        )
        if response.status_code == 200:
            logger.info(f"Response from service_url : {service_url}: {response.json()}")
            response_data = response.json()
            envelope_status = models_v6.EnvelopeGetConfigurationResponse(
                **response_data
            )
            return envelope_status
        else:
            self._handle_response_errors(
                service_url, response=response, request_data=request_data
            )

    def get_envelope_files(
        self,
        envelope_id: str,
        version="v6",
    ):
        """
        Return an envelope files for the given id.

        :param envelope_id: str
        :param version: string for api version
        :return: models_v6.EnvelopeGetFilesResponse
        """
        if version == "v6":
            service_url = f"{self.api_uri}v6/envelope/{envelope_id}/files"
        else:
            raise exceptions.ESawInvalidVersionError(
                version=version, supported_versions=["v6"]
            )

        request_data = {}  # type:ignore
        response = requests.get(
            url=service_url, data=request_data, headers=self._get_request_headers()
        )
        if response.status_code == 200:
            logger.info(f"Response from service_url : {service_url}: {response.json()}")
            response_data = response.json()
            envelope_status = models_v6.EnvelopeGetFilesResponse(**response_data)
            return envelope_status
        else:
            self._handle_response_errors(
                service_url, response=response, request_data=request_data
            )

    def get_envelope_viewer_links(
        self,
        envelope_id: str,
        version="v6",
    ):
        """
        Return an envelope viewer links for the given id.

        :param envelope_id: str
        :param version: string for api version
        :return: models_v6.EnvelopeGetViewerLinksResponse
        """
        if version == "v6":
            service_url = f"{self.api_uri}v6/envelope/{envelope_id}/viewerlinks"
        else:
            raise exceptions.ESawInvalidVersionError(
                version=version, supported_versions=["v6"]
            )

        request_data = {}  # type:ignore
        response = requests.get(
            url=service_url, data=request_data, headers=self._get_request_headers()
        )
        if response.status_code == 200:
            logger.info(f"Response from service_url : {service_url}: {response.json()}")
            response_data = response.json()
            envelope_status = models_v6.EnvelopeGetViewerLinksResponse(**response_data)
            return envelope_status
        else:
            self._handle_response_errors(
                service_url, response=response, request_data=request_data
            )

    def get_envelope_history(
        self,
        envelope_id: str,
        version="v6",
    ):
        """
        Return an envelope event history for the given id.

        :param envelope_id: str
        :param version: string for api version
        :return: models_v6.EnvelopeGetHistoryResponse
        """
        if version == "v6":
            service_url = f"{self.api_uri}v6/envelope/{envelope_id}/history"
        else:
            raise exceptions.ESawInvalidVersionError(
                version=version, supported_versions=["v6"]
            )

        request_data = {}  # type:ignore
        response = requests.get(
            url=service_url, data=request_data, headers=self._get_request_headers()
        )
        if response.status_code == 200:
            logger.info(f"Response from service_url : {service_url}: {response.json()}")
            response_data = response.json()
            envelope_status = models_v6.EnvelopeGetHistoryResponse(**response_data)
            return envelope_status
        else:
            self._handle_response_errors(
                service_url, response=response, request_data=request_data
            )

    def get_envelope_elements(
        self,
        envelope_id: str,
        version="v6",
    ):
        """
        Return the elements belonging to an envelope for the given id.

        :param envelope_id: str
        :param version: string for api version
        :return: models_v6.EnvelopeGetElementsResponse
        """
        if version == "v6":
            service_url = f"{self.api_uri}v6/envelope/{envelope_id}/elements"
        else:
            raise exceptions.ESawInvalidVersionError(
                version=version, supported_versions=["v6"]
            )

        request_data = {}  # type:ignore
        response = requests.get(
            url=service_url, data=request_data, headers=self._get_request_headers()
        )
        if response.status_code == 200:
            logger.info(f"Response from service_url : {service_url}: {response.json()}")
            response_data = response.json()
            envelope_status = models_v6.EnvelopeGetElementsResponse(**response_data)
            return envelope_status
        else:
            self._handle_response_errors(
                service_url, response=response, request_data=request_data
            )

    def dowload_completed_document(self, file_id: str, version="v6"):
        """
        Return an envelope for the given id.

        :param envelope_id: str
        :param version: string for api version
        :return: Envelope
        """
        if version == "v6":
            service_url = f"{self.api_uri}v6/file/{file_id}"
        else:
            raise exceptions.ESawInvalidVersionError(
                version=version, supported_versions=["v6"]
            )

        request_data = {}  # type:ignore
        response = requests.get(
            url=service_url,
            data=request_data,
            headers=self._get_request_headers(is_json=False),
        )
        if response.status_code == 200:
            logger.info(f"Response from service_url : {service_url}")
            return response.content
        else:
            self._handle_response_errors(
                service_url, response=response, request_data=request_data
            )

    def cancel_envelope(self, envelope_id: str, version="v5"):
        """
        Cancel an envelope with the given envelope id.

        :param envelope_id: str
        :param version: string for api version
        :return:
        """
        service_url = self.api_uri + version + f"/envelope/{envelope_id}/cancel/"
        request_data = {}  # type:ignore
        response = requests.get(
            url=service_url, data=request_data, headers=self._get_request_headers()
        )
        if response.status_code == 204:
            logger.info(
                f"Response from service_url : {service_url} -> {response.status_code}"
            )
            return {}
        else:
            self._handle_response_errors(
                service_url, response=response, request_data=request_data
            )

    def delete_envelope(self, envelope_id: str, version="v6"):
        """
        Delete an envelope with the given id.

        :param envelope_id: str
        :param version: string for api version
        :return:
        """
        if version == "v6":
            service_url = self.api_uri + "v6/envelope/delete"
        else:
            raise exceptions.ESawInvalidVersionError(
                version=version, supported_versions=["v6"]
            )

        request_data = models_v6.EnvelopeDeleteRequest(EnvelopeId=envelope_id).json()
        response = requests.post(
            url=service_url, data=request_data, headers=self._get_request_headers()
        )
        if response.status_code == 200:
            logger.debug(
                f"Response from service_url : {service_url} -> {response.status_code}"
            )
        else:
            self._handle_response_errors(
                service_url, response=response, request_data=request_data
            )

    def download_completed_document(self, document_id: str, version="v6"):
        """
        Return a pdf document for the given id.

        :param document_id: string
        :param version: string for api version
        :return: file
        """

        if version == "v6":
            service_url = self.api_uri + f"v6/file/{document_id}"
        else:
            raise exceptions.ESawInvalidVersionError(
                version=version, supported_versions=["v6"]
            )

        request_data = {}  # type:ignore
        response = requests.get(
            url=service_url,
            data=request_data,
            headers=self._get_request_headers(is_json=False),
        )
        if response.status_code == 200:
            return response.content
        else:
            self._handle_response_errors(
                service_url, response=response, request_data=request_data
            )

    # ======================================
    #  PAY ATTENTION!!! Below methods are draft and maybe not implemented
    # ======================================
    def get_user_by_email(self, email: str, version="v5"):
        """
        Get user by email.

        :param email: str
        :param version: string for api version
        :return User
        """
        service_url = self.api_uri + version + f"/user/{email}"
        request_data = {}  # type:ignore
        response = requests.get(
            url=service_url,
            data=request_data,
            headers=self._get_request_headers(is_json=False),
        )

        if response.status_code == 200:
            logger.debug(
                f"Response from service_url : {service_url}: {response.json()}"
            )
            response_data = response.json()
            # return models_v5.UserDescription(**response_data)
            return models_v5.ExtendedFindUsersResultEntry(**response_data)
        else:
            self._handle_response_errors(
                service_url, response=response, request_data=request_data
            )

    def create_user(self, user_data: models_v5.UserCreateModel, version="v5"):
        """Create an user in the organization of the api user."""
        service_url = self.api_uri + version + "/user/create"
        request_data = user_data.json()
        response = requests.post(
            url=service_url, data=request_data, headers=self._get_request_headers()
        )
        if response.status_code == 200:
            logger.debug(
                f"Response from service_url : {service_url}: {response.json()}"
            )
            response_data = response.json()
            return models_v5.CreateUserResult(**response_data)
        else:
            self._handle_response_errors(
                service_url, response=response, request_data=request_data
            )

    def create_envelope(
        self, draft_create_model: models_v5.DraftCreateModel, version="v4"
    ):
        """
        Create a draft with the given information.

        :param: version: string for api version
        :return: Envelope
        """
        service_url = self.api_uri + version + "/envelope/create"
        request_data = draft_create_model
        response = requests.post(
            url=service_url, data=request_data, headers=self._get_request_headers()
        )
        if response.status_code == 200:
            logger.debug(
                f"Response from service_url : {service_url}: {response.json()}"
            )
            response_data = response.json()
            return models_v5.CreateDraftResult(**response_data)
        else:
            self._handle_response_errors(
                service_url, response=response, request_data=request_data.dict()
            )

    def create_envelope_from_template(
        self,
        create_from_template_model: models_v5.DraftCreateFromTemplateModel,
        version="v4",
    ):
        """
        Create a draft from an existing template.

        :param models_v5.DraftCreateFromTemplateModel
        :param: version: string for api version
        :return: Envelope
        """
        service_url = self.api_uri + version + "/envelope/createFromTemplate"
        request_data = create_from_template_model
        response = requests.post(
            url=service_url, data=request_data, headers=self._get_request_headers()
        )
        if response.status_code == 200:
            logger.debug(
                f"Response from service_url : {service_url}: {response.json()}"
            )
            response_data = response.json()
            return models_v5.CreateDraftResult(**response_data)
        else:
            self._handle_response_errors(
                service_url, response=response, request_data=request_data.dict()
            )

    def find_envelope(
        self, descriptors: models_v5.FindEnvelopesDescriptor, version="v4"
    ):
        """
        Return the found envelopes for the given descriptor.

        :param version: string for api version
        :param descriptors: models_v5.Descriptor[]
        :return: list of Envelope:
        """
        service_url = self.api_uri + version + "/envelope/find"
        request_data = {}  # type:ignore
        response = requests.get(
            url=service_url, data=request_data, headers=self._get_request_headers()
        )
        if response.status_code == 200:
            logger.debug(
                f"Response from service_url : {service_url}: {response.json()}"
            )
            response_data = response.json()
            return models_v5.ExtendedFindEnvelopesResult(**response_data)
        else:
            self._handle_response_errors(
                service_url, response=response, request_data=request_data
            )

    def get_document_page(
        self, envelope_id: str, doc_ref_number: str, page_number: str, version="v4"
    ):
        """
        Return a png image for the given page.

        :param envelope_id: string
        :param doc_ref_number: string
        :param page_number: string
        :param version: string for api version
        :return: file .png
        """
        service_url = (
            self.api_uri
            + version
            + f"/envelope/{envelope_id}/downloadPageImage/{doc_ref_number}/{page_number}"
        )
        request_data = {}  # type:ignore
        response = requests.get(
            url=service_url,
            data=request_data,
            headers=self._get_request_headers(is_json=False),
        )
        if response.status_code == 200:
            return response.content
        else:
            self._handle_response_errors(
                service_url, response=response, request_data=request_data
            )

    def prepare_envelope(
        self, prepare_model: models_v5.EnvelopePrepareModel, version="v4"
    ):
        """
        Parse the provided files for markup fields and sig string and returns the containing elements.

        :param version: string for api version
        :param models_v5.EnvelopePrepareModel
        """
        service_url = self.api_uri + version + "/envelope/prepare"
        request_data = prepare_model
        response = requests.post(
            url=service_url, data=request_data, headers=self._get_request_headers()
        )
        if response.status_code == 200:
            logger.debug(
                f"Response from service_url : {service_url}: {response.json()}"
            )
            response_data = response.json()
            return models_v5.PrepareSendEnvelopeStepsResult(**response_data)
        else:
            self._handle_response_errors(
                service_url, response=response, request_data=request_data.dict()
            )

    def restart_envelope_expiration_days(
        self, envelope_id: str, expiration_in_days: int, version="v4"
    ):
        """
        Restart the envelope with the given id and sets the expiration days.

        :param envelope_id: string
        :param expiration_in_days: integer
        :param version: string for api version
        :return:
        """
        service_url = (
            self.api_uri
            + version
            + f"/envelope/{envelope_id}/restart/{expiration_in_days}"
        )
        request_data = {}  # type:ignore
        response = requests.post(
            url=service_url, data=request_data, headers=self._get_request_headers()
        )
        if response.status_code == 204:
            logger.debug(
                f"Response from service_url : {service_url} -> {response.status_code}"
            )
            return {}
        else:
            self._handle_response_errors(
                service_url, response=response, request_data=request_data
            )

    def send_envelope_from_template(
        self,
        send_from_template_model: models_v5.EnvelopeSendFromTemplateModel,
        version="v4",
    ):
        """
        Create an envelope from a existing template and directly sends it.

        :param models_v5.EnvelopeSendFromTemplateModel
        :param version: string for api version
        :return Envelope
        """
        service_url = self.api_uri + version + "/envelope/sendFromTemplate"
        request_data = {"sendFromTemplateModel": send_from_template_model}
        response = requests.post(
            url=service_url, data=request_data, headers=self._get_request_headers()
        )
        if response.status_code == 200:
            logger.debug(
                f"Response from service_url : {service_url}: {response.json()}"
            )
            response_data = response.json()
            return models_v5.SendEnvelopeResult(**response_data)
        else:
            self._handle_response_errors(
                service_url, response=response, request_data=request_data
            )

    def remind_envelope(self, envelope_id: str, version="v4"):
        """
        Send a reminder email to the recipient which action is awaited for the provided envelope.

        :param envelope_id: string
        :param version: string for api version
        :return:
            {
                "Count": 0,
                "AvoidedDueToRateLimitCount": 0,
                "AvoidedDueToDisabledEmailCount": 0
            }
        """
        service_url = self.api_uri + version + f"/envelope/{envelope_id}/remind"
        request_data = {}  # type:ignore
        response = requests.get(
            url=service_url, data=request_data, headers=self._get_request_headers()
        )
        if response.status_code == 200:
            logger.debug(
                f"Response from service_url : {service_url}: {response.json()}"
            )
            response_data = response.json()
            return models_v5.SendRemindersResult(**response_data)
        else:
            self._handle_response_errors(
                service_url, response=response, request_data=request_data
            )

    def copy_envelope_from_template(self, template_id: str, version="v4"):
        """
        Copy all the ids from the documents uploaded in the provided template.

        :param template_id: string
        :param version: string for api version
        :return: models_v5.CopyDocumentFromTemplateResult
        """
        service_url = (
            self.api_uri + version + f"/envelope/{template_id}/copyFromTemplate"
        )
        request_data = {}  # type:ignore
        response = requests.get(
            url=service_url, data=request_data, headers=self._get_request_headers()
        )
        if response.status_code == 200:
            logger.debug(
                f"Response from service_url : {service_url}: {response.json()}"
            )
            response_data = response.json()
            return models_v5.CopyDocumentFromTemplateResult(**response_data)
        else:
            self._handle_response_errors(
                service_url, response=response, request_data=request_data
            )

    def unlock_envelope(self, envelope_id: str, version="v4"):
        """
        Unlock an envelope with the given id.

        :param envelope_id: string
        :param version: string for api version
        :return:
        """
        service_url = self.api_uri + version + f"/envelope/{envelope_id}/unlock"
        request_data = {}  # type:ignore
        response = requests.get(
            url=service_url, data=request_data, headers=self._get_request_headers()
        )
        if response.status_code == 204:
            logger.debug(
                f"Response from service_url : {service_url} -> {response.status_code}"
            )
            return {}
        else:
            self._handle_response_errors(
                service_url, response=response, request_data=request_data
            )

    def get_license(self, version="v4"):
        """
        Return the License state. Only for usermanager.

        :param version: string for api version
        :return: models_v5.LicenseInformation
        """
        service_url = self.api_uri + version + "/license"
        request_data = {}
        response = requests.get(
            url=service_url, data=request_data, headers=self._get_request_headers()
        )
        if response.status_code == 200:
            logger.debug(
                f"Response from service_url : {service_url}: {response.json()}"
            )
            response_data = response.json()
            return models_v5.LicenseInformation(**response_data)
        else:
            self._handle_response_errors(
                service_url, response=response, request_data=request_data
            )

    def remove_recipient_from_envelope(
        self, recipient_id: str, envelope_id: str, version="v4"
    ):
        """
        Delete a recipient from an envelope.

        :param recipient_id: string
        :param envelope_id: string
        :param version: string for api version
        :return:
        """
        service_url = (
            self.api_uri
            + version
            + f"/recipient/{recipient_id}/fromEnvelope/{envelope_id}"
        )
        request_data = {}  # type:ignore
        response = requests.delete(
            url=service_url, data=request_data, headers=self._get_request_headers()
        )
        if response.status_code == 204:
            logger.debug(
                f"Response from service_url : {service_url} -> {response.status_code}"
            )
            return {}
        else:
            self._handle_response_errors(
                service_url, response=response, request_data=request_data
            )

    def replace_recipient_from_envelope(
        self,
        recipient_id: str,
        envelope_id: str,
        recipient: models_v5.ReplaceRecipientData,
        version="v4",
    ):
        """
        Replace a recipient in an envelope.

        :param recipient_id: string
        :param envelope_id: string
        :param version: string for api version
        :param recipient: models_v5.ReplaceRecipientData
        :return
        """
        service_url = (
            self.api_uri
            + version
            + f"/recipient/{recipient_id}/fromEnvelope/{envelope_id}"
        )
        request_data = {"recipient": recipient}
        response = requests.put(
            url=service_url, data=request_data, headers=self._get_request_headers()
        )
        if response.status_code == 204:
            logger.debug(
                f"Response from service_url : {service_url} -> {response.status_code}"
            )
            return {}
        else:
            self._handle_response_errors(
                service_url, response=response, request_data=request_data
            )

    def dispose_uploaded_file(self, file_id: str, version="v4"):
        """
        Dipose a file which was uploaded beforehand.

        :param file_id: string
        :param version: string for api version
        :return:
        """
        requests.delete(
            url=self.api_uri
            + version
            + "/sspfile/disposefile/{sspFileId}".format(
                sspFileId=file_id,
            ),
            headers=self._get_request_headers(),
        )
        raise NotImplementedError()

    def get_teams(self, version="v4"):
        """
        Return the teams set for the organization of the api user.

        :param version: string for api version
        :return Teams:
        """
        service_url = self.api_uri + version + "/user/team"
        request_data = {}
        response = requests.get(
            url=service_url, data=request_data, headers=self._get_request_headers()
        )
        if response.status_code == 200:
            logger.debug(
                f"Response from service_url : {service_url}: {response.json()}"
            )
            response_data = response.json()
            return models_v5.Teams(**response_data)
        else:
            self._handle_response_errors(
                service_url, response=response, request_data=request_data
            )

    def create_team(self, teams: dict, version="v4"):
        """
        Replace all teams with the provided teams.

        :param version: string for api version
        :param teams:
            {
                "TeamList": [{
                    "Name": "string",
                    "AllowEnvelopeSharingWithinTeam": true,
                    "AllowTemplateSharingWithinTeam": true,
                    "Head": {
                        "Email": "string",
                        "Members": [{}]
                    }
                }]
            }
        :return:
        """
        service_url = self.api_uri + version + "/user/team"
        request_data = {"teams": teams}
        response = requests.post(
            url=service_url, data=request_data, headers=self._get_request_headers()
        )
        if response.status_code == 204:
            return {}
        else:
            self._handle_response_errors(
                service_url, response=response, request_data=request_data
            )

    def delete_user(self, user_id: str, reassign_descriptor: dict, version="v5"):
        """
        Delete an user from the api user's organization.

        :param user_id: str
        :param version: string for api version
        :param reassign_descriptor:
            {
                "UserId": "string",
                "ReassignDrafts": true,
                "ReassignTemplates": true,
                "ReassignClipboard": true,
                "ReassignAddressBook": true
            }
        :return:
        """
        service_url = self.api_uri + version + f"/user/{user_id}"
        request_data = {"reassignDescriptor": reassign_descriptor}
        requests.delete(
            url=service_url, data=request_data, headers=self._get_request_headers()
        )
        raise NotImplementedError()

    def update_user(self, user_id: str, user_update_description, version="v5"):
        """
        Update settings of a particular user.

        :param user_id: string
        :param user_update_description:
        :param version: string for api version
        :return User:
        """
        service_url = self.api_uri + version + f"/user/{user_id}"
        request_data = {"userUpdateDescription": user_update_description}
        requests.patch(
            url=service_url, data=request_data, headers=self._get_request_headers()
        )
        raise NotImplementedError()

    def find_users(self, find_user_descriptor: str, version="v5"):
        """
        Find users corresponding to the given user descriptor.

        :param find_user_descriptor:
            {
                "Roles": [
                    "string"
                ],
                "IsAutomatedDelegatedUser": true
            }
        :param version: string for api version
        :return List of Users:
            {
                "Entries": [{
                    "Id": "string",
                    "Email": "string",
                    "FirstName": "string",
                    "LastName": "string",
                    "UserName": "string",
                    "Sid": "string",
                    "IsEnabled": true,
                    "Authentications": [{
                        "DiscriminatorType": "string"
                    }],
                    "Roles": [
                        "string"
                    ]
                }]
            }
        """
        service_url = self.api_uri + version + "/user/find"
        request_data = {"findUsersDescriptor": find_user_descriptor}
        response = requests.post(
            url=service_url, data=request_data, headers=self._get_request_headers()
        )
        if response.status_code == 200:
            logger.debug(
                f"Response from service_url : {service_url}: {response.json()}"
            )
            response_data = response.json()
            return models_v5.ExtendedFindUsersResult(**response_data)
        else:
            self._handle_response_errors(
                service_url, response=response, request_data=request_data
            )

    def replace_user_signature_image(self, user_id: str, file, version="v5"):
        """
        Replace the signature image.

        :param user_id: string
        :param file: File
        :param version: string for api version
        :return:
        """
        service_url = self.api_uri + version + f"/user/{user_id}/uploadSignatureImage"
        request_data = {"File": open(file.path, "rb").read()}
        requests.post(
            url=service_url, data=request_data, headers=self._get_request_headers()
        )
        raise NotImplementedError()

    def get_me_info(self, version="v5"):
        """
        Return data about yourself.

        :param version: string for api version
        :return User
        """
        service_url = self.api_uri + version + "/user/me"
        request_data = {}
        response = requests.get(
            url=service_url, data=request_data, headers=self._get_request_headers()
        )

        if response.status_code == 200:
            logger.debug(
                f"Response from service_url : {service_url}: {response.json()}"
            )
            response_data = response.json()
            return models_v5.MeResult(**response_data)
        else:
            self._handle_response_errors(
                service_url, response=response, request_data=request_data
            )
