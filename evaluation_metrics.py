from detector import detect_sensitive_info
from pipeline import process_request


# =========================================================
# Build expected detection records
# =========================================================

def build_expected_detections(
    text: str,
    labeled_values: list[tuple[str, str]]
) -> set[tuple[str, str, int, int]]:
    """
    Creates the expected detection set for a labeled
    synthetic test case.

    Each record contains:

    category
    value
    start
    end

    Every occurrence of a labeled value is included.
    """

    expected = set()

    # Remove duplicate category/value entries while
    # preserving order.
    unique_values = list(
        dict.fromkeys(labeled_values)
    )

    for category, value in unique_values:

        start = 0

        while True:

            position = text.find(
                value,
                start
            )

            if position == -1:
                break

            expected.add(
                (
                    category,
                    value,
                    position,
                    position + len(value)
                )
            )

            start = position + len(value)

    return expected


# =========================================================
# Convert actual detections to comparable records
# =========================================================

def build_actual_detections(
    text: str
) -> set[tuple[str, str, int, int]]:
    """
    Runs detector.py and converts its output into a set
    that can be compared with the expected detections.
    """

    detections = detect_sensitive_info(
        text
    )

    return {
        (
            detection.category,
            detection.value,
            detection.start,
            detection.end
        )
        for detection in detections
    }


# =========================================================
# Count outbound privacy leaks
# =========================================================

def count_outbound_leaks(
    outbound_text: str,
    labeled_values: list[tuple[str, str]]
) -> int:
    """
    Counts occurrences of protected original values that
    remain in the outbound masked text.

    Any original protected value that remains visible in the
    outbound payload counts as a privacy leak.
    """

    leak_count = 0

    unique_values = {
        value
        for _, value in labeled_values
    }

    for value in unique_values:

        leak_count += outbound_text.count(
            value
        )

    return leak_count


# =========================================================
# Calculate precision and recall
# =========================================================

def calculate_precision(
    tp: int,
    fp: int
):
    """
    Precision = TP / (TP + FP)
    """

    denominator = tp + fp

    if denominator == 0:
        return None

    return tp / denominator


def calculate_recall(
    tp: int,
    fn: int
):
    """
    Recall = TP / (TP + FN)
    """

    denominator = tp + fn

    if denominator == 0:
        return None

    return tp / denominator


# =========================================================
# Synthetic evaluation cases
# =========================================================

EVALUATION_CASES = [

    # -----------------------------------------------------
    # Case 1: Standard supported formats
    # -----------------------------------------------------

    {
        "name": "Normal supported input",

        "request_id": "r101",

        "text": (
            "Jane Smith lives at "
            "123 Example Street, Sampletown, GA 30000. "
            "Contact Jane Smith at "
            "jane.smith@example.com or "
            "478-555-1234."
        ),

        "expected": [
            (
                "NAME",
                "Jane Smith"
            ),
            (
                "ADDRESS",
                "123 Example Street, Sampletown, GA 30000"
            ),
            (
                "EMAIL",
                "jane.smith@example.com"
            ),
            (
                "PHONE",
                "478-555-1234"
            )
        ]
    },

    # -----------------------------------------------------
    # Case 2: Repeated value and punctuation
    # -----------------------------------------------------

    {
        "name": "Repeated value with punctuation",

        "request_id": "r102",

        "text": (
            "Jane Smith, an experienced developer, "
            "worked on a Python project. "
            "Contact Jane Smith at "
            "jane.smith@example.com."
        ),

        "expected": [
            (
                "NAME",
                "Jane Smith"
            ),
            (
                "EMAIL",
                "jane.smith@example.com"
            )
        ]
    },

    # -----------------------------------------------------
    # Case 3: Unicode text
    # -----------------------------------------------------

    {
        "name": "Unicode text",

        "request_id": "r103",

        "text": (
            "Résumé for Maria Lopez — "
            "experienced in Python and SQL. "
            "Email: maria.lopez@example.com."
        ),

        "expected": [
            (
                "NAME",
                "Maria Lopez"
            ),
            (
                "EMAIL",
                "maria.lopez@example.com"
            )
        ]
    },

    # -----------------------------------------------------
    # Case 4: Known detection limitation
    # -----------------------------------------------------
    #
    # The M3 implementation documents phone support as
    # ###-###-####.
    #
    # This case intentionally uses another common phone
    # format to measure the limitation honestly.
    # -----------------------------------------------------

    {
        "name": "Unsupported phone format limitation",

        "request_id": "r104",

        "text": (
            "Candidate can be reached at "
            "(478) 555-0199."
        ),

        "expected": [
            (
                "PHONE",
                "(478) 555-0199"
            )
        ]
    }
]


