from napps.amlight.coloring import constants


FLOW_PRIORITY = 50001
COLORING_INTERVAL = 10
COLOR_FIELD = 'dl_src'

flow_dict_v10 = {'idle_timeout': 0, 'hard_timeout': 0, 'table_id': 0, 'buffer_id': None,
                 'in_port': 0, 'dl_src': '00:00:00:00:00:00', 'dl_dst': '00:00:00:00:00:00',
                 'dl_vlan': 0, 'dl_type': 0, 'nw_src': '0.0.0.0', 'nw_dst': '0.0.0.0',
                 'tp_src': 0, 'tp_dst': 0, 'priority': FLOW_PRIORITY,
                 'actions': [{'port': constants.OFP_CONTROLLER}]}