import cmd
import yaml
from colorama import init, Fore
import networkx as nx
import matplotlib.pyplot as plt
import os
import copy

from src.equipment.meta_controller import MetaController

class Api(cmd.Cmd, MetaController):
    def __init__(self, meta_controller: MetaController):
        cmd.Cmd.__init__(self)
        init(autoreset=True)
        self.meta_controller = meta_controller
        self.prompt = f"{Fore.GREEN}RaPaCe-API>{Fore.RESET} "
        self.topology_file = self.meta_controller.file_yaml
        self.topology = None
        self.load_topology()
        
        
    def generate_graph(self, output_file="graph.png"):
        # Load the topology yaml file
        with open(self.topology_file, 'r') as file:
            topology_data = yaml.safe_load(file)

        # Create a directed or undirected graph
        G = nx.Graph()

        # Add nodes to the graph with color attributes
        node_colors = []
        for node in topology_data['nodes']:
            node_id = node['name'].split()[0]
            node_type = node['type'].split()[0]

            if node_type == 'host':
                G.add_node(node_id, color='green')
                node_colors.append('green')
            else:
                G.add_node(node_id, color='red')
                node_colors.append('red')

        added_edges = set()  
        for node in topology_data['nodes']:
            node_id = node['name'].split()[0]
            neighbors = node['neighbors'].split()
            for neighbor in neighbors:
                edge = tuple(sorted([node_id, neighbor]))
                if edge not in added_edges: 
                    G.add_edge(node_id, neighbor)
                    added_edges.add(edge)

        # Draw the graph with node colors and specified node shape
        pos = nx.spring_layout(G)
        
        # Clear the current figure (prevents overlapping graphs)
        plt.clf()
        
        nx.draw(
            G,
            pos,
            with_labels=True,
            font_weight='bold',
            node_size=700,
            node_color=node_colors,
            font_size=8,
            font_color='black',
            edge_color='black',
            node_shape='o' 
        )

        # Save the graph as an image file
        output_path = os.path.join(os.getcwd(), output_file)
        plt.savefig(output_path, format="png")

        print(f"Topology graph saved as {output_file}")
        
        
    def load_topology(self):
        with open(self.topology_file, 'r') as file:
            topology = yaml.safe_load(file)
        self.topology = topology
    
    
    def display_logical_links(self):
        # Refresh the topology
        self.load_topology()
        
        print("Logical Links:")
        for node in self.topology['nodes']:
            node_name = node['name']
            neighbors = node.get('neighbors', []).split()
            switch_type = node.get('type')
            for neighbor in neighbors:
                print(f"{switch_type} : {node_name} <---> {neighbor}")
                
        
    def do_help(self, args):
        print("Available commands:")
        # Get a list of all methods in the class
        methods = self.get_names()
        # Filter the list to only include methods that start with 'do_'
        excluded_methods = {'do_EOF', 'do_help', 'do_quit', 'do_exit'}
        commands = [method[3:] for method in methods if method.startswith('do_') and method not in excluded_methods]
        for command in commands:
            print(f"  {command}")
        print("Type '<command> help' for more information on a specific command")
        
        
    def do_add_fw_rule(self, args):
        # Split the argument string into a list of words
        args = args.split()

        # Check if args is empty or if the first argument is "help"
        if not args or (args[0] == "help") or len(args) < 5:
            print("Usage: add_fw_rule <src_ip> <dst_ip> <udp | tcp> <src_port> <dst_port>")
            return

        firewall = self.meta_controller.get_firewall()
        firewall.add_rule(args[0], args[1], args[2], int(args[3]), int(args[4]))
        print(f"Added firewall rule: {args[0]} {args[1]} {args[2]} {args[3]} {args[4]}")
        
        
    def do_set_rate_lb(self, args):
        # Split the argument string into a list of words
        args = args.split()

        # Check if args is empty or if the first argument is "help"
        if not args or (args[0] == "help") or len(args) < 1:
            print("Usage: set_rate_lb <pkts/s>")
            return

        print("Setting rate...")
        
        
    def do_add_encap_node(self, args):
        # Split the argument string into a list of words
        args = args.split()

        # Check if args is empty or if the first argument is "help"
        if not args or (args[0] == "help") or len(args) < 2:
            print("Usage: add_encap_node <flow> <node>")
            return

        print("Adding encap node...")


    def do_swap(self, args):
        # Split the argument string into a list of words
        args = args.split()

        # Check if args is empty or if the first argument is "help"
        if not args or (args[0] == "help") or len(args) < 2:
            print("Usage: swap <node_id> <equipment> [args]")
            return

        # Swap node
        self.meta_controller.swap_node(args[0], args[1])
        
        # Reset all tables to recalculate shortest path
        self.meta_controller.reset_all_tables()      
        
        print(f"Swapped {args[0]} with {args[1]}")

        
    def do_see(self, args):
        args = args.split()  # Split the argument string into a list of words
        if not args or (args[0] == "help") or len(args) != 1:
            print("Usage: see <argument>")
            print("available arguments: topology, filters, load, tunnelled")
            return
        
        if args[0] == "topology":
            self.display_logical_links()
            self.generate_graph()
        elif args[0] == "filters":
            fws_packets = self.meta_controller.get_filtered_packets_nb()
            print(f"Number of packets filtered by firewalls: {fws_packets}")
        elif args[0] == "load":
            nodes_packets = self.meta_controller.get_total_packets_nb()
            print("Number of packets received per equipment: ")
            for node_packets in nodes_packets:
                print(f"- on {node_packets[0]}: {node_packets[1]} packets received")
        elif args[0] == "tunnelled":
            routers_packets = self.meta_controller.get_encapsulated_packets_nb()
            print(f"Number of packets encapsulated by routers: {routers_packets}")
        else:
            print("Usage: see <argument>")
            print("available arguments: topology, filters, load, tunnelled")
            
    
    def do_change_weight(self, args):
        # Check for arguments
        args = args.split()
        if not args or (args[0] == "help") or len(args) != 2:
            print("Usage: change_weight <link> <weight>")
            return
        
        print("Changing weight...")

    
    def do_remove_link(self, args):
        # Check for arguments
        args = args.split()
        if not args or (args[0] == "help") or len(args) != 2:
            print("Usage: remove_link <node1> <node2>")
            return
        
        # Check if link exists
        for node in self.topology['nodes']:
            if node['name'] == args[0]:
                if args[1] not in node['neighbors'].split():
                    print(f"Link between {args[0]} and {args[1]} does not exist")
                    return
            elif node['name'] == args[1]:
                if args[0] not in node['neighbors'].split():
                    print(f"Link between {args[0]} and {args[1]} does not exist")
                    return
     
            # Remove link from topology yaml file
            with open(self.topology_file, 'w') as file:
                yaml.dump(self.topology, file,  default_flow_style=None)

            # Make a copy of the file
            topology_copy = copy.deepcopy(self.topology)
            with open(self.topology_file.split('.')[0] + '_save.yaml', 'w') as file_save:
                yaml.dump(topology_copy, file_save,  default_flow_style=None)

            for node in topology_copy['nodes']:
                if node['name'] == args[0]:
                    node['neighbors'] = node['neighbors'].replace(args[1], '')
                elif node['name'] == args[1]:
                    node['neighbors'] = node['neighbors'].replace(args[0], '')

            # Write the modified topology to the original file
            with open(self.topology_file, 'w') as file:
                yaml.dump(topology_copy, file,  default_flow_style=None)

            
        # Remove link from the controller
        self.meta_controller.remove_link(args[0], args[1])
        
        # Reset all tables to recalculate shortest path
        self.meta_controller.reset_all_tables()
        
        print(f"Removed link between {args[0]} and {args[1]} and reset tables to recalculate shortest path")

    
    def do_add_link(self, args):
        # Check for arguments
        args = args.split()
        if not args or (args[0] == "help") or len(args) != 2:
            print("Usage: add_link <node1> <node2>")
            return
        
        # Check if link already exists
        for node in self.topology['nodes']:
            if node['name'] == args[0]:
                if args[1] in node['neighbors'].split():
                    print(f"Link between {args[0]} and {args[1]} already exists")
                    return
            elif node['name'] == args[1]:
                if args[0] in node['neighbors'].split():
                    print(f"Link between {args[0]} and {args[1]} already exists")
                    return
        
        # Add link to the topoly yaml file
        with open(self.topology_file, 'w') as file:
            yaml.dump(self.topology, file)
            
        for node in self.topology['nodes']:
            if node['name'] == args[0]:
                node['neighbors'] = node['neighbors']+' '+str(args[1])
            elif node['name'] == args[1]:
                node['neighbors'] = node['neighbors']+' '+str(args[0])
                
        with open(self.topology_file, 'w') as file:
            yaml.dump(self.topology, file)
        
        # Update topology
        self.meta_controller.update_topology()
        
        # Add link to the controller
        self.meta_controller.add_link(args[0], args[1])
        
        # Reset all tables to recalculate shortest path
        self.meta_controller.reset_all_tables()
        
        print(f"Added link between {args[0]} and {args[1]} and reset tables to recalculate shortest path")


    def do_quit(self, args):
        print("Quitting...")
        return True
    
    def do_exit(self, args):
        return self.do_quit(args)
    

    def do_EOF(self, args):
        return self.do_quit(args)
    