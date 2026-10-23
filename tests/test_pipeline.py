import unittest

from pipeline import process_request, process_json_request


class TestPrivacyGatewayPipeline(unittest.TestCase):

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

        self.assertEqual(
            result["status"],
            "ok"
        )

        self.assertEqual(
            result["request_id"],
            "r1"
        )

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

        # Sensitive values should not appear in the
        # provider response.
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

        self.assertIn(
            "478-555-1234",
            result["output"]
        )


    # =====================================================
    # Test 2: Repeated sensitive values
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

        # Jane Smith appears twice and should use the
        # same placeholder both times.
        self.assertEqual(
            result["masked_text"].count(
                "[[r2:NAME:1]]"
            ),
            2
        )

        # A second NAME placeholder should not be created.
        self.assertNotIn(
            "[[r2:NAME:2]]",
            result["masked_text"]
        )


    # =====================================================
    # Test 3: No sensitive information
    # =====================================================

    def test_no_sensitive_information(self):

        original_text = (
            "Candidate has four years of Python experience "
            "and experience with AWS."
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

        # Nothing should be changed.
        self.assertEqual(
            result["masked_text"],
            original_text
        )

        # No placeholders should appear.
        self.assertNotIn(
            "[[",
            result["masked_text"]
        )


    # =====================================================
    # Test 4: Unknown placeholder
    # =====================================================

    def test_unknown_placeholder_response(self):

        request = {
            "request_id": "r4",
            "text": (
                "Jane Smith has three years of "
                "Python experience."
            )
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

        # Final restored output should not be produced.
        self.assertNotIn(
            "output",
            result
        )


    # =====================================================
    # Test 5: Malformed placeholder
    # =====================================================

    def test_malformed_placeholder_response(self):

        request = {
            "request_id": "r5",
            "text": (
                "Jane Smith has three years of "
                "Python experience."
            )
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

        self.assertNotIn(
            "output",
            result
        )


    # =====================================================
    # Test 6: Different entities in one request
    # =====================================================

    def test_different_entities(self):

        request = {
            "request_id": "r6",
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

        # Different people should receive different
        # placeholders.
        self.assertIn(
            "[[r6:NAME:1]]",
            result["masked_text"]
        )

        self.assertIn(
            "[[r6:NAME:2]]",
            result["masked_text"]
        )

        # Both names should be restored in final output.
        self.assertIn(
            "Jane Smith",
            result["output"]
        )

        self.assertIn(
            "John Davis",
            result["output"]
        )


    # =====================================================
    # Test 7: Reserved placeholder in original input
    # =====================================================

    def test_reserved_placeholder_in_input(self):

        request = {
            "request_id": "r7",
            "text": (
                "Jane Smith worked on "
                "[[r7:NAME:1]]."
            )
        }

        result = process_request(request)

        self.assertEqual(
            result["status"],
            "error"
        )

        self.assertEqual(
            result["error"]["code"],
            "RESERVED_PLACEHOLDER_IN_INPUT"
        )


    # =====================================================
    # Test 8: Provider failure
    # =====================================================

    def test_provider_error(self):

        request = {
            "request_id": "r8",
            "text": (
                "Jane Smith has Python experience."
            )
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


    # =====================================================
    # Test 9: Invalid JSON
    # =====================================================

    def test_invalid_json(self):

        invalid_json = """
        {
            "request_id": "r9",
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
    # Test 10: Missing required field
    # =====================================================

    def test_missing_text_field(self):

        request = {
            "request_id": "r10"
        }

        result = process_request(request)

        self.assertEqual(
            result["status"],
            "error"
        )

        self.assertEqual(
            result["error"]["code"],
            "INVALID_REQUEST"
        )

# Run tests

if __name__ == "__main__":
    unittest.main()