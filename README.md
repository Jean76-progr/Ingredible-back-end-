# Ingredible back-end

## Description
Le projet est une application de gestion de recettes culinaires. 
Les utilisateurs peuvent créer un compte, ajouter des ingrédients à leur liste personnelle, créer, modifier et supprimer des recettes, et organiser des menus. 
L'application offre également la possibilité de marquer des recettes comme favorites, fournissant ainsi une expérience personnalisée pour chaque utilisateur. 
La gestion des ingrédients, des recettes et des menus se fait de manière interactive, permettant aux utilisateurs de planifier leurs repas de manière efficace et créative.

## Prérequis
Python version 3.10 conseillée · Postman https://www.postman.com/ (application gratuite à télécharger)

## Installation

1. Clonez le dépôt :
   ```bash
   git clone https://github.com/votre_utilisateur/votre_projet.git
Accédez au répertoire du projet :

bash
Copy code
cd votre_projet
Créez un environnement virtuel :

bash
Copy code
python -m venv venv
Activez l'environnement virtuel (sous Windows) :

bash
Copy code
venv\Scripts\activate
Ou (sous Linux/macOS) :

bash
Copy code
source venv/bin/activate
Installez les dépendances :

bash
Copy code
pip install -r requirements.txt
Configuration
Copiez le fichier .env.example et renommez-le en .env :

bash
Copy code
cp .env.example .env
Mettez à jour le fichier .env avec vos configurations.

Lancement de l'application
bash
Copy code
python app.py
L'application sera accessible à l'adresse http://127.0.0.1:5000/ dans votre navigateur.
