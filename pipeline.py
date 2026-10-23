import json

from detector import detect_sensitive_info
from masker import mask_sensitive_info, validate_request_id
from mock_provider import mock_provider, MockProviderError
from restorer import restore_sensitive_info
from validator import ValidationError

# Error response helper

def create_error_response(
    request_id,
    code: str,
    message: str
) -> dict:
    """
    Creates a controlled JSON-style error response.

    Example:

    {
        "status": "error",
        "request_id": "r1",
        "error": {
            "code": "INVALID_REQUEST",
            "message": "..."
        }
    }
    """

    return {
        "status": "error",
        "request_id": request_id,
        "error": {
            "code": code,
            "message": message
        }
    }

# Request validation

def validate_request(request_data: dict) -> tuple[str, str]:
    """
    Validates the JSON request fields.

    Required format:

    {
        "request_id": "r1",
        "text": "resume text"
    }

    Returns:
        request_id, text

    Raises:
        ValueError if the request is invalid.
    """

    if not isinstance(request_data, dict):
        raise ValueError(
            "Request must be a JSON object."
        )

    # -----------------------------------------------------
    # Check request_id
    # -----------------------------------------------------

    if "request_id" not in request_data:
        raise ValueError(
            "Required field 'request_id' is missing."
        )

    request_id = request_data["request_id"]

    if not isinstance(request_id, str):
        raise ValueError(
            "'request_id' must be a string."
        )

    # Reuse the validation rule from masker.py
    validate_request_id(request_id)

    # -----------------------------------------------------
    # Check text
    # -----------------------------------------------------

    if "text" not in request_data:
        raise ValueError(
            "Required field 'text' is missing."
        )

    text = request_data["text"]

    if not isinstance(text, str):
        raise ValueError(
            "'text' must be a string."
        )

    if not text.strip():
        raise ValueError(
            "'text' must not be empty."
        )

    # -----------------------------------------------------
    # Reserved placeholder syntax
    # -----------------------------------------------------

    # Users are not allowed to place gateway placeholder
    # syntax directly into their original input.
    if "[[" in text or "]]" in text:
        raise ValidationError(
            code="RESERVED_PLACEHOLDER_IN_INPUT",
            message=(
                "Input contains syntax reserved for "
                "gateway-generated placeholders."
            )
        )

    return request_id, text

# Process one request

def process_request(
    request_data: dict,
    provider_mode: str = "normal"
) -> dict:
    """
    Runs one complete privacy-gateway request.

    Pipeline:

    Input
        ->
    Detection
        ->
    Masking
        ->
    Offline Mock Provider
        ->
    Validation
        ->
    Restoration
        ->
    Output

    The placeholder mapping remains local and is never
    included in the returned success response.
    """

    request_id = None

    try:

        # -------------------------------------------------
        # 1. Validate input
        # -------------------------------------------------

        if isinstance(request_data, dict):
            request_id = request_data.get(
                "request_id"
            )

        request_id, text = validate_request(
            request_data
        )

        # -------------------------------------------------
        # 2. Detect sensitive information
        # -------------------------------------------------

        detections = detect_sensitive_info(
            text
        )

        # -------------------------------------------------
        # 3. Mask sensitive information
        # -------------------------------------------------

        masking_result = mask_sensitive_info(
            text=text,
            detections=detections,
            request_id=request_id
        )

        masked_text = (
            masking_result.masked_text
        )

        placeholder_map = (
            masking_result.placeholder_to_value
        )

        # -------------------------------------------------
        # 4. Send only masked text to mock provider
        # -------------------------------------------------

        provider_response = mock_provider(
            masked_text=masked_text,
            mode=provider_mode
        )

        # -------------------------------------------------
        # 5. Validate and restore locally
        # -------------------------------------------------
        #
        # restore_sensitive_info() calls the validator
        # before performing any restoration.
        #
        # If validation fails, no sensitive values are
        # restored.
        # -------------------------------------------------

        final_output = restore_sensitive_info(
            response_text=provider_response,
            placeholder_to_value=placeholder_map
        )

        # -------------------------------------------------
        # 6. Successful JSON response
        # -------------------------------------------------

        return {
            "status": "ok",
            "request_id": request_id,
            "masked_text": masked_text,
            "provider_response": provider_response,
            "output": final_output
        }

    # Controlled validation errors

    except ValidationError as error:

        return create_error_response(
            request_id=request_id,
            code=error.code,
            message=error.message
        )

    # Invalid request errors

    except ValueError as error:

        return create_error_response(
            request_id=request_id,
            code="INVALID_REQUEST",
            message=str(error)
        )

    # Mock provider errors

    except MockProviderError as error:

        return create_error_response(
            request_id=request_id,
            code="PROVIDER_ERROR",
            message=str(error)
        )

# Process JSON text

def process_json_request(
    json_text: str,
    provider_mode: str = "normal"
) -> dict:
    """
    Accepts a JSON string and processes it through the
    privacy gateway.

    Handles invalid JSON separately from invalid request
    fields.
    """

    try:

        request_data = json.loads(
            json_text
        )

    except json.JSONDecodeError:

        return create_error_response(
            request_id=None,
            code="INVALID_JSON",
            message=(
                "Input could not be parsed as valid JSON."
            )
        )

    return process_request(
        request_data=request_data,
        provider_mode=provider_mode
    )

# Optional standalone test

if __name__ == "__main__":

    # -----------------------------------------------------
    # Normal request
    # -----------------------------------------------------

    sample_request = {
        "request_id": "r1",
        "text": (
            "Jane Smith lives at "
            "123 Example Street, Sampletown, GA 30000. "
            "Jane Smith has 3 years of Python experience. "
            "Contact Jane Smith at "
            "jane.smith@example.com or 478-555-1234."
        )
    }

    print("INPUT")
    print("-----")

    print(
        json.dumps(
            sample_request,
            indent=4
        )
    )

    result = process_request(
        sample_request
    )

    print("\nOUTPUT")
    print("------")

    print(
        json.dumps(
            result,
            indent=4
        )
    )