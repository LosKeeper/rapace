from p4utils.utils.helper import load_topo
from p4utils.utils.sswitch_p4runtime_API import SimpleSwitchP4RuntimeAPI
from p4utils.utils.sswitch_thrift_API import SimpleSwitchThriftAPI
from p4utils.utils.topology import NetworkGraph 

topo = load_topo('topology.json')
controllers = {}

for switch, data in topo.get_p4rtswitches().items():
    controllers[switch] = SimpleSwitchP4RuntimeAPI(data['device_id'], data['grpc_port'],
                                                   p4rt_path=data['p4rt_path'],
                                                   json_path=data['json_path'])

class P4Switch:
    def __init__(self, name: str, topo: NetworkGraph) -> None:
        self.name = name
        self.topo = topo
        self.api = SimpleSwitchThriftAPI(self.topo.get_thrift_port(name))
        
    def compile(self, p4_src: str):
        source = P4C(p4_src, "/usr/local/bin/p4c")
        source.compile()
        
    def flash(self, json_src: str):
        self.api.load_new_config_file(json_src)
        self.api.swap_configs()
        
    def init_table(self):
        pass
    
    def mininet_update(self):
        self.api.switch_info.load_json_config(self.api.client)
        self.api.table_entries_match_to_handle = self.api.create_match_to_handle_dict()
        self.api.load_table_entries_match_to_handle()
        
    def add_link(self, new_neigh, attribute):
        # To be overridden
        pass
    
    def can_remove_link(self, neighboor: str):
        # To be overridden
        pass
    
    def remove_link(self, neighboor: str):
        # To be overridden
        pass
    
    
from p4utils.utils.p4runtime_lib import TableEntry

class Firewall(P4Switch):
    def __init__(self, name: str, topo: NetworkGraph) -> None:
        super().__init__(name, topo)
        """Add specific attributes for firewall"""
        self.rules = []  # List to store firewall rules

    def init_table(self):
        """Implement firewall table initialization"""
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

    
class LoadBalancer(P4Switch):
    def __init__(self, name: str, topo: NetworkGraph) -> None:
        super().__init__(name, topo)
        self.in_port = self.determine_in_port()
        self.out_ports = []  # List to store dynamically determined out ports
        self.rate_limit = 1  # Default rate limit, can be adjusted
        self.init_out_ports()
    
    def determine_in_port(self):
        """Determine the in port dynamically based on the topology"""
        for link in self.topo.links:
            if link['target'] == self.name:
                return link['source']
        return None  # In port not found
    
    def init_out_ports(self):
        """Determine the out ports dynamically based on the topology"""
        for link in self.topo.links:
            if link['source'] == self.name:
                self.out_ports.append(link['target'])
    
    def init_table(self):
        """Implement load balancer table initialization"""
        for port in self.out_ports:
            entry = {
                "hdr.ipv4.srcAddr": "0.0.0.0",
                "hdr.ipv4.dstAddr": "0.0.0.0",
                "hdr.ipv4.protocol": 0,
                "hdr.tcp.srcPort": 0,
                "hdr.tcp.dstPort": 0,
                "action": "forward",
                "port": port,
            }
            self.api.table_add("load_balancer", entry)
    
    def set_rate_limit(self, rate: int):
        """Implement method to set rate limit"""
        self.rate_limit = rate
    
    def mininet_update(self):
        super().mininet_update()
        """Set the rate limit for each out port"""
        for port in self.out_ports:
            self.api.set_egress_port_rate_limit(port, self.rate_limit)
    
    
class RouterController(P4Switch):
    def __init__(self, name: str, topo: NetworkGraph) -> None:
        super().__init__(name, topo)
        # Add specific attributes for router controller
    
    def init_table(self):
        # Implement router controller table initialization

    
class RouterLWController(P4Switch):
    def __init__(self, name: str, topo: NetworkGraph) -> None:
        super().__init__(name, topo)
        # Add specific attributes for lightweight router controller
    
    def init_table(self):
        # Implement lightweight router controller table initialization

