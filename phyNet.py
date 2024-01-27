from p4utils.mininetlib.network_API import NetworkAPI

import argparse

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Create a physical network')
    parser.add_argument('--layer', type=int, help='Layer of the network (2 or 3)',required=True)
    parser.add_argument('--light', action='store_true', help='Use predefined light version of the network')
    parser.add_argument('--medium', action='store_true', help='Use predefined medium version of the network')
    parser.add_argument('--complex', action='store_true', help='Use predefined complex version of the network')
    args = parser.parse_args()

    if args.light:
        switchNb=2
        hostNb=2
    elif args.medium:
        switchNb=4
        hostNb=2
    elif args.complex:
        switchNb=10
        hostNb=2
    
    net = NetworkAPI()

    # General settings
    net.setLogLevel('info')
    net.setCompiler(p4rt=True)


    # Create N switches
    for i in range(1, switchNb + 1):
        net.addP4Switch(f's{i}')
        
    for i in range(1, switchNb):
        for j in range(i, switchNb + 1):
            if i != j:
                net.addLink(f's{i}', f's{j}')

    # Create N hosts
    for i in range(1, hostNb + 1):
        net.addHost(f'h{i}')
    
    if args.light:
        net.addLink('s1','h1')
        net.addLink('s2','h2')
    elif args.medium:
        net.addLink('s1','h1')
        net.addLink('s4','h2')
    elif args.complex:
        net.addLink('s1','h1')
        net.addLink('s10','h2')

    # Assignment strategy
    if args.layer == 2:
        net.l2()
    else:
        net.l3()

    # Node general options
    net.enablePcapDumpAll()
    net.enableLogAll()
    net.enableCli()
    net.startNetwork()
