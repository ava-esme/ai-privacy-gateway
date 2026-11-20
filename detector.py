from dataclasses import dataclass
from pathlib import Path
import re


# =========================================================
# File locations
# =========================================================

PROJECT_ROOT = Path(__file__).resolve().parent
DATA_DIR = PROJECT_ROOT / "data"

DEFAULT_NAMES_FILE = DATA_DIR / "synthetic_names.txt"
DEFAULT_ADDRESSES_FILE = DATA_DIR / "synthetic_addresses.txt"


# =========================================================
# Structured patterns
# =========================================================

EMAIL_PATTERN = re.compile(
    r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b"
)

PHONE_PATTERN = re.compile(
    r"\b\d{3}-\d{3}-\d{4}\b"
)


# =========================================================
# Overlap category priority
# =========================================================

# Lower number = higher priority.
#
# This priority is used only when two detections:
# - start at the same position; and
# - have the same length.
#
# The main overlap rules are:
#
# 1. Earlier starting position wins.
# 2. If two matches start at the same position,
#    the longer match wins.
# 3. If start and length are equal, category
#    priority decides the winner.

CATEGORY_PRIORITY = {
    "EMAIL": 1,
    "PHONE": 2,
    "ADDRESS": 3,
    "NAME": 4
}


# =========================================================
# Detection result
# =========================================================

@dataclass(frozen=True)
class Detection:
    category: str
    value: str
    start: int
    end: int


# =========================================================
# Load synthetic term lists
# =========================================================

def load_terms(
    file_path: Path
) -> list[str]:
    """
    Loads sensitive values from a synthetic text file.

    Each non-empty line is treated as one exact term.
    """

    try:

        with file_path.open(
            "r",
            encoding="utf-8"
        ) as file:

            return [
                line.strip()
                for line in file
                if line.strip()
            ]

    except FileNotFoundError:

        raise FileNotFoundError(
            f"Could not find required term-list file: "
            f"{file_path}"
        )


# =========================================================
# Exact term-list detection
# =========================================================

def find_exact_terms(
    text: str,
    terms: list[str],
    category: str
) -> list[Detection]:
    """
    Finds every exact occurrence of each term.

    Used for:
    - NAME
    - ADDRESS
    """

    detections = []

    for term in terms:

        escaped_term = re.escape(
            term
        )

        for match in re.finditer(
            escaped_term,
            text
        ):

            detections.append(
                Detection(
                    category=category,
                    value=match.group(),
                    start=match.start(),
                    end=match.end()
                )
            )

    return detections


# =========================================================
# Email detection
# =========================================================

def find_emails(
    text: str
) -> list[Detection]:
    """
    Finds email addresses using the documented
    structured pattern.
    """

    detections = []

    for match in EMAIL_PATTERN.finditer(
        text
    ):

        detections.append(
            Detection(
                category="EMAIL",
                value=match.group(),
                start=match.start(),
                end=match.end()
            )
        )

    return detections


# =========================================================
# Phone-number detection
# =========================================================

def find_phone_numbers(
    text: str
) -> list[Detection]:
    """
    Finds phone numbers in the supported format:

    ###-###-####
    """

    detections = []

    for match in PHONE_PATTERN.finditer(
        text
    ):

        detections.append(
            Detection(
                category="PHONE",
                value=match.group(),
                start=match.start(),
                end=match.end()
            )
        )

    return detections


# =========================================================
# Remove exact duplicate detections
# =========================================================

def remove_duplicate_detections(
    detections: list[Detection]
) -> list[Detection]:
    """
    Removes exact duplicate detections.

    Two detections are duplicates if they have the same:
    - category
    - value
    - start
    - end
    """

    unique = []
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
            unique.append(
                detection
            )

    return unique


# =========================================================
# Check whether two detections overlap
# =========================================================

def detections_overlap(
    first: Detection,
    second: Detection
) -> bool:
    """
    Returns True if two detection ranges overlap.
    """

    return (
        first.start < second.end
        and second.start < first.end
    )


# =========================================================
# Deterministic overlap resolution
# =========================================================

def resolve_overlaps(
    detections: list[Detection]
) -> list[Detection]:
    """
    Resolves overlapping sensitive-data detections
    deterministically.

    Rules:

    1. Earlier starting position wins.

    2. If two detections start at the same position,
       the longer detection wins.

    3. If both start position and length are equal,
       category priority decides the winner:

       EMAIL
       PHONE
       ADDRESS
       NAME

    4. A detection that overlaps a previously accepted
       detection is discarded.

    This guarantees that the same set of detections
    always produces the same result.
    """

    if not detections:
        return []

    detections = (
        remove_duplicate_detections(
            detections
        )
    )

    # -----------------------------------------------------
    # Sort candidates according to our documented rules.
    # -----------------------------------------------------

    sorted_detections = sorted(
        detections,
        key=lambda detection: (
            detection.start,

            # Longer detection first if start is equal.
            -(
                detection.end
                - detection.start
            ),

            # Category priority breaks exact-length ties.
            CATEGORY_PRIORITY.get(
                detection.category,
                999
            ),

            detection.end,
            detection.value
        )
    )

    accepted = []

    for candidate in sorted_detections:

        overlaps_existing = False

        for existing in accepted:

            if detections_overlap(
                candidate,
                existing
            ):

                overlaps_existing = True
                break

        if not overlaps_existing:

            accepted.append(
                candidate
            )

    # Return accepted detections in original text order.
    accepted.sort(
        key=lambda detection: (
            detection.start,
            detection.end
        )
    )

    return accepted


