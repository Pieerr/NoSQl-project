# Projet NoSQL - Exploration de Bases de Données MongoDB et Neo4j

Ce projet est réalisé dans le cadre du cours "NoSQL Databases" à ESIEA 2024-2025.

## Description

Cette application permet d'explorer et d'analyser des données de films stockées dans deux types de bases de données NoSQL :
- **MongoDB** (base de données orientée document)
- **Neo4j** (base de données orientée graphe)

L'application offre une interface utilisateur développée avec Streamlit pour interagir avec les données, exécuter des requêtes et visualiser les résultats.

## Fonctionnalités

- Connexion aux bases de données MongoDB et Neo4j (locales ou cloud)
- Import de données depuis un fichier JSON
- Conversion de données de MongoDB vers Neo4j
- Exécution de requêtes sur MongoDB :
  - Analyses statistiques des films (années, votes, revenus, etc.)
  - Visualisations des distributions et corrélations
  - Filtrage et regroupement des données
- Exécution de requêtes sur Neo4j :
  - Analyse des relations entre acteurs et films
  - Recherche de chemins et de connexions
  - Détection de communautés d'acteurs
  - Recommandations de films

## Installation

1. Cloner le dépôt :
```bash
git clone https://github.com/Pieerr/NoSQl-project.git
cd NoSQl-project
```

2. Installer les dépendances :
```bash
pip install -r requirements.txt
```

3. Configurer les bases de données :
   - MongoDB (local ou Atlas)
   - Neo4j (local ou cloud)

## Structure du projet

```
projet_nosql/
├── app.py                  # Application Streamlit principale
├── mongodb_connect.py      # Connecteur MongoDB
├── neo4j_connect.py        # Connecteur Neo4j
├── queries/
│   ├── __init__.py         # (fichier vide)
│   ├── mongodb_queries.py  # Requêtes MongoDB
│   └── neo4j_queries.py    # Requêtes Neo4j
└── data/
    └── movies.json         # Données des films
```

## Utilisation

1. Lancer l'application Streamlit :
```bash
streamlit run app.py
```

2. Dans l'interface web :
   - Configurer les connexions aux bases de données
   - Importer les données
   - Exécuter des requêtes
   - Visualiser les résultats

## Requêtes implémentées

L'application implémente les 30 requêtes demandées dans l'énoncé du projet, dont :

### MongoDB
- Année avec le plus de films
- Nombre de films après 1999
- Moyenne des votes en 2007
- Corrélation entre durée et revenus
- Evolution de la durée moyenne par décennie
- Et plus...

### Neo4j
- Acteur avec le plus de films
- Acteurs ayant joué avec Anne Hathaway
- Chemin le plus court entre deux acteurs
- Communautés d'acteurs
- Recommandations de films
- Et plus...

## Captures d'écran

[À ajouter]

## Contributeurs

- [Votre nom]

## Licence

[À définir]
