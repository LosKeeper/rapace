import yaml
import json

from p4utils.utils.helper import load_topo

from src.equipment.firewall import Firewall
from src.equipment.load_balancer import LoadBalancer
from src.equipment.router import RouterController
from src.equipment.router_lw import RouterLWController
from src.equipment.host import Host
from src.equipment import helpers

DEFAULT = 100

class MetaController:
    def __init__(self, user_input: str, compileWanted: bool = True):
        self.user_input = user_input
        self.file_yaml = f'{user_input}.yaml'
        self.file_json = f'{user_input}.json'
        self.topology = None
        self.controllers = {}
        self.compileWanted = compileWanted
        self.index = DEFAULT
        self.update_topology()
        self.convert_phy_to_logi()

    def update_topology(self):
        """Update topology with json file"""
        self.topology = load_topo(self.file_json)
        

    def convert_phy_to_logi(self):
        """Convert physical topology into logical topology entered by the user"""
        print('Importing user-input logical topology into physical topology...')
        
        with open(self.file_yaml, 'r') as file:
            config_data = yaml.safe_load(file)
            nodes = []
            
            for node_config in config_data.get('nodes', []):
                node_name = node_config.get('name')
                node_type = node_config.get('type')
                node_neighbors = node_config.get('neighbors').split()
                node_inflow = node_config.get('inflow')

                # remove unused links in logical topology (! : not physical topology)
                for neighbors in self.topology.get_neighbors(node_name):
                    if neighbors not in node_neighbors:
                        self.remove_link(node_name, neighbors)
                        
                # if node is a router, add loopback ip address
                if node_type != 'host':
                    self.add_loopback(node_name)
                
                self.update_topology()
            
                print(f'Working on {node_name} switch:')

                if node_type == 'firewall':
                    fw_node = Firewall(node_name, node_neighbors, node_inflow, self.topology, self.compileWanted)
                    self.controllers[node_name] = fw_node

                elif node_type == 'load-balancer':
                    lb_node = LoadBalancer(node_name, node_neighbors, node_inflow, self.topology, self.compileWanted)
                    self.controllers[node_name] = lb_node

                elif node_type == 'router':
                    router_node = RouterController(node_name, node_neighbors, node_inflow, self.topology, self.compileWanted)
                    self.controllers[node_name] = router_node

                elif node_type == 'router-lw':
                    lw_router_node = RouterLWController(node_name, node_neighbors, node_inflow, self.topology, self.compileWanted)
                    self.controllers[node_name] = lw_router_node
                    
                elif node_type == 'host':
                    host_node = Host(node_name, node_neighbors, node_inflow, self.topology, self.compileWanted)
                    self.controllers[node_name] = host_node

                else:
                    print(f"Invalid type for node: {node_type}")
                    exit(1)
                    
                nodes.append(node_name)
                
        for node in self.topology.get_nodes():
            if node not in nodes:
                self.remove_node(node)
                
        self.update_topology()
        
        print('Logical topology imported successfully!')
        
    def add_loopback(self, node_name: str):
        """Add loopback ip address for router (needed for encapsulation)"""
        with open(self.file_json, 'r') as json_file:
            topology_data = json.load(json_file)
            
        node_config = topology_data.get('nodes', [])
        # get only the "id" == node_name
        node_config = [node for node in node_config if node['id'] == node_name][0]
        node_config['loopback'] = "127.0.0."+str(node_name.split('s')[1])
        
        with open(self.file_json, 'w') as json_file:
            json.dump(topology_data, json_file, indent=2)
                    

    def add_node(self, name: str, isP4Switch: bool, isSwitch: bool):
        """Add a node in the topology json file"""
        with open(self.file_json, 'r') as json_file:
            topology_data = json.load(json_file)

        # Check if the node already exists
        existing_nodes = [node['id'] for node in topology_data.get('nodes', [])]
        if name in existing_nodes:
            return

        new_node = {
            "cls": null,
            "isP4Switch": f"{isP4Switch}",
            "isSwitch": f"{isSwitch}",
            "device_id": 1,
            "pcap_dump": true,
            "pcap_dir": "./pcap",
            "log_enabled": true,
            "log_dir": "./log",
            "thrift_port": 909+int(name.split('s')[1]),
            "id": f"{name}",
            "loopback": "127.0.0."+str(name.split('s')[1]),
        }

        topology_data.setdefault('nodes', []).append(new_node)

        with open(self.file_json, 'w') as json_file:
            json.dump(topology_data, json_file, indent=2)

    def remove_node(self, name):
        """Remove a node in the topology json file"""
        with open(self.file_json, 'r') as json_file:
            topology_data = json.load(json_file)

        existing_nodes = [node['id'] for node in topology_data.get('nodes', [])]
        if name not in existing_nodes:
            return

        topology_data['nodes'] = [node for node in topology_data['nodes'] if node['id'] != name]
        topology_data['links'] = [link for link in topology_data['links'] if link['node1'] != name and link['node2'] != name]

        with open(self.file_json, 'w') as json_file:
            json.dump(topology_data, json_file, indent=2)
            
            
    def add_link(self, node1: str, node2: str):
        """Add a link between node1 and node2 in the topology json file"""
        with open(self.file_json, 'r') as json_file:
            topology_data = json.load(json_file)
            
        existing_links = topology_data.get('links', [])
        for link in existing_links:
            if (link['node1'] == node1 and link['node2'] == node2) or \
               (link['node1'] == node2 and link['node2'] == node1):
                   return
        
        port_node1 = self.index
        self.index += 1
        port_node2 = self.index
        self.index += 1
        
        new_link = {
            "cls": None,
            "weight": 1,
            "intfName1": f"{node1}-eth{port_node1}",
            "intfName2": f"{node2}-eth{port_node2}",
            "addr1": f"{helpers.generate_mac_address()}",
            "addr2": f"{helpers.generate_mac_address()}",
            "node1": f"{node1}",
            "node2": f"{node2}",
            "port1": f"{port_node1}",
            "port2": f"{port_node2}",
            "ip1": None,
            "ip2": None,
            "source": f"{node1}",
            "target": f"{node2}"
        }

        topology_data['links'].append(new_link)

        with open(self.file_json, 'w') as json_file:
            json.dump(topology_data, json_file, indent=2)
            
    def remove_link(self, node1: str, node2: str):
        """Remove the link between node1 and node2 in the topology json file"""
        with open(self.file_json, 'r') as json_file:
            topology_data = json.load(json_file)

        link_index = None
        for i, link in enumerate(topology_data.get('links', [])):
            if (link['node1'] == node1 and link['node2'] == node2) or \
               (link['node1'] == node2 and link['node2'] == node1):
                link_index = i
                break

        if link_index is not None:  
            removed_link = topology_data['links'].pop(link_index)
            with open(self.file_json, 'w') as json_file:
                json.dump(topology_data, json_file, indent=2)
            
    def list_controllers(self):
        """List all controllers running in the network."""
        print("Controllers:")
        for node_id, controller in self.controllers.items():
            print(f"{node_id}: {type(controller).__name__}")
    
    def list_neighbors(self):
        """List all neighbors of each controller."""
        print("Neighbors:")
        for node_id, controller in self.controllers.items():
            print(f"{node_id}: {self.topology.get_neighbors(node_id)}")
