import re


# =========================================================
# Placeholder pattern
# =========================================================

PLACEHOLDER_PATTERN = re.compile(
    r"\[\[(r[1-9]\d*):(NAME|EMAIL|PHONE|ADDRESS):([1-9]\d*)\]\]"
)


# =========================================================
# Custom provider error
# =========================================================

class MockProviderError(Exception):
    """
    Raised when the mock provider intentionally simulates
    a provider failure.
    """

    pass


# =========================================================
# Normal response
# =========================================================

def create_normal_response(
    masked_text: str
) -> str:
    """
    Returns a deterministic normal provider response.
    """

    return (
        "Qualification Summary:\n"
        f"{masked_text}"
    )

# =========================================================
# Missing placeholder response
# =========================================================

def create_missing_placeholder_response(
    masked_text: str
) -> str:
    """
    Simulates a provider dropping a placeholder that was
    present in the masked request.

    This is not an unauthorized placeholder. The value is
    simply absent from the provider response, so it cannot
    be restored.
    """

    match = PLACEHOLDER_PATTERN.search(
        masked_text
    )

    if match is None:

        return create_normal_response(
            masked_text
        )

    missing_placeholder_text = (
        masked_text.replace(
            match.group(0),
            "",
            1
        )
    )

    return (
        "Qualification Summary:\n"
        f"{missing_placeholder_text}"
    )


# =========================================================
# Modified placeholder response
# =========================================================

def create_modified_placeholder_response(
    masked_text: str
) -> str:
    """
    Simulates a provider changing a valid placeholder into
    a different valid-looking placeholder that was not
    issued for the request.
    """

    match = PLACEHOLDER_PATTERN.search(
        masked_text
    )

    if match is None:

        return create_normal_response(
            masked_text
        )

    request_id = match.group(1)
    category = match.group(2)
    index = match.group(3)

    # Change the category while keeping otherwise valid
    # placeholder syntax.
    if category == "NAME":

        modified_category = "EMAIL"

    else:

        modified_category = "NAME"

    modified_placeholder = (
        f"[[{request_id}:"
        f"{modified_category}:{index}]]"
    )

    modified_text = masked_text.replace(
        match.group(0),
        modified_placeholder,
        1
    )

    return (
        "Qualification Summary:\n"
        f"{modified_text}"
    )


# =========================================================
# Unknown placeholder response
# =========================================================

def create_unknown_placeholder_response(
    masked_text: str
) -> str:
    """
    Returns a well-formed placeholder that was not issued
    by the current request.
    """

    match = PLACEHOLDER_PATTERN.search(
        masked_text
    )

    if match is None:

        unknown_placeholder = (
            "[[r1:NAME:999]]"
        )

    else:

        request_id = match.group(1)
        category = match.group(2)

        unknown_placeholder = (
            f"[[{request_id}:{category}:999]]"
        )

    return (
        "Qualification Summary:\n"
        f"Candidate {unknown_placeholder} "
        "has relevant experience."
    )


# =========================================================
# Malformed placeholder response
# =========================================================

def create_malformed_placeholder_response(
    masked_text: str
) -> str:
    """
    Returns malformed reserved placeholder syntax.
    """

    match = PLACEHOLDER_PATTERN.search(
        masked_text
    )

    if match is None:

        malformed_placeholder = (
            "[[r1:NAME]]"
        )

    else:

        request_id = match.group(1)
        category = match.group(2)

        malformed_placeholder = (
            f"[[{request_id}:{category}]]"
        )

    return (
        "Qualification Summary:\n"
        f"Candidate {malformed_placeholder} "
        "has relevant experience."
    )


# =========================================================
# Foreign-request placeholder response
# =========================================================

def create_foreign_placeholder_response(
    masked_text: str
) -> str:
    """
    Returns a valid placeholder that belongs to a different
    request.

    Example:

    Current request:
    r1

    Returned placeholder:
    [[r999:NAME:1]]
    """

    match = PLACEHOLDER_PATTERN.search(
        masked_text
    )

    if match is None:

        category = "NAME"
        current_request_id = "r1"

    else:

        current_request_id = match.group(1)
        category = match.group(2)

    # Choose a request ID guaranteed to differ from the
    # current one.
    if current_request_id == "r999":

        foreign_request_id = "r998"

    else:

        foreign_request_id = "r999"

    foreign_placeholder = (
        f"[[{foreign_request_id}:"
        f"{category}:1]]"
    )

    return (
        "Qualification Summary:\n"
        f"Candidate {foreign_placeholder} "
        "has relevant experience."
    )


# =========================================================
# Malformed provider response
# =========================================================

def create_malformed_provider_response():
    """
    Simulates a provider returning an unexpected response
    type instead of text.

    The pipeline will later detect this as a malformed
    provider response.
    """

    return {
        "unexpected": "provider response"
    }


# =========================================================
# Main mock provider
# =========================================================

