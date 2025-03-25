import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.stats import pearsonr
from pymongo import MongoClient
import json

class MongoDBQueries:
    def __init__(self, mongo_connector):
        """
        Initialise la classe avec un connecteur MongoDB
        
        Args:
            mongo_connector: Instance de MongoDBConnector
        """
        self.mongo = mongo_connector
        self.films = self.mongo.films if self.mongo and self.mongo.client else None
    
    def query_1_year_with_most_films(self):
        """
        1. Affiche l'année où le plus grand nombre de films ont été sortis
        
        Returns:
            tuple: (année, nombre de films)
        """
        if self.films is None:
            return None, None
            
        pipeline = [
            {"$group": {"_id": "$year", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}},
            {"$limit": 1}
        ]
        
        result = list(self.films.aggregate(pipeline))
        if result:
            year = result[0]['_id']
            count = result[0]['count']
            return year, count
        else:
            return None, None
    
    def query_2_films_after_1999(self):
        """
        2. Compte le nombre de films sortis après l'année 1999
        
        Returns:
            int: Nombre de films après 1999
        """
        if self.films is None:
            return 0
            
        count = self.films.count_documents({"year": {"$gt": 1999}})
        return count
    
    def query_3_average_votes_2007(self):
        """
        3. Calcule la moyenne des votes des films sortis en 2007
        
        Returns:
            float: Moyenne des votes
        """
        if self.films is None:
            return 0
            
        pipeline = [
            {"$match": {"year": 2007}},
            {"$group": {"_id": None, "avg_votes": {"$avg": "$Votes"}}}
        ]
        
        result = list(self.films.aggregate(pipeline))
        if result:
            avg_votes = result[0]['avg_votes']
            return avg_votes
        else:
            return 0
    
    def query_4_films_per_year_histogram(self):
        """
        4. Crée un histogramme du nombre de films par année
        
        Returns:
            matplotlib.figure.Figure: L'histogramme généré
        """
        if self.films is None:
            return None
            
        # Récupérer les années de tous les films
        years = list(self.films.find({}, {"year": 1, "_id": 0}))
        years_df = pd.DataFrame(years)
        
        if years_df.empty:
            return None
            
        # Créer l'histogramme
        fig, ax = plt.subplots(figsize=(12, 6))
        years_df['year'].value_counts().sort_index().plot(kind='bar', ax=ax)
        
        ax.set_title('Nombre de films par année')
        ax.set_xlabel('Année')
        ax.set_ylabel('Nombre de films')
        ax.grid(axis='y', linestyle='--', alpha=0.7)
        
        plt.tight_layout()
        return fig
    
    def query_5_available_genres(self):
        """
        5. Liste les genres de films disponibles dans la base
        
        Returns:
            list: Liste des genres uniques
        """
        if self.films is None:
            return []
            
        # Récupérer tous les genres (qui sont stockés sous forme de chaîne séparée par des virgules)
        genres_docs = list(self.films.find({}, {"genre": 1, "_id": 0}))
        
        # Extraire et aplatir la liste des genres
        all_genres = []
        for doc in genres_docs:
            if 'genre' in doc and doc['genre']:
                genres = [genre.strip() for genre in doc['genre'].split(',')]
                all_genres.extend(genres)
        
        # Retourner les genres uniques triés
        unique_genres = sorted(list(set(all_genres)))
        return unique_genres
    
    def query_6_highest_revenue_film(self):
        """
        6. Trouve le film qui a généré le plus de revenu
        
        Returns:
            dict: Document du film avec le revenu le plus élevé
        """
        if self.films is None:
            return None
            
        # Convertir le champ Revenue en nombre et trouver le maximum
        pipeline = [
            {"$match": {"Revenue (Millions)": {"$ne": "", "$exists": True}}},
            {"$sort": {"Revenue (Millions)": -1}},
            {"$limit": 1}
        ]
        
        result = list(self.films.aggregate(pipeline))
        if result:
            return result[0]
        else:
            return None
    
    def query_7_directors_with_more_than_5_films(self):
        """
        7. Liste les réalisateurs ayant réalisé plus de 5 films
        
        Returns:
            list: Liste des réalisateurs avec le nombre de films
        """
        if self.films is None:
            return []
            
        pipeline = [
            {"$group": {"_id": "$Director", "count": {"$sum": 1}}},
            {"$match": {"count": {"$gt": 5}}},
            {"$sort": {"count": -1}}
        ]
        
        result = list(self.films.aggregate(pipeline))
        return result
    
    def query_8_highest_average_revenue_genre(self):
        """
        8. Détermine le genre de film qui rapporte en moyenne le plus de revenus
        
        Returns:
            tuple: (genre, revenu moyen)
        """
        if self.films is None:
            return None, 0
            
        # Récupérer tous les films avec leur genre et revenu
        films_data = list(self.films.find(
            {"Revenue (Millions)": {"$ne": "", "$exists": True}}, 
            {"genre": 1, "Revenue (Millions)": 1, "_id": 0}
        ))
        
        if not films_data:
            return None, 0
        
        # Créer un DataFrame pour l'analyse
        df = pd.DataFrame(films_data)
        
        # Exploser les genres (transformer une ligne avec plusieurs genres en plusieurs lignes)
        df['genre'] = df['genre'].str.split(',')
        df = df.explode('genre')
        df['genre'] = df['genre'].str.strip()
        
        # Calculer le revenu moyen par genre
        avg_revenue_by_genre = df.groupby('genre')['Revenue (Millions)'].mean().reset_index()
        
        # Trouver le genre avec le revenu moyen le plus élevé
        if not avg_revenue_by_genre.empty:
            top_genre = avg_revenue_by_genre.sort_values('Revenue (Millions)', ascending=False).iloc[0]
            return top_genre['genre'], top_genre['Revenue (Millions)']
        
        return None, 0
    
    def query_9_top_3_films_by_decade(self):
        """
        9. Trouve les 3 films les mieux notés pour chaque décennie
        
        Returns:
            dict: Dictionnaire avec décennies comme clés et listes de films comme valeurs
        """
        if self.films is None:
            return {}
            
        # Récupérer tous les films avec année et note
        films_data = list(self.films.find(
            {"Metascore": {"$ne": "", "$exists": True}}, 
            {"title": 1, "year": 1, "Metascore": 1, "_id": 0}
        ))
        
        if not films_data:
            return {}
        
        # Créer un DataFrame pour l'analyse
        df = pd.DataFrame(films_data)
        
        # Convertir Metascore en numérique
        df['Metascore'] = pd.to_numeric(df['Metascore'], errors='coerce')
        
        # Créer une colonne pour la décennie
        df['decade'] = (df['year'] // 10) * 10
        
        # Trouver les 3 meilleurs films par décennie
        result = {}
        for decade, group in df.groupby('decade'):
            top_3 = group.nlargest(3, 'Metascore')[['title', 'year', 'Metascore']].to_dict('records')
            result[f"{decade}-{decade+9}"] = top_3
        
        return result
    
    def query_10_longest_film_by_genre(self):
        """
        10. Trouve le film le plus long par genre
        
        Returns:
            list: Liste des films les plus longs par genre
        """
        if self.films is None:
            return []
            
        # Récupérer tous les films avec genre et durée
        films_data = list(self.films.find(
            {"Runtime (Minutes)": {"$ne": "", "$exists": True}}, 
            {"title": 1, "genre": 1, "Runtime (Minutes)": 1, "_id": 0}
        ))
        
        if not films_data:
            return []
        
        # Créer un DataFrame pour l'analyse
        df = pd.DataFrame(films_data)
        
        # Exploser les genres
        df['genre'] = df['genre'].str.split(',')
        df = df.explode('genre')
        df['genre'] = df['genre'].str.strip()
        
        # Trouver le film le plus long par genre
        result = []
        for genre, group in df.groupby('genre'):
            longest_film = group.nlargest(1, 'Runtime (Minutes)')[['title', 'genre', 'Runtime (Minutes)']].to_dict('records')[0]
            result.append(longest_film)
        
        return result
    
    def query_11_create_high_rated_high_revenue_view(self):
        """
        11. Crée une vue MongoDB avec les films à note > 80 et revenus > 50M
        
        Returns:
            int: Nombre de documents dans la vue
        """
        if self.films is None:
            return 0
            
        try:
            # Créer ou remplacer la vue
            view_name = "high_rated_high_revenue"
            pipeline = [
                {"$match": {
                    "Metascore": {"$gt": 80},
                    "Revenue (Millions)": {"$gt": 50}
                }}
            ]
            
            self.mongo.db.command({
                "create": view_name,
                "viewOn": "films",
                "pipeline": pipeline
            })
            
            # Compter les documents dans la vue
            count = self.mongo.db[view_name].count_documents({})
            return count
            
        except Exception as e:
            print(f"Erreur lors de la création de la vue: {e}")
            return 0
    
    def query_12_runtime_revenue_correlation(self):
        """
        12. Calcule la corrélation entre durée et revenus des films
        
        Returns:
            tuple: (coefficient de corrélation, p-value, DataFrame pour visualisation)
        """
        if self.films is None:
            return 0, 0, None
            
        # Récupérer les films avec durée et revenus
        films_data = list(self.films.find(
            {
                "Runtime (Minutes)": {"$ne": "", "$exists": True},
                "Revenue (Millions)": {"$ne": "", "$exists": True}
            }, 
            {"title": 1, "Runtime (Minutes)": 1, "Revenue (Millions)": 1, "_id": 0}
        ))
        
        if not films_data:
            return 0, 0, None
        
        # Créer un DataFrame
        df = pd.DataFrame(films_data)
        
        # Convertir en numérique
        df['Runtime (Minutes)'] = pd.to_numeric(df['Runtime (Minutes)'], errors='coerce')
        df['Revenue (Millions)'] = pd.to_numeric(df['Revenue (Millions)'], errors='coerce')
        
        # Supprimer les valeurs manquantes
        df = df.dropna()
        
        if len(df) < 2:
            return 0, 0, None
        
        # Calculer la corrélation
        corr, p_value = pearsonr(df['Runtime (Minutes)'], df['Revenue (Millions)'])
        
        return corr, p_value, df
    
    def query_13_average_runtime_by_decade(self):
        """
        13. Analyse l'évolution de la durée moyenne des films par décennie
        
        Returns:
            tuple: (DataFrame des durées moyennes, Figure matplotlib)
        """
        if self.films is None:
            return None, None
            
        # Récupérer les films avec année et durée
        films_data = list(self.films.find(
            {"Runtime (Minutes)": {"$ne": "", "$exists": True}}, 
            {"year": 1, "Runtime (Minutes)": 1, "_id": 0}
        ))
        
        if not films_data:
            return None, None
        
        # Créer un DataFrame
        df = pd.DataFrame(films_data)
        
        # Convertir en numérique
        df['Runtime (Minutes)'] = pd.to_numeric(df['Runtime (Minutes)'], errors='coerce')
        
        # Créer une colonne pour la décennie
        df['decade'] = (df['year'] // 10) * 10
        
        # Calculer la durée moyenne par décennie
        avg_runtime_by_decade = df.groupby('decade')['Runtime (Minutes)'].mean().reset_index()
        avg_runtime_by_decade = avg_runtime_by_decade.sort_values('decade')
        
        # Créer un graphique
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.plot(avg_runtime_by_decade['decade'], avg_runtime_by_decade['Runtime (Minutes)'], 
                marker='o', linestyle='-', linewidth=2)
        
        ax.set_title('Durée moyenne des films par décennie')
        ax.set_xlabel('Décennie')
        ax.set_ylabel('Durée moyenne (minutes)')
        ax.grid(linestyle='--', alpha=0.7)
        
        # Ajouter les valeurs sur les points
        for i, row in avg_runtime_by_decade.iterrows():
            ax.annotate(f"{row['Runtime (Minutes)']:.1f}", 
                       (row['decade'], row['Runtime (Minutes)']),
                       textcoords="offset points", 
                       xytext=(0,10), 
                       ha='center')
        
        plt.tight_layout()
        
        return avg_runtime_by_decade, fig
    
    # Questions transversales
    def query_27_films_with_common_genres_different_directors(self):
        """
        27. Films qui ont des genres en commun mais des réalisateurs différents
        
        Returns:
            list: Liste de tuples (film1, film2, genres_communs)
        """
        if self.films is None:
            return []
            
        # Récupérer tous les films avec leur genre et réalisateur
        films_data = list(self.films.find({}, {"title": 1, "genre": 1, "Director": 1, "_id": 0}))
        
        if not films_data:
            return []
        
        # Préparer les données
        result = []
        for i, film1 in enumerate(films_data):
            for film2 in films_data[i+1:]:
                # Vérifier si les réalisateurs sont différents
                if film1.get('Director') != film2.get('Director'):
                    # Trouver les genres communs
                    genres1 = set([g.strip() for g in film1.get('genre', '').split(',')])
                    genres2 = set([g.strip() for g in film2.get('genre', '').split(',')])
                    common_genres = genres1.intersection(genres2)
                    
                    if common_genres:
                        result.append((
                            film1.get('title'),
                            film2.get('title'),
                            list(common_genres)
                        ))
        
        # Limiter les résultats pour ne pas surcharger
        return result[:100]

# Test du module
if __name__ == "__main__":
    from mongodb_connect import MongoDBConnector
    
    # Se connecter à MongoDB
    mongo = MongoDBConnector(local=True)
    
    if mongo.client:
        # Créer une instance de MongoDBQueries
        queries = MongoDBQueries(mongo)
        
        # Tester quelques requêtes
        print("\nRequête 1: Année avec le plus de films")
        year, count = queries.query_1_year_with_most_films()
        print(f"Année: {year}, Nombre de films: {count}")
        
        print("\nRequête 2: Nombre de films après 1999")
        count = queries.query_2_films_after_1999()
        print(f"Nombre de films: {count}")
        
        print("\nRequête 6: Film avec le plus de revenus")
        top_film = queries.query_6_highest_revenue_film()
        if top_film:
            print(f"Titre: {top_film.get('title')}, Revenus: {top_film.get('Revenue (Millions)')} millions")