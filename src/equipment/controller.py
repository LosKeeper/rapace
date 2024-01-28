from p4utils.utils.compiler import P4C
from p4utils.utils.sswitch_thrift_API import SimpleSwitchThriftAPI
from p4utils.utils.topology import NetworkGraph 
from typing import List

class Controller:
    def __init__(self, name: str, neighbors: List[str], inflow: str, topology: NetworkGraph, compileWanted: bool) -> None:
        self.name = name
        self.topology = topology
        if name != 'host':
            self.api = SimpleSwitchThriftAPI(self.topology.get_thrift_port(name))
        self.compileWanted = compileWanted
        self.mininet_update()
        
    def compile(self, p4_src: str):
        if self.compileWanted:
            print('Compiling P4 source file...')
            source = P4C(p4_src, "/usr/local/bin/p4c")
            source.compile()
        else:
            print('No compilation, only loading JSON file...')
        
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
        
    def update_controller_topology(self, topology: NetworkGraph):
        self.topology = topology
        self.mininet_update()