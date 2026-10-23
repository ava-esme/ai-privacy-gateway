import json

from pipeline import process_json_request


# =========================================================
# Main command-line program
# =========================================================

def main():
    """
    Reads one JSON request from standard input,
    processes it through the privacy gateway,
    and prints the JSON result.
    """

    print("AI Privacy Gateway")
    print("------------------")
    print("Enter a JSON request.")
    print()

    try:
        # Read one line of JSON input from the user.
        user_input = input()

        # Send the JSON text through the complete pipeline.
        result = process_json_request(user_input)

        # Print formatted JSON output.
        print()
        print(
            json.dumps(
                result,
                indent=4
            )
        )

    except KeyboardInterrupt:
        print("\nProgram cancelled.")

    except EOFError:
        print(
            json.dumps(
                {
                    "status": "error",
                    "request_id": None,
                    "error": {
                        "code": "INVALID_JSON",
                        "message": "No JSON input was provided."
                    }
                },
                indent=4
            )
        )


# =========================================================
# Run program
# =========================================================

if __name__ == "__main__":
    main()