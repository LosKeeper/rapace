import yaml
import json

from p4utils.utils.helper import load_topo

from src.equipment.firewall import Firewall
from src.equipment.load_balancer import LoadBalancer
from src.equipment.router import RouterController
from src.equipment.router_lw import RouterLWController
from src.equipment.host import Host

class MetaController:
    def __init__(self, user_input: str, file_to_compile: str, compileWanted: bool = True):
        self.user_input = user_input
        self.file_yaml = f'{user_input}.yaml'
        self.file_json = f'{user_input}.json'
        self.file_modified_json = f'{user_input}_modified.json'
        self.topology = load_topo(self.file_json)
        self.controllers = {}
        self.file_to_compile = file_to_compile
        self.compileWanted = compileWanted
        if file_to_compile != "":
            self.compileWanted = False
        self.init_import_logi_topology()
        self.import_logi_topology()

    def update_topology(self):
        """Update topology with json file"""
        self.topology = load_topo(self.file_modified_json)
        
        
    def init_import_logi_topology(self):
        """Prepare logical topology to make the conversion"""
        print("Preparing logical topology for import...")
            
        with open(self.file_json, 'r') as json_file:
            topology_data = json.load(json_file)
        
        with open(self.file_modified_json, 'w') as json_file:
            json.dump(topology_data, json_file, indent=2)
            
        with open(self.file_yaml, 'r') as file:
            config_data = yaml.safe_load(file)
        
        nodes = []
            
        for node_config in config_data.get('nodes', []):
            node_name = node_config.get('name')
            node_type = node_config.get('type')
            node_neighbors = node_config.get('neighbors').split()
                
            # if node is not an host, add loopback ip address
            if node_type != 'host':
                self.add_loopback(node_name)       
                    
            # remove unused links in logical topology (! : not physical topology)
            for neighbors in self.topology.get_neighbors(node_name):
                if neighbors not in node_neighbors:
                    self.remove_link(node_name, neighbors)
                        
            nodes.append(node_name)
        
        # remove unused nodes in logical topology (! : not physical topology) 
        for node in self.topology.get_nodes():
            if node not in nodes:
                self.remove_node(node)
            
        self.update_topology() 
        

    def import_logi_topology(self):
        """Convert physical topology into logical topology entered by the user"""
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
                    if self.file_to_compile == 'firewall':
                        self.compileWanted = True
                    fw_node = Firewall(node_name, node_neighbors, node_inflow, self.topology, self.compileWanted)
                    self.controllers[node_name] = fw_node
                    self.compileWanted = False

                elif node_type == 'load-balancer':
                    if self.file_to_compile == 'load-balancer':
                        self.compileWanted = True
                    lb_node = LoadBalancer(node_name, node_neighbors, node_inflow, self.topology, self.compileWanted)
                    self.controllers[node_name] = lb_node
                    self.compileWanted = False

                elif node_type == 'router':
                    if self.file_to_compile == 'router':
                        self.compileWanted = True
                    router_node = RouterController(node_name, node_neighbors, node_inflow, self.topology, self.compileWanted)
                    self.controllers[node_name] = router_node
                    self.compileWanted = False

                elif node_type == 'router-lw':
                    if self.file_to_compile == 'router-lw':
                        self.compileWanted = True
                    lw_router_node = RouterController(node_name, node_neighbors, node_inflow, self.topology, self.compileWanted)
                    self.controllers[node_name] = lw_router_node
                    self.compileWanted = False
                    
                elif node_type == 'host':
                    host_node = Host(node_name, node_neighbors, node_inflow, self.topology, False)
                    self.controllers[node_name] = host_node

                else:
                    print(f"Invalid type for node: {node_type}")
                    exit(1)

        
    def add_loopback(self, node_name: str):
        """Add loopback ip address"""
        with open(self.file_modified_json, 'r') as json_file:
            topology_data = json.load(json_file)
            
        node_config = topology_data.get('nodes', [])
        
        node_config = [node for node in node_config if node['id'] == node_name][0]
        node_config['loopback'] = "127.0.0."+str(int(node_name.split('s')[1]) + 1)
        
        with open(self.file_modified_json, 'w') as json_file:
            json.dump(topology_data, json_file, indent=2)
                    

    def add_node(self, name: str):
        """Add a node in the topology json file"""
        with open(self.file_modified_json, 'r') as json_file:
            topology_data = json.load(json_file)
                
        with open(self.file_json, 'r') as json_file:
            topology_save_data = json.load(json_file)

        # retrieve the node in the copy file
        node_config = [node for node in topology_save_data.get('nodes', []) if node['id'] == name]
        
        if node_config == []:
            print(f"Node {name} is not existing in the physical network")
            return
        
        topology_data.setdefault('nodes', []).append(node_config)

        with open(self.file_modified_json, 'w') as json_file:
            json.dump(topology_data, json_file, indent=2)

    def remove_node(self, name):
        """Remove a node in the topology json file"""
        with open(self.file_modified_json, 'r') as json_file:
            topology_data = json.load(json_file)

        existing_nodes = [node['id'] for node in topology_data.get('nodes', [])]
        if name not in existing_nodes:
            return

        topology_data['nodes'] = [node for node in topology_data['nodes'] if node['id'] != name]
        topology_data['links'] = [link for link in topology_data['links'] if link['node1'] != name and link['node2'] != name]

        with open(self.file_modified_json, 'w') as json_file:
            json.dump(topology_data, json_file, indent=2)
            
            
    def add_link(self, node1: str, node2: str):
        """Add a link between node1 and node2 in the topology json file"""
        with open(self.file_modified_json, 'r') as json_file:
            topology_data = json.load(json_file)
                
        with open(self.file_json, 'r') as json_file:
            topology_save_data = json.load(json_file)
            
        # retrieve the link in the copy file
        link = None
        for link_data in topology_save_data.get('links', []):
            if (link_data['node1'] == node1 and link_data['node2'] == node2) or \
            (link_data['node1'] == node2 and link_data['node2'] == node1):
                link = link_data
                break

        if link is not None:
            topology_data.setdefault('links', []).append(link)

        with open(self.file_modified_json, 'w') as json_file:
            json.dump(topology_data, json_file, indent=2)
            
    def remove_link(self, node1: str, node2: str):
        """Remove the link between node1 and node2 in the topology json file"""
        with open(self.file_modified_json, 'r') as json_file:
            topology_data = json.load(json_file)

        link_index = None
        for i, link in enumerate(topology_data.get('links', [])):
            if (link['node1'] == node1 and link['node2'] == node2) or \
               (link['node1'] == node2 and link['node2'] == node1):
                link_index = i
                break

        if link_index is not None:  
            removed_link = topology_data['links'].pop(link_index)
            with open(self.file_modified_json, 'w') as json_file:
                json.dump(topology_data, json_file, indent=2)
                
                
    def list_nodes(self):
        """List all nodes running in the network."""
        print("Nodes:")
        for node in list(self.topology.get_nodes().keys()):
            print(f"{node}")
            
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
