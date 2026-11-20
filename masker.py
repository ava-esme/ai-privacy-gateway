from dataclasses import dataclass

from detector import Detection, detect_sensitive_info
from mapping import RequestMapping
from policy import resolve_policies, get_policy


# =========================================================
# Masking result
# =========================================================

@dataclass
class MaskingResult:
    masked_text: str
    removed_count: int


# =========================================================
# Remove duplicate detections
# =========================================================

def remove_duplicate_detections(
    detections: list[Detection]
) -> list[Detection]:
    """
    Removes exact duplicate Detection objects.

    A duplicate has the same:
    - category
    - value
    - start position
    - end position
    """

    unique_detections = []
    seen = set()

    for detection in detections:

        key = (
            detection.category,
            detection.value,
            detection.start,
            detection.end
        )

        if key not in seen:

            seen.add(key)
            unique_detections.append(
                detection
            )

    return unique_detections


# =========================================================
# Temporary overlap check
# =========================================================

def check_for_overlaps(
    detections: list[Detection]
) -> None:
    """
    Temporarily checks for overlapping detections.

    Milestone 3 requires deterministic overlap resolution.
    That logic will be added in the next refinement step.

    For now, this function prevents ambiguous replacements
    while the policy and mapping refactor is tested.
    """

    if not detections:
        return

    sorted_detections = sorted(
        detections,
        key=lambda detection: (
            detection.start,
            detection.end
        )
    )

    previous = sorted_detections[0]

    for current in sorted_detections[1:]:

        if current.start < previous.end:

            raise ValueError(
                "Overlapping sensitive-information "
                "detections must be resolved before masking."
            )

        previous = current


# =========================================================
# Main masking function
# =========================================================

def mask_sensitive_info(
    text: str,
    detections: list[Detection],
    request_mapping: RequestMapping,
    resolved_policies: dict[str, str]
) -> MaskingResult:
    """
    Applies MASK and REMOVE policies to detected sensitive
    information.

    MASK:
        Replaces the value with a request-local placeholder.

    REMOVE:
        Removes the value completely and does not create a
        placeholder mapping.

    Repeated MASK values reuse the same placeholder because
    RequestMapping owns the request-local mapping state.
    """

    if not isinstance(text, str):

        raise ValueError(
            "Text must be a string."
        )

    if not isinstance(
        request_mapping,
        RequestMapping
    ):

        raise ValueError(
            "request_mapping must be a RequestMapping object."
        )

    # -----------------------------------------------------
    # Remove exact duplicate detections
    # -----------------------------------------------------

    detections = (
        remove_duplicate_detections(
            detections
        )
    )

    # -----------------------------------------------------
    # Temporary overlap protection
    # -----------------------------------------------------

    check_for_overlaps(
        detections
    )

    # -----------------------------------------------------
    # Build replacement list
    # -----------------------------------------------------

    replacements = []

    removed_count = 0

    sorted_detections = sorted(
        detections,
        key=lambda detection: (
            detection.start,
            detection.end
        )
    )

    for detection in sorted_detections:

        category = detection.category

        policy = get_policy(
            category,
            resolved_policies
        )

        # =================================================
        # MASK
        # =================================================

        if policy == "MASK":

            placeholder = (
                request_mapping.get_or_create_placeholder(
                    category=category,
                    value=detection.value
                )
            )

            replacement_text = placeholder

        # =================================================
        # REMOVE
        # =================================================

        elif policy == "REMOVE":

            # REMOVE values are not added to the request
            # mapping and therefore cannot be restored later.
            replacement_text = ""

            removed_count += 1

        # This should never occur because policy.py already
        # validates policy values.
        else:

            raise ValueError(
                f"Unexpected policy: {policy}"
            )

        replacements.append(
            (
                detection.start,
                detection.end,
                replacement_text
            )
        )

    # -----------------------------------------------------
    # Apply replacements from right to left
    # -----------------------------------------------------
    #
    # Replacing from the end prevents an earlier replacement
    # from changing the character positions of later ones.
    # -----------------------------------------------------

    masked_text = text

    for (
        start,
        end,
        replacement_text
    ) in reversed(replacements):

        masked_text = (
            masked_text[:start]
            + replacement_text
            + masked_text[end:]
        )

    return MaskingResult(
        masked_text=masked_text,
        removed_count=removed_count
    )


# =========================================================
# Optional standalone tests
# =========================================================

if __name__ == "__main__":

    sample_text = (
        "Jane Smith lives at "
        "123 Example Street, Sampletown, GA 30000. "
        "Contact Jane Smith at "
        "jane.smith@example.com "
        "or 478-555-1234. "
        "John Davis worked with Jane Smith."
    )

    # -----------------------------------------------------
    # Detect sensitive information
    # -----------------------------------------------------

    detections = detect_sensitive_info(
        sample_text
    )

    # =====================================================
    # TEST 1 - DEFAULT MASK POLICIES
    # =====================================================

    print("TEST 1 - DEFAULT MASK POLICIES")
    print("------------------------------")

    request_map_1 = RequestMapping(
        "r1"
    )

    default_policies = resolve_policies(
        None
    )

    result_1 = mask_sensitive_info(
        text=sample_text,
        detections=detections,
        request_mapping=request_map_1,
        resolved_policies=default_policies
    )

    print("\nOriginal text:")
    print(sample_text)

    print("\nMasked text:")
    print(result_1.masked_text)

    print("\nLocal mapping:")

    for (
        placeholder,
        original_value
    ) in request_map_1.placeholder_to_value.items():

        print(
            f"{placeholder} -> "
            f"{original_value}"
        )

    print(
        "\nRemoved values:",
        result_1.removed_count
    )


    # =====================================================
    # TEST 2 - MIXED MASK / REMOVE POLICIES
    # =====================================================

    print("\n\nTEST 2 - MIXED MASK / REMOVE")
    print("----------------------------")

    request_map_2 = RequestMapping(
        "r2"
    )

    mixed_policies = resolve_policies(
        {
            "NAME": "MASK",
            "EMAIL": "REMOVE",
            "PHONE": "REMOVE",
            "ADDRESS": "MASK"
        }
    )

    result_2 = mask_sensitive_info(
        text=sample_text,
        detections=detections,
        request_mapping=request_map_2,
        resolved_policies=mixed_policies
    )

    print("\nMasked text:")
    print(result_2.masked_text)

    print("\nLocal mapping:")

    for (
        placeholder,
        original_value
    ) in request_map_2.placeholder_to_value.items():

        print(
            f"{placeholder} -> "
            f"{original_value}"
        )

    print(
        "\nRemoved values:",
        result_2.removed_count
    )


    # =====================================================
    # TEST 3 - VERIFY REMOVED VALUES ARE NOT MAPPED
    # =====================================================

    print(
        "\n\nTEST 3 - REMOVED VALUES ARE NOT MAPPED"
    )
    print(
        "---------------------------------------"
    )

    print(
        "Email stored in mapping:",
        any(
            value == "jane.smith@example.com"
            for value
            in request_map_2.placeholder_to_value.values()
        )
    )

    print(
        "Phone stored in mapping:",
        any(
            value == "478-555-1234"
            for value
            in request_map_2.placeholder_to_value.values()
        )
    )