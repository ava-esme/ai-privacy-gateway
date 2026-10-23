# USER_GUIDE.md

## 1. Overview

The AI Privacy Gateway is a command-line program that protects selected sensitive information before a resume is processed by an AI-style provider.

For Milestone 2, the program uses a deterministic offline mock provider rather than a live AI service.

The gateway processes one request through the following pipeline:

`Input -> Detection -> Masking -> Offline Mock Provider -> Validation -> Restoration -> Output`

The program currently supports four categories of sensitive information:

- Name
- Email address
- Phone number
- Physical address

Only synthetic data should be used with the current prototype.

---

## 2. Requirements

The program requires:

- Python 3.13.7
- A command-line terminal
- The project files and synthetic data files

The Python version installed on the system can be checked with:

```bash
python --version
```

---

## 3. Project Files

The main project files are:

```text
ai-privacy-gateway/
|
|-- data/
|   |-- synthetic_names.txt
|   |-- synthetic_addresses.txt
|
|-- docs/
|   |-- ASSISTANCE.md
|   |-- DESIGN.md
|   |-- EVALUATION.md
|   |-- USER_GUIDE.md
|
|-- tests/
|   |-- test_pipeline.py
|
|-- detector.py
|-- masker.py
|-- mock_provider.py
|-- validator.py
|-- restorer.py
|-- pipeline.py
|-- main.py
|-- README.md
```

---

## 4. Running the Program

Open a terminal in the project directory.

Run:

```bash
python main.py
```

The program will display:

```text
AI Privacy Gateway
------------------
Enter a JSON request.
```

Enter the JSON request on one line.

Example:

```json
{"request_id":"r1","text":"Jane Smith lives at 123 Example Street, Sampletown, GA 30000. Jane Smith has 3 years of Python experience. Contact Jane Smith at jane.smith@example.com or 478-555-1234."}
```

Press Enter to process the request.

---

## 5. JSON Input Format

The program accepts one JSON object with two required fields:

```json
{
  "request_id": "r1",
  "text": "resume text"
}
```

### `request_id`

The request ID must:

- be a string;
- begin with the lowercase letter `r`; and
- be followed by a positive integer.

Valid examples:

```text
r1
r2
r15
```

Invalid examples:

```text
r0
R1
request1
```

### `text`

The `text` field contains the plain-text synthetic resume information to process.

The field must:

- be present;
- be a string; and
- not be empty.

---

## 6. Successful Output

A successful request returns JSON similar to:

```json
{
    "status": "ok",
    "request_id": "r1",
    "masked_text": "[[r1:NAME:1]] has 3 years of Python experience.",
    "provider_response": "Qualification Summary:\n[[r1:NAME:1]] has 3 years of Python experience.",
    "output": "Qualification Summary:\nJane Smith has 3 years of Python experience."
}
```

The fields mean:

### `status`

Indicates whether the request succeeded.

A successful request returns:

```text
ok
```

### `request_id`

The ID supplied with the original request.

### `masked_text`

The resume text after supported sensitive values have been replaced with placeholders.

### `provider_response`

The response returned by the offline mock provider.

This response should contain placeholders rather than the original sensitive values.

### `output`

The final locally restored response.

Valid placeholders are replaced with their original values only after validation succeeds.

---

## 7. Supported Sensitive Information

### Names

Names are detected using exact matching against:

```text
data/synthetic_names.txt
```

Example:

```text
Jane Smith
```

becomes:

```text
[[r1:NAME:1]]
```

Only names contained in the synthetic term list are detected.

---

### Physical Addresses

Physical addresses are detected using exact matching against:

```text
data/synthetic_addresses.txt
```

Example:

```text
123 Example Street, Sampletown, GA 30000
```

becomes:

```text
[[r1:ADDRESS:1]]
```

Only addresses contained in the synthetic term list are detected.

---

### Email Addresses

Email addresses are detected using a structured regular-expression pattern.

Example:

```text
jane.smith@example.com
```

becomes:

```text
[[r1:EMAIL:1]]
```

---

### Phone Numbers

The current prototype supports phone numbers using the format:

```text
###-###-####
```

Example:

```text
478-555-1234
```

becomes:

```text
[[r1:PHONE:1]]
```

Other phone-number formats may not be detected.

---

## 8. Repeated Sensitive Values

Repeated occurrences of the same sensitive value use the same placeholder within a request.

