"""Test module for the monitoring function handlers."""

import importlib
import unittest
from unittest.mock import patch, MagicMock, call

from crowdstrike.foundry.function import Request

import main


def mock_handler(*_args, **_kwargs):
    """Mock handler decorator for testing."""

    def identity(func):
        return func

    return identity


def query_page(ids, offset, limit, total):
    """Build a mocked query_sensors response for one page of sensor IDs."""
    return {
        "status_code": 200,
        "body": {
            "resources": ids,
            "meta": {"pagination": {"offset": offset, "limit": limit, "total": total}}
        }
    }


def details_response(ids):
    """Build a mocked get_sensor_details response for the given sensor IDs."""
    return {
        "status_code": 200,
        "body": {"resources": [{"device_id": i, "hostname": f"dc-{i}"} for i in ids]}
    }


class GetDcStatusTestCase(unittest.TestCase):
    """Test case class for the get_dc_status handler."""

    def setUp(self):
        """Set up test fixtures before each test method."""
        patcher = patch("crowdstrike.foundry.function.Function.handler", new=mock_handler)
        self.addCleanup(patcher.stop)
        self.handler_patch = patcher.start()

        importlib.reload(main)

    @patch("main.IdentityProtection")
    def test_single_page(self, mock_idp_class):
        """Test a single page of sensors returns a flat list of details."""
        mock_idp = MagicMock()
        mock_idp_class.return_value = mock_idp
        mock_idp.query_sensors.return_value = query_page(["a", "b"], 0, 100, 2)
        mock_idp.get_sensor_details.side_effect = details_response

        request = Request()
        request.body = {"status": ["NORMAL"], "domains": ["example.com"]}

        response = main.get_dc_status(request)

        self.assertEqual(response.code, 200)
        self.assertEqual(
            response.body["domain_controllers"],
            [{"device_id": "a", "hostname": "dc-a"}, {"device_id": "b", "hostname": "dc-b"}]
        )
        mock_idp.query_sensors.assert_called_once_with(
            limit=100, offset="", filter="(status:'NORMAL')+(machine_domain:'example.com')"
        )
        mock_idp.get_sensor_details.assert_called_once_with(ids=["a", "b"])

    @patch("main.IdentityProtection")
    def test_multiple_pages(self, mock_idp_class):
        """Test details are requested for IDs from every page, in batches."""
        mock_idp = MagicMock()
        mock_idp_class.return_value = mock_idp
        mock_idp.query_sensors.side_effect = [
            query_page(["a", "b"], 0, 2, 5),
            query_page(["c", "d"], 2, 2, 5),
            query_page(["e"], 4, 2, 5),
        ]
        mock_idp.get_sensor_details.side_effect = details_response

        with patch("main.QUERY_LIMIT", 2), patch("main.BATCH_SIZE", 3):
            response = main.get_dc_status(Request())

        self.assertEqual(response.code, 200)
        self.assertEqual(
            [dc["device_id"] for dc in response.body["domain_controllers"]],
            ["a", "b", "c", "d", "e"]
        )
        self.assertEqual(
            mock_idp.query_sensors.call_args_list,
            [
                call(limit=2, offset="", filter=""),
                call(limit=2, offset=2, filter=""),
                call(limit=2, offset=4, filter=""),
            ]
        )
        self.assertEqual(
            mock_idp.get_sensor_details.call_args_list,
            [call(ids=["a", "b", "c"]), call(ids=["d", "e"])]
        )

    @patch("main.IdentityProtection")
    def test_empty_result(self, mock_idp_class):
        """Test no matching sensors returns an empty list without a details call."""
        mock_idp = MagicMock()
        mock_idp_class.return_value = mock_idp
        mock_idp.query_sensors.return_value = query_page([], 0, 100, 0)

        response = main.get_dc_status(Request())

        self.assertEqual(response.code, 200)
        self.assertEqual(response.body["domain_controllers"], [])
        mock_idp.get_sensor_details.assert_not_called()

    @patch("main.IdentityProtection")
    def test_api_error(self, mock_idp_class):
        """Test an API error from the sensor query is returned to the caller."""
        mock_idp = MagicMock()
        mock_idp_class.return_value = mock_idp
        mock_idp.query_sensors.return_value = {
            "status_code": 403,
            "body": {"errors": [{"message": "access denied, authorization failed"}]}
        }

        response = main.get_dc_status(Request())

        self.assertEqual(response.code, 403)
        self.assertEqual(len(response.errors), 1)
        self.assertEqual(response.errors[0].message, "access denied, authorization failed")
        mock_idp.get_sensor_details.assert_not_called()


if __name__ == "__main__":
    unittest.main()
