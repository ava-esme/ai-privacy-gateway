# =========================================================
# Supported categories and policy values
# =========================================================

SUPPORTED_CATEGORIES = {
    "NAME",
    "EMAIL",
    "PHONE",
    "ADDRESS"
}

VALID_POLICIES = {
    "MASK",
    "REMOVE"
}

DEFAULT_POLICY = "MASK"


# =========================================================
# Policy error
# =========================================================

class PolicyError(Exception):
    """
    Represents a controlled policy-related error.

    The error code can later be returned through the
    pipeline's JSON error response.
    """

    def __init__(self, code: str, message: str):
        super().__init__(message)

        self.code = code
        self.message = message


# =========================================================
# Validate and complete policy configuration
# =========================================================

def resolve_policies(
    policies: dict | None
) -> dict[str, str]:
    """
    Validates the policy configuration and returns a complete
    policy dictionary for all supported categories.

    Rules:

    1. If no policies are provided, every category defaults
       to MASK.

    2. If a category is missing from the supplied dictionary,
       that category defaults to MASK.

    3. Only MASK and REMOVE are valid policy values.

    4. Only supported sensitive-data categories may appear.

    Example input:

    {
        "NAME": "MASK",
        "EMAIL": "REMOVE"
    }

    Example result:

    {
        "NAME": "MASK",
        "EMAIL": "REMOVE",
        "PHONE": "MASK",
        "ADDRESS": "MASK"
    }
    """

    # -----------------------------------------------------
    # No policy configuration supplied
    # -----------------------------------------------------

    if policies is None:

        return {
            category: DEFAULT_POLICY
            for category in SUPPORTED_CATEGORIES
        }

    # -----------------------------------------------------
    # Policies must be a dictionary
    # -----------------------------------------------------

    if not isinstance(policies, dict):

        raise PolicyError(
            code="INVALID_POLICY",
            message=(
                "'policies' must be a JSON object containing "
                "category-to-policy mappings."
            )
        )

    # -----------------------------------------------------
    # Begin with the default policy for every category
    # -----------------------------------------------------

    resolved = {
        category: DEFAULT_POLICY
        for category in SUPPORTED_CATEGORIES
    }

    # -----------------------------------------------------
    # Validate supplied policy entries
    # -----------------------------------------------------

    for category, policy in policies.items():

        # Normalize category name
        if not isinstance(category, str):

            raise PolicyError(
                code="INVALID_POLICY",
                message=(
                    "Policy category names must be strings."
                )
            )

        category = category.upper()

        # Category must be supported
        if category not in SUPPORTED_CATEGORIES:

            raise PolicyError(
                code="INVALID_POLICY",
                message=(
                    f"Unsupported policy category: {category}"
                )
            )

        # Policy value must be a string
        if not isinstance(policy, str):

            raise PolicyError(
                code="INVALID_POLICY",
                message=(
                    f"Policy for {category} must be "
                    "'MASK' or 'REMOVE'."
                )
            )

        # Normalize policy value
        policy = policy.upper()

        # Policy value must be valid
        if policy not in VALID_POLICIES:

            raise PolicyError(
                code="INVALID_POLICY",
                message=(
                    f"Invalid policy '{policy}' for "
                    f"{category}. Expected MASK or REMOVE."
                )
            )

        resolved[category] = policy

    return resolved


# =========================================================
# Get policy for one category
# =========================================================

def get_policy(
    category: str,
    resolved_policies: dict[str, str]
) -> str:
    """
    Returns the policy for one sensitive-data category.

    Missing categories default to MASK as an additional
    safety measure.
    """

    if not isinstance(category, str):

        raise PolicyError(
            code="INVALID_POLICY",
            message="Sensitive-data category must be a string."
        )

    category = category.upper()

    if category not in SUPPORTED_CATEGORIES:

        raise PolicyError(
            code="INVALID_POLICY",
            message=(
                f"Unsupported sensitive-data category: {category}"
            )
        )

    return resolved_policies.get(
        category,
        DEFAULT_POLICY
    )


# =========================================================
# Optional standalone tests
# =========================================================

if __name__ == "__main__":

    # -----------------------------------------------------
    # Test 1: No policies supplied
    # -----------------------------------------------------

    print("TEST 1 - DEFAULT POLICIES")
    print("-------------------------")

    try:

        result = resolve_policies(None)

        for category in sorted(result):
            print(
                f"{category}: {result[category]}"
            )

    except PolicyError as error:
        print(f"Error code: {error.code}")
        print(f"Message: {error.message}")

    # -----------------------------------------------------
    # Test 2: Mixed MASK and REMOVE policies
    # -----------------------------------------------------

    print("\nTEST 2 - MIXED POLICIES")
    print("-----------------------")

    try:

        policies = {
            "NAME": "MASK",
            "EMAIL": "REMOVE"
        }

        result = resolve_policies(
            policies
        )

        for category in sorted(result):
            print(
                f"{category}: {result[category]}"
            )

    except PolicyError as error:
        print(f"Error code: {error.code}")
        print(f"Message: {error.message}")

    # -----------------------------------------------------
    # Test 3: Invalid policy value
    # -----------------------------------------------------

    print("\nTEST 3 - INVALID POLICY")
    print("-----------------------")

    try:

        policies = {
            "NAME": "HIDE"
        }

        result = resolve_policies(
            policies
        )

        print(result)

    except PolicyError as error:
        print(f"Error code: {error.code}")
        print(f"Message: {error.message}")

    # -----------------------------------------------------
    # Test 4: Unsupported category
    # -----------------------------------------------------

    print("\nTEST 4 - UNSUPPORTED CATEGORY")
    print("-----------------------------")

    try:

        policies = {
            "SSN": "MASK"
        }

        result = resolve_policies(
            policies
        )

        print(result)

    except PolicyError as error:
        print(f"Error code: {error.code}")
        print(f"Message: {error.message}")