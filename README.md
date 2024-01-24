# RAPACE
> Programmable networks project

## Authors
- Thomas DUMOND
- Ethan HURET

## Prerequisites
> The project has been tested on a virtual machine [QEMU] [QEMU](https://polybox.ethz.ch/index.php/s/QlrfHm7uYw6vISe) provided by p4.

- ### Patch
Before starting, it is necessary to patch this virtual machine with the following script:
```bash
cd patch
./patch.sh
```
## [Sujet](sujet.pdf)

## Startup
- To start the project, you first need to start the "physical" network with :
```bash
sudo python phyNet.py
```
- Next, enter the logical network topology (the one that will be used) in ``topology.yaml``.
- Finally, start the logical network with :
```bash
sudo python logiNet.py 
```