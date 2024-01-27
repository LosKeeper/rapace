import yaml
import json

from p4utils.utils.helper import load_topo

from src.equipment.firewall import Firewall
from src.equipment.load_balancer import LoadBalancer
from src.equipment.router import RouterController
from src.equipment.router_lw import RouterLwController

class MetaController:
    def __init__(self, user_input: str, file_to_compile: str, compileWanted: bool = True):
        self.user_input = user_input
        self.file_yaml = f'{user_input}.yaml'
        self.file_json = 'topology.json'
        self.file_2_json = 'topology_2.json'
        self.topology = load_topo(self.file_json)
        self.controllers = {}
        self.equipment = {'firewall': [], 'load-balancer': [], 'router': [], 'router-lw': []}
        self.file_to_compile = file_to_compile
        self.compileWanted = compileWanted
        if file_to_compile != "" and file_to_compile is not None:
            self.compileWanted = False
        self.compiledFiles = []
        self.init_import_logi_topology()
        self.import_logi_topology()


    def update_topology(self):
        """Update topology with json file"""
        self.topology = load_topo(self.file_2_json)
        
        
    def init_import_logi_topology(self):
        """Prepare logical topology to make the conversion"""
        print("Preparing logical topology for import...")
            
        with open(self.file_json, 'r') as json_file:
            topology_data = json.load(json_file)
        
        with open(self.file_2_json, 'w') as json_file:
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

                if node_type == 'firewall':
                    print(f'{node_name} node: firewall')
                    _compile = self.compileWanted
                    if self.file_to_compile == 'firewall' and 'firewall' not in self.compiledFiles:
                        _compile = True
                    if 'firewall' in self.compiledFiles:
                        _compile = False
                    fw_node = Firewall(node_name, node_neighbors, node_inflow, self.topology, _compile)
                    self.controllers[node_name] = fw_node
                    self.equipment['firewall'].append(fw_node)
                    if _compile == True:
                        self.compiledFiles.append('firewall')

                elif node_type == 'load-balancer':
                    print(f'{node_name} node: load-balancer')
                    _compile = self.compileWanted
                    if self.file_to_compile == 'load-balancer':
                        _compile = True
                    if 'load-balancer' not in self.compiledFiles:
                        _compile = False
                    lb_node = LoadBalancer(node_name, node_neighbors, node_inflow, self.topology, _compile)
                    self.controllers[node_name] = lb_node
                    self.equipment['load-balancer'].append(lb_node)
                    if _compile == True:
                        self.compiledFiles.append('load-balancer')

                elif node_type == 'router':
                    print(f'- {node_name} node: router')
                    _compile = self.compileWanted
                    if self.file_to_compile == 'router' and 'router' not in self.compiledFiles:
                        _compile = True
                    if 'router' in self.compiledFiles:
                        _compile = False
                    router_node = RouterController(node_name, node_neighbors, node_inflow, self.topology, _compile)
                    self.controllers[node_name] = router_node
                    self.equipment['router'].append(router_node)
                    if _compile == True:
                        self.compiledFiles.append('router')
                    

                elif node_type == 'router-lw':
                    print(f'- {node_name} node: router-lw')
                    _compile = self.compileWanted
                    if self.file_to_compile == 'router-lw' and 'router-lw' not in self.compiledFiles:
                        _compile = True
                    if 'router-lw' in self.compiledFiles:
                        _compile = False
                    lw_router_node = RouterLwController(node_name, node_neighbors, node_inflow, self.topology, _compile)
                    self.controllers[node_name] = lw_router_node
                    self.equipment['router-lw'].append(lw_router_node)
                    if _compile == True:
                        self.compiledFiles.append('router-lw')
                   
                elif node_type == 'host':
                    pass

                else:
                    print(f"Invalid type for node: {node_type}")
                    exit(1)

        
    def add_loopback(self, node_name: str):
        """Add loopback ip address"""
        with open(self.file_2_json, 'r') as json_file:
            topology_data = json.load(json_file)
            
        node_config = topology_data.get('nodes', [])
        
        node_config = [node for node in node_config if node['id'] == node_name][0]
        node_config['loopback'] = "127.0.0."+str(int(node_name.split('s')[1]))
        
        with open(self.file_2_json, 'w') as json_file:
            json.dump(topology_data, json_file, indent=2)
                    

    def add_node(self, name: str):
        """Add a node in the topology json file"""
        with open(self.file_2_json, 'r') as json_file:
            topology_data = json.load(json_file)
                
        with open(self.file_json, 'r') as json_file:
            topology_save_data = json.load(json_file)

        # retrieve the node in the copy file
        node_config = [node for node in topology_save_data.get('nodes', []) if node['id'] == name]
        
        if node_config == []:
            print(f"Node {name} is not existing in the physical network")
            return
        
        topology_data.setdefault('nodes', []).append(node_config)

        with open(self.file_2_json, 'w') as json_file:
            json.dump(topology_data, json_file, indent=2)

    def remove_node(self, name):
        """Remove a node in the topology json file"""
        with open(self.file_2_json, 'r') as json_file:
            topology_data = json.load(json_file)

        existing_nodes = [node['id'] for node in topology_data.get('nodes', [])]
        if name not in existing_nodes:
            return

        topology_data['nodes'] = [node for node in topology_data['nodes'] if node['id'] != name]
        topology_data['links'] = [link for link in topology_data['links'] if link['node1'] != name and link['node2'] != name]

        with open(self.file_2_json, 'w') as json_file:
            json.dump(topology_data, json_file, indent=2)
            
            
    def add_link(self, node1: str, node2: str):
        """Add a link between node1 and node2 in the topology json file"""
        with open(self.file_2_json, 'r') as json_file:
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

        with open(self.file_2_json, 'w') as json_file:
            json.dump(topology_data, json_file, indent=2)
            
    def remove_link(self, node1: str, node2: str):
        """Remove the link between node1 and node2 in the topology json file"""
        with open(self.file_2_json, 'r') as json_file:
            topology_data = json.load(json_file)

        link_index = None
        for i, link in enumerate(topology_data.get('links', [])):
            if (link['node1'] == node1 and link['node2'] == node2) or \
               (link['node1'] == node2 and link['node2'] == node1):
                link_index = i
                break

        if link_index is not None:  
            removed_link = topology_data['links'].pop(link_index)
            with open(self.file_2_json, 'w') as json_file:
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

    def get_firewall(self):
        """Get firewall controller."""
        for node_id, controller in self.controllers.items():
            if type(controller).__name__ == 'Firewall':
                return controller
        return None
    
    def swap_node(self, node_name:str, equipment: str):
        """Swap a node by another one"""
        
        # Check if this node is existing
        if node_name not in self.topology.get_p4switches():
            print(f"Node {node_name} is not existing in the physical network or it's an host")
            return
        
        # Update the yaml file
        with open(self.file_yaml, 'r') as file:
            config_data = yaml.safe_load(file)
            
        for node_config in config_data.get('nodes', []):
            if node_config.get('name') == node_name:
                node_config['type'] = equipment
                node_inflow = node_config.get('inflow')
                
        with open(self.file_yaml, 'w') as file:
            yaml.dump(config_data, file, indent=2)
            
        # Update the json file
        with open(self.file_2_json, 'r') as json_file:
            topology_data = json.load(json_file)
            
        for node_config in topology_data.get('nodes', []):
            if node_config.get('id') == node_name:
                node_config['type'] = equipment
                
        with open(self.file_2_json, 'w') as json_file:
            json.dump(topology_data, json_file, indent=2)
            
        # Update the topology
        self.update_topology()
        
        # Start new equipment
        if equipment == "firewall":
            self.controllers[node_name] = Firewall(node_name, self.topology.get_neighbors(node_name), None, self.topology, False)
        elif equipment == "load-balancer":
            self.controllers[node_name] = LoadBalancer(node_name, self.topology.get_neighbors(node_name), node_inflow, self.topology, False)
        elif equipment == "router":
            self.controllers[node_name] = RouterController(node_name, self.topology.get_neighbors(node_name), None, self.topology, False)
        elif equipment == "router-lw":
            self.controllers[node_name] = RouterLwController(node_name, self.topology.get_neighbors(node_name), None, self.topology, False)
        else:
            print(f"Invalid type for node: {node_type}")
            
            
    def reset_all_tables(self):
        """Reset all tables of all controllers"""
        for node_id, controller in self.controllers.items():
            print(f"Resetting tables of {node_id}...")
            controller.init_table()
            controller.mininet_update()
            
            
    def get_filtered_packets_nb(self):
        """Get the number of packets filtered by firewalls"""
        fws_packets = 0
        for controller in self.equipment['firewall']:
            fws_packets += controller.get_filtered_packets_nb()
        return fws_packets
    
    def get_total_packets_nb(self):
        """Get the number of packets received on every equipment"""
        nodes_packets = []
        for node_id, controller in self.controllers.items():
            nodes_packets.append([node_id, controller.get_total_packets_nb()])
        return nodes_packets
    
    def get_encapsulated_packets_nb(self):
        """Get the number of packets encapsulated by routers"""
        routers_packets = 0
        for controller in self.equipment['router']:
            routers_packets += controller.get_total_packets_nb()
        return routers_packets
        
        