# =========================================================
# Main detector
# =========================================================

def detect_sensitive_info(
    text: str,
    names_file: Path = DEFAULT_NAMES_FILE,
    addresses_file: Path = DEFAULT_ADDRESSES_FILE
) -> list[Detection]:
    """
    Detects all supported sensitive information.

    Supported categories:

    - NAME
    - ADDRESS
    - EMAIL
    - PHONE

    NAME and ADDRESS use exact matching from local
    synthetic term lists.

    EMAIL and PHONE use structured regular-expression
    patterns.

    Overlapping detections are resolved before the
    results are returned.
    """

    names = load_terms(
        names_file
    )

    addresses = load_terms(
        addresses_file
    )

    detections = []

    # -----------------------------------------------------
    # Exact synthetic term-list matching
    # -----------------------------------------------------

    detections.extend(
        find_exact_terms(
            text=text,
            terms=names,
            category="NAME"
        )
    )

    detections.extend(
        find_exact_terms(
            text=text,
            terms=addresses,
            category="ADDRESS"
        )
    )

    # -----------------------------------------------------
    # Structured pattern matching
    # -----------------------------------------------------

    detections.extend(
        find_emails(
            text
        )
    )

    detections.extend(
        find_phone_numbers(
            text
        )
    )

    # -----------------------------------------------------
    # Resolve any overlapping matches
    # -----------------------------------------------------

    return resolve_overlaps(
        detections
    )


# =========================================================
# Standalone tests
# =========================================================

if __name__ == "__main__":

    # =====================================================
    # TEST 1 - NORMAL DETECTION
    # =====================================================

    print("TEST 1 - NORMAL DETECTION")
    print("-------------------------")

    sample_text = (
        "Jane Smith lives at "
        "123 Example Street, Sampletown, GA 30000. "
        "Contact Jane Smith at "
        "jane.smith@example.com "
        "or 478-555-1234."
    )

    results = detect_sensitive_info(
        sample_text
    )

    for result in results:

        print(
            f"\nCategory: {result.category}"
        )

        print(
            f"Value: {result.value}"
        )

        print(
            f"Start: {result.start}"
        )

        print(
            f"End: {result.end}"
        )


    # =====================================================
    # TEST 2 - SAME START, LONGER MATCH WINS
    # =====================================================

    print(
        "\n\nTEST 2 - LONGER OVERLAP WINS"
    )
    print(
        "----------------------------"
    )

    overlap_test = [
        Detection(
            category="ADDRESS",
            value="123 Example Street",
            start=0,
            end=18
        ),

        Detection(
            category="ADDRESS",
            value=(
                "123 Example Street, "
                "Sampletown, GA 30000"
            ),
            start=0,
            end=40
        )
    ]

    resolved = resolve_overlaps(
        overlap_test
    )

    for result in resolved:

        print(
            f"Winner: {result.category} - "
            f"{result.value}"
        )


    # =====================================================
    # TEST 3 - EARLIER START WINS
    # =====================================================

    print(
        "\nTEST 3 - EARLIER START WINS"
    )
    print(
        "---------------------------"
    )

    earlier_start_test = [
        Detection(
            category="ADDRESS",
            value="123 Example Street",
            start=0,
            end=18
        ),

        Detection(
            category="NAME",
            value="Example Street",
            start=4,
            end=18
        )
    ]

    resolved = resolve_overlaps(
        earlier_start_test
    )

    for result in resolved:

        print(
            f"Winner: {result.category} - "
            f"{result.value}"
        )


    # =====================================================
    # TEST 4 - CATEGORY PRIORITY
    # =====================================================

    print(
        "\nTEST 4 - CATEGORY PRIORITY"
    )
    print(
        "--------------------------"
    )

    priority_test = [
        Detection(
            category="NAME",
            value="Test",
            start=0,
            end=4
        ),

        Detection(
            category="ADDRESS",
            value="Test",
            start=0,
            end=4
        )
    ]

    resolved = resolve_overlaps(
        priority_test
    )

    for result in resolved:

        print(
            f"Winner: {result.category} - "
            f"{result.value}"
        )