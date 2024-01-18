from p4utils.mininetlib.network_API import NetworkAPI
import yaml

net = NetworkAPI()

# General settings
net.setLogLevel('info')
net.setCompiler(p4rt=True)
net.execScript('python controller.py', reboot=True)

# Load network configuration from YAML file
config_file = "topology.yaml"
with open(config_file, 'r') as file:
    config_data = yaml.safe_load(file)

# Network definition
available_equipment = ['firewall', 'router-controller', 'router-lw-controller', 'load-balancer', 'host']

for node_config in config_data.get('nodes', []):
    node_name = node_config.get('name')
    node_type = node_config.get('type')

    print(node_name)

    if node_type in available_equipment:
        if node_type == 'firewall':
            net.addP4Switch(node_name)
            net.setP4Source(node_name, f'equipment/{node_type}.p4')
        elif node_type in ['router-controller', 'router-lw-controller', 'load-balancer']:
            net.addP4Switch(node_name)
            net.setP4Source(node_name, f'equipment/{node_type}.p4')
        elif node_type == 'host':
            net.addHost(node_name)
    else:
        print(f"Invalid type for node : {node_type}")
        exit(1)

for link_config in config_data.get('links', []):
    source = link_config.get('source')
    print(source)
    target = link_config.get('target')
    print(target)
    net.addLink(source, target)

# Assignment strategy
net.l3()

# Node general options
net.enablePcapDumpAll()
net.enableLogAll()
net.enableCli()
net.startNetwork()
