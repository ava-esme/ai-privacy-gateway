import unittest
from unittest.mock import patch

from detector import Detection, resolve_overlaps
from mapping import RequestMapping
from pipeline import process_request, process_json_request


class TestPrivacyGatewayM3(unittest.TestCase):

    # =====================================================
    # Test 1: Normal input
    # =====================================================

    def test_normal_input(self):

        request = {
            "request_id": "r1",
            "text": (
                "Jane Smith lives at "
                "123 Example Street, Sampletown, GA 30000. "
                "Contact Jane Smith at jane.smith@example.com "
                "or 478-555-1234."
            )
        }

        result = process_request(request)

        self.assertEqual(result["status"], "ok")

        self.assertIn(
            "[[r1:NAME:1]]",
            result["masked_text"]
        )

        self.assertIn(
            "[[r1:ADDRESS:1]]",
            result["masked_text"]
        )

        self.assertIn(
            "[[r1:EMAIL:1]]",
            result["masked_text"]
        )

        self.assertIn(
            "[[r1:PHONE:1]]",
            result["masked_text"]
        )

        # Original sensitive values should not reach provider.
        self.assertNotIn(
            "Jane Smith",
            result["provider_response"]
        )

        self.assertNotIn(
            "jane.smith@example.com",
            result["provider_response"]
        )

        self.assertNotIn(
            "478-555-1234",
            result["provider_response"]
        )

        # Values should be restored in final output.
        self.assertIn(
            "Jane Smith",
            result["output"]
        )

        self.assertIn(
            "jane.smith@example.com",
            result["output"]
        )


    # =====================================================
    # Test 2: Repeated sensitive value
    # =====================================================

    def test_repeated_sensitive_value(self):

        request = {
            "request_id": "r2",
            "text": (
                "Jane Smith has Python experience. "
                "Contact Jane Smith at "
                "jane.smith@example.com."
            )
        }

        result = process_request(request)

        self.assertEqual(
            result["status"],
            "ok"
        )

        self.assertEqual(
            result["masked_text"].count(
                "[[r2:NAME:1]]"
            ),
            2
        )

        self.assertNotIn(
            "[[r2:NAME:2]]",
            result["masked_text"]
        )


    # =====================================================
    # Test 3: No sensitive information
    # =====================================================

    def test_no_sensitive_information(self):

        original_text = (
            "Candidate has four years of Python "
            "experience and experience with AWS."
        )

        request = {
            "request_id": "r3",
            "text": original_text
        }

        result = process_request(request)

        self.assertEqual(
            result["status"],
            "ok"
        )

        self.assertEqual(
            result["masked_text"],
            original_text
        )

        self.assertNotIn(
            "[[",
            result["masked_text"]
        )


    # =====================================================
    # Test 4: Different entities
    # =====================================================

    def test_different_entities(self):

        request = {
            "request_id": "r4",
            "text": (
                "Jane Smith worked with John Davis "
                "on a Python project."
            )
        }

        result = process_request(request)

        self.assertEqual(
            result["status"],
            "ok"
        )

        self.assertIn(
            "[[r4:NAME:1]]",
            result["masked_text"]
        )

        self.assertIn(
            "[[r4:NAME:2]]",
            result["masked_text"]
        )

        self.assertIn(
            "Jane Smith",
            result["output"]
        )

        self.assertIn(
            "John Davis",
            result["output"]
        )


    # =====================================================
    # Test 5: Longer overlapping detection wins
    # =====================================================

    def test_overlap_longer_match_wins(self):

        detections = [
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

        result = resolve_overlaps(
            detections
        )

        self.assertEqual(
            len(result),
            1
        )

        self.assertEqual(
            result[0].value,
            (
                "123 Example Street, "
                "Sampletown, GA 30000"
            )
        )


    # =====================================================
    # Test 6: Earlier overlapping detection wins
    # =====================================================

    def test_overlap_earlier_start_wins(self):

        detections = [
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

        result = resolve_overlaps(
            detections
        )

        self.assertEqual(
            len(result),
            1
        )

        self.assertEqual(
            result[0].category,
            "ADDRESS"
        )


    # =====================================================
    # Test 7: Missing policies default to MASK
    # =====================================================

    def test_missing_policies_default_to_mask(self):

        request = {
            "request_id": "r7",
            "text": (
                "Jane Smith can be reached at "
                "jane.smith@example.com or "
                "478-555-1234."
            ),
            "policies": {
                "EMAIL": "REMOVE"
            }
        }

        result = process_request(request)

        self.assertEqual(
            result["status"],
            "ok"
        )

        # NAME and PHONE were not specified,
        # so they should default to MASK.
        self.assertIn(
            "[[r7:NAME:1]]",
            result["masked_text"]
        )

        self.assertIn(
            "[[r7:PHONE:1]]",
            result["masked_text"]
        )

        # EMAIL was explicitly REMOVE.
        self.assertNotIn(
            "jane.smith@example.com",
            result["masked_text"]
        )

        self.assertNotIn(
            "[[r7:EMAIL:1]]",
            result["masked_text"]
        )


    # =====================================================
    # Test 8: REMOVE policy
    # =====================================================

    def test_remove_policy(self):

        request = {
            "request_id": "r8",
            "text": (
                "Jane Smith can be reached at "
                "jane.smith@example.com."
            ),
            "policies": {
                "NAME": "MASK",
                "EMAIL": "REMOVE"
            }
        }

        result = process_request(request)

        self.assertEqual(
            result["status"],
            "ok"
        )

        # Name is masked.
        self.assertIn(
            "[[r8:NAME:1]]",
            result["masked_text"]
        )

        # Email is removed completely.
        self.assertNotIn(
            "jane.smith@example.com",
            result["masked_text"]
        )

        self.assertNotIn(
            "[[r8:EMAIL:1]]",
            result["masked_text"]
        )

        # Removed value must not reappear after restoration.
        self.assertNotIn(
            "jane.smith@example.com",
            result["output"]
        )


    # =====================================================
    # Test 9: Invalid policy
    # =====================================================

    def test_invalid_policy(self):

        request = {
            "request_id": "r9",
            "text": "Jane Smith has Python experience.",
            "policies": {
                "NAME": "HIDE"
            }
        }

        result = process_request(request)

        self.assertEqual(
            result["status"],
            "error"
        )

        self.assertEqual(
            result["error"]["code"],
            "INVALID_POLICY"
        )


    # =====================================================
    # Test 10: Unknown placeholder
    # =====================================================

    def test_unknown_placeholder(self):

        request = {
            "request_id": "r10",
            "text": "Jane Smith has Python experience."
        }

        result = process_request(
            request,
            provider_mode="unknown_placeholder"
        )

        self.assertEqual(
            result["status"],
            "error"
        )

        self.assertEqual(
            result["error"]["code"],
            "UNKNOWN_PLACEHOLDER"
        )

        self.assertNotIn(
            "output",
            result
        )


    # =====================================================
    # Test 11: Malformed placeholder
    # =====================================================

    def test_malformed_placeholder(self):

        request = {
            "request_id": "r11",
            "text": "Jane Smith has Python experience."
        }

        result = process_request(
            request,
            provider_mode="malformed_placeholder"
        )

        self.assertEqual(
            result["status"],
            "error"
        )

        self.assertEqual(
            result["error"]["code"],
            "INVALID_PLACEHOLDER"
        )


    # =====================================================
    # Test 12: Foreign-request placeholder
    # =====================================================

    def test_foreign_request_placeholder(self):

        request = {
            "request_id": "r12",
            "text": "Jane Smith has Python experience."
        }

        result = process_request(
            request,
            provider_mode="foreign_placeholder"
        )

        self.assertEqual(
            result["status"],
            "error"
        )

        self.assertEqual(
            result["error"]["code"],
            "FOREIGN_REQUEST_PLACEHOLDER"
        )

        self.assertNotIn(
            "output",
            result
        )


    # =====================================================
    # Test 13: Independent requests
    # =====================================================

    def test_independent_requests(self):

        request_1 = {
            "request_id": "r13",
            "text": "Jane Smith has Python experience."
        }

        request_2 = {
            "request_id": "r14",
            "text": "John Davis has Java experience."
        }

        result_1 = process_request(
            request_1
        )

        result_2 = process_request(
            request_2
        )

        self.assertEqual(
            result_1["status"],
            "ok"
        )

        self.assertEqual(
            result_2["status"],
            "ok"
        )

        self.assertIn(
            "[[r13:NAME:1]]",
            result_1["masked_text"]
        )

        self.assertIn(
            "[[r14:NAME:1]]",
            result_2["masked_text"]
        )

        # One request's placeholder should not appear
        # in the other request.
        self.assertNotIn(
            "[[r13:NAME:1]]",
            result_2["masked_text"]
        )

        self.assertNotIn(
            "[[r14:NAME:1]]",
            result_1["masked_text"]
        )


    # =====================================================
    # Test 14: Mapping clear
    # =====================================================

    def test_mapping_clear(self):

        request_map = RequestMapping(
            "r15"
        )

        request_map.get_or_create_placeholder(
            "NAME",
            "Jane Smith"
        )

        request_map.get_or_create_placeholder(
            "EMAIL",
            "jane.smith@example.com"
        )

        self.assertEqual(
            request_map.size(),
            2
        )

        request_map.clear()

        self.assertEqual(
            request_map.size(),
            0
        )


    # =====================================================
    # Test 15: Pipeline calls mapping cleanup
    # =====================================================

    def test_pipeline_releases_mapping(self):

        request = {
            "request_id": "r16",
            "text": "Jane Smith has Python experience."
        }

        with patch.object(
            RequestMapping,
            "clear",
            autospec=True
        ) as mock_clear:

            result = process_request(
                request
            )

            self.assertEqual(
                result["status"],
                "ok"
            )

            # validate_request() clears its temporary
            # validation object, and process_request()
            # clears the actual request mapping in finally.
            self.assertGreaterEqual(
                mock_clear.call_count,
                2
            )


    # =====================================================
    # Test 16: Reserved placeholder in input
    # =====================================================

    def test_reserved_placeholder_in_input(self):

        request = {
            "request_id": "r17",
            "text": (
                "Jane Smith worked on "
                "[[r17:NAME:1]]."
            )
        }

        result = process_request(
            request
        )

        self.assertEqual(
            result["status"],
            "error"
        )

        self.assertEqual(
            result["error"]["code"],
            "RESERVED_PLACEHOLDER_IN_INPUT"
        )


    # =====================================================
    # Test 17: Provider failure
    # =====================================================

    def test_provider_error(self):

        request = {
            "request_id": "r18",
            "text": "Jane Smith has Python experience."
        }

        result = process_request(
            request,
            provider_mode="provider_error"
        )

        self.assertEqual(
            result["status"],
            "error"
        )

        self.assertEqual(
            result["error"]["code"],
            "PROVIDER_ERROR"
        )

        self.assertNotIn(
            "output",
            result
        )


    # =====================================================
    # Test 18: Provider timeout
    # =====================================================

    def test_provider_timeout(self):

        request = {
            "request_id": "r19",
            "text": "Jane Smith has Python experience."
        }

        result = process_request(
            request,
            provider_mode="provider_timeout"
        )

        self.assertEqual(
            result["status"],
            "error"
        )

        self.assertEqual(
            result["error"]["code"],
            "PROVIDER_TIMEOUT"
        )

        self.assertNotIn(
            "output",
            result
        )


    # =====================================================
    # Test 19: Malformed provider response
    # =====================================================

    def test_malformed_provider_response(self):

        request = {
            "request_id": "r20",
            "text": "Jane Smith has Python experience."
        }

        result = process_request(
            request,
            provider_mode="malformed_response"
        )

        self.assertEqual(
            result["status"],
            "error"
        )

        self.assertEqual(
            result["error"]["code"],
            "MALFORMED_PROVIDER_RESPONSE"
        )

        self.assertNotIn(
            "output",
            result
        )


    # =====================================================
    # Test 20: Invalid JSON
    # =====================================================

    def test_invalid_json(self):

        invalid_json = """
        {
            "request_id": "r21",
            "text": "Jane Smith"
        """

        result = process_json_request(
            invalid_json
        )

        self.assertEqual(
            result["status"],
            "error"
        )

        self.assertEqual(
            result["error"]["code"],
            "INVALID_JSON"
        )

    # =====================================================
    # Test 21: Missing placeholder
    # =====================================================

    def test_missing_placeholder(self):

        request = {
            "request_id": "r22",
            "text": "Jane Smith has Python experience."
        }

        result = process_request(
            request,
            provider_mode="missing_placeholder"
        )

        self.assertEqual(
            result["status"],
            "ok"
        )

        # Provider omitted the issued placeholder.
        self.assertNotIn(
            "[[r22:NAME:1]]",
            result["provider_response"]
        )

        # Because the placeholder was omitted, Jane Smith
        # cannot be restored.
        self.assertNotIn(
            "Jane Smith",
            result["output"]
        )


    # =====================================================
    # Test 22: Modified placeholder
    # =====================================================

    def test_modified_placeholder(self):

        request = {
            "request_id": "r23",
            "text": "Jane Smith has Python experience."
        }

        result = process_request(
            request,
            provider_mode="modified_placeholder"
        )

        self.assertEqual(
            result["status"],
            "error"
        )

        self.assertEqual(
            result["error"]["code"],
            "UNKNOWN_PLACEHOLDER"
        )

        self.assertNotIn(
            "output",
            result
        )


if __name__ == "__main__":
    unittest.main()