import re

# Valid placeholder pattern

VALID_PLACEHOLDER_PATTERN = re.compile(
    r"\[\[(r[1-9]\d*):(NAME|EMAIL|PHONE|ADDRESS):([1-9]\d*)\]\]"
)


# Finds anything surrounded by reserved [[...]] syntax.
RESERVED_PLACEHOLDER_PATTERN = re.compile(
    r"\[\[.*?\]\]",
    re.DOTALL
)

# Validation error

class ValidationError(Exception):
    """
    Represents a controlled validation error.

    The code can later be placed directly into the JSON
    error response.
    """

    def __init__(self, code: str, message: str):
        super().__init__(message)

        self.code = code
        self.message = message

# Find reserved placeholders

def find_reserved_placeholders(
    response_text: str
) -> list[str]:
    """
    Finds all text using the reserved [[...]] syntax.
    """

    return RESERVED_PLACEHOLDER_PATTERN.findall(
        response_text
    )

# Check for incomplete reserved syntax

def check_incomplete_placeholder_syntax(
    response_text: str
) -> None:
    """
    Detects reserved placeholder markers that are not part
    of a complete [[...]] token.

    Examples:

    [[r1:NAME:1

    r1:NAME:1]]

    These should be treated as malformed placeholders.
    """

    # Remove all complete [[...]] sections.
    text_without_complete_tokens = (
        RESERVED_PLACEHOLDER_PATTERN.sub(
            "",
            response_text
        )
    )

    # If any reserved markers remain, the provider returned
    # incomplete placeholder syntax.
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

# Validate placeholder structure

def validate_placeholder_format(
    placeholder: str
) -> None:
    """
    Verifies that a placeholder follows the required format:

    [[request_id:CATEGORY:index]]

    Example:

    [[r1:NAME:1]]
    """

    if VALID_PLACEHOLDER_PATTERN.fullmatch(
        placeholder
    ) is None:

        raise ValidationError(
            code="INVALID_PLACEHOLDER",
            message=(
                "Provider response contained malformed "
                f"reserved placeholder syntax: {placeholder}"
            )
        )

# Validate issued placeholder

def validate_placeholder_exists(
    placeholder: str,
    placeholder_to_value: dict[str, str]
) -> None:
    """
    Checks that the placeholder was actually issued by the
    masker for the current request.

    Example:

    Valid:
    [[r1:NAME:1]]

    Unknown:
    [[r1:NAME:999]]
    """

    if placeholder not in placeholder_to_value:

        raise ValidationError(
            code="UNKNOWN_PLACEHOLDER",
            message=(
                "Provider response contained placeholder "
                f"{placeholder}, which was not issued "
                "for this request."
            )
        )

# Main response validator

def validate_provider_response(
    response_text: str,
    placeholder_to_value: dict[str, str]
) -> bool:
    """
    Validates all placeholders in a provider response.

    Validation rules:

    1. Reserved placeholder syntax must be complete.
    2. Every [[...]] token must follow the valid format.
    3. Every valid-looking placeholder must have been issued
       by the current request.

    Returns True if validation succeeds.

    Raises ValidationError if validation fails.
    """

    if not isinstance(response_text, str):
        raise ValidationError(
            code="INVALID_PLACEHOLDER",
            message="Provider response must be a string."
        )

    if not isinstance(
        placeholder_to_value,
        dict
    ):
        raise TypeError(
            "placeholder_to_value must be a dictionary."
        )

    # -----------------------------------------------------
    # Step 1: Look for incomplete reserved syntax
    # -----------------------------------------------------

    check_incomplete_placeholder_syntax(
        response_text
    )

    # -----------------------------------------------------
    # Step 2: Find all reserved [[...]] tokens
    # -----------------------------------------------------

    placeholders = find_reserved_placeholders(
        response_text
    )

    # -----------------------------------------------------
    # Step 3: Validate each placeholder
    # -----------------------------------------------------

    for placeholder in placeholders:

        # Must follow the required structure.
        validate_placeholder_format(
            placeholder
        )

        # Must have been issued by this request.
        validate_placeholder_exists(
            placeholder,
            placeholder_to_value
        )

    return True

# Optional standalone tests

if __name__ == "__main__":

    # This represents the local map produced by masker.py.
    placeholder_map = {
        "[[r1:NAME:1]]": "Jane Smith",
        "[[r1:ADDRESS:1]]":
            "123 Example Street, Sampletown, GA 30000",
        "[[r1:EMAIL:1]]":
            "jane.smith@example.com",
        "[[r1:PHONE:1]]":
            "478-555-1234"
    }

    # Test 1: Valid response

    valid_response = (
        "Qualification Summary:\n"
        "[[r1:NAME:1]] has relevant experience. "
        "Contact [[r1:EMAIL:1]]."
    )

    print("VALID RESPONSE")
    print("--------------")

    try:
        validate_provider_response(
            valid_response,
            placeholder_map
        )

        print("Validation successful.")

    except ValidationError as error:
        print(f"Error code: {error.code}")
        print(f"Message: {error.message}")

    # -----------------------------------------------------
    # Test 2: Unknown placeholder
    # -----------------------------------------------------

    unknown_response = (
        "Qualification Summary:\n"
        "[[r1:NAME:999]] has relevant experience."
    )

    print("\nUNKNOWN PLACEHOLDER")
    print("-------------------")

    try:
        validate_provider_response(
            unknown_response,
            placeholder_map
        )

        print("Validation successful.")

    except ValidationError as error:
        print(f"Error code: {error.code}")
        print(f"Message: {error.message}")

    # -----------------------------------------------------
    # Test 3: Malformed placeholder
    # -----------------------------------------------------

    malformed_response = (
        "Qualification Summary:\n"
        "[[r1:NAME]] has relevant experience."
    )

    print("\nMALFORMED PLACEHOLDER")
    print("---------------------")

    try:
        validate_provider_response(
            malformed_response,
            placeholder_map
        )

        print("Validation successful.")

    except ValidationError as error:
        print(f"Error code: {error.code}")
        print(f"Message: {error.message}")