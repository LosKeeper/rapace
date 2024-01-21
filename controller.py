from p4utils.utils.helper import load_topo
from p4utils.utils.sswitch_p4runtime_API import SimpleSwitchP4RuntimeAPI
from p4utils.utils.sswitch_thrift_API import SimpleSwitchThriftAPI
from p4utils.utils.topology import NetworkGraph 
from p4utils.utils.p4runtime_API.api import TableEntry
from p4utils.utils.compiler import P4C
import yaml
from typing import List 

topology = load_topo('topology.json')
controllers = {}

class P4Switch:
    def __init__(self, name: str, neighbors: List[str], inflow: str, topology: NetworkGraph) -> None:
        self.name = name
        self.topology = topology
        self.api = SimpleSwitchThriftAPI(self.topology.get_thrift_port(name))
        
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


class Firewall(P4Switch):
    def __init__(self, name: str, neighbors: List[str], inflow: str, topology: NetworkGraph) -> None:
        super().__init__(name, neighbors, inflow, topology)
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
    def __init__(self, name: str, neighbors: List[str], inflow: str, topology: NetworkGraph) -> None:
        super().__init__(name, neighbors, inflow, topology)
        self.in_port = inflow
        self.out_ports = neighbors 
        self.rate_limit = 1  # Default rate limit, can be adjusted
        self.init_out_ports()
    
    
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
    def __init__(self, name: str, neighbors: List[str], inflow: str, topology: NetworkGraph) -> None:
        super().__init__(name, neighbors, inflow, topology)
        # Add specific attributes for router controller
    
    def init_table(self):
        # Implement router controller table initialization
        pass

    
class RouterLWController(P4Switch):
    def __init__(self, name: str, neighbors: List[str], inflow: str, topology: NetworkGraph) -> None:
        super().__init__(name, neighbors, inflow, topology)
        # Add specific attributes for lightweight router controller
    
    def init_table(self):
        # Implement lightweight router controller table initialization
        pass

### Network topology parsing and creation

config_file = "topology.yaml"
with open(config_file, 'r') as file:
    config_data = yaml.safe_load(file)
    
for node_config in config_data.get('nodes', []):
    node_name = node_config.get('name')
    node_type = node_config.get('type')
    node_neighbors = node_config.get('neighbors')
    node_inflow = node_config.get('inflow')

    if node_type == 'firewall':
        fw_node = Firewall(node_name, node_neighbors, node_inflow, topology)
        fw_node.compile('equipment/firewall.p4')
        fw_node.flash('topology.json')
        controllers[node_name] = fw_node
        
    elif node_type == 'load-balancer':
        lb_node = LoadBalancer(node_name, node_neighbors, node_inflow, topology)
        lb_node.compile('equipment/loadbalancer.p4')
        lb_node.flash('topology.json')
        controllers[node_name] = lb_node
        
    elif node_type == 'router':
        router_node = RouterController(node_name, node_neighbors, node_inflow, topology)
        router_node.compile('equipment/router.p4')
        router_node.flash('topology.json')
        controllers[node_name] = router_node
        
    elif node_type == 'lwrouter':
        lw_router_node = RouterLWController(node_name, node_neighbors, node_inflow, topology)
        lw_router_node.compile('equipment/router-lw.p4')
        lw_router_node.flash('topology.json')
        controllers[node_name] = lw_router_node

    else:
        print(f"Invalid type for node: {node_type}")
        exit(1)
