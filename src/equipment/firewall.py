from p4utils.utils.topology import NetworkGraph 
from p4utils.utils.p4runtime_API.api import TableEntry
from typing import List

from src.equipment.controller import Controller

class Firewall(Controller):
    def __init__(self, name: str, neighbors: List[str], inflow: str, topology: NetworkGraph, compileWanted: bool) -> None:
        super().__init__(name, neighbors, inflow, topology, compileWanted)
        """Add specific attributes for firewall"""
        if len(neighbors) != 2:
            print("Firewall must have exactly 2 links")
            exit(1)
        self.out_ports = neighbors
        self.rules = []  # List to store firewall rules
        self.compile('p4src/firewall.p4')
        self.flash('p4src/firewall.json')
        self.init_table()

    def init_table(self):
        """Implement firewall table initialization"""
        self.api.table_clear("filter_table")
                
        port_1 = self.topology.node_to_node_port_num(self.name, self.out_ports[0])
        port_2 = self.topology.node_to_node_port_num(self.name, self.out_ports[1])
        self.api.table_add("entry_port", "set_nhop", [str(port_1)],[str(port_2)])
        self.api.table_add("entry_port", "set_nhop", [str(port_2)],[str(port_1)])
                
        for rule in self.rules:
            self.add_rule(rule[0], rule[1], rule[2], rule[3], rule[4])

    def add_rule(self, srcAddr: str, dstAddr: str, protocol: str, srcPort: str, dstPort: str):
        """Implement method to add firewall rule"""
        # Convert protocol to hex
        protocol_hex = "0x6" if protocol == "tcp" else "0x11"
        
        # Add rule to firewall table
        self.api.table_add("filter_table", "drop", [srcAddr,dstAddr, protocol_hex, hex(int(srcPort)), hex(int(dstPort))])
        self.rules.append([srcAddr,dstAddr, protocol, srcPort, dstPort])
        
    def get_total_packets_nb(self):
        """Retrieve the number of packets received on the firewall"""
        return self.api.register_read("total_packets", 0)
    
    def get_filtered_packets_nb(self):
        """Retrieve the number of packets received on the firewall"""
        return self.api.register_read("filtered_packets", 0)
    
    