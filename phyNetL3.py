from p4utils.mininetlib.network_API import NetworkAPI

net = NetworkAPI()

# General settings
net.setLogLevel('info')
net.setCompiler(p4rt=True)

NB_S = 2

# Create N switches
for i in range(1, NB_S):
    net.addP4Switch(f's{i}')
    
for i in range(1, NB_S):
    for j in range(i, NB_S):
        if i != j:
            net.addLink(f's{i}', f's{j}')

# Create N hosts
net.addHost('h1')
net.addHost('h2')
net.addLink('s1','h1')
net.addLink('s1','h2')

# Assignment strategy
net.l3()

# Node general options
net.enablePcapDumpAll()
net.enableLogAll()
net.enableCli()
net.startNetwork()
