from p4utils.mininetlib.network_API import NetworkAPI

net = NetworkAPI()

# General settings
net.setLogLevel('info')
net.setCompiler(p4rt=True)
net.execScript('python controller.py', reboot=True)

# Network definition
availables_equipment = ['firewall', 'router-controller','touter-lw-controller', 'load-balancer', 'host']

# Ask for the equipement running on each node
node_number = int(input("Nombre de noeuds: "))

for i in range(node_number):
    node_name = input("Nom du noeud: ")
    node_type = input("Type du noeud: (firewall, router-controller, router-lw-controller, load-balancer, host)")
    if node_type in availables_equipment:
        if node_type == 'firewall':
            net.addP4Switch(node_name)
            net.setP4Source(node_name, 'equipment/firewall.p4')
            
        elif node_type == 'router-controller':
            net.addP4Switch(node_name)
            net.setP4Source(node_name, 'equipment/router-controller.p4')
            
        elif node_type == 'router-lw-controller':
            net.addP4Switch(node_name)
            net.setP4Source(node_name, 'equipment/router-lw-controller.p4')
            
        elif node_type == 'load-balancer':
            net.addP4Switch(node_name)
            net.setP4Source(node_name, 'equipment/load-balancer.p4')
            
        elif node_type == 'host':
            net.addHost(node_name)
            
    else:
        print("Type de noeud invalide")
        exit(1)

# Ask for the links between the nodes
link_number = int(input("Nombre de liens: "))

for i in range(link_number):
    node1 = input("Nom du premier noeud: ")
    node2 = input("Nom du deuxième noeud: ")
    net.addLink(node1, node2) #TODO: User port for each link
    
    
#Assignment strategy
net.l3()   
    
# Node general options
net.enablePcapDumpAll()
net.enableLogAll()
net.enableCli()
net.startNetwork()