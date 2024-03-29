from p4utils.utils.sswitch_thrift_API import SimpleSwitchThriftAPI
from p4utils.utils.topology import NetworkGraph 
from typing import List

from src.equipment.controller import Controller

class RouterController(Controller):
    def __init__(self, name: str, neighbors: List[str], inflow: str, topology: NetworkGraph, compileWanted: bool) -> None:
        super().__init__(name, neighbors, inflow, topology, compileWanted)
        self.compile('p4src/router.p4')
        self.flash('p4src/router.json')
        self.init_table()
    
    
    def init_table(self):
        """Implement router controller table initialization"""
        self.api.table_clear("ipv4_lpm")
        self.api.table_clear("icmp_ingress_port")
        
        for host_name, host_config in self.topology.get_hosts().items():
            try:
                all_paths = self.topology.get_all_paths_between_nodes(self.name, host_name)
            except Exception as e:
                continue
            if not all_paths:
                continue
            next_hop_name = self.topology.get_shortest_paths_between_nodes(self.name, host_name)[0][1]
            port_out = self.topology.node_to_node_port_num(self.name, next_hop_name)
            next_hop_mac = self.topology.node_to_node_mac(next_hop_name, self.name)
            if self.topology.isHost(next_hop_name):
                self.api.table_add("ipv4_lpm", "set_nhop_host", [str(host_config["ip"]).split('/')[0] + "/32"], [str(next_hop_mac), str(port_out)])
            else:
                self.api.table_add("ipv4_lpm", "set_nhop_router", [str(host_config["ip"]).split('/')[0] + "/32"], [str(next_hop_mac), str(port_out)])
        
        for sw_name, sw_config in self.topology.get_p4switches().items():
            if sw_name != self.name:
                try:
                    all_paths = self.topology.get_all_paths_between_nodes(self.name, sw_name)
                except Exception as e:
                    continue
                if not all_paths:
                    continue
                next_hop_name = self.topology.get_shortest_paths_between_nodes(self.name, sw_name)[0][1]
                port_out = self.topology.node_to_node_port_num(self.name, next_hop_name)
                next_hop_mac = self.topology.node_to_node_mac(next_hop_name, self.name)
                self.api.table_add("ipv4_lpm", "set_nhop_router", [str(sw_config["loopback"]) + "/32"], [str(next_hop_mac), str(port_out)])
                
        for sw_name, controller in self.topology.get_p4switches().items():
            for intf, node in self.topology.get_interfaces_to_node(sw_name).items():
                if self.topology.node_to_node_interface_ip(sw_name, node) != None:
                    ip = self.topology.node_to_node_interface_ip(sw_name, node).split("/")[0]
                    port_number = self.topology.interface_to_port(sw_name, intf)
                    self.api.table_add("icmp_ingress_port", "set_src_icmp_ip", [str(port_number)], [str(ip)])
                
        for sw_name, controller in self.topology.get_hosts().items():
            for intf, node in self.topology.get_interfaces_to_node(sw_name).items():
                if self.topology.node_to_node_interface_ip(sw_name, node) != None:    
                    ip = self.topology.node_to_node_interface_ip(sw_name, node).split("/")[0]
                    port_number = self.topology.interface_to_port(sw_name, intf)
                    self.api.table_add("icmp_ingress_port", "set_src_icmp_ip", [str(port_number)], [str(ip)])          
           
                
    def get_total_packets_nb(self):
        """Retrieve the number of packets received on the controller"""
        return self.api.register_read("total_packets", 0)