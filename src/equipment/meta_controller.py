import yaml
from p4utils.utils.helper import load_topo

from src.equipment.firewall import Firewall
from src.equipment.load_balancer import LoadBalancer
from src.equipment.router import RouterController
from src.equipment.router_lw import RouterLWController


class MetaController:
    def __init__(self, user_input: str, compileWanted: bool = True):
        self.user_input = user_input
        self.file_yaml = f'{user_input}.yaml'
        self.file_json = f'{user_input}.json'
        self.topology = load_topo(self.file_json)
        self.controllers = {}
        self.compileWanted = compileWanted

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

                else:
                    print(f"Invalid type for node: {node_type}")
                    exit(1)

    def list_controllers(self):
        """List all controllers running in the network."""
        print("Controllers:")
        for node_id, controller in self.controllers.items():
            print(f"{node_id}: {type(controller).__name__}")