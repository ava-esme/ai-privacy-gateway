from mapping import RequestMapping
from validator import validate_provider_response, ValidationError


# =========================================================
# Restore placeholders
# =========================================================

def restore_sensitive_info(
    response_text: str,
    request_mapping: RequestMapping
) -> str:
    """
    Restores valid MASK placeholders using the local
    RequestMapping.

    Validation always occurs before restoration.

    REMOVE values are never stored in RequestMapping,
    so they cannot be restored.
    """

    if not isinstance(
        request_mapping,
        RequestMapping
    ):
        raise TypeError(
            "request_mapping must be a RequestMapping object."
        )

    # -----------------------------------------------------
    # Step 1: Validate provider response
    # -----------------------------------------------------

    validate_provider_response(
        response_text=response_text,
        request_mapping=request_mapping
    )

    # -----------------------------------------------------
    # Step 2: Restore valid placeholders
    # -----------------------------------------------------

    restored_text = response_text

    for (
        placeholder,
        original_value
    ) in request_mapping.placeholder_to_value.items():

        restored_text = restored_text.replace(
            placeholder,
            original_value
        )

    return restored_text


# =========================================================
# Standalone tests
# =========================================================

if __name__ == "__main__":

    # -----------------------------------------------------
    # Create request-local mapping
    # -----------------------------------------------------

    request_map = RequestMapping(
        "r1"
    )

    name_placeholder = (
        request_map.get_or_create_placeholder(
            "NAME",
            "Jane Smith"
        )
    )

    email_placeholder = (
        request_map.get_or_create_placeholder(
            "EMAIL",
            "jane.smith@example.com"
        )
    )

    address_placeholder = (
        request_map.get_or_create_placeholder(
            "ADDRESS",
            "123 Example Street, Sampletown, GA 30000"
        )
    )

    phone_placeholder = (
        request_map.get_or_create_placeholder(
            "PHONE",
            "478-555-1234"
        )
    )


    # =====================================================
    # TEST 1 - VALID RESTORATION
    # =====================================================

    print("TEST 1 - VALID RESTORATION")
    print("--------------------------")

    valid_response = (
        "Qualification Summary:\n"
        f"{name_placeholder} has relevant experience. "
        f"Contact {email_placeholder} or "
        f"{phone_placeholder}. "
        f"Address: {address_placeholder}."
    )

    try:

        restored = restore_sensitive_info(
            response_text=valid_response,
            request_mapping=request_map
        )

        print(restored)

    except ValidationError as error:

        print(
            f"Error code: {error.code}"
        )

        print(
            f"Message: {error.message}"
        )


    # =====================================================
    # TEST 2 - UNKNOWN PLACEHOLDER
    # =====================================================

    print(
        "\nTEST 2 - UNKNOWN PLACEHOLDER"
    )
    print(
        "----------------------------"
    )

    unknown_response = (
        "Qualification Summary:\n"
        "[[r1:NAME:999]] has relevant experience."
    )

    try:

        restored = restore_sensitive_info(
            response_text=unknown_response,
            request_mapping=request_map
        )

        print(restored)

    except ValidationError as error:

        print(
            f"Error code: {error.code}"
        )

        print(
            f"Message: {error.message}"
        )


    # =====================================================
    # TEST 3 - MALFORMED PLACEHOLDER
    # =====================================================

    print(
        "\nTEST 3 - MALFORMED PLACEHOLDER"
    )
    print(
        "------------------------------"
    )

    malformed_response = (
        "Qualification Summary:\n"
        "[[r1:NAME]] has relevant experience."
    )

    try:

        restored = restore_sensitive_info(
            response_text=malformed_response,
            request_mapping=request_map
        )

        print(restored)

    except ValidationError as error:

        print(
            f"Error code: {error.code}"
        )

        print(
            f"Message: {error.message}"
        )


    # =====================================================
    # TEST 4 - FOREIGN REQUEST PLACEHOLDER
    # =====================================================

    print(
        "\nTEST 4 - FOREIGN REQUEST PLACEHOLDER"
    )
    print(
        "------------------------------------"
    )

    foreign_response = (
        "Qualification Summary:\n"
        "[[r2:NAME:1]] has relevant experience."
    )

    try:

        restored = restore_sensitive_info(
            response_text=foreign_response,
            request_mapping=request_map
        )

        print(restored)

    except ValidationError as error:

        print(
            f"Error code: {error.code}"
        )

        print(
            f"Message: {error.message}"
        )