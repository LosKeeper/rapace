from p4utils.utils.topology import NetworkGraph 
from p4utils.utils.p4runtime_API.api import TableEntry
from typing import List

from src.equipment.controller import Controller

class Firewall(Controller):
    def __init__(self, name: str, neighbors: List[str], inflow: str, topology: NetworkGraph, compileWanted: bool) -> None:
        super().__init__(name, neighbors, inflow, topology, compileWanted)
        """Add specific attributes for firewall"""
        self.rules = []  # List to store firewall rules
        self.compile('p4src/firewall.p4')
        self.flash('p4src/firewall.json')

    def init_table(self):
        """Implement firewall table initialization"""
        # ...
                
        for rule in self.rules:
            self.add_rule(rule)

    def add_rule(self, srcAddr: str, dstAddr: str, protocol: str, srcPort: str, dstPort: str):
        """Implement method to add firewall rule"""
        # Convert protocol to hex
        protocol = "0x6" if protocol == "tcp" else "0x11"
        
        # Add rule to firewall table
        self.api.table_add("filter_table", "drop", [srcAddr,dstAddr, protocol, hex(int(srcPort)), hex(int(dstPort))])
        self.rules.append([srcAddr,dstAddr, protocol, srcPort, dstPort])