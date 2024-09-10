# Mirroot setup tool

Mirroot setup tool est un projet en cours de developpement d'outil blueteam de configuration d'environnement Docker avec des utilisateurs leurres et une surveillance de leur activité. Cet outil est particulièrement utile pour les tests de sécurité et la mise en place d’un environnement de type honeypot.

## Fonctionnalités

	*	Génération de mots de passe sécurisés : Le script génère automatiquement des mots de passe forts pour les utilisateurs leurres.
	*	Création de fichiers Docker essentiels : Génère un Dockerfile, un fichier docker-compose.yml, et des scripts shell pour créer et surveiller les utilisateurs leurres.
	* 	Configuration personnalisée : Demande des informations spécifiques pour configurer l’environnement, telles que l’image Docker à utiliser, le nom et le mot de passe de l’administrateur, et le nombre d’utilisateurs leurres.

## Utilisation

## Prérequis

	*	Python version 3
 	*       pip install docker click pwgen
  	* 	chmod +x dmroot.py
   	*	sudo ln -s $(pwd)/dmroot.py /usr/local/bin/dmroot


## Installation
Clonez le dépôt et accédez au répertoire :

	* git clone <URL_DU_DEPOT>
	* cd <NOM_DU_REPERTOIRE> 

## Exécution du script
Pour exécuter le script et générer les fichiers nécessaires, utilisez la commande suivante :

python3 dmroot.py

## Options du script

Le script vous demandera de fournir les informations suivantes :

	* Docker image for the Dockerfile : L'image Docker à utiliser pour le Dockerfile.
	* Admin user name : Le nom de l'utilisateur administrateur avec des privilèges sudo.
	* Admin user password : Le mot de passe pour l'utilisateur administrateur.
	* Docker image for the database : L'image Docker à utiliser pour la base de données.
	* Number of lure users : Le nombre d'utilisateurs leurres à créer (maximum 100).

## Exemple de sortie
Le script générera les fichiers suivants :

	* Dockerfile
	* create_lure_users.sh : Script pour créer les utilisateurs leurres.
	* lure_monitor.sh : Script de surveillance des utilisateurs leurres, qui logue leur connexion et les déconnecte immédiatement.
	* docker-compose.yml : Fichier de configuration Docker Compose.

Ces fichiers seront configurés selon les informations fournies lors de l'exécution du script.

## Notes

Les fichiers générés sont configurés pour une utilisation immédiate, mais peuvent être modifiés pour répondre à des besoins spécifiques.
Le script lure_monitor.sh est configuré avec des permissions restrictives (lecture, écriture et exécution uniquement pour le propriétaire) pour des raisons de sécurité.

## Problèmes à résoudre

* L'utilisation du CPU trop élevée
