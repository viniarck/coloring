"""Module to create a singleton class to track all switches. After being
loaded by the main napp, this class can be reached just using
Switches().desired_method()

For example:

from switches import Switches

list_of_switches = Switches().get_switches()
switch_01 = Switches().get_switch("00:00:00:00:00:00:00:01")
"""

from napps.amlight.coloring.shared.singleton import Singleton


class Switches(metaclass=Singleton):
    """This class is used to easy app development, decoupling
    modules from Kytos core. With a Singleton class for Switches,
    napps will not need to keep passing Kytos main class to get
    a list of switches.
    """

    def __init__(self, switches):
        self._switches = switches

    def __len__(self):
        """Return the number of switches instantiated """
        return len(self._switches)

    def get_switch(self, dpid):
        """Query the self.switches
        Args:
            dpid: datapath id 'str'

        Returns:
            a kytos.core.switch.Switch() object
            False if not found
        """
        for switch in self._switches.values():
            if switch.dpid == dpid:
                return self._switches[switch.dpid]
        return False

    def get_switches(self):
        """Return all switches """
        return self._switches.values()
