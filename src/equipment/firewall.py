from p4utils.utils.topology import NetworkGraph 
from p4utils.utils.p4runtime_API.api import TableEntry
from typing import List

from src.equipment.controller import Controller

class Firewall(Controller):
    def __init__(self, name: str, neighbors: List[str], inflow: str, topology: NetworkGraph) -> None:
        super().__init__(name, neighbors, inflow, topology)
        """Add specific attributes for firewall"""
        self.rules = []  # List to store firewall rules
        self.compile('equipment/firewall.p4')
        self.flash('equipment/firewall.json')

    def init_table(self):
        """Implement firewall table initialization"""
        # ...
                
        for rule in self.rules:
            self.add_rule(rule)

    def add_rule(self, flow: str):
        """Implement method to add firewall rule"""
        entry = TableEntry("firewall")
        entry.match["hdr.ipv4.srcAddr"] = flow.split(",")[0]
        entry.match["hdr.ipv4.dstAddr"] = flow.split(",")[1]
        entry.match["hdr.ipv4.protocol"] = int(flow.split(",")[2])
        entry.match["hdr.tcp.srcPort"] = int(flow.split(",")[3])
        entry.match["hdr.tcp.dstPort"] = int(flow.split(",")[4])
        entry.action = "drop"
        self.api.table_add(entry)
        self.rules.append(flow)