import pymongo
import json
from pymongo import MongoClient
import pandas as pd
import matplotlib.pyplot as plt

class MongoDBConnector:
    def __init__(self, connection_string=None, local=True):
        """
        Initialise la connexion à MongoDB
        
        Args:
            connection_string (str): Chaîne de connexion MongoDB Atlas (si local=False)
            local (bool): Si True, se connecte à MongoDB local, sinon utilise Atlas
        """
        try:
            if local:
                self.client = MongoClient('mongodb://localhost:27017/')
            else:
                if not connection_string:
                    raise ValueError("connection_string doit être fourni pour une connexion Atlas")
                self.client = MongoClient(connection_string)
                
            # Vérifier la connexion
            self.client.admin.command('ping')
            print("✅ Connexion à MongoDB réussie!")
            
            # Créer/accéder à la base de données 'entertainment'
            self.db = self.client['entertainment']
            
            # Accéder à la collection 'films'
            self.films = self.db['films']
            
        except Exception as e:
            print(f"❌ Erreur de connexion à MongoDB: {e}")
            self.client = None
    
    def import_json_data(self, json_file):
        """
        Importe des données depuis un fichier JSON dans la collection 'films'
        
        Args:
            json_file (str): Chemin vers le fichier JSON
        """
        try:
            # Vérifier si la collection existe et est vide
            if self.films.count_documents({}) > 0:
                print("⚠️ La collection 'films' n'est pas vide. Voulez-vous remplacer les données? (o/n)")
                response = input().lower()
                if response != 'o':
                    print("❌ Importation annulée")
                    return
                # Supprimer les données existantes
                self.films.delete_many({})
            
            # Lire et importer les données
            movies = []
            with open(json_file, 'r') as file:
                for line in file:
                    line = line.strip()
                    if line and not line.startswith('{"_id":"_design'):  # Ignorer les documents de design
                        try:
                            movie_data = json.loads(line)
                            movies.append(movie_data)
                        except json.JSONDecodeError:
                            print(f"⚠️ Ligne ignorée (format JSON incorrect): {line[:50]}...")
            
            if movies:
                result = self.films.insert_many(movies)
                print(f"✅ {len(result.inserted_ids)} films importés avec succès!")
            else:
                print("❌ Aucun film à importer")
                
        except Exception as e:
            print(f"❌ Erreur lors de l'importation: {e}")
    
    def query_year_with_most_films(self):
        """Affiche l'année où le plus grand nombre de films ont été sortis."""
        pipeline = [
            {"$group": {"_id": "$year", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}},
            {"$limit": 1}
        ]
        
        result = list(self.films.aggregate(pipeline))
        if result:
            year = result[0]['_id']
            count = result[0]['count']
            print(f"L'année avec le plus de films est {year} avec {count} films.")
            return year, count
        else:
            print("Aucun résultat trouvé")
            return None, None
    
    # Autres méthodes de requêtes à implémenter...

# Test d'utilisation
if __name__ == "__main__":
    # Connexion locale
    mongo = MongoDBConnector(local=True)
    
    # Import des données
    if mongo.client:
        mongo.import_json_data('data/movies.json')
        
        # Test de requête
        mongo.query_year_with_most_films()