Example input:

```text
Jane Smith has Python experience. Contact Jane Smith at jane.smith@example.com.
```

Masked result:

```text
[[r1:NAME:1]] has Python experience. Contact [[r1:NAME:1]] at [[r1:EMAIL:1]].
```

Both occurrences of `Jane Smith` use:

```text
[[r1:NAME:1]]
```

---

## 9. Different Sensitive Values

Different values within the same category receive different placeholder numbers.

Example:

```text
Jane Smith worked with John Davis.
```

becomes:

```text
[[r1:NAME:1]] worked with [[r1:NAME:2]].
```

---

## 10. Error Responses

Errors are returned using JSON.

Example:

```json
{
    "status": "error",
    "request_id": "r1",
    "error": {
        "code": "UNKNOWN_PLACEHOLDER",
        "message": "Provider response contained an unknown placeholder."
    }
}
```

The Milestone 2 prototype supports the following controlled error codes.

### `INVALID_JSON`

The input could not be parsed as valid JSON.

### `INVALID_REQUEST`

The JSON request is missing a required field or contains an invalid value.

### `RESERVED_PLACEHOLDER_IN_INPUT`

The original input contains syntax reserved for gateway-generated placeholders.

Users should not include values such as:

```text
[[r1:NAME:1]]
```

in the original resume text.

### `INVALID_PLACEHOLDER`

The provider returned malformed placeholder syntax.

Example:

```text
[[r1:NAME]]
```

### `UNKNOWN_PLACEHOLDER`

The provider returned a valid-looking placeholder that was not issued for the current request.

Example:

```text
[[r1:NAME:999]]
```

### `PROVIDER_ERROR`

The offline mock provider reported a simulated failure.

---

## 11. Running the Automated Tests

From the project root, run:

```bash
python -m unittest discover -s tests -v
```

A successful test run should end with:

```text
Ran 10 tests

OK
```

The test suite currently checks:

- normal input;
- repeated sensitive values;
- no sensitive information;
- unknown placeholders;
- malformed placeholders;
- different entities;
- reserved placeholder syntax;
- provider failure;
- invalid JSON; and
- missing required fields.

---

## 12. Supported Input

Milestone 2 supports:

- plain-text resume content;
- JSON command-line requests;
- synthetic names;
- synthetic physical addresses;
- supported email formats; and
- phone numbers in `###-###-####` format.

---

## 13. Unsupported Features

The current prototype does not support:

- PDF files;
- DOCX files;
- images;
- OCR;
- live AI APIs;
- graphical interfaces;
- multi-turn conversations;
- every possible name or address;
- every possible phone-number format;
- MASK/REMOVE category policy; or
- cross-request isolation testing.

---

## 14. Privacy Warning

Use synthetic data only.

Do not enter or commit:

- real applicant information;
- real employee records;
- Social Security numbers;
- passwords;
- API keys;
- live credentials; or
- other private or confidential records.

The current system is a course prototype and is not intended for production use.

---

## 15. Troubleshooting

### Python is not recognized

Run:

```bash
python --version
```

If Python is installed but the command is not recognized, verify that Python has been added to the system PATH and restart the terminal or Visual Studio Code.

---

### Synthetic data file not found

Verify that these files exist:

```text
data/synthetic_names.txt
data/synthetic_addresses.txt
```

Also verify that the filenames exactly match the names expected by `detector.py`.

---

### A name is not masked

Verify that the exact name appears in:

```text
data/synthetic_names.txt
```

Name matching is currently exact and case-sensitive.

---

### An address is not masked

Verify that the exact address appears in:

```text
data/synthetic_addresses.txt
```

Address matching is currently exact and case-sensitive.

---

### A phone number is not masked

Verify that it uses the supported format:

```text
###-###-####
```

Example:

```text
478-555-1234
```

---

### The program returns `RESERVED_PLACEHOLDER_IN_INPUT`

The original input contains `[[...]]` syntax reserved for the privacy gateway.

Remove the reserved placeholder syntax from the input and try again.

---

### Tests fail

Run:

```bash
python -m unittest discover -s tests -v
```

Review the failing test name and error message.

Also verify that:

- `Jane Smith` exists in `synthetic_names.txt`;
- `John Davis` exists in `synthetic_names.txt`;
- the expected synthetic address exists in `synthetic_addresses.txt`; and
- all required Python files are in the project root.