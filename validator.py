import re

from mapping import RequestMapping


# =========================================================
# Valid placeholder pattern
# =========================================================

VALID_PLACEHOLDER_PATTERN = re.compile(
    r"\[\[(r[1-9]\d*):(NAME|EMAIL|PHONE|ADDRESS):([1-9]\d*)\]\]"
)


# Finds anything surrounded by reserved [[...]] syntax.
RESERVED_PLACEHOLDER_PATTERN = re.compile(
    r"\[\[.*?\]\]",
    re.DOTALL
)


# =========================================================
# Validation error
# =========================================================

class ValidationError(Exception):
    """
    Represents a controlled validation error.

    Supported M3 validation errors include:

    INVALID_PLACEHOLDER
    UNKNOWN_PLACEHOLDER
    FOREIGN_REQUEST_PLACEHOLDER
    """

    def __init__(
        self,
        code: str,
        message: str
    ):
        super().__init__(message)

        self.code = code
        self.message = message


# =========================================================
# Find reserved placeholders
# =========================================================

def find_reserved_placeholders(
    response_text: str
) -> list[str]:
    """
    Finds all complete [[...]] tokens in the provider
    response.
    """

    return RESERVED_PLACEHOLDER_PATTERN.findall(
        response_text
    )


# =========================================================
# Check incomplete placeholder syntax
# =========================================================

def check_incomplete_placeholder_syntax(
    response_text: str
) -> None:
    """
    Detects incomplete reserved placeholder syntax.

    Examples:

    [[r1:NAME:1

    r1:NAME:1]]

    These are malformed and produce
    INVALID_PLACEHOLDER.
    """

    text_without_complete_tokens = (
        RESERVED_PLACEHOLDER_PATTERN.sub(
            "",
            response_text
        )
    )

    if (
        "[[" in text_without_complete_tokens
        or "]]" in text_without_complete_tokens
    ):

        raise ValidationError(
            code="INVALID_PLACEHOLDER",
            message=(
                "Provider response contained incomplete "
                "reserved placeholder syntax."
            )
        )


# =========================================================
# Parse placeholder
# =========================================================

def parse_placeholder(
    placeholder: str
) -> tuple[str, str, int]:
    """
    Validates and parses one placeholder.

    Required format:

    [[request_id:CATEGORY:index]]

    Example:

    [[r1:NAME:1]]

    Returns:

    request_id, category, index
    """

    match = VALID_PLACEHOLDER_PATTERN.fullmatch(
        placeholder
    )

    if match is None:

        raise ValidationError(
            code="INVALID_PLACEHOLDER",
            message=(
                "Provider response contained malformed "
                f"reserved placeholder syntax: "
                f"{placeholder}"
            )
        )

    request_id = match.group(1)
    category = match.group(2)
    index = int(match.group(3))

    return (
        request_id,
        category,
        index
    )


# =========================================================
# Validate request ownership
# =========================================================

def validate_request_ownership(
    placeholder: str,
    request_mapping: RequestMapping
) -> None:
    """
    Rejects placeholders that belong to a different request.

    Example:

    Current request:
    r2

    Provider returns:
    [[r1:NAME:1]]

    Result:
    FOREIGN_REQUEST_PLACEHOLDER
    """

    placeholder_request_id, _, _ = (
        parse_placeholder(
            placeholder
        )
    )

    if (
        placeholder_request_id
        != request_mapping.request_id
    ):

        raise ValidationError(
            code="FOREIGN_REQUEST_PLACEHOLDER",
            message=(
                f"Provider response contained placeholder "
                f"{placeholder}, which belongs to request "
                f"{placeholder_request_id} rather than "
                f"current request "
                f"{request_mapping.request_id}."
            )
        )


# =========================================================
# Validate issued placeholder
# =========================================================

def validate_placeholder_exists(
    placeholder: str,
    request_mapping: RequestMapping
) -> None:
    """
    Checks whether the current request actually issued
    the placeholder.

    Example:

    Mapping contains:
    [[r1:NAME:1]]

    Provider returns:
    [[r1:NAME:999]]

    Result:
    UNKNOWN_PLACEHOLDER
    """

    if not request_mapping.contains_placeholder(
        placeholder
    ):

        raise ValidationError(
            code="UNKNOWN_PLACEHOLDER",
            message=(
                "Provider response contained placeholder "
                f"{placeholder}, which was not issued "
                "for this request."
            )
        )


# =========================================================
# Main response validator
# =========================================================

def validate_provider_response(
    response_text: str,
    request_mapping: RequestMapping
) -> bool:
    """
    Validates all placeholders in a provider response.

    Validation order:

    1. Response must be a string.
    2. Reserved syntax must be complete.
    3. Every [[...]] token must be well-formed.
    4. Placeholder request ID must match the current request.
    5. Placeholder must have been issued by the current request.

    Returns True if validation succeeds.

    Raises ValidationError if validation fails.
    """

    if not isinstance(
        response_text,
        str
    ):

        raise ValidationError(
            code="INVALID_PLACEHOLDER",
            message=(
                "Provider response must be a string."
            )
        )

    if not isinstance(
        request_mapping,
        RequestMapping
    ):

        raise TypeError(
            "request_mapping must be a RequestMapping object."
        )

    # -----------------------------------------------------
    # Step 1: Check incomplete reserved syntax
    # -----------------------------------------------------

    check_incomplete_placeholder_syntax(
        response_text
    )

    # -----------------------------------------------------
    # Step 2: Find complete reserved tokens
    # -----------------------------------------------------

    placeholders = find_reserved_placeholders(
        response_text
    )

    # -----------------------------------------------------
    # Step 3: Validate each placeholder
    # -----------------------------------------------------

    for placeholder in placeholders:

        # Validates format.
        parse_placeholder(
            placeholder
        )

        # Rejects placeholders from another request.
        validate_request_ownership(
            placeholder,
            request_mapping
        )

        # Rejects placeholders that were never issued.
        validate_placeholder_exists(
            placeholder,
            request_mapping
        )

    return True


# =========================================================
# Standalone tests
# =========================================================

if __name__ == "__main__":

    # -----------------------------------------------------
    # Create mapping for request r1
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


    # =====================================================
    # TEST 1 - VALID RESPONSE
    # =====================================================

    print("TEST 1 - VALID RESPONSE")
    print("-----------------------")

    valid_response = (
        "Qualification Summary:\n"
        f"{name_placeholder} has relevant experience. "
        f"Contact {email_placeholder}."
    )

    try:

        validate_provider_response(
            valid_response,
            request_map
        )

        print(
            "Validation successful."
        )

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

        validate_provider_response(
            unknown_response,
            request_map
        )

        print(
            "Validation successful."
        )

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

        validate_provider_response(
            malformed_response,
            request_map
        )

        print(
            "Validation successful."
        )

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

        validate_provider_response(
            foreign_response,
            request_map
        )

        print(
            "Validation successful."
        )

    except ValidationError as error:

        print(
            f"Error code: {error.code}"
        )

        print(
            f"Message: {error.message}"
        )