def mock_provider(
    masked_text: str,
    mode: str = "normal"
):
    """
    Simulates an offline AI provider.

    Supported modes:

    normal
        Returns a deterministic response.

    unknown_placeholder
        Returns a valid-looking placeholder that was never
        issued by the current request.

    malformed_placeholder
        Returns malformed placeholder syntax.

    foreign_placeholder
        Returns a valid placeholder belonging to another
        request.

    malformed_response
        Returns an unexpected non-string provider response.

    provider_error
        Simulates a general provider failure.

    provider_timeout
        Simulates a provider timeout.
    """

    if not isinstance(
        masked_text,
        str
    ):

        raise TypeError(
            "masked_text must be a string."
        )

    # -----------------------------------------------------
    # Normal response
    # -----------------------------------------------------

    if mode == "normal":

        return create_normal_response(
            masked_text
        )

    # -----------------------------------------------------
    # Unknown placeholder
    # -----------------------------------------------------

    elif mode == "unknown_placeholder":

        return (
            create_unknown_placeholder_response(
                masked_text
            )
        )

    # -----------------------------------------------------
    # Malformed placeholder
    # -----------------------------------------------------

    elif mode == "malformed_placeholder":

        return (
            create_malformed_placeholder_response(
                masked_text
            )
        )

    # -----------------------------------------------------
    # Foreign-request placeholder
    # -----------------------------------------------------

    elif mode == "foreign_placeholder":

        return (
            create_foreign_placeholder_response(
                masked_text
            )
        )

    # -----------------------------------------------------
    # Missing placeholder
    # -----------------------------------------------------

    elif mode == "missing_placeholder":

        return create_missing_placeholder_response(
            masked_text
        )

    # -----------------------------------------------------
    # Modified placeholder
    # -----------------------------------------------------

    elif mode == "modified_placeholder":

        return create_modified_placeholder_response(
            masked_text
        )  


    # -----------------------------------------------------
    # Malformed provider response
    # -----------------------------------------------------

    elif mode == "malformed_response":

        return (
            create_malformed_provider_response()
        )

    # -----------------------------------------------------
    # General provider failure
    # -----------------------------------------------------

    elif mode == "provider_error":

        raise MockProviderError(
            "The offline mock provider "
            "simulated a failure."
        )

    # -----------------------------------------------------
    # Provider timeout
    # -----------------------------------------------------

    elif mode == "provider_timeout":

        raise TimeoutError(
            "The offline mock provider "
            "simulated a timeout."
        )

    # -----------------------------------------------------
    # Unsupported mode
    # -----------------------------------------------------

    else:

        raise ValueError(
            f"Unsupported mock provider mode: "
            f"{mode}"
        )


# =========================================================
# Standalone tests
# =========================================================

if __name__ == "__main__":

    sample_masked_text = (
        "[[r1:NAME:1]] lives at "
        "[[r1:ADDRESS:1]]. "
        "Contact [[r1:NAME:1]] at "
        "[[r1:EMAIL:1]] or "
        "[[r1:PHONE:1]]."
    )


    # =====================================================
    # TEST 1 - NORMAL RESPONSE
    # =====================================================

    print("TEST 1 - NORMAL RESPONSE")
    print("------------------------")

    print(
        mock_provider(
            sample_masked_text,
            mode="normal"
        )
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

    print(
        mock_provider(
            sample_masked_text,
            mode="unknown_placeholder"
        )
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

    print(
        mock_provider(
            sample_masked_text,
            mode="malformed_placeholder"
        )
    )


    # =====================================================
    # TEST 4 - FOREIGN PLACEHOLDER
    # =====================================================

    print(
        "\nTEST 4 - FOREIGN PLACEHOLDER"
    )
    print(
        "----------------------------"
    )

    print(
        mock_provider(
            sample_masked_text,
            mode="foreign_placeholder"
        )
    )


    # =====================================================
    # TEST 5 - MALFORMED PROVIDER RESPONSE
    # =====================================================

    print(
        "\nTEST 5 - MALFORMED RESPONSE"
    )
    print(
        "---------------------------"
    )

    print(
        mock_provider(
            sample_masked_text,
            mode="malformed_response"
        )
    )


    # =====================================================
    # TEST 6 - PROVIDER ERROR
    # =====================================================

    print(
        "\nTEST 6 - PROVIDER ERROR"
    )
    print(
        "-----------------------"
    )

    try:

        mock_provider(
            sample_masked_text,
            mode="provider_error"
        )

    except MockProviderError as error:

        print(
            f"Provider error: {error}"
        )


    # =====================================================
    # TEST 7 - PROVIDER TIMEOUT
    # =====================================================

    print(
        "\nTEST 7 - PROVIDER TIMEOUT"
    )
    print(
        "-------------------------"
    )

    try:

        mock_provider(
            sample_masked_text,
            mode="provider_timeout"
        )

    except TimeoutError as error:

        print(
            f"Provider timeout: {error}"
        )