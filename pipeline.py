import json

from detector import detect_sensitive_info
from mapping import RequestMapping
from masker import mask_sensitive_info
from mock_provider import mock_provider, MockProviderError
from policy import resolve_policies, PolicyError
from restorer import restore_sensitive_info
from validator import ValidationError


# =========================================================
# Error response helper
# =========================================================

def create_error_response(
    request_id,
    code: str,
    message: str
) -> dict:
    """
    Creates a controlled JSON-style error response.
    """

    return {
        "status": "error",
        "request_id": request_id,
        "error": {
            "code": code,
            "message": message
        }
    }


# =========================================================
# Request validation
# =========================================================

def validate_request(
    request_data: dict
) -> tuple[str, str, dict | None]:
    """
    Validates one request.

    Required fields:
    - request_id
    - text

    Optional field:
    - policies

    Example:

    {
        "request_id": "r1",
        "text": "Jane Smith has Python experience.",
        "policies": {
            "NAME": "MASK",
            "EMAIL": "REMOVE"
        }
    }
    """

    if not isinstance(
        request_data,
        dict
    ):
        raise ValueError(
            "Request must be a JSON object."
        )

    # -----------------------------------------------------
    # request_id
    # -----------------------------------------------------

    if "request_id" not in request_data:
        raise ValueError(
            "Required field 'request_id' is missing."
        )

    request_id = request_data[
        "request_id"
    ]

    if not isinstance(
        request_id,
        str
    ):
        raise ValueError(
            "'request_id' must be a string."
        )

    # RequestMapping performs the formal request ID check.
    # We create a temporary validation object here only to
    # verify the format.
    validation_mapping = RequestMapping(
        request_id
    )

    validation_mapping.clear()

    # -----------------------------------------------------
    # text
    # -----------------------------------------------------

    if "text" not in request_data:
        raise ValueError(
            "Required field 'text' is missing."
        )

    text = request_data[
        "text"
    ]

    if not isinstance(
        text,
        str
    ):
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

    if (
        "[[" in text
        or "]]" in text
    ):
        raise ValidationError(
            code="RESERVED_PLACEHOLDER_IN_INPUT",
            message=(
                "Input contains syntax reserved for "
                "gateway-generated placeholders."
            )
        )

    # -----------------------------------------------------
    # Optional policies
    # -----------------------------------------------------

    policies = request_data.get(
        "policies"
    )

    return (
        request_id,
        text,
        policies
    )


# =========================================================
# Process one request
# =========================================================

def process_request(
    request_data: dict,
    provider_mode: str = "normal"
) -> dict:
    """
    Runs one complete M3 privacy-gateway request.

    Pipeline:

    Input
        ->
    Detection
        ->
    Policy
        ->
    Mapping / Masking
        ->
    Offline Mock Provider
        ->
    Validation
        ->
    Restoration
        ->
    Mapping Cleanup
        ->
    Output
    """

    request_id = None
    request_mapping = None

    try:

        # -------------------------------------------------
        # 1. Validate request
        # -------------------------------------------------

        if isinstance(
            request_data,
            dict
        ):
            request_id = request_data.get(
                "request_id"
            )

        (
            request_id,
            text,
            supplied_policies
        ) = validate_request(
            request_data
        )

        # -------------------------------------------------
        # 2. Resolve policies
        # -------------------------------------------------
        #
        # Missing categories automatically default to MASK.
        # -------------------------------------------------

        resolved_policies = resolve_policies(
            supplied_policies
        )

        # -------------------------------------------------
        # 3. Create request-local mapping
        # -------------------------------------------------

        request_mapping = RequestMapping(
            request_id
        )

        # -------------------------------------------------
        # 4. Detect sensitive information
        # -------------------------------------------------

        detections = detect_sensitive_info(
            text
        )

        # -------------------------------------------------
        # 5. Apply MASK / REMOVE policies
        # -------------------------------------------------

        masking_result = mask_sensitive_info(
            text=text,
            detections=detections,
            request_mapping=request_mapping,
            resolved_policies=resolved_policies
        )

        masked_text = (
            masking_result.masked_text
        )

        # -------------------------------------------------
        # 6. Send only protected text to provider
        # -------------------------------------------------

        provider_response = mock_provider(
            masked_text=masked_text,
            mode=provider_mode
        )

        # -------------------------------------------------
        # Validate provider response type
