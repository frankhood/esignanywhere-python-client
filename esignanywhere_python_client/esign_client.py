import inspect
import logging
from io import BufferedReader
from typing import Any

import requests

from . import exceptions
from .models import models_v5, models_v6

logger = logging.getLogger(__name__)


class ESignAnyWhereClient:
    """Base class client for eSignAnyWhere V6."""

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

    def _handle_response_errors(
        self,
        service_url: str,
        method_name: str,
        request_data: dict[str, Any],
        response: requests.Response,
    ):
        if response.status_code == 401:
            raise exceptions.ESawUnauthorizedRequest(
                status_code=response.status_code,
                method_name=method_name,
                service_url=service_url,
                request_data=request_data,
                response=response,
            )
        else:
            raise exceptions.ESawErrorResponse(
                status_code=response.status_code,
                method_name=method_name,
                service_url=service_url,
                request_data=request_data,
                response=response,
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
                service_url=service_url,
                method_name=(
                    inspect.currentframe().f_code.co_name  # type: ignore
                    if inspect.currentframe() is not None
                    else ""
                ),
                request_data={},
                response=response,
            )

    def upload_file(
        self,
        resource_to_upload: str | BufferedReader,
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
                    service_url=service_url,
                    method_name=(
                        inspect.currentframe().f_code.co_name  # type: ignore
                        if inspect.currentframe() is not None
                        else ""
                    ),
                    response=response,
                    request_data=request_data,
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

        request_data = envelope_data.model_dump_json()
        response = requests.post(
            url=service_url, data=request_data, headers=self._get_request_headers()
        )
        logger.debug(f"create_and_send_envelope Request : {request_data}")
        if response.status_code == 200:
            logger.info(f"Response from service_url : {service_url}: {response.json()}")
            if "EnvelopeId" not in response.json().keys():
                raise exceptions.ESawUnexpectedResponse(
                    method_name=(
                        inspect.currentframe().f_code.co_name  # type: ignore
                        if inspect.currentframe()
                        else ""
                    ),
                    status_code=response.status_code,
                    service_url=service_url,
                    request_data=request_data,
                    response=response,
                )
            return models_v6.EnvelopeSendResponse(**response.json())
        else:
            self._handle_response_errors(
                service_url=service_url,
                method_name=(
                    inspect.currentframe().f_code.co_name  # type: ignore
                    if inspect.currentframe() is not None
                    else ""
                ),
                response=response,
                request_data=request_data,
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

        request_data = envelope_data.model_dump_json()
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
                service_url=service_url,
                method_name=(
                    inspect.currentframe().f_code.co_name  # type: ignore
                    if inspect.currentframe() is not None
                    else ""
                ),
                response=response,
                request_data=request_data,
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
                service_url=service_url,
                method_name=(
                    inspect.currentframe().f_code.co_name  # type: ignore
                    if inspect.currentframe() is not None
                    else ""
                ),
                response=response,
                request_data=request_data,
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
                service_url=service_url,
                method_name=(
                    inspect.currentframe().f_code.co_name  # type: ignore
                    if inspect.currentframe() is not None
                    else ""
                ),
                response=response,
                request_data=request_data,
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
                service_url=service_url,
                method_name=(
                    inspect.currentframe().f_code.co_name  # type: ignore
                    if inspect.currentframe() is not None
                    else ""
                ),
                request_data=request_data,
                response=response,
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
                service_url=service_url,
                method_name=(
                    inspect.currentframe().f_code.co_name  # type: ignore
                    if inspect.currentframe() is not None
                    else ""
                ),
                request_data=request_data,
                response=response,
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
                service_url=service_url,
                method_name=(
                    inspect.currentframe().f_code.co_name  # type: ignore
                    if inspect.currentframe() is not None
                    else ""
                ),
                request_data=request_data,
                response=response,
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
                service_url=service_url,
                method_name=(
                    inspect.currentframe().f_code.co_name  # type: ignore
                    if inspect.currentframe() is not None
                    else ""
                ),
                request_data=request_data,
                response=response,
            )

    def cancel_envelope(
        self,
        cancel_request: models_v6.EnvelopeCancelRequest,
        version="v6",
    ):
        """
        Cancel an envelope with the given envelope id.

        :param cancel_request: models_v6.EnvelopeCancelRequest
        :param version: string for api version
        :return:
        """
        if version == "v6":
            service_url = f"{self.api_uri}v6/envelope/cancel"
        else:
            raise exceptions.ESawInvalidVersionError(
                version=version, supported_versions=["v6"]
            )

        request_data = cancel_request.model_dump_json()
        response = requests.post(
            url=service_url, data=request_data, headers=self._get_request_headers()
        )
        if response.status_code == 200:
            logger.info(
                f"Response from service_url : {service_url} -> {response.status_code}"
            )
            return {}
        else:
            self._handle_response_errors(
                service_url=service_url,
                method_name=(
                    inspect.currentframe().f_code.co_name  # type: ignore
                    if inspect.currentframe() is not None
                    else ""
                ),
                request_data=request_data,
                response=response,
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

        request_data = models_v6.EnvelopeDeleteRequest(
            EnvelopeId=envelope_id
        ).model_dump_json()
        response = requests.post(
            url=service_url, data=request_data, headers=self._get_request_headers()
        )
        if response.status_code == 200:
            logger.debug(
                f"Response from service_url : {service_url} -> {response.status_code}"
            )
        else:
            self._handle_response_errors(
                service_url=service_url,
                method_name=(
                    inspect.currentframe().f_code.co_name  # type: ignore
                    if inspect.currentframe() is not None
                    else ""
                ),
                request_data=request_data,
                response=response,
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
            logger.info(f"Response from service_url : {service_url}")
            return response.content
        else:
            self._handle_response_errors(
                service_url=service_url,
                method_name=(
                    inspect.currentframe().f_code.co_name  # type: ignore
                    if inspect.currentframe() is not None
                    else ""
                ),
                request_data=request_data,
                response=response,
            )

    # ======================================
    #  PAY ATTENTION!!! Below methods are draft and maybe not implemented
    # ======================================
    def create_draft(
        self,
        draft_create_model: models_v6.DraftCreateRequest,
        version="v6",
    ):
        """
        Create a draft with the given information.

        :param draft_create_model: models_v6.DraftCreateRequest
        :param version: string for api version
        :return models_v6.DraftCreateResponse
        """
        if version == "v6":
            service_url = f"{self.api_uri}v6/draft/create"
        else:
            raise exceptions.ESawInvalidVersionError(
                version=version, supported_versions=["v6"]
            )

        request_data = draft_create_model.model_dump_json()
        response = requests.post(
            url=service_url, data=request_data, headers=self._get_request_headers()
        )
        if response.status_code == 200:
            logger.debug(
                f"Response from service_url : {service_url}: {response.json()}"
            )
            response_data = response.json()
            return models_v6.DraftCreateResponse(**response_data)
        else:
            self._handle_response_errors(
                service_url=service_url,
                method_name=(
                    inspect.currentframe().f_code.co_name  # type: ignore
                    if inspect.currentframe() is not None
                    else ""
                ),
                request_data=request_data,
                response=response,
            )

    def create_draft_from_template(
        self,
        create_from_template_model: models_v6.TemplateCreateDraftRequest,
        version="v6",
    ):
        """
        Create a draft from an existing template.

        :param create_from_template_model: models_v6.TemplateCreateDraftRequest
        :param version: string for api version
        :return models_v6.TemplateCreateDraftResponse
        """
        if version == "v6":
            service_url = f"{self.api_uri}v6/template/createdraft"
        else:
            raise exceptions.ESawInvalidVersionError(
                version=version, supported_versions=["v6"]
            )

        request_data = create_from_template_model.model_dump_json()
        response = requests.post(
            url=service_url, data=request_data, headers=self._get_request_headers()
        )
        if response.status_code == 200:
            logger.debug(
                f"Response from service_url : {service_url}: {response.json()}"
            )
            response_data = response.json()
            return models_v6.TemplateCreateDraftResponse(**response_data)
        else:
            self._handle_response_errors(
                service_url=service_url,
                method_name=(
                    inspect.currentframe().f_code.co_name  # type: ignore
                    if inspect.currentframe() is not None
                    else ""
                ),
                request_data=request_data,
                response=response,
            )

    def find_envelope(self, descriptor: models_v6.EnvelopeFindRequest, version="v6"):
        """
        Return the found envelopes for the given descriptor.

        :param descriptor: models_v6.EnvelopeFindRequest
        :param version: string for api version
        :return models_v6.EnvelopeFindResponse
        """
        if version == "v6":
            service_url = f"{self.api_uri}v6/envelope/find"
        else:
            raise exceptions.ESawInvalidVersionError(
                version=version, supported_versions=["v6"]
            )

        request_data = descriptor.model_dump_json()
        response = requests.post(
            url=service_url, data=request_data, headers=self._get_request_headers()
        )
        if response.status_code == 200:
            logger.debug(
                f"Response from service_url : {service_url}: {response.json()}"
            )
            response_data = response.json()
            return models_v6.EnvelopeFindResponse(**response_data)
        else:
            self._handle_response_errors(
                service_url=service_url,
                method_name=(
                    inspect.currentframe().f_code.co_name  # type: ignore
                    if inspect.currentframe() is not None
                    else ""
                ),
                request_data=request_data,
                response=response,
            )

    def prepare_file(self, prepare_model: models_v6.FilePrepareRequest, version="v6"):
        """
        Parse the provided files for markup fields and sig string and returns the containing elements.

        :param prepare_model: models_v6.FilePrepareRequest
        :param version: string for api version
        :return models_v6.FilePrepareResponse
        """
        if version == "v6":
            service_url = f"{self.api_uri}v6/file/prepare"
        else:
            raise exceptions.ESawInvalidVersionError(
                version=version, supported_versions=["v6"]
            )

        request_data = prepare_model.model_dump_json()
        response = requests.post(
            url=service_url, data=request_data, headers=self._get_request_headers()
        )
        if response.status_code == 200:
            logger.debug(
                f"Response from service_url : {service_url}: {response.json()}"
            )
            response_data = response.json()
            return models_v6.FilePrepareResponse(**response_data)
        else:
            self._handle_response_errors(
                service_url=service_url,
                method_name=(
                    inspect.currentframe().f_code.co_name  # type: ignore
                    if inspect.currentframe() is not None
                    else ""
                ),
                request_data=request_data,
                response=response,
            )

    def restart_envelope_expiration_days(
        self,
        restart_expired_request: models_v6.EnvelopeRestartExpiredRequest,
        version="v6",
    ):
        """
        Restart the envelope with the given id and sets the expiration days.

        :param restart_expired_request: models_v6.EnvelopeRestartExpiredRequest
        :param version: string for api version
        :return:
        """
        if version == "v6":
            service_url = f"{self.api_uri}v6/envelope/restartexpired"
        else:
            raise exceptions.ESawInvalidVersionError(
                version=version, supported_versions=["v6"]
            )

        request_data = restart_expired_request.model_dump_json()
        response = requests.post(
            url=service_url, data=request_data, headers=self._get_request_headers()
        )
        if response.status_code == 200:
            logger.debug(
                f"Response from service_url : {service_url} -> {response.status_code}"
            )
            return {}
        else:
            self._handle_response_errors(
                service_url=service_url,
                method_name=(
                    inspect.currentframe().f_code.co_name  # type: ignore
                    if inspect.currentframe() is not None
                    else ""
                ),
                request_data=request_data,
                response=response,
            )

    def send_draft(
        self,
        send_from_template_model: models_v6.DraftSendRequest,
        version="v6",
    ):
        """
        Create an envelope from a existing template and directly sends it.

        :param send_from_template_model: models_v6.DraftSendRequest
        :param version: string for api version
        :return models_v6.DraftSendResponse
        """
        if version == "v6":
            service_url = f"{self.api_uri}v6/draft/send"
        else:
            raise exceptions.ESawInvalidVersionError(
                version=version, supported_versions=["v6"]
            )

        request_data = send_from_template_model.model_dump_json()
        response = requests.post(
            url=service_url, data=request_data, headers=self._get_request_headers()
        )
        if response.status_code == 200:
            logger.debug(
                f"Response from service_url : {service_url}: {response.json()}"
            )
            response_data = response.json()
            return models_v6.DraftSendResponse(**response_data)
        else:
            self._handle_response_errors(
                service_url=service_url,
                method_name=(
                    inspect.currentframe().f_code.co_name  # type: ignore
                    if inspect.currentframe() is not None
                    else ""
                ),
                request_data=request_data,
                response=response,
            )

    def remind_envelope(
        self,
        remind_request: models_v6.EnvelopeRemindRequest,
        version="v6",
    ):
        """
        Send a reminder email to the recipient which action is awaited for the provided envelope.

        :param remind_request: models_v6
        :param version: string for api version
        :return models_v6.EnvelopeRemindResponse
        """
        if version == "v6":
            service_url = f"{self.api_uri}v6/envelope/remind"
        else:
            raise exceptions.ESawInvalidVersionError(
                version=version, supported_versions=["v6"]
            )

        request_data = remind_request.model_dump_json()
        response = requests.post(
            url=service_url, data=request_data, headers=self._get_request_headers()
        )
        if response.status_code == 200:
            logger.debug(
                f"Response from service_url : {service_url}: {response.json()}"
            )
            response_data = response.json()
            return models_v6.EnvelopeRemindResponse(**response_data)
        else:
            self._handle_response_errors(
                service_url=service_url,
                method_name=(
                    inspect.currentframe().f_code.co_name  # type: ignore
                    if inspect.currentframe() is not None
                    else ""
                ),
                request_data=request_data,
                response=response,
            )

    def unlock_envelope(
        self, unlock_request: models_v6.EnvelopeUnlockRequest, version="v6"
    ):
        """
        Unlock an envelope with the given id.

        :param unlock_request: models_v6.EnvelopeUnlockRequest
        :param version: string for api version
        :return:
        """
        if version == "v6":
            service_url = f"{self.api_uri}v6/envelope/unlock"
        else:
            raise exceptions.ESawInvalidVersionError(
                version=version, supported_versions=["v6"]
            )

        request_data = unlock_request.json()
        response = requests.get(
            url=service_url, data=request_data, headers=self._get_request_headers()
        )
        if response.status_code == 200:
            logger.debug(
                f"Response from service_url : {service_url} -> {response.status_code}"
            )
            return {}
        else:
            self._handle_response_errors(
                service_url=service_url,
                method_name=(
                    inspect.currentframe().f_code.co_name  # type: ignore
                    if inspect.currentframe() is not None
                    else ""
                ),
                request_data=request_data,
                response=response,
            )

    def get_license(self, version="v6"):
        """
        Return the License state. Only for usermanager.

        :param version: string for api version
        :return models_v6.LicenseGetResponse
        """
        if version == "v6":
            service_url = f"{self.api_uri}v6/organization/license"
        else:
            raise exceptions.ESawInvalidVersionError(
                version=version, supported_versions=["v6"]
            )

        request_data = {}
        response = requests.get(
            url=service_url, data=request_data, headers=self._get_request_headers()
        )
        if response.status_code == 200:
            logger.debug(
                f"Response from service_url : {service_url}: {response.json()}"
            )
            response_data = response.json()
            return models_v6.LicenseGetResponse(**response_data)
        else:
            self._handle_response_errors(
                service_url=service_url,
                method_name=(
                    inspect.currentframe().f_code.co_name  # type: ignore
                    if inspect.currentframe() is not None
                    else ""
                ),
                request_data=request_data,
                response=response,
            )

    def remove_activity_from_envelope(
        self,
        activity_delete_request: models_v6.EnvelopeActivityDeleteRequest,
        version="v6",
    ):
        """
        Delete a recipient from an envelope.

        :param activity_delete_request: models_v6.EnvelopeActivityDeleteRequest
        :param version: string for api version
        :return:
        """
        if version == "v6":
            service_url = f"{self.api_uri}v6/envelope/activity/delete"
        else:
            raise exceptions.ESawInvalidVersionError(
                version=version, supported_versions=["v6"]
            )

        request_data = activity_delete_request.model_dump_json()
        response = requests.post(
            url=service_url, data=request_data, headers=self._get_request_headers()
        )
        if response.status_code == 200:
            logger.debug(
                f"Response from service_url : {service_url} -> {response.status_code}"
            )
            return {}
        else:
            self._handle_response_errors(
                service_url=service_url,
                method_name=(
                    inspect.currentframe().f_code.co_name  # type: ignore
                    if inspect.currentframe() is not None
                    else ""
                ),
                request_data=request_data,
                response=response,
            )

    def replace_activity_from_envelope(
        self,
        activity_replace_request: models_v6.EnvelopeActivityReplaceRequest,
        version="v6",
    ):
        """
        Replace a recipient in an envelope.

        :param activity_replace_request: models_v6.EnvelopeActivityReplaceRequest
        :param version: string for api version
        :return
        """
        if version == "v6":
            service_url = f"{self.api_uri}v6/envelope/activity/replace"
        else:
            raise exceptions.ESawInvalidVersionError(
                version=version, supported_versions=["v6"]
            )

        request_data = activity_replace_request.model_dump_json()
        response = requests.post(
            url=service_url, data=request_data, headers=self._get_request_headers()
        )
        if response.status_code == 200:
            logger.debug(
                f"Response from service_url : {service_url} -> {response.status_code}"
            )
            return {}
        else:
            self._handle_response_errors(
                service_url=service_url,
                method_name=(
                    inspect.currentframe().f_code.co_name  # type: ignore
                    if inspect.currentframe() is not None
                    else ""
                ),
                request_data=request_data,
                response=response,
            )

    def dispose_uploaded_file(
        self,
        delete_request: models_v6.FileDeleteRequest,
        version="v6",
    ):
        """
        Dipose a file which was uploaded beforehand.

        :param delete_request: models_v6.FileDeleteRequest
        :param version: string for api version
        :return:
        """
        if version == "v6":
            service_url = f"{self.api_uri}v6/file/delete"
        else:
            raise exceptions.ESawInvalidVersionError(
                version=version, supported_versions=["v6"]
            )

        request_data = delete_request.model_dump_json()
        response = requests.post(
            url=service_url, data=request_data, headers=self._get_request_headers()
        )
        if response.status_code == 200:
            logger.debug(
                f"Response from service_url : {service_url} -> {response.status_code}"
            )
            return {}
        else:
            self._handle_response_errors(
                service_url=service_url,
                method_name=(
                    inspect.currentframe().f_code.co_name  # type: ignore
                    if inspect.currentframe() is not None
                    else ""
                ),
                request_data=request_data,
                response=response,
            )

    def get_teams(self, version="v6"):
        """
        Return the teams set for the organization of the api user.

        :param version: string for api version
        :return models_v6.TeamGetAllResponse
        """
        if version == "v6":
            service_url = f"{self.api_uri}v6/organization/team"
        else:
            raise exceptions.ESawInvalidVersionError(
                version=version, supported_versions=["v6"]
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
            return models_v6.TeamGetAllResponse(**response_data)
        else:
            self._handle_response_errors(
                service_url=service_url,
                method_name=(
                    inspect.currentframe().f_code.co_name  # type: ignore
                    if inspect.currentframe() is not None
                    else ""
                ),
                request_data=request_data,
                response=response,
            )

    def replace_teams(self, teams: models_v6.TeamReplaceRequest, version="v6"):
        """
        Replace all teams with the provided teams.

        :param teams: models_v6.TeamReplaceRequest
        :param version: string for api version
        :return:
        """
        if version == "v6":
            service_url = f"{self.api_uri}v6/organization/team/replace"
        else:
            raise exceptions.ESawInvalidVersionError(
                version=version, supported_versions=["v6"]
            )

        request_data = teams.model_dump_json()
        response = requests.post(
            url=service_url, data=request_data, headers=self._get_request_headers()
        )
        if response.status_code == 200:
            return {}
        else:
            self._handle_response_errors(
                service_url=service_url,
                method_name=(
                    inspect.currentframe().f_code.co_name  # type: ignore
                    if inspect.currentframe() is not None
                    else ""
                ),
                request_data=request_data,
                response=response,
            )
