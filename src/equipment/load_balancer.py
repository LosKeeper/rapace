from p4utils.utils.topology import NetworkGraph 
from typing import List

from src.equipment.controller import Controller

class LoadBalancer(Controller):
    def __init__(self, name: str, neighbors: List[str], inflow: str, topology: NetworkGraph) -> None:
        super().__init__(name, neighbors, inflow, topology)
        self.in_port = inflow
        self.out_ports = neighbors 
        self.rate_limit = 1  # Default rate limit, can be adjusted
        self.compile('equipment/load-balancer.p4')
        self.flash('equipment/load-balancer.json')
        self.init_table()
    
    def init_table(self):
        """Implement load balancer table initialization"""
        self.api.table_clear("entry_port")
        self.api.table_clear("load_balancer")
        
        port_in = self.topology.node_to_node_port_num(self.name, self.in_port)
        self.api.table_add("entry_port", "random_nhop", [str(port_in)], [str(len(self.out_ports))])
        for port_out_name in self.out_ports:
            port_out = self.topology.node_to_node_port_num(self.name, port_out_name)   
            print(port_in, port_out)
            self.api.table_add("load_balancer", "set_nhop", [str(port_in)], [str(port_out)])
            self.api.table_add("entry_port", "set_nhop", [str(port_out)], [str(port_in)])
    
    def set_rate_limit(self, rate: int):    
        """Implement method to set rate limit"""
        self.rate_limit = rate
    
    def mininet_update(self):
        super().mininet_update()
        """Set the rate limit for each out port"""
        for port in self.out_ports:
            self.api.set_egress_port_rate_limit(port, self.rate_limit)