# -------------------------------------------------

        if not isinstance(
            provider_response,
            str
        ):
            raise ValidationError(
                code="MALFORMED_PROVIDER_RESPONSE",
                message=(
                    "Provider returned a malformed response. "
                    "Expected text."
                )
            )

        # -------------------------------------------------
        # 7. Validate and restore MASK values
        # -------------------------------------------------
        #
        # REMOVE values never entered RequestMapping,
        # so they cannot be restored.
        # -------------------------------------------------

        final_output = restore_sensitive_info(
            response_text=provider_response,
            request_mapping=request_mapping
        )

        # -------------------------------------------------
        # 8. Success response
        # -------------------------------------------------

        return {
            "status": "ok",
            "request_id": request_id,
            "masked_text": masked_text,
            "provider_response": provider_response,
            "output": final_output
        }

    # =====================================================
    # Policy errors
    # =====================================================

    except PolicyError as error:

        return create_error_response(
            request_id=request_id,
            code=error.code,
            message=error.message
        )

    # =====================================================
    # Placeholder / validation errors
    # =====================================================

    except ValidationError as error:

        return create_error_response(
            request_id=request_id,
            code=error.code,
            message=error.message
        )

    # =====================================================
    # Invalid request errors
    # =====================================================

    except ValueError as error:

        return create_error_response(
            request_id=request_id,
            code="INVALID_REQUEST",
            message=str(error)
        )

    # =====================================================
    # Provider errors
    # =====================================================

    except MockProviderError as error:

        return create_error_response(
            request_id=request_id,
            code="PROVIDER_ERROR",
            message=str(error)
        )

    # =====================================================
    # Provider timeout
    # =====================================================

    except TimeoutError as error:

        return create_error_response(
            request_id=request_id,
            code="PROVIDER_TIMEOUT",
            message=str(error)
        )

    # =====================================================
    # ALWAYS release request mapping
    # =====================================================

    finally:

        if request_mapping is not None:

            request_mapping.clear()


# =========================================================
# Process JSON text
# =========================================================

