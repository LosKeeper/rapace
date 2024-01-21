from p4utils.mininetlib.network_API import NetworkAPI
import yaml

net = NetworkAPI()

# General settings
net.setLogLevel('info')
net.setCompiler(p4rt=True)

# Create N nodes
for i in range(0, 10):
    net.addP4Switch(f's{i}')
    
for i in range(0, 10):
    for j in range(i, 10):
        if i != j:
            net.addLink(f's{i}', f's{j}')
    
# Assignment strategy
net.l3()

# Node general options
net.enablePcapDumpAll()
net.enableLogAll()
net.enableCli()
net.startNetwork()
