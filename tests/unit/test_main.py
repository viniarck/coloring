"""Test the Main class."""
from unittest import TestCase
from unittest.mock import Mock, patch

from napps.amlight.coloring.main import Main

from tests.helpers import get_controller_mock


class TestMain(TestCase):
    """Test the Main class."""

    def setUp(self):
        self.napp = Main(get_controller_mock())

    def test_color_to_field(self):
        """Test method color_to_field."""

        color = self.napp.color_to_field(300, 'dl_src')
        self.assertEqual(color, 'ee:ee:ee:ee:01:2c')

    @patch('requests.post')
    def test_update_colors(self, req_post_mock):
        """Test method update_colors."""
        switch1 = Mock()
        switch1.dpid = '00:00:00:00:00:00:00:01'
        switch1.ofp_version = '0x04'
        switch2 = Mock()
        switch2.dpid = '00:00:00:00:00:00:00:02'
        switch2.ofp_version = '0x04'

        self.napp.controller.switches = {'1': switch1, '2': switch2}

        def switch_by_dpid(dpid):
            if dpid == '00:00:00:00:00:00:00:01':
                return switch1
            if dpid == '00:00:00:00:00:00:00:02':
                return switch2
            return None
        self.napp.controller.get_switch_by_dpid = \
            Mock(side_effect=switch_by_dpid)

        links = [
            {
                'endpoint_a': {'switch': switch1.dpid},
                'endpoint_b': {'switch': switch2.dpid}
            },
            {
                'endpoint_a': {'switch': switch1.dpid},
                'endpoint_b': {'switch': switch1.dpid}
            }
        ]

        self.napp.update_colors(links)
        self.assertEqual(req_post_mock.call_count, 2)

        links = [
            {
                'endpoint_a': {'switch': switch1.dpid},
                'endpoint_b': {'switch': switch1.dpid}
            }
        ]

        req_post_mock.reset_mock()
        self.napp.update_colors(links)
        req_post_mock.assert_not_called()
