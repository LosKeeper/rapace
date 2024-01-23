from p4utils.mininetlib.network_API import NetworkAPI

net = NetworkAPI()

# General settings
net.setLogLevel('info')
net.setCompiler(p4rt=True)

NB = 8

# Create N nodes
for i in range(0, NB):
    net.addP4Switch(f's{i}')
    
for i in range(0, NB):
    for j in range(i, NB):
        if i != j:
            net.addLink(f's{i}', f's{j}')
    
# Assignment strategy
net.l2()

# Node general options
net.enablePcapDumpAll()
net.enableLogAll()
net.enableCli()
net.startNetwork()