# =========================================================
# Run evaluation
# =========================================================

def run_evaluation():

    total_tp = 0
    total_fp = 0
    total_fn = 0
    total_leaks = 0

    print("AI PRIVACY GATEWAY - M3 DETECTION EVALUATION")
    print("=============================================")

    for case in EVALUATION_CASES:

        print()
        print(case["name"])
        print("-" * len(case["name"]))

        text = case["text"]

        expected = build_expected_detections(
            text,
            case["expected"]
        )

        actual = build_actual_detections(
            text
        )

        # -------------------------------------------------
        # Detection metrics
        # -------------------------------------------------

        true_positives = (
            actual & expected
        )

        false_positives = (
            actual - expected
        )

        false_negatives = (
            expected - actual
        )

        tp = len(
            true_positives
        )

        fp = len(
            false_positives
        )

        fn = len(
            false_negatives
        )

        precision = calculate_precision(
            tp,
            fp
        )

        recall = calculate_recall(
            tp,
            fn
        )

        # -------------------------------------------------
        # Run full gateway
        # -------------------------------------------------

        request = {
            "request_id": case["request_id"],
            "text": text
        }

        result = process_request(
            request
        )

        # -------------------------------------------------
        # Privacy leak measurement
        # -------------------------------------------------

        if result["status"] == "ok":

            outbound_text = result[
                "masked_text"
            ]

            leaks = count_outbound_leaks(
                outbound_text,
                case["expected"]
            )

        else:

            leaks = 0

        # -------------------------------------------------
        # Print case results
        # -------------------------------------------------

        print(
            f"TP: {tp}"
        )

        print(
            f"FP: {fp}"
        )

        print(
            f"FN: {fn}"
        )

        if precision is None:

            print(
                "Precision: N/A"
            )

        else:

            print(
                f"Precision: "
                f"{precision:.3f}"
            )

        if recall is None:

            print(
                "Recall: N/A"
            )

        else:

            print(
                f"Recall: "
                f"{recall:.3f}"
            )

        print(
            f"Outbound privacy leaks: {leaks}"
        )

        # Show failures so they can be documented.
        if false_positives:

            print(
                "False positives:"
            )

            for item in sorted(
                false_positives
            ):
                print(
                    f"  {item}"
                )

        if false_negatives:

            print(
                "False negatives:"
            )

            for item in sorted(
                false_negatives
            ):
                print(
                    f"  {item}"
                )

        # -------------------------------------------------
        # Add to totals
        # -------------------------------------------------

        total_tp += tp
        total_fp += fp
        total_fn += fn
        total_leaks += leaks

    # =====================================================
    # Overall results
    # =====================================================

    overall_precision = calculate_precision(
        total_tp,
        total_fp
    )

    overall_recall = calculate_recall(
        total_tp,
        total_fn
    )

    print()
    print("OVERALL RESULTS")
    print("===============")

    print(
        f"TP: {total_tp}"
    )

    print(
        f"FP: {total_fp}"
    )

    print(
        f"FN: {total_fn}"
    )

    if overall_precision is None:

        print(
            "Precision: N/A"
        )

    else:

        print(
            f"Precision: "
            f"{overall_precision:.3f}"
        )

    if overall_recall is None:

        print(
            "Recall: N/A"
        )

    else:

        print(
            f"Recall: "
            f"{overall_recall:.3f}"
        )

    print(
        f"Outbound privacy leaks: "
        f"{total_leaks}"
    )


# =========================================================
# Main
# =========================================================

if __name__ == "__main__":
    run_evaluation()