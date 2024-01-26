import cmd
import yaml
from colorama import init, Fore

from src.equipment.meta_controller import MetaController

class Api(cmd.Cmd, MetaController):
    def __init__(self, meta_controller: MetaController):
        cmd.Cmd.__init__(self)
        init(autoreset=True)
        self.meta_controller = meta_controller
        self.prompt = f"{Fore.GREEN}RaPaCe-API>{Fore.RESET} "
        self.topology_file = self.meta_controller.file_yaml
        self.topology = self.load_topology()
        
        
    def load_topology(self):
        with open(self.topology_file, 'r') as file:
            topology = yaml.safe_load(file)
        return topology
    
    
    def display_logical_links(self):
        # Refresh the topology
        self.topology = self.load_topology()
        
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
        elif args[0] == "filters":
            print("Seeing filters...")
        elif args[0] == "load":
            print("Seeing load...")
        elif args[0] == "tunnelled":
            print("Seeing tunnelled...")
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
            yaml.dump(self.topology, file)
            
        for node in self.topology['nodes']:
            if node['name'] == args[0]:
                node['neighbors'] = node['neighbors'].replace(args[1], '')
            elif node['name'] == args[1]:
                node['neighbors'] = node['neighbors'].replace(args[0], '')
                
        with open(self.topology_file, 'w') as file:
            yaml.dump(self.topology, file)
            
        # Update topology
        self.meta_controller.update_topology()
        
        # Remove link from the controller
        self.meta_controller.remove_link(args[0], args[1])
        
        # Reset all tables to recalculate shortest path
        self.meta_controller.reset_all_tables()
        
        print(f"Removed link between {args[0]} and {args[1]} and restarted controllers")

    
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
        
        print(f"Added link between {args[0]} and {args[1]} and restarted controllers")



    def do_quit(self, args):
        print("Quitting...")
        return True
    
    def do_exit(self, args):
        return self.do_quit(args)
    

    def do_EOF(self, args):
        return self.do_quit(args)
    