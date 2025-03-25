"""
Script pour initialiser les bases de données MongoDB et Neo4j avec les données de films.
Ce script effectue les opérations suivantes :
1. Importe les données depuis movies.json dans MongoDB
2. Crée les nœuds et relations dans Neo4j
"""

import os
import sys
import json
from mongodb_connect import MongoDBConnector
from neo4j_connect import Neo4jConnector

def load_team_members():
    """Demande et charge les noms des membres de l'équipe."""
    print("\n👥 Veuillez entrer les noms des membres de l'équipe (séparés par des virgules) :")
    team_input = input().strip()
    team_members = [name.strip() for name in team_input.split(",") if name.strip()]
    
    if not team_members:
        print("⚠️ Aucun membre d'équipe n'a été défini.")
        return []
    
    print(f"✅ {len(team_members)} membres d'équipe enregistrés.")
    return team_members

def initialize_mongodb(json_file="data/movies.json", local=True, connection_string=None):
    """Initialise MongoDB avec les données du fichier JSON."""
    print("\n🔄 Initialisation de MongoDB...")
    
    # Créer une connexion MongoDB
    mongo = MongoDBConnector(connection_string=connection_string, local=local)
    
    if not mongo.client:
        print("❌ Échec de la connexion à MongoDB.")
        return None
    
    # Vérifier si le fichier JSON existe
    if not os.path.isfile(json_file):
        print(f"❌ Le fichier {json_file} n'existe pas.")
        return mongo
    
    # Importer les données
    mongo.import_json_data(json_file)
    
    return mongo

def initialize_neo4j(mongo_connector, local=True, uri=None, user=None, password=None):
    """Initialise Neo4j avec les données de MongoDB."""
    print("\n🔄 Initialisation de Neo4j...")
    
    # Créer une connexion Neo4j
    neo4j = Neo4jConnector(uri=uri, user=user, password=password, local=local)
    
    if not neo4j.graph:
        print("❌ Échec de la connexion à Neo4j.")
        return None
    
    # Créer les contraintes et index
    print("\n🔄 Création des contraintes et index...")
    neo4j.create_constraints_and_indexes()
    
    if not mongo_connector or not mongo_connector.client:
        print("❌ MongoDB n'est pas connecté, impossible d'importer les données.")
        return neo4j
    
    # Créer les nœuds Film
    print("\n🔄 Création des nœuds Film...")
    neo4j.create_film_nodes(mongo_connector)
    
    # Créer les nœuds Actor et leurs relations
    print("\n🔄 Création des nœuds Actor et leurs relations...")
    neo4j.create_actor_nodes_and_relationships(mongo_connector)
    
    # Créer les nœuds Director et leurs relations
    print("\n🔄 Création des nœuds Director et leurs relations...")
    neo4j.create_director_nodes_and_relationships(mongo_connector)
    
    # Ajouter les membres de l'équipe
    team_members = load_team_members()
    if team_members:
        print("\n🔄 Ajout des membres de l'équipe...")
        neo4j.create_team_nodes(team_members)
    
    return neo4j

def main():
    print("🚀 Initialisation des bases de données pour le projet NoSQL...\n")
    
    # Demander à l'utilisateur s'il utilise des connexions locales ou cloud
    use_local_mongodb = input("Utiliser MongoDB local? (O/n): ").lower() != 'n'
    mongo_connection_string = None
    
    if not use_local_mongodb:
        mongo_connection_string = input("Entrez la chaîne de connexion MongoDB Atlas: ")
    
    use_local_neo4j = input("Utiliser Neo4j local? (O/n): ").lower() != 'n'
    neo4j_uri = None
    neo4j_user = None
    neo4j_password = None
    
    if not use_local_neo4j:
        neo4j_uri = input("Entrez l'URI Neo4j: ")
        neo4j_user = input("Entrez le nom d'utilisateur Neo4j: ")
        neo4j_password = input("Entrez le mot de passe Neo4j: ")
    
    # Initialiser MongoDB
    mongo_connector = initialize_mongodb(
        local=use_local_mongodb,
        connection_string=mongo_connection_string
    )
    
    # Initialiser Neo4j
    if mongo_connector and mongo_connector.client:
        neo4j_connector = initialize_neo4j(
            mongo_connector,
            local=use_local_neo4j,
            uri=neo4j_uri,
            user=neo4j_user,
            password=neo4j_password
        )
    else:
        print("\n⚠️ Impossible d'initialiser Neo4j sans une connexion MongoDB fonctionnelle.")
    
    print("\n🎉 Initialisation terminée !")
    print("   Vous pouvez maintenant lancer l'application avec : streamlit run app.py")

if __name__ == "__main__":
    main()
