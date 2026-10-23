from dataclasses import dataclass
from pathlib import Path
import re

# File locations

PROJECT_ROOT = Path(__file__).resolve().parent
DATA_DIR = PROJECT_ROOT / "data"

DEFAULT_NAMES_FILE = DATA_DIR / "synthetic_names.txt"
DEFAULT_ADDRESSES_FILE = DATA_DIR / "synthetic_addresses.txt"

# Structured patterns

EMAIL_PATTERN = re.compile(
    r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b"
)

PHONE_PATTERN = re.compile(
    r"\b\d{3}-\d{3}-\d{4}\b"
)

# Detection result

@dataclass(frozen=True)
class Detection:
    category: str
    value: str
    start: int
    end: int

# Load synthetic term lists

def load_terms(file_path: Path) -> list[str]:
    """
    Loads sensitive values from a synthetic text file.

    Each non-empty line in the file is treated as one term.
    """

    try:
        with file_path.open("r", encoding="utf-8") as file:
            return [
                line.strip()
                for line in file
                if line.strip()
            ]

    except FileNotFoundError:
        raise FileNotFoundError(
            f"Could not find required term-list file: {file_path}"
        )

# Exact term-list detection

def find_exact_terms(
    text: str,
    terms: list[str],
    category: str
) -> list[Detection]:
    """
    Finds every exact occurrence of each term in the input text.

    Used for:
    - NAME
    - ADDRESS
    """

    detections = []

    for term in terms:
        escaped_term = re.escape(term)

        for match in re.finditer(escaped_term, text):
            detections.append(
                Detection(
                    category=category,
                    value=match.group(),
                    start=match.start(),
                    end=match.end()
                )
            )

    return detections

# Email detection

def find_emails(text: str) -> list[Detection]:
    """
    Finds email addresses using the documented structured pattern.
    """

    detections = []

    for match in EMAIL_PATTERN.finditer(text):
        detections.append(
            Detection(
                category="EMAIL",
                value=match.group(),
                start=match.start(),
                end=match.end()
            )
        )

    return detections

# Phone number detection

def find_phone_numbers(text: str) -> list[Detection]:
    """
    Finds phone numbers in the supported format:

    ###-###-####
    """

    detections = []

    for match in PHONE_PATTERN.finditer(text):
        detections.append(
            Detection(
                category="PHONE",
                value=match.group(),
                start=match.start(),
                end=match.end()
            )
        )

    return detections

# Main detector function

def detect_sensitive_info(
    text: str,
    names_file: Path = DEFAULT_NAMES_FILE,
    addresses_file: Path = DEFAULT_ADDRESSES_FILE
) -> list[Detection]:
    """
    Detects all supported sensitive information in the input text.

    Supported categories:
    - NAME
    - ADDRESS
    - EMAIL
    - PHONE

    NAME and ADDRESS use exact matching from local synthetic
    term lists.

    EMAIL and PHONE use structured regular-expression patterns.
    """

    names = load_terms(names_file)
    addresses = load_terms(addresses_file)

    detections = []

    # Detect names from synthetic term list
    detections.extend(
        find_exact_terms(
            text=text,
            terms=names,
            category="NAME"
        )
    )

    # Detect physical addresses from synthetic term list
    detections.extend(
        find_exact_terms(
            text=text,
            terms=addresses,
            category="ADDRESS"
        )
    )

    # Detect email addresses
    detections.extend(
        find_emails(text)
    )

    # Detect phone numbers
    detections.extend(
        find_phone_numbers(text)
    )

    # Sort detections by their location in the original text.
    # If two detections start in the same place, put the longer
    # detection first.
    detections.sort(
        key=lambda detection: (
            detection.start,
            -(detection.end - detection.start)
        )
    )

    return detections

# Optional standalone test

if __name__ == "__main__":

    sample_text = (
        "Jane Smith lives at "
        "123 Example Street, Sampletown, GA 30000. "
        "Contact Jane Smith at jane.smith@example.com "
        "or 478-555-1234."
    )

    results = detect_sensitive_info(sample_text)

    print("Detected sensitive information:\n")

    for result in results:
        print(
            f"Category: {result.category}\n"
            f"Value: {result.value}\n"
            f"Start: {result.start}\n"
            f"End: {result.end}\n"
        )