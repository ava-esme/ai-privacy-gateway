import re
from collections import defaultdict

from policy import SUPPORTED_CATEGORIES


# =========================================================
# Request ID pattern
# =========================================================

REQUEST_ID_PATTERN = re.compile(
    r"^r[1-9]\d*$"
)


# =========================================================
# Request mapping
# =========================================================

class RequestMapping:
    """
    Stores placeholder mappings for one request only.

    Example:

    [[r1:NAME:1]] -> Jane Smith

    The mapping is created for one request and should be
    cleared after that request finishes.
    """

    def __init__(self, request_id: str):

        self._validate_request_id(
            request_id
        )

        self.request_id = request_id

        # Stores:
        #
        # [[r1:NAME:1]] -> Jane Smith
        #
        self.placeholder_to_value = {}

        # Stores:
        #
        # ("NAME", "Jane Smith") -> [[r1:NAME:1]]
        #
        # The category is included so the same text value
        # could belong to different categories without
        # sharing a placeholder.
        self.value_to_placeholder = {}

        # Separate index counter for each category.
        #
        # NAME -> 1
        # EMAIL -> 1
        # ADDRESS -> 2
        #
        self.category_counts = defaultdict(int)


    # =====================================================
    # Request ID validation
    # =====================================================

    def _validate_request_id(
        self,
        request_id: str
    ) -> None:
        """
        Validates the request ID.

        Valid:
        r1
        r2
        r25

        Invalid:
        r0
        R1
        request1
        """

        if not isinstance(
            request_id,
            str
        ):
            raise ValueError(
                "Request ID must be a string."
            )

        if REQUEST_ID_PATTERN.fullmatch(
            request_id
        ) is None:
            raise ValueError(
                "Request ID must use the format 'r' "
                "followed by a positive integer."
            )


    # =====================================================
    # Category validation
    # =====================================================

    def _validate_category(
        self,
        category: str
    ) -> str:
        """
        Verifies that the category is supported.
        """

        if not isinstance(
            category,
            str
        ):
            raise ValueError(
                "Sensitive-data category must be a string."
            )

        category = category.upper()

        if category not in SUPPORTED_CATEGORIES:
            raise ValueError(
                f"Unsupported sensitive-data category: "
                f"{category}"
            )

        return category


    # =====================================================
    # Create placeholder
    # =====================================================

    def _create_placeholder(
        self,
        category: str
    ) -> str:
        """
        Creates the next placeholder for a category.

        Example:

        [[r1:NAME:1]]
        """

        self.category_counts[
            category
        ] += 1

        index = self.category_counts[
            category
        ]

        return (
            f"[[{self.request_id}:"
            f"{category}:{index}]]"
        )


    # =====================================================
    # Get or create placeholder
    # =====================================================

    def get_or_create_placeholder(
        self,
        category: str,
        value: str
    ) -> str:
        """
        Returns an existing placeholder for a repeated value
        or creates a new placeholder for a new value.

        Example:

        First occurrence:

        Jane Smith
            ->
        [[r1:NAME:1]]

        Repeated occurrence:

        Jane Smith
            ->
        [[r1:NAME:1]]
        """

        category = self._validate_category(
            category
        )

        if not isinstance(
            value,
            str
        ):
            raise ValueError(
                "Sensitive value must be a string."
            )

        key = (
            category,
            value
        )

        # Reuse placeholder for repeated value.
        if key in self.value_to_placeholder:

            return self.value_to_placeholder[
                key
            ]

        # Create placeholder for a new value.
        placeholder = (
            self._create_placeholder(
                category
            )
        )

        self.value_to_placeholder[
            key
        ] = placeholder

        self.placeholder_to_value[
            placeholder
        ] = value

        return placeholder


    # =====================================================
    # Check placeholder
    # =====================================================

    def contains_placeholder(
        self,
        placeholder: str
    ) -> bool:
        """
        Returns True if this request issued the placeholder.
        """

        return (
            placeholder
            in self.placeholder_to_value
        )


    # =====================================================
    # Get original value
    # =====================================================

    def get_original_value(
        self,
        placeholder: str
    ) -> str | None:
        """
        Returns the original sensitive value for a valid
        placeholder.

        Returns None if the placeholder does not belong to
        this mapping.
        """

        return self.placeholder_to_value.get(
            placeholder
        )


    # =====================================================
    # Number of stored mappings
    # =====================================================

    def size(self) -> int:
        """
        Returns the number of unique placeholders currently
        stored for this request.
        """

        return len(
            self.placeholder_to_value
        )


    # =====================================================
    # Clear mapping
    # =====================================================

    def clear(self) -> None:
        """
        Releases all sensitive mapping information stored
        for this request.

        This should be called after the request finishes,
        whether the request succeeds or fails.
        """

        self.placeholder_to_value.clear()

        self.value_to_placeholder.clear()

        self.category_counts.clear()


# =========================================================
# Optional standalone tests
# =========================================================

if __name__ == "__main__":

    print("TEST 1 - CREATE REQUEST MAPPING")
    print("-------------------------------")

    request_map = RequestMapping(
        "r1"
    )

    name_1 = (
        request_map.get_or_create_placeholder(
            "NAME",
            "Jane Smith"
        )
    )

    email_1 = (
        request_map.get_or_create_placeholder(
            "EMAIL",
            "jane.smith@example.com"
        )
    )

    address_1 = (
        request_map.get_or_create_placeholder(
            "ADDRESS",
            "123 Example Street, Sampletown, GA 30000"
        )
    )

    phone_1 = (
        request_map.get_or_create_placeholder(
            "PHONE",
            "478-555-1234"
        )
    )

    print(name_1)
    print(email_1)
    print(address_1)
    print(phone_1)


    # -----------------------------------------------------
    # Test 2: Repeated value
    # -----------------------------------------------------

    print("\nTEST 2 - REPEATED VALUE")
    print("-----------------------")

    repeated_name = (
        request_map.get_or_create_placeholder(
            "NAME",
            "Jane Smith"
        )
    )

    print(
        f"First:    {name_1}"
    )

    print(
        f"Repeated: {repeated_name}"
    )

    print(
        "Same placeholder:",
        name_1 == repeated_name
    )


    # -----------------------------------------------------
    # Test 3: Different entity
    # -----------------------------------------------------

    print("\nTEST 3 - DIFFERENT ENTITY")
    print("-------------------------")

    name_2 = (
        request_map.get_or_create_placeholder(
            "NAME",
            "John Davis"
        )
    )

    print(
        f"Jane Smith: {name_1}"
    )

    print(
        f"John Davis: {name_2}"
    )


    # -----------------------------------------------------
    # Test 4: Local mapping contents
    # -----------------------------------------------------

    print("\nTEST 4 - LOCAL MAPPING")
    print("----------------------")

    for (
        placeholder,
        original_value
    ) in request_map.placeholder_to_value.items():

        print(
            f"{placeholder} -> "
            f"{original_value}"
        )


    # -----------------------------------------------------
    # Test 5: Independent request
    # -----------------------------------------------------

    print("\nTEST 5 - INDEPENDENT REQUEST")
    print("----------------------------")

    second_request = RequestMapping(
        "r2"
    )

    second_name = (
        second_request.get_or_create_placeholder(
            "NAME",
            "Maria Lopez"
        )
    )

    print(
        f"Request 1 placeholder: {name_1}"
    )

    print(
        f"Request 2 placeholder: {second_name}"
    )

    print(
        "Does r2 know r1 placeholder?",
        second_request.contains_placeholder(
            name_1
        )
    )


    # -----------------------------------------------------
    # Test 6: Release mapping
    # -----------------------------------------------------

    print("\nTEST 6 - RELEASE MAPPING")
    print("------------------------")

    print(
        "Mappings before clear:",
        request_map.size()
    )

    request_map.clear()

    print(
        "Mappings after clear:",
        request_map.size()
    )