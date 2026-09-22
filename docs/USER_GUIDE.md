# USER_GUIDE.md

## Current Version
Milestone 1

The full AI Privacy Gateway is not yet implemented.
The current version contains only a Tech Spike that verifies
the selected Python runtime and basic text input/output.

## Requirements
- Python 3.14.7

## Running the Tech Spike

From the project directory:

python tech_spike.py

## Example

Input:

Candidate has 3 years of Python experience.

Output:

Received text: Candidate has 3 years of Python experience.

## Planned M2 Usage

The M2 prototype will accept plain-text resume content and process it
through:

input → detection → masking → mock provider →
validation → restoration → output

## Supported Input
M1:
- Plain text entered through the command line

Planned for M2:
- Plain-text resume data

## Not Supported
- PDF files
- DOCX files
- Images
- OCR
- Multi-turn conversations
- Real applicant records

## Privacy Warning
Only synthetic data should be used during development and testing. Do not include any real personal information.

## Troubleshooting

### `python` command not found
Verify that Python is installed and available on the system PATH.

### Program exits immediately
Run the program from a terminal and enter text when prompted.