def process_json_request(
    json_text: str,
    provider_mode: str = "normal"
) -> dict:
    """
    Parses a JSON string and sends it through the complete
    privacy-gateway pipeline.
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


# =========================================================
# Standalone tests
# =========================================================

if __name__ == "__main__":

    # =====================================================
    # TEST 1 - DEFAULT MASK POLICIES
    # =====================================================

    print("TEST 1 - DEFAULT MASK POLICIES")
    print("------------------------------")

    request_1 = {
        "request_id": "r1",
        "text": (
            "Jane Smith lives at "
            "123 Example Street, Sampletown, GA 30000. "
            "Contact Jane Smith at "
            "jane.smith@example.com or "
            "478-555-1234."
        )
    }

    result_1 = process_request(
        request_1
    )

    print(
        json.dumps(
            result_1,
            indent=4
        )
    )


    # =====================================================
    # TEST 2 - MIXED MASK / REMOVE
    # =====================================================

    print(
        "\nTEST 2 - MIXED MASK / REMOVE"
    )
    print(
        "----------------------------"
    )

    request_2 = {
        "request_id": "r2",
        "text": (
            "Jane Smith lives at "
            "123 Example Street, Sampletown, GA 30000. "
            "Contact Jane Smith at "
            "jane.smith@example.com or "
            "478-555-1234."
        ),
        "policies": {
            "NAME": "MASK",
            "ADDRESS": "MASK",
            "EMAIL": "REMOVE",
            "PHONE": "REMOVE"
        }
    }

    result_2 = process_request(
        request_2
    )

    print(
        json.dumps(
            result_2,
            indent=4
        )
    )


    # =====================================================
    # TEST 3 - PARTIAL POLICIES
    # =====================================================

    print(
        "\nTEST 3 - MISSING POLICIES DEFAULT TO MASK"
    )
    print(
        "-----------------------------------------"
    )

    request_3 = {
        "request_id": "r3",
        "text": (
            "Jane Smith can be reached at "
            "jane.smith@example.com or "
            "478-555-1234."
        ),
        "policies": {
            "EMAIL": "REMOVE"
        }
    }

    result_3 = process_request(
        request_3
    )

    print(
        json.dumps(
            result_3,
            indent=4
        )
    )


    # =====================================================
    # TEST 4 - INVALID POLICY
    # =====================================================

    print(
        "\nTEST 4 - INVALID POLICY"
    )
    print(
        "-----------------------"
    )

    request_4 = {
        "request_id": "r4",
        "text": (
            "Jane Smith has Python experience."
        ),
        "policies": {
            "NAME": "HIDE"
        }
    }

    result_4 = process_request(
        request_4
    )

    print(
        json.dumps(
            result_4,
            indent=4
        )
    )


    # =====================================================
    # TEST 5 - UNKNOWN PLACEHOLDER
    # =====================================================

    print(
        "\nTEST 5 - UNKNOWN PLACEHOLDER"
    )
    print(
        "----------------------------"
    )

    request_5 = {
        "request_id": "r5",
        "text": (
            "Jane Smith has Python experience."
        )
    }

    result_5 = process_request(
        request_5,
        provider_mode="unknown_placeholder"
    )

    print(
        json.dumps(
            result_5,
            indent=4
        )
    )

    # =====================================================
    # TEST 6 - FOREIGN REQUEST PLACEHOLDER
    # =====================================================

    print(
        "\nTEST 6 - FOREIGN REQUEST PLACEHOLDER"
    )
    print(
        "------------------------------------"
    )

    request_6 = {
        "request_id": "r6",
        "text": "Jane Smith has Python experience."
    }

    result_6 = process_request(
        request_6,
        provider_mode="foreign_placeholder"
    )

    print(
        json.dumps(
            result_6,
            indent=4
        )
    )


    # =====================================================
    # TEST 7 - MALFORMED PROVIDER RESPONSE
    # =====================================================

    print(
        "\nTEST 7 - MALFORMED PROVIDER RESPONSE"
    )
    print(
        "------------------------------------"
    )

    request_7 = {
        "request_id": "r7",
        "text": "Jane Smith has Python experience."
    }

    result_7 = process_request(
        request_7,
        provider_mode="malformed_response"
    )

    print(
        json.dumps(
            result_7,
            indent=4
        )
    )


    # =====================================================
    # TEST 8 - PROVIDER ERROR
    # =====================================================

    print(
        "\nTEST 8 - PROVIDER ERROR"
    )
    print(
        "-----------------------"
    )

    request_8 = {
        "request_id": "r8",
        "text": "Jane Smith has Python experience."
    }

    result_8 = process_request(
        request_8,
        provider_mode="provider_error"
    )

    print(
        json.dumps(
            result_8,
            indent=4
        )
    )


    # =====================================================
    # TEST 9 - PROVIDER TIMEOUT
    # =====================================================

    print(
        "\nTEST 9 - PROVIDER TIMEOUT"
    )
    print(
        "-------------------------"
    )

    request_9 = {
        "request_id": "r9",
        "text": "Jane Smith has Python experience."
    }

    result_9 = process_request(
        request_9,
        provider_mode="provider_timeout"
    )

    print(
        json.dumps(
            result_9,
            indent=4
        )
    )