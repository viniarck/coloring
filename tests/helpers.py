"""Module to help to create tests."""
from unittest.mock import Mock

from kytos.core import Controller
from kytos.core.config import KytosConfig


def get_controller_mock():
    """Return a controller mock."""
    options = KytosConfig().options['daemon']
    controller = Controller(options)
    controller.log = Mock()
    return controller
