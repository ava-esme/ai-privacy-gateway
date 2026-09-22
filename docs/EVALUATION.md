# EVALUATION.md

## 1. Evaluation Goal
Verify that sensitive information remains local while the AI-assisted
resume analysis still produces useful output.

## 2. Planned Acceptance Cases

### Case 1: Normal Input

Input:
Jane Smith
jane.smith@email.com
478-555-1234
3 years of Python experience.

Expected masked text:
[[r1:NAME:1]]
[[r1:EMAIL:1]]
[[r1:PHONE:1]]
3 years of Python experience.

Expected behavior:
- All three sensitive values are masked.
- Skills and experience remain unchanged.

---

### Case 2: Repeated Sensitive Values

Input:
Jane Smith has Python experience.
Contact Jane Smith at jane.smith@email.com.

Expected behavior:
- Both occurrences of Jane Smith use the same placeholder.
- Jane Smith should not become two different entities.

---

### Case 3: No Sensitive Information

Input:
Candidate has 4 years of Python experience and experience with AWS.

Expected behavior:
- Input remains unchanged.
- No placeholder map entries are created.

---

### Case 4: Invalid Placeholder Response

Valid request contains:
[[r1:NAME:1]]

Mock provider returns:
[[r1:NAME:2]]

Expected behavior:
- Response is rejected or produces a controlled error.
- The program does not invent or restore a value.

## 3. Tech Spike
Command:
Enter resume text:

Input:
Candidate has 3 years of Python experience.

Observed output: 
Received text: Candidate has 3 years of Python experience.
Runtime version: 3.14.7 (main, Aug 14 2026, 15:39:58) [MSC v.1944 64 bit (AMD64)]

## 4. Current Limitations
For M1:
- Detection is not implemented yet.
- Placeholder validation is not implemented yet.
- Provider behavior is not implemented yet.
- Cases above are planned, not executed.