from p4utils.mininetlib.network_API import NetworkAPI

net = NetworkAPI()

# General settings
net.setLogLevel('info')
net.setCompiler(p4rt=True)

NB_S = 8
NB_H = 3

# Create N switches
for i in range(0, NB_S):
    net.addP4Switch(f's{i}')
    
for i in range(0, NB_S):
    for j in range(i, NB_S):
        if i != j:
            net.addLink(f's{i}', f's{j}')

# Create N hosts
for i in range(1, NB_H):
    net.addHost(f'h{i}')
    
for i in range(1, NB_H):
    for j in range(0, NB_S):
        net.addLink(f'h{i}', f's{j}')


# Assignment strategy
net.l3()

# Node general options
net.enablePcapDumpAll()
net.enableLogAll()
net.enableCli()
net.startNetwork()
