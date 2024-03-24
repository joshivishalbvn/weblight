# -*- coding: utf-8 -*-

from rest_framework import status
from rest_framework.exceptions import ErrorDetail
from rest_framework.renderers import JSONRenderer


def get_status(code):
    """Get the human readable SNAKE_CASE version of a status code."""
    for name, val in status.__dict__.items():
        if not callable(val) and code == val:
            return name.replace("HTTP_%s_" % code, "")
    return "UNKNOWN"


def get_error_message(error_dict):
    """Get error message"""
    response = error_dict[next(iter(error_dict))]
    if isinstance(response, dict):
        response = get_error_message(response)
    elif isinstance(response, list):
        response_message = response[0]
        if isinstance(response_message, dict):
            response = get_error_message(response_message)
        else:
            response = response[0]
    return response


class BaseJSONRenderer(JSONRenderer):
    def render(self, data, accepted_media_type=None, renderer_context=None):
        """
        Modify API response format.
        Example success:
        {
            "code": 200,
            "status": "OK",
            "data": {
                "username": "username"
            }
        }

        Example error:
        {
            "code": 404,
            "status": "NOT_FOUND",
            "error" : [
                {
                    "source": "detail",
                    "detail": "Invalid"
                }
            ]
        }
        """
        response = renderer_context["response"]

        # Modify the response into a cohesive response format
        modified_data = {}
        modified_data["code"] = response.status_code
        modified_data["status"] = get_status(response.status_code)
        if status.is_client_error(response.status_code) or status.is_server_error(response.status_code):
            modified_data["errors"] = self.get_clean_errors(data)
            # if isinstance(data, list) and data:
            #     if isinstance(data[0], dict):
            #         message = (get_error_message(data),)
            #     elif isinstance(data[0], str):
            #         message = data[0]
            # if isinstance(data, dict):
            #     message = get_error_message(data)
            # modified_data["error"] = message
        else:
            modified_data["data"] = data

        return super().render(modified_data, accepted_media_type, renderer_context)

    def get_api_error(self, source, detail, code):
        """
        Return an error object for use in the errors key of the response.
        http://jsonapi.org/examples/#error-objects-multiple-errors
        """
        error_obj = {}
        error_obj["source"] = source
        error_obj["detail"] = detail
        if code:
            error_obj["code"] = code
        return error_obj

    def get_clean_errors(self, data):
        """DRF will send errors through as data so let's rework it."""
        errors = []
        if isinstance(data, dict):
            for k, v in data.items():  # noqa
                ed = ErrorDetail(v)
                if isinstance(v, list):
                    try:
                        v = ", ".join(v)
                    except Exception:
                        pass
            errors.append(self.get_api_error(source=k, detail=v, code=ed.code))
        else:
            for v in data:
                ed = ErrorDetail(v)
                if isinstance(v, list):
                    try:
                        v = ", ".join(v)
                    except Exception:
                        pass
            errors.append(self.get_api_error(source="non_field_errors", detail=v, code=ed.code))
        return errors


class SimpleRenderer(JSONRenderer):
    def render(self, data, accepted_media_type=None, renderer_context=None):
        """
        Modify API response format.
        Example success:
        {
            "code": 200,
            "status": "OK",
            "data": {
                "username": "username"
            }
        }

        Example error:
        {
            "code": 404,
            "status": "NOT_FOUND",
            "error" : [
                {
                    "source": "detail",
                    "detail": "Invalid"
                }
            ]
        }
        """
        response = renderer_context["response"]  # noqa

        # Modify the response into a cohesive response format

        return super().render(data, accepted_media_type, renderer_context)
