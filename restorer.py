from validator import validate_provider_response, ValidationError

# Restore placeholders

def restore_sensitive_info(
    response_text: str,
    placeholder_to_value: dict[str, str]
) -> str:
    """
    Restores valid placeholders in the provider response
    using the local placeholder map.

    Validation occurs before restoration.

    Example:

    [[r1:NAME:1]]
        ->
    Jane Smith
    """

    # -----------------------------------------------------
    # Step 1: Validate the provider response
    # -----------------------------------------------------

    validate_provider_response(
        response_text=response_text,
        placeholder_to_value=placeholder_to_value
    )

    # -----------------------------------------------------
    # Step 2: Restore valid placeholders
    # -----------------------------------------------------

    restored_text = response_text

    for placeholder, original_value in placeholder_to_value.items():

        restored_text = restored_text.replace(
            placeholder,
            original_value
        )

    return restored_text

# Optional standalone tests

if __name__ == "__main__":

    # Example local placeholder map
    placeholder_map = {
        "[[r1:NAME:1]]": "Jane Smith",
        "[[r1:ADDRESS:1]]":
            "123 Example Street, Sampletown, GA 30000",
        "[[r1:EMAIL:1]]":
            "jane.smith@example.com",
        "[[r1:PHONE:1]]":
            "478-555-1234"
    }

    # -----------------------------------------------------
    # Test 1: Valid restoration
    # -----------------------------------------------------

    valid_response = (
        "Qualification Summary:\n"
        "[[r1:NAME:1]] has relevant experience. "
        "Contact [[r1:NAME:1]] at [[r1:EMAIL:1]] "
        "or [[r1:PHONE:1]]. "
        "Address: [[r1:ADDRESS:1]]."
    )

    print("VALID RESTORATION")
    print("-----------------")

    try:

        restored = restore_sensitive_info(
            response_text=valid_response,
            placeholder_to_value=placeholder_map
        )

        print(restored)

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

        restored = restore_sensitive_info(
            response_text=unknown_response,
            placeholder_to_value=placeholder_map
        )

        print(restored)

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

        restored = restore_sensitive_info(
            response_text=malformed_response,
            placeholder_to_value=placeholder_map
        )

        print(restored)

    except ValidationError as error:

        print(f"Error code: {error.code}")
        print(f"Message: {error.message}")