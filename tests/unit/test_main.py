"""Test the Main class."""
from unittest import TestCase

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
