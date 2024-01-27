from p4utils.utils.topology import NetworkGraph 
from typing import List

from src.equipment.controller import Controller

class LoadBalancer(Controller):
    def __init__(self, name: str, neighbors: List[str], inflow: str, topology: NetworkGraph, compileWanted: bool) -> None:
        super().__init__(name, neighbors, inflow, topology, compileWanted)
        self.in_port = inflow
        self.out_ports = neighbors 
        self.rate_limit = 1  # Default rate limit, can be adjusted
        self.compile('p4src/load-balancer.p4')
        self.flash('p4src/load-balancer.json')
        self.init_table()
    
    def init_table(self):
        """Implement load balancer table initialization"""
        self.api.table_clear("entry_port")
        self.api.table_clear("load_balancer")
        self.out_ports.remove(self.in_port)
        
        port_in = self.topology.node_to_node_port_num(self.name, self.in_port)
        self.api.table_add("entry_port", "random_nhop", [str(port_in)], [str(len(self.out_ports))])
        i = 0
        for port_out_name in self.out_ports:
            port_out = self.topology.node_to_node_port_num(self.name, port_out_name)
            self.api.table_add("load_balancer", "set_nhop", [str(i)], [str(port_out)])
            self.api.table_add("entry_port", "set_nhop", [str(port_out)], [str(port_in)])
            i += 1
            
        self.out_ports.append(self.in_port)
    
    def set_rate_limit(self, rate: int):    
        """Implement method to set rate limit"""
        self.rate_limit = rate
    
    def get_total_packets_nb(self):
        """Retrieve the number of packets received on the controller"""
        return self.api.register_read("total_packets", 0)