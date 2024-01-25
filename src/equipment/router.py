from p4utils.utils.sswitch_thrift_API import SimpleSwitchThriftAPI
from p4utils.utils.topology import NetworkGraph 
from typing import List

from src.equipment.controller import Controller

class RouterController(Controller):
    def __init__(self, name: str, neighbors: List[str], inflow: str, topology: NetworkGraph, compileWanted: bool) -> None:
        super().__init__(name, neighbors, inflow, topology, compileWanted)
        # Add specific attributes for router controller
        self.compile('p4src/router.p4')
        self.flash('p4src/router.json')
        self.init_table()
    
    def init_table(self):
        """Implement router controller table initialization"""
        self.api.table_clear("ipv4_lpm")
        
        for host_name, host_config in self.topology.get_hosts().items():
            next_hop_name = self.topology.get_shortest_paths_between_nodes(self.name, host_name)[0][1]
            port_out = self.topology.node_to_node_port_num(self.name, next_hop_name)
            next_hop_mac = self.topology.node_to_node_mac(next_hop_name, self.name)
            self.api.table_add("ipv4_lpm", "set_nhop", [str(host_config["ip"]).split('/')[0] + "/32"], [str(next_hop_mac), str(port_out)])
        
        for sw_name, sw_config in self.topology.get_p4switches().items():
            if sw_name != self.name:
                next_hop_name = self.topology.get_shortest_paths_between_nodes(self.name, sw_name)[0][1]
                port_out = self.topology.node_to_node_port_num(self.name, next_hop_name)
                next_hop_mac = self.topology.node_to_node_mac(next_hop_name, self.name)
                self.api.table_add("ipv4_lpm", "set_nhop", [str(sw_config["loopback"] + "/32")], [str(next_hop_mac), str(port_out)])