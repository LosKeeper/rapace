from p4utils.utils.sswitch_thrift_API import SimpleSwitchThriftAPI
from p4utils.utils.topology import NetworkGraph 
from typing import List

from src.equipment.controller import Controller

class RouterLWController(Controller):
    def __init__(self, name: str, neighbors: List[str], inflow: str, topology: NetworkGraph) -> None:
        super().__init__(name, neighbors, inflow, topology)
        # Add specific attributes for lightweight router controller
        self.compile('equipment/router-lw.p4')
        self.flash('equipment/router-lw.json')
    
    def init_table(self):
        # Implement lightweight router controller table initialization
        pass