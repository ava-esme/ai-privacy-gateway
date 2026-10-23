import re

# Placeholder pattern

PLACEHOLDER_PATTERN = re.compile(
    r"\[\[(r[1-9]\d*):(NAME|EMAIL|PHONE|ADDRESS):([1-9]\d*)\]\]"
)

# Custom provider error

class MockProviderError(Exception):
    """
    Raised when the mock provider is intentionally set to
    simulate a provider failure.
    """
    pass

# Normal mock response

def create_normal_response(masked_text: str) -> str:
    """
    Creates the normal deterministic response.

    The mock provider does not perform real AI analysis.
    Its purpose is to simulate an external provider while
    preserving placeholders so the rest of the privacy
    gateway can be tested.
    """

    return (
        "Qualification Summary:\n"
        f"{masked_text}"
    )

# Unknown placeholder simulation

def create_unknown_placeholder_response(masked_text: str) -> str:
    """
    Returns a response containing a well-formed placeholder
    that was not issued by the masker.

    This is used to test UNKNOWN_PLACEHOLDER handling.
    """

    match = PLACEHOLDER_PATTERN.search(masked_text)

    if match is None:
        # If there are no placeholders in the input, use a
        # synthetic unknown placeholder for testing.
        unknown_placeholder = "[[r1:NAME:999]]"

    else:
        request_id = match.group(1)
        category = match.group(2)

        unknown_placeholder = (
            f"[[{request_id}:{category}:999]]"
        )

    return (
        "Qualification Summary:\n"
        f"Candidate {unknown_placeholder} has relevant experience."
    )

# Malformed placeholder simulation

def create_malformed_placeholder_response(masked_text: str) -> str:
    """
    Returns a response containing malformed reserved
    placeholder syntax.

    This is used to test INVALID_PLACEHOLDER handling.
    """

    match = PLACEHOLDER_PATTERN.search(masked_text)

    if match is None:
        malformed_placeholder = "[[r1:NAME]]"

    else:
        request_id = match.group(1)
        category = match.group(2)

        malformed_placeholder = (
            f"[[{request_id}:{category}]]"
        )

    return (
        "Qualification Summary:\n"
        f"Candidate {malformed_placeholder} has relevant experience."
    )

# Main mock provider function

def mock_provider(
    masked_text: str,
    mode: str = "normal"
) -> str:
    """
    Simulates an offline AI provider.

    Supported modes:

    normal
        Returns a deterministic response while preserving
        the masked input.

    unknown_placeholder
        Returns a valid-looking placeholder that was never
        issued by the current request.

    malformed_placeholder
        Returns malformed reserved placeholder syntax.

    provider_error
        Simulates a provider failure.

    The special modes are intended for automated testing.
    """

    if not isinstance(masked_text, str):
        raise TypeError("masked_text must be a string.")

    if mode == "normal":
        return create_normal_response(masked_text)

    elif mode == "unknown_placeholder":
        return create_unknown_placeholder_response(masked_text)

    elif mode == "malformed_placeholder":
        return create_malformed_placeholder_response(masked_text)

    elif mode == "provider_error":
        raise MockProviderError(
            "The offline mock provider simulated a failure."
        )

    else:
        raise ValueError(
            f"Unsupported mock provider mode: {mode}"
        )

# Optional standalone test

if __name__ == "__main__":

    sample_masked_text = (
        "[[r1:NAME:1]] lives at [[r1:ADDRESS:1]]. "
        "Contact [[r1:NAME:1]] at [[r1:EMAIL:1]] "
        "or [[r1:PHONE:1]]."
    )

    print("NORMAL RESPONSE")
    print("----------------")
    print(
        mock_provider(
            sample_masked_text,
            mode="normal"
        )
    )

    print("\nUNKNOWN PLACEHOLDER RESPONSE")
    print("----------------------------")
    print(
        mock_provider(
            sample_masked_text,
            mode="unknown_placeholder"
        )
    )

    print("\nMALFORMED PLACEHOLDER RESPONSE")
    print("------------------------------")
    print(
        mock_provider(
            sample_masked_text,
            mode="malformed_placeholder"
        )
    )