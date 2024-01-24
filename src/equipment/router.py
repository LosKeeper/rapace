from p4utils.utils.sswitch_thrift_API import SimpleSwitchThriftAPI
from p4utils.utils.topology import NetworkGraph 
from typing import List

from src.equipment.controller import Controller

class RouterController(Controller):
    def __init__(self, name: str, neighbors: List[str], inflow: str, topology: NetworkGraph, compileWanted: bool) -> None:
        super().__init__(name, neighbors, inflow, topology, compileWanted)
        # Add specific attributes for router controller
        self.compile('p4src/router.p4')
        self.flash('p4src/router.json')
    
    def init_table(self):
        # Implement router controller table initialization
        pass
