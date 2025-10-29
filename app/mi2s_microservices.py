"""
Module for integrating with the Mi2S Microservice Hub.

This module provides a decorator factory, `mi2s_microservice`, which wraps a function
so that it sends a sentence to the Mi2S Microservice Hub for processing. The decorator
handles the network communication, error handling, and returns a `KeyResponse` object
indicating the result of the operation.
"""

from http import HTTPStatus
from functools import wraps
from typing import Callable
import os

from keydnn.utilities import KeyResponse
import requests


def mi2s_microservice(api_token: str) -> Callable:
    """
    Decorator factory for integrating with the Mi2S Microservice Hub.

    This function returns a decorator that, when applied to a target function, modifies it
    to perform a POST request to the Mi2S Microservice Hub. The decorated function is expected
    to process the JSON response returned from the microservice.

    Args:
        api_token (str): The API token required for authenticating requests to the Mi2S Microservice Hub.

    Returns:
        Callable: A decorator that wraps the target function with Mi2S Microservice Hub integration.
    """
    assert isinstance(api_token, str)

    def _mi2s_microservice(function: Callable) -> Callable:
        """
        Decorator that wraps a function to integrate with the Mi2S Microservice Hub.

        The wrapped function will send a POST request with the provided sentence to the Mi2S
        Microservice Hub. Upon receiving the response, it will check the HTTP status code and,
        if successful, pass the JSON response to the original function for processing. In case of
        errors, a failure message is returned via a KeyResponse.

        Args:
            function (Callable): The function to be wrapped. This function should expect a JSON
                                 response from the microservice as its input.

        Returns:
            Callable: The wrapped function that performs the microservice call and processes the response.
        """
        assert callable(function)

        @wraps(function)
        def call_mi2s_microservice(sentence: str) -> KeyResponse:
            """
            Sends a sentence to the Mi2S Microservice Hub and processes the returned response.

            This function sends a POST request to the Mi2S Microservice Hub with the given sentence
            and API token. It evaluates the response, and if successful, calls the original function
            with the JSON data. In the event of an HTTP error, timeout, or any other exception, it
            returns a KeyResponse indicating the failure.

            Args:
                sentence (str): The input sentence to be processed by the Mi2S Microservice Hub.

            Returns:
                KeyResponse: An object containing a success flag and either the processed result
                             or an error message.
            """
            assert isinstance(sentence, str)
            try:
                response = requests.post(
                    os.environ["MICROSERVICES_HUB_URI"],
                    json={"data": sentence, "api-key": api_token},
                    timeout=int(os.environ["MICROSERVICES_HUB_TIMEOUT"]),
                )
                if response.status_code != HTTPStatus.OK:
                    return KeyResponse(
                        False,
                        "Request to Mi2S Microservice Hub resulted in HTTP status code: {}".format(
                            response.status_code
                        ),
                    )
                return KeyResponse(True, function(response.json()))
            except KeyboardInterrupt:
                raise
            except requests.exceptions.Timeout:
                return KeyResponse(
                    False, "Connection to the Mi2S Microservice Hub timed out."
                )
            except Exception:
                return KeyResponse(
                    False, "An unexpected error occurred while processing your request."
                )

        return call_mi2s_microservice

    return _mi2s_microservice
