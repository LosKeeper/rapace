from p4utils.utils.helper import load_topo
from p4utils.utils.sswitch_p4runtime_API import SimpleSwitchP4RuntimeAPI
from p4utils.utils.sswitch_thrift_API import SimpleSwitchThriftAPI
from p4utils.utils.topology import NetworkGraph 
from p4utils.utils.p4runtime_API.api import TableEntry
from p4utils.utils.compiler import P4C
import yaml
from typing import List 

USER_INPUT = 'topology' # file name without extension input of the user

class MetaController:
    def __init__(self, user_input: str):
        self.user_input = user_input
        self.file_yaml = f'{user_input}.yaml'
        self.file_json = f'{user_input}.json'
        self.topology = load_topo(self.file_json)
        self.controllers = {}

    def Import(self):
        """Import logical topology entered by the user on physical topology"""
        print('Importing user-input logical topology into physical topology...')
        
        with open(self.file_yaml, 'r') as file:
            config_data = yaml.safe_load(file)
            
            for node_config in config_data.get('nodes', []):
                node_name = node_config.get('name')
                node_type = node_config.get('type')
                node_neighbors = node_config.get('neighbors').split()
                node_inflow = node_config.get('inflow')

                print(f'Working on {node_name} switch:')

                if node_type == 'firewall':
                    fw_node = Firewall(node_name, node_neighbors, node_inflow, self.topology)
                    self.controllers[node_name] = fw_node

                elif node_type == 'load-balancer':
                    lb_node = LoadBalancer(node_name, node_neighbors, node_inflow, self.topology)
                    self.controllers[node_name] = lb_node

                elif node_type == 'router':
                    router_node = RouterController(node_name, node_neighbors, node_inflow, self.topology)
                    self.controllers[node_name] = router_node

                elif node_type == 'router-lw':
                    lw_router_node = RouterLWController(node_name, node_neighbors, node_inflow, self.topology)
                    self.controllers[node_name] = lw_router_node

                else:
                    print(f"Invalid type for node: {node_type}")
                    exit(1)

    def list_controllers(self):
        """List all controllers running in the network."""
        print("Controllers:")
        for node_id, controller in self.controllers.items():
            print(f"{node_id}: {type(controller).__name__}")
            

class Controller:
    def __init__(self, name: str, neighbors: List[str], inflow: str, topology: NetworkGraph) -> None:
        self.name = name
        self.topology = topology
        self.api = SimpleSwitchThriftAPI(self.topology.get_thrift_port(name))
        
    def compile(self, p4_src: str):
        print('Compiling P4 source file...')
        source = P4C(p4_src, "/usr/local/bin/p4c")
        source.compile()
        
    def flash(self, json_src: str):
        print('Loading and swaping JSON file...')
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
    
    
class RouterController(Controller):
    def __init__(self, name: str, neighbors: List[str], inflow: str, topology: NetworkGraph) -> None:
        super().__init__(name, neighbors, inflow, topology)
        # Add specific attributes for router controller
        self.compile('equipment/router.p4')
        self.flash('equipment/router.json')
    
    def init_table(self):
        # Implement router controller table initialization
        pass

    
class RouterLWController(Controller):
    def __init__(self, name: str, neighbors: List[str], inflow: str, topology: NetworkGraph) -> None:
        super().__init__(name, neighbors, inflow, topology)
        # Add specific attributes for lightweight router controller
        self.compile('equipment/router-lw.p4')
        self.flash('equipment/router-lw.json')
    
    def init_table(self):
        # Implement lightweight router controller table initialization
        pass

### Network topology parsing and creation
meta_controller = MetaController(USER_INPUT)
meta_controller.Import()
meta_controller.list_controllers()