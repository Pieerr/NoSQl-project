# Documentation du Projet NoSQL

Cette documentation détaille l'utilisation de l'application d'exploration de bases de données NoSQL (MongoDB et Neo4j) pour l'analyse de données de films.

## Table des matières

1. [Installation](#installation)
2. [Configuration des bases de données](#configuration)
3. [Interface de l'application](#interface)
4. [Requêtes MongoDB](#requetes-mongodb)
5. [Requêtes Neo4j](#requetes-neo4j)
6. [Visualisations](#visualisations)
7. [Structure du code](#structure)
8. [Étendre le projet](#extensions)

## Installation <a name="installation"></a>

### Prérequis

- Python 3.8+
- MongoDB (locale ou Atlas)
- Neo4j (locale ou cloud)

### Installation des dépendances

```bash
# Cloner le dépôt
git clone https://github.com/Pieerr/NoSQl-project.git
cd NoSQl-project

# Installer les dépendances
pip install -r requirements.txt

# Vérifier l'environnement
python setup.py
```

## Configuration des bases de données <a name="configuration"></a>

### MongoDB

#### Locale
- Assurez-vous que MongoDB est installé et en cours d'exécution sur votre machine
- Port par défaut : 27017

#### Atlas (Cloud)
- Créez un compte MongoDB Atlas
- Créez un cluster
- Obtenez la chaîne de connexion

### Neo4j

#### Locale
- Assurez-vous que Neo4j est installé et en cours d'exécution sur votre machine
- Port par défaut : 7687
- Identifiants par défaut : neo4j/Neo4j123 (configurés dans `neo4j_connect.py`)

#### Cloud
- Créez un compte Neo4j Aura ou utilisez une instance Neo4j sur le cloud
- Obtenez l'URI, le nom d'utilisateur et le mot de passe

### Initialisation des bases de données

Un script d'initialisation est fourni pour faciliter la configuration :

```bash
python init_databases.py
```

Ce script vous guide à travers les étapes suivantes :
1. Connexion à MongoDB (locale ou Atlas)
2. Import des données depuis `data/movies.json`
3. Connexion à Neo4j (locale ou cloud)
4. Création des nœuds et relations dans Neo4j

## Interface de l'application <a name="interface"></a>

L'application utilise Streamlit pour fournir une interface web intuitive.

### Lancement de l'application

```bash
streamlit run app.py
```

### Navigation

L'application est divisée en plusieurs pages accessibles depuis la barre latérale :

1. **Accueil** : Présentation du projet
2. **Configuration** : Connexion aux bases de données
3. **MongoDB - Requêtes** : Exécution des requêtes MongoDB
4. **Neo4j - Requêtes** : Exécution des requêtes Neo4j
5. **Visualisations** : Visualisations graphiques des données
6. **À propos** : Informations sur le projet

## Requêtes MongoDB <a name="requetes-mongodb"></a>

L'application implémente 13 requêtes MongoDB correspondant aux questions de l'énoncé du projet.

### Liste des requêtes disponibles

1. Année avec le plus de films
2. Nombre de films après 1999
3. Moyenne des votes en 2007
4. Histogramme des films par année
5. Genres disponibles
6. Film avec le plus de revenus
7. Réalisateurs avec plus de 5 films
8. Genre avec le plus de revenus en moyenne
9. Top 3 films par décennie
10. Film le plus long par genre
11. Vue des films avec notes > 80 et revenus > 50M
12. Corrélation durée/revenus
13. Évolution durée moyenne par décennie

### Exemple d'utilisation

1. Accédez à la page "MongoDB - Requêtes"
2. Sélectionnez une requête dans la liste déroulante
3. Cliquez sur "Exécuter la requête"
4. Les résultats s'affichent sous forme de tableau ou de graphique

## Requêtes Neo4j <a name="requetes-neo4j"></a>

L'application implémente 17 requêtes Neo4j correspondant aux questions de l'énoncé du projet.

### Liste des requêtes disponibles

14. Acteur avec le plus de films
15. Acteurs ayant joué avec Anne Hathaway
16. Acteur avec le plus de revenus
17. Moyenne des votes
18. Genre le plus représenté
19. Films des acteurs ayant joué avec vous
20. Réalisateur avec le plus d'acteurs
21. Films les plus connectés
22. 5 acteurs avec le plus de réalisateurs
23. Recommandation de film pour un acteur
24. Relation d'influence entre réalisateurs
25. Chemin le plus court entre deux acteurs
26. Analyse des communautés d'acteurs
28. Recommandation basée sur les préférences d'un acteur
29. Relation de concurrence entre réalisateurs
30. Analyse des collaborations réalisateur-acteur

### Exemple d'utilisation

1. Accédez à la page "Neo4j - Requêtes"
2. Sélectionnez une requête dans la liste déroulante
3. Remplissez les champs supplémentaires si nécessaire (ex: noms d'acteurs)
4. Cliquez sur "Exécuter la requête"
5. Les résultats s'affichent sous forme de tableau ou de graphique

## Visualisations <a name="visualisations"></a>

La page "Visualisations" offre des représentations graphiques des données pour MongoDB et Neo4j.

### Visualisations MongoDB

- Histogramme des films par année
- Distribution des genres
- Corrélation durée/revenus
- Évolution de la durée moyenne par décennie
- Top réalisateurs par nombre de films

### Visualisations Neo4j

- Top acteurs par nombre de films
- Statistiques des acteurs
- Collaborations réalisateur-acteur

## Structure du code <a name="structure"></a>

### Fichiers principaux

- `app.py` : Application Streamlit principale
- `mongodb_connect.py` : Classe pour la connexion à MongoDB
- `neo4j_connect.py` : Classe pour la connexion à Neo4j
- `queries/mongodb_queries.py` : Implémentation des requêtes MongoDB
- `queries/neo4j_queries.py` : Implémentation des requêtes Neo4j

### Classes principales

#### MongoDBConnector

```python
class MongoDBConnector:
    def __init__(self, connection_string=None, local=True)
    def import_json_data(self, json_file)
```

#### Neo4jConnector

```python
class Neo4jConnector:
    def __init__(self, uri=None, user=None, password=None, local=True)
    def create_constraints_and_indexes(self)
    def create_film_nodes(self, mongo_connector)
    def create_actor_nodes_and_relationships(self, mongo_connector)
    def create_director_nodes_and_relationships(self, mongo_connector)
    def create_team_nodes(self, team_members)
```

#### MongoDBQueries

```python
class MongoDBQueries:
    def __init__(self, mongo_connector)
    # Méthodes pour chaque requête (query_1_year_with_most_films, etc.)
```

#### Neo4jQueries

```python
class Neo4jQueries:
    def __init__(self, neo4j_connector)
    # Méthodes pour chaque requête (query_14_actor_with_most_films, etc.)
```

## Étendre le projet <a name="extensions"></a>

### Ajouter une nouvelle requête MongoDB

1. Ajoutez une méthode dans la classe `MongoDBQueries` dans `queries/mongodb_queries.py`
2. Mettez à jour l'interface utilisateur dans `app.py` pour inclure la nouvelle requête

### Ajouter une nouvelle requête Neo4j

1. Ajoutez une méthode dans la classe `Neo4jQueries` dans `queries/neo4j_queries.py`
2. Mettez à jour l'interface utilisateur dans `app.py` pour inclure la nouvelle requête

### Améliorer les visualisations

Les visualisations peuvent être améliorées en :
- Ajoutant de nouveaux types de graphiques
- Améliorant l'interactivité avec des widgets Streamlit
- Intégrant des bibliothèques de visualisation plus avancées comme Plotly ou Bokeh

### Optimisations possibles

- Mise en cache des résultats de requêtes avec `@st.cache_data`
- Parallélisation des requêtes longues
- Amélioration de la gestion des erreurs
- Ajout d'un système de journalisation
