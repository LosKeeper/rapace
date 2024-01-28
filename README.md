# RAPACE
[![Author](https://img.shields.io/badge/author-@ThomasD-blue)](https://github.com/LosKeeper)
[![Author](https://img.shields.io/badge/author-@EthanH-blue)](https://github.com/EthanAndreas)
> Programmable networks project for M2 study at the University of Strasbourg.

1. [Prerequisites](#prerequisites)
2. [Sujet](#sujet)
3. [Startup "physical" network](#startup-physical-network)
4. [Startup "logical" network](#startup-logical-network)
5. [WARNINGS](#warnings)

## Prerequisites
> The project has been tested on a virtual machine [QEMU](https://polybox.ethz.ch/index.php/s/QlrfHm7uYw6vISe) provided by p4.

- ### Patch
Before starting, it is necessary to patch this virtual machine with the following script:
```bash
cd patch
./patch.sh
```
- ### Python requirements
The project requires many python libraries. To install them, you can use the following command:
```bash
sudo pip install -r requirements.txt
```
> You need to install it as root because all the python programs are launched with sudo.
## [Sujet](sujet.pdf)

## Startup "physical" network
To start the project, you first need to start the "physical" network with :
```bash
sudo python phyNet.py --<light|medium|complex> --layer <2|3>
```
>The ``--layer`` option allows you to choose the layer of the network (layer 2 or 3). The ``--<light|medium|complex>`` option allows you to choose the topology of the network corresponding to the predefined topologies (light, medium or complex).

## Startup "logical" network
After that, you can start the "logical" network with :
```bash
sudo python logiNet.py --input <input_file> 
```
>The ``--input`` option allows you to choose the input file of the logical network corresponding to the predefined input files in the ``topology`` folder.

Other options are available:
| Option                     | Description                   |
| -------------------------- | ----------------------------- |
| ``--no-compile``           | Do not compile the p4 program |
| ``--compile <p4_program>`` | Compile the p4 program only   |
| ``--no-cli``               | Do not start the API CLI      |

It will also start the API CLI. You can see the available commands with ``help``.

## WARNINGS 
- The traceroute is available in TCP using the ``--layer 3`` option only.
