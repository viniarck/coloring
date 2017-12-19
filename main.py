"""Main module of amlight/coloring Kytos Network Application.

NApp to color a network topology
"""

from kytos.core import KytosEvent, KytosNApp, log, rest
import requests
import json
import struct
from kytos.core.flow import Flow
from kytos.core.helpers import listen_to
from kytos.core.switch import Interface
from napps.amlight.coloring import settings, constants
from napps.amlight.coloring.shared.switches import Switches


class Main(KytosNApp):
    """Main class of amlight/coloring NApp.

    This class is the entry point for this napp.
    """

    def setup(self):
        """Replace the '__init__' method for the KytosNApp subclass.

        The setup method is automatically called by the controller when your
        application is loaded. """
        self._flow_mgr_url = 'http://localhost:8181/api/kytos/of_flow_manager/flows/%s'
        self._switches = dict()
        self.register_rest()
        self.instantiate_switches = Switches(self.controller.switches)

    def register_rest(self):
        """Register REST calls to be used
        GET /coloring/colors to get all switch fields and color values
        """
        endpoints = [('/coloring/colors', self.rest_colors, ['GET'])]
        for endpoint in endpoints:
            self.controller.register_rest_endpoint(*endpoint)

    @staticmethod
    @listen_to('kytos/of_core.messages.in.ofpt_port_status')
    def update_link_on_port_status_change(event):
        """Update topology when a port-status is received.
        """
        port_status = event.message
        reasons = ['CREATED', 'DELETED', 'MODIFIED']
        switch = event.source.switch
        port_no = port_status.desc.port_no
        reason = reasons[port_status.reason.value]

        if reason is 'MODIFIED':
            interface = switch.get_interface_by_port_no(port_no.value)
            for endpoint, _ in interface.endpoints:
                if isinstance(endpoint, Interface):
                    interface.delete_endpoint(endpoint)

    def execute(self):
        """This method is executed right after the setup method execution.

            Color each switch, with the color based on the switch's DPID.
            After that, if not yet installed, installs, for each switch, flows
            with the color of its neighbors, to send probe packets to the
            controller.
        """
        self._discover_neighbors()
        self._install_colored_flows()
        self.execute_as_loop(settings.COLORING_INTERVAL)

    def _discover_neighbors(self):
        """Create a dictionary with all colors and neighbors
        """
        # First, set the color of all the switches, if not already set
        for switch in Switches().get_switches():
            if switch.dpid not in self._switches:
                color = int(switch.dpid.replace(':', '')[4:], 16)
                self._switches[switch.dpid] = {'color': color, 'neighbors': [], 'flows': []}
            else:
                self._switches[switch.dpid]['neighbors'] = []

            # Register all switch neighbors based on the topology
            for interface in switch.interfaces.values():
                for endpoint, _ in interface.endpoints:
                    if isinstance(endpoint, Interface):
                        self._switches[switch.dpid]['neighbors'].append(endpoint.switch)

    def _install_colored_flows(self):
        """Create the flows for each neighbor of each switch and installs
        it if not already installed """
        for dpid, switch_dict in self._switches.items():
            for neighbor in switch_dict['neighbors']:
                flow_dict = settings.flow_dict_v10  # Future expansion to OF1.3
                flow_dict[settings.COLOR_FIELD] = self.color_to_field(self._switches[neighbor.dpid]['color'],
                                                                      settings.COLOR_FIELD)
                flow = Flow.from_dict(flow_dict)
                if flow not in switch_dict['flows']:  # TODO: switch_dict['flows'] might lose sync
                    if self._push_flows(dpid, flow):
                        switch_dict['flows'].append(flow)

    def _push_flows(self, dpid, flow):
        """Push flows to kytos/of_flow_manager
        """
        r = requests.post(self._flow_mgr_url % dpid, json=[flow.as_dict()['flow']])
        if r.status_code // 100 != 2:
            log.error('Flow manager returned an error inserting flow. Status code %s, flow id %s.' %
                      (r.status_code, flow.id))
            return False
        return True

    @staticmethod
    def color_to_field(color, field='dl_src'):
        """
        Gets the color number and returns it in a format suitable for the field
        :param color: The color of the switch (integer)
        :param field: The field that will be used to create the flow for the 
        color
        :return: A representation of the color suitable for the given field
        """
        # TODO: calculate field value for other fields
        if field == 'dl_src' or field == 'dl_dst':
            c = color & 0xffffffffffffffff
            int_mac = struct.pack('!Q', c)[2:]
            color_value = ':'.join(['%02x' % b for b in int_mac])
            return color_value.replace('00', 'ee')
        if field == 'nw_src' or field == 'nw_dst':
            c = color & 0xffffffff
            int_ip = struct.pack('!L', c)
            return '.'.join(map(str, int_ip))
        if field == 'in_port' or field == 'dl_vlan' \
                or field == 'tp_src' or field == 'tp_dst':
            c = color & 0xffff
            return c
        if field == 'nw_tos' or field == 'nw_proto':
            c = color & 0xff
            return c

    def rest_colors(self):
        """Process REST output"""
        colors = {}
        for dpid, switch_dict in self._switches.items():
            colors[dpid] = {'color_field': settings.COLOR_FIELD,
                            'color_value': self.color_to_field(switch_dict['color'],
                                                               settings.COLOR_FIELD)}
        return json.dumps({'colors': colors})

    def shutdown(self):
        """This method is executed when your napp is unloaded.

        If you have some cleanup procedure, insert it here.
        """
        pass
