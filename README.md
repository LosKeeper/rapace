# RAPACE
> Projet de réseaux programmables

## Auteurs
- Thomas DUMOND
- Ethan HURET

## Prérequis
> Le projet a été testé sur une machine virtuelle [QEMU](https://polybox.ethz.ch/index.php/s/QlrfHm7uYw6vISe) fournie par p4.

- ### Patch
Avant de commencer, il est nécessaire de patcher cette machine virtuelle avec le script suivant :
```bash
cd patch
./patch.sh
```
## [Sujet](sujet.pdf)

## Démarrage
Pour démarrer le projet, il faut dans un premier rentre la topologie du réseau dans ``topology.yaml`` et éxecuter la commande :
```bash
python network.py 
```