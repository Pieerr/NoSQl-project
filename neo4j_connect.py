from py2neo import Graph, Node, Relationship
import pandas as pd

class Neo4jConnector:
    def __init__(self, uri=None, user=None, password=None, local=True):
        """
        Initialise la connexion à Neo4j
        
        Args:
            uri (str): URI de connexion Neo4j (obligatoire si local=False)
            user (str): Nom d'utilisateur Neo4j (obligatoire si local=False)
            password (str): Mot de passe Neo4j (obligatoire si local=False)
            local (bool): Si True, utilise les paramètres de connexion par défaut pour Neo4j local
        """
        try:
            if local:
                # Paramètres par défaut pour Neo4j local
                    self.graph = Graph("bolt://localhost:7687", auth=("neo4j", "Neo4j123"))
            else:
                if not uri or not user or not password:
                    raise ValueError("uri, user et password doivent être fournis pour une connexion Neo4j cloud")
                self.graph = Graph(uri, auth=(user, password))
            
            # Test de connexion
            self.graph.run("MATCH (n) RETURN count(n) LIMIT 1")
            print("✅ Connexion à Neo4j réussie!")
            
        except Exception as e:
            print(f"❌ Erreur de connexion à Neo4j: {e}")
            self.graph = None
    
    def create_constraints_and_indexes(self):
        """Crée les contraintes et index nécessaires pour le projet"""
        if not self.graph:
            return
        
        try:
            # Créer des contraintes d'unicité pour les identifiants
            self.graph.run("CREATE CONSTRAINT film_id IF NOT EXISTS FOR (f:Film) REQUIRE f.id IS UNIQUE")
            self.graph.run("CREATE CONSTRAINT actor_name IF NOT EXISTS FOR (a:Actor) REQUIRE a.name IS UNIQUE")
            self.graph.run("CREATE CONSTRAINT director_name IF NOT EXISTS FOR (d:Director) REQUIRE d.name IS UNIQUE")
            print("✅ Contraintes et index créés avec succès")
            
        except Exception as e:
            print(f"❌ Erreur lors de la création des contraintes: {e}")
    
    def create_film_nodes(self, mongo_connector):
        """
        Crée des nœuds Film à partir des données MongoDB
        
        Args:
            mongo_connector: Instance de MongoDBConnector
        """
        if not self.graph or not mongo_connector.client:
            return
        
        try:
            # Récupérer les films depuis MongoDB
            movies = list(mongo_connector.films.find({}, {
                "_id": 1, 
                "title": 1, 
                "year": 1, 
                "Votes": 1, 
                "Revenue (Millions)": 1, 
                "rating": 1, 
                "Director": 1
            }))
            
            # Créer un batch de requêtes Cypher
            batch_size = 100
            count = 0
            
            for i in range(0, len(movies), batch_size):
                batch = movies[i:i+batch_size]
                query = """
                UNWIND $movies AS movie
                MERGE (f:Film {id: movie._id})
                SET f.title = movie.title,
                    f.year = movie.year,
                    f.votes = movie.Votes,
                    f.revenue = movie.`Revenue (Millions)`,
                    f.rating = movie.rating
                """
                self.graph.run(query, movies=batch)
                count += len(batch)
                print(f"✅ {count}/{len(movies)} nœuds Film créés")
            
            print("✅ Création des nœuds Film terminée")
            
        except Exception as e:
            print(f"❌ Erreur lors de la création des nœuds Film: {e}")
    
    def create_actor_nodes_and_relationships(self, mongo_connector):
        """
        Crée des nœuds Actor et les relations 'A_JOUE_DANS' avec les films
        
        Args:
            mongo_connector: Instance de MongoDBConnector
        """
        if not self.graph or not mongo_connector.client:
            return
            
        try:
            # Récupérer les films et leurs acteurs depuis MongoDB
            movies = list(mongo_connector.films.find({}, {
                "_id": 1, 
                "Actors": 1
            }))
            
            # Traiter chaque film
            for movie in movies:
                if "Actors" in movie and movie["Actors"]:
                    # Diviser la chaîne d'acteurs
                    actors = [actor.strip() for actor in movie["Actors"].split(",")]
                    
                    # Créer des nœuds Actor et des relations avec le film
                    for actor in actors:
                        query = """
                        MATCH (f:Film {id: $film_id})
                        MERGE (a:Actor {name: $actor_name})
                        MERGE (a)-[:A_JOUE_DANS]->(f)
                        """
                        self.graph.run(query, film_id=movie["_id"], actor_name=actor)
            
            print("✅ Création des nœuds Actor et des relations terminée")
            
        except Exception as e:
            print(f"❌ Erreur lors de la création des nœuds Actor: {e}")
    
    def create_director_nodes_and_relationships(self, mongo_connector):
        """
        Crée des nœuds Director et les relations 'A_REALISE' avec les films
        
        Args:
            mongo_connector: Instance de MongoDBConnector
        """
        if not self.graph or not mongo_connector.client:
            return
            
        try:
            # Récupérer les films et leurs réalisateurs depuis MongoDB
            movies = list(mongo_connector.films.find({}, {
                "_id": 1, 
                "Director": 1
            }))
            
            # Traiter chaque film
            for movie in movies:
                if "Director" in movie and movie["Director"]:
                    query = """
                    MATCH (f:Film {id: $film_id})
                    MERGE (d:Director {name: $director_name})
                    MERGE (d)-[:A_REALISE]->(f)
                    """
                    self.graph.run(query, film_id=movie["_id"], director_name=movie["Director"])
            
            print("✅ Création des nœuds Director et des relations terminée")
            
        except Exception as e:
            print(f"❌ Erreur lors de la création des nœuds Director: {e}")
    
    def create_team_nodes(self, team_members):
        """
        Crée des nœuds Actor pour les membres de l'équipe du projet
        
        Args:
            team_members (list): Liste des noms des membres de l'équipe
        """
        if not self.graph:
            return
            
        try:
            # Sélectionner un film au hasard
            film_result = self.graph.run("MATCH (f:Film) RETURN f.id AS id ORDER BY rand() LIMIT 1").data()
            
            if film_result:
                film_id = film_result[0]["id"]
                
                # Créer des nœuds Actor pour chaque membre et les relier au film
                for member in team_members:
                    query = """
                    MATCH (f:Film {id: $film_id})
                    MERGE (a:Actor {name: $member_name, is_team_member: true})
                    MERGE (a)-[:A_JOUE_DANS]->(f)
                    """
                    self.graph.run(query, film_id=film_id, member_name=member)
                
                print(f"✅ Nœuds d'équipe créés et liés au film avec ID {film_id}")
            else:
                print("❌ Aucun film trouvé dans la base de données")
            
        except Exception as e:
            print(f"❌ Erreur lors de la création des nœuds d'équipe: {e}")
    
    # Méthodes pour les requêtes Cypher (à implémenter)

# Test d'utilisation
if __name__ == "__main__":
    # Exemple de connexion locale
    neo4j = Neo4jConnector(local=True)
    
    if neo4j.graph:
        neo4j.create_constraints_and_indexes()
        
        # Pour l'importation des données depuis MongoDB, vous devrez
        # instancier MongoDBConnector depuis le module mongodb_connect
        
        # Exemple d'ajout des membres de l'équipe
        team_members = ["Votre Nom", "Membre 1", "Membre 2"]
        neo4j.create_team_nodes(team_members)