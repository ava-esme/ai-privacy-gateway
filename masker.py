from dataclasses import dataclass
from collections import defaultdict
import re

from detector import Detection, detect_sensitive_info

# Request ID pattern

REQUEST_ID_PATTERN = re.compile(r"^r[1-9]\d*$")

# Masking result

@dataclass
class MaskingResult:
    masked_text: str
    placeholder_to_value: dict[str, str]
    value_to_placeholder: dict[tuple[str, str], str]

# Request ID validation

def validate_request_id(request_id: str) -> None:
    """
    Verifies that the request ID follows the required format.

    Valid examples:
    r1
    r2
    r15

    Invalid examples:
    request1
    r0
    R1
    """

    if not isinstance(request_id, str):
        raise ValueError("Request ID must be a string.")

    if not REQUEST_ID_PATTERN.fullmatch(request_id):
        raise ValueError(
            "Request ID must use the format 'r' followed by "
            "a positive integer, such as r1."
        )

# Remove duplicate detections

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
            unique_detections.append(detection)

    return unique_detections

# Overlap check

def check_for_overlaps(
    detections: list[Detection]
) -> None:
    """
    Checks whether two detections overlap.

    Full overlap handling belongs to a later milestone, so the
    M2 masker raises an error rather than masking ambiguous text.
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
                "Overlapping sensitive-information detections "
                "are not supported in Milestone 2."
            )

        previous = current

# Create placeholders

def create_placeholder(
    request_id: str,
    category: str,
    index: int
) -> str:
    """
    Creates a placeholder using the project's documented format.

    Example:
    [[r1:NAME:1]]
    """

    return f"[[{request_id}:{category}:{index}]]"

# Main masking function

def mask_sensitive_info(
    text: str,
    detections: list[Detection],
    request_id: str
) -> MaskingResult:
    """
    Replaces detected sensitive values with request-specific
    placeholders.

    Repeated occurrences of the same category/value pair reuse
    the same placeholder.

    Different values in the same category receive different
    placeholder indexes.

    Example:

    Jane Smith worked with Jane Smith and John Davis.

    becomes:

    [[r1:NAME:1]] worked with [[r1:NAME:1]]
    and [[r1:NAME:2]].
    """

    validate_request_id(request_id)

    # Remove accidental duplicate Detection objects.
    detections = remove_duplicate_detections(detections)

    # M2 does not yet resolve overlapping detections.
    check_for_overlaps(detections)

    # Stores:
    #
    # [[r1:NAME:1]] -> Jane Smith
    #
    placeholder_to_value = {}

    # Stores:
    #
    # ("NAME", "Jane Smith") -> [[r1:NAME:1]]
    #
    value_to_placeholder = {}

    # Keeps a separate counter for every category.
    #
    # Example:
    # NAME -> 2
    # EMAIL -> 1
    # PHONE -> 1
    #
    category_counts = defaultdict(int)

    # Maps each detection position to the placeholder that
    # should replace it.
    replacements = []

    # Process detections in their original text order.
    sorted_detections = sorted(
        detections,
        key=lambda detection: detection.start
    )

    for detection in sorted_detections:

        value_key = (
            detection.category,
            detection.value
        )

        # -------------------------------------------------
        # Repeated sensitive value
        # -------------------------------------------------

        if value_key in value_to_placeholder:
            placeholder = value_to_placeholder[value_key]

        # -------------------------------------------------
        # New sensitive value
        # -------------------------------------------------

        else:
            category_counts[detection.category] += 1

            placeholder = create_placeholder(
                request_id=request_id,
                category=detection.category,
                index=category_counts[detection.category]
            )

            value_to_placeholder[value_key] = placeholder

            placeholder_to_value[placeholder] = detection.value

        replacements.append(
            (
                detection.start,
                detection.end,
                placeholder
            )
        )

    # -----------------------------------------------------
    # Replace text from right to left
    # -----------------------------------------------------
    #
    # Replacing from the end prevents earlier character
    # positions from changing while replacements are made.
    # -----------------------------------------------------

    masked_text = text

    for start, end, placeholder in reversed(replacements):
        masked_text = (
            masked_text[:start]
            + placeholder
            + masked_text[end:]
        )

    return MaskingResult(
        masked_text=masked_text,
        placeholder_to_value=placeholder_to_value,
        value_to_placeholder=value_to_placeholder
    )

# Optional standalone test

if __name__ == "__main__":

    sample_text = (
        "Jane Smith lives at "
        "123 Example Street, Sampletown, GA 30000. "
        "Jane Smith has 3 years of Python experience. "
        "Contact Jane Smith at jane.smith@example.com "
        "or 478-555-1234. "
        "John Davis worked with Jane Smith."
    )

    request_id = "r1"

    # Run the detector first
    detections = detect_sensitive_info(sample_text)

    # Send detector results to the masker
    result = mask_sensitive_info(
        text=sample_text,
        detections=detections,
        request_id=request_id
    )

    print("Original text:")
    print(sample_text)

    print("\nMasked text:")
    print(result.masked_text)

    print("\nLocal placeholder map:")

    for placeholder, original_value in result.placeholder_to_value.items():
        print(f"{placeholder} -> {original_value}")