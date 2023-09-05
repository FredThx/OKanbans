# OKanbans

Une gestion de cartes kanbans électroniques.

## Techno

- mongodb
- python
- QT5

## Installation

Télécharger les fichiers okankan.exe et okbanban.css dans un répertoire.
Executer okanban.exe

## Mise à jour

Le programme va chercher la dernière release sur Github et propose de l'installer.

# API

sur http://srv-debian:50890/okanban

Permet à l'application access de saisie des mesures du perçage de créer un kanban incluant de détail des mesures.

mise à jour : ./deploy_server.cmd


## Qté de produit par kanban par defaut

GET http://srv-debian:50890/okanban/qte/{proref}

## Création d'un kanban

POST http://192.168.0.11:50890/okanban avec données au format json



