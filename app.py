import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import json
import os
import sys

# Après la ligne d'import de os et sys

# Affichage des informations de diagnostic
print("Chemin Python:", sys.path)
print("Dossier courant:", os.getcwd())
print("Contenu du dossier:", os.listdir())

# Ajouter le répertoire courant au chemin d'importation
sys.path.append(os.getcwd())

# Vérifier si le dossier queries existe
if os.path.exists("queries"):
    print("Contenu du dossier queries:", os.listdir("queries"))
else:
    print("Le dossier queries n'existe pas!")
    # Tenter de créer le dossier __init__.py si nécessaire
    os.makedirs("queries", exist_ok=True)
    with open(os.path.join("queries", "__init__.py"), "w") as f:
        pass  # Créer un fichier vide

# Importer les modules de connexion
from mongodb_connect import MongoDBConnector
from neo4j_connect import Neo4jConnector

# Importer les modules de requêtes
try:
    # Essayer d'importer directement
    sys.path.append("queries")
    from queries.mongodb_queries import MongoDBQueries
    from queries.neo4j_queries import Neo4jQueries
    queries_imported = True
    print("✅ Modules de requêtes importés avec succès!")
except ImportError as e:
    print(f"❌ Erreur d'importation: {e}")
    try:
        # Essayer une autre méthode d'importation
        import importlib.util
        
        # Importer mongodb_queries.py
        spec_mongo = importlib.util.spec_from_file_location(
            "mongodb_queries", 
            os.path.join(os.getcwd(), "queries", "mongodb_queries.py")
        )
        mongodb_queries = importlib.util.module_from_spec(spec_mongo)
        spec_mongo.loader.exec_module(mongodb_queries)
        
        # Importer neo4j_queries.py
        spec_neo4j = importlib.util.spec_from_file_location(
            "neo4j_queries", 
            os.path.join(os.getcwd(), "queries", "neo4j_queries.py")
        )
        neo4j_queries = importlib.util.module_from_spec(spec_neo4j)
        spec_neo4j.loader.exec_module(neo4j_queries)
        
        # Accéder aux classes
        MongoDBQueries = mongodb_queries.MongoDBQueries
        Neo4jQueries = neo4j_queries.Neo4jQueries
        
        queries_imported = True
        print("✅ Modules de requêtes importés avec la méthode alternative!")
    except Exception as e2:
        print(f"❌ Erreur d'importation alternative: {e2}")
        queries_imported = False
        st.warning("Les modules de requêtes n'ont pas été trouvés. Certaines fonctionnalités seront limitées.")

# Titre et description
st.title("🎬 Exploration et interrogation de bases de données NoSQL")
st.markdown("""
Cette application permet d'explorer et d'interroger des données de films stockées dans MongoDB et Neo4j.
""")

# Le reste de votre code app.py suit...
# Sidebar pour la navigation
st.sidebar.title("Navigation")
page = st.sidebar.radio(
    "Sélectionnez une page",
    ["Accueil", "Configuration", "MongoDB - Requêtes", "Neo4j - Requêtes", "Visualisations", "À propos"]
)

# Variables de session pour stocker les connecteurs
if 'mongo_connector' not in st.session_state:
    st.session_state.mongo_connector = None
if 'neo4j_connector' not in st.session_state:
    st.session_state.neo4j_connector = None
if 'mongo_queries' not in st.session_state:
    st.session_state.mongo_queries = None
if 'neo4j_queries' not in st.session_state:
    st.session_state.neo4j_queries = None

# Page d'accueil
if page == "Accueil":
    st.header("Bienvenue dans l'application de projet NoSQL")
    
    st.subheader("Présentation du projet")
    st.write("""
    Ce projet vise à explorer deux types de systèmes de gestion de bases de données NoSQL :
    - **MongoDB** : une base de données orientée document
    - **Neo4j** : une base de données orientée graphe
    
    L'application permet de :
    1. Se connecter aux bases de données
    2. Importer des données de films
    3. Exécuter diverses requêtes
    4. Visualiser les résultats
    """)
    
    st.subheader("Comment utiliser cette application")
    st.write("""
    1. Commencez par configurer les connexions aux bases de données dans l'onglet "Configuration".
    2. Explorez les requêtes MongoDB et Neo4j dans leurs onglets respectifs.
    3. Visualisez les données dans l'onglet "Visualisations".
    """)

# Page de configuration
elif page == "Configuration":
    st.header("Configuration des connexions aux bases de données")
    
    # Configuration MongoDB
    st.subheader("Configuration MongoDB")
    mongo_tab1, mongo_tab2 = st.tabs(["Connexion locale", "Connexion Atlas"])
    
    with mongo_tab1:
        if st.button("Connexion MongoDB locale"):
            st.session_state.mongo_connector = MongoDBConnector(local=True)
            if st.session_state.mongo_connector.client:
                st.success("Connexion à MongoDB locale établie avec succès!")
                if queries_imported:
                    st.session_state.mongo_queries = MongoDBQueries(st.session_state.mongo_connector)
            else:
                st.error("Échec de la connexion à MongoDB locale.")
    
    with mongo_tab2:
        connection_string = st.text_input("Chaîne de connexion MongoDB Atlas", type="password")
        if st.button("Connexion MongoDB Atlas"):
            st.session_state.mongo_connector = MongoDBConnector(connection_string=connection_string, local=False)
            if st.session_state.mongo_connector.client:
                st.success("Connexion à MongoDB Atlas établie avec succès!")
                if queries_imported:
                    st.session_state.mongo_queries = MongoDBQueries(st.session_state.mongo_connector)
            else:
                st.error("Échec de la connexion à MongoDB Atlas.")
    
    # Import des données MongoDB
    if st.session_state.mongo_connector and st.session_state.mongo_connector.client:
        st.subheader("Import des données dans MongoDB")
        json_file = st.text_input("Chemin du fichier JSON", "data/movies.json")
        
        # Vérifier si le fichier existe
        file_exists = os.path.isfile(json_file)
        if not file_exists:
            st.warning(f"Le fichier {json_file} n'existe pas. Veuillez vérifier le chemin.")
        
        if st.button("Importer les données", disabled=not file_exists):
            st.session_state.mongo_connector.import_json_data(json_file)
            st.success("Données importées avec succès!")
    
    # Configuration Neo4j
    st.subheader("Configuration Neo4j")
    neo4j_tab1, neo4j_tab2 = st.tabs(["Connexion locale", "Connexion cloud"])
    
    with neo4j_tab1:
        if st.button("Connexion Neo4j locale"):
            st.session_state.neo4j_connector = Neo4jConnector(local=True)
            if st.session_state.neo4j_connector.graph:
                st.success("Connexion à Neo4j locale établie avec succès!")
                if queries_imported:
                    st.session_state.neo4j_queries = Neo4jQueries(st.session_state.neo4j_connector)
            else:
                st.error("Échec de la connexion à Neo4j locale.")
    
    with neo4j_tab2:
        uri = st.text_input("URI Neo4j")
        user = st.text_input("Nom d'utilisateur Neo4j")
        password = st.text_input("Mot de passe Neo4j", type="password")
        if st.button("Connexion Neo4j cloud"):
            st.session_state.neo4j_connector = Neo4jConnector(uri=uri, user=user, password=password, local=False)
            if st.session_state.neo4j_connector.graph:
                st.success("Connexion à Neo4j cloud établie avec succès!")
                if queries_imported:
                    st.session_state.neo4j_queries = Neo4jQueries(st.session_state.neo4j_connector)
            else:
                st.error("Échec de la connexion à Neo4j cloud.")
    
    # Import des données dans Neo4j depuis MongoDB
    if (st.session_state.mongo_connector and st.session_state.mongo_connector.client and 
        st.session_state.neo4j_connector and st.session_state.neo4j_connector.graph):
        
        st.subheader("Import des données de MongoDB vers Neo4j")
        
        st.write("Créer des contraintes et des index dans Neo4j")
        if st.button("Créer des contraintes"):
            st.session_state.neo4j_connector.create_constraints_and_indexes()
            st.success("Contraintes et index créés avec succès!")
        
        st.write("Créer les nœuds Film")
        if st.button("Créer les nœuds Film"):
            st.session_state.neo4j_connector.create_film_nodes(st.session_state.mongo_connector)
            st.success("Nœuds Film créés avec succès!")
        
        st.write("Créer les nœuds Actor et leurs relations")
        if st.button("Créer les nœuds Actor"):
            st.session_state.neo4j_connector.create_actor_nodes_and_relationships(st.session_state.mongo_connector)
            st.success("Nœuds Actor et relations créés avec succès!")
        
        st.write("Créer les nœuds Director et leurs relations")
        if st.button("Créer les nœuds Director"):
            st.session_state.neo4j_connector.create_director_nodes_and_relationships(st.session_state.mongo_connector)
            st.success("Nœuds Director et relations créés avec succès!")
        
        st.write("Ajouter les membres de l'équipe du projet")
        team_members = st.text_input("Noms des membres de l'équipe (séparés par des virgules)")
        if st.button("Ajouter l'équipe"):
            members_list = [member.strip() for member in team_members.split(",") if member.strip()]
            if members_list:
                st.session_state.neo4j_connector.create_team_nodes(members_list)
                st.success("Membres de l'équipe ajoutés avec succès!")
            else:
                st.warning("Veuillez entrer au moins un nom d'équipe.")

# Page MongoDB Requêtes
elif page == "MongoDB - Requêtes":
    st.header("Requêtes MongoDB")
    
    if not st.session_state.mongo_connector or not st.session_state.mongo_connector.client:
        st.warning("Vous devez d'abord configurer la connexion à MongoDB!")
    elif not queries_imported:
        st.warning("Le module de requêtes MongoDB n'a pas été importé correctement.")
    else:
        # S'assurer que mongo_queries est instancié
        if st.session_state.mongo_queries is None:
            st.session_state.mongo_queries = MongoDBQueries(st.session_state.mongo_connector)
        
        # Liste des requêtes disponibles
        query_options = [
            "1. Année avec le plus de films",
            "2. Nombre de films après 1999",
            "3. Moyenne des votes en 2007",
            "4. Histogramme des films par année",
            "5. Genres disponibles",
            "6. Film avec le plus de revenus",
            "7. Réalisateurs avec plus de 5 films",
            "8. Genre avec le plus de revenus en moyenne",
            "9. Top 3 films par décennie",
            "10. Film le plus long par genre",
            "11. Vue des films avec notes > 80 et revenus > 50M",
            "12. Corrélation durée/revenus",
            "13. Évolution durée moyenne par décennie",
            "27. Films avec genres communs et réalisateurs différents"
        ]
        
        selected_query = st.selectbox("Sélectionnez une requête", query_options)
        
        if st.button("Exécuter la requête"):
            # Exécuter la requête sélectionnée
            query_num = int(selected_query.split('.')[0])
            
            if query_num == 1:
                year, count = st.session_state.mongo_queries.query_1_year_with_most_films()
                if year and count:
                    st.success(f"L'année avec le plus de films est {year} avec {count} films.")
                else:
                    st.warning("Aucun résultat trouvé.")
            
            elif query_num == 2:
                count = st.session_state.mongo_queries.query_2_films_after_1999()
                st.success(f"Nombre de films sortis après 1999 : {count}")
            
            elif query_num == 3:
                avg_votes = st.session_state.mongo_queries.query_3_average_votes_2007()
                st.success(f"Moyenne des votes des films de 2007 : {avg_votes:.2f}")
            
            elif query_num == 4:
                fig = st.session_state.mongo_queries.query_4_films_per_year_histogram()
                if fig:
                    st.pyplot(fig)
                else:
                    st.warning("Impossible de générer l'histogramme.")
            
            elif query_num == 5:
                genres = st.session_state.mongo_queries.query_5_available_genres()
                st.write("Genres disponibles dans la base :")
                st.write(genres)
            
            elif query_num == 6:
                film = st.session_state.mongo_queries.query_6_highest_revenue_film()
                if film:
                    st.success(f"Le film avec le plus de revenus est '{film.get('title')}' avec {film.get('Revenue (Millions)')} millions de dollars.")
                    st.json(film)
                else:
                    st.warning("Aucun film trouvé.")
            
            elif query_num == 7:
                directors = st.session_state.mongo_queries.query_7_directors_with_more_than_5_films()
                if directors:
                    st.write("Réalisateurs ayant réalisé plus de 5 films :")
                    st.table(pd.DataFrame(directors).rename(columns={"_id": "Réalisateur", "count": "Nombre de films"}))
                else:
                    st.warning("Aucun réalisateur n'a réalisé plus de 5 films.")
            
            elif query_num == 8:
                genre, avg_revenue = st.session_state.mongo_queries.query_8_highest_average_revenue_genre()
                if genre:
                    st.success(f"Le genre '{genre}' rapporte en moyenne le plus de revenus avec {avg_revenue:.2f} millions de dollars par film.")
                else:
                    st.warning("Aucun résultat trouvé.")
            
            elif query_num == 9:
                top_films = st.session_state.mongo_queries.query_9_top_3_films_by_decade()
                if top_films:
                    st.write("Top 3 films par décennie :")
                    for decade, films in top_films.items():
                        st.subheader(f"Décennie {decade}")
                        st.table(pd.DataFrame(films))
                else:
                    st.warning("Aucun résultat trouvé.")
            
            elif query_num == 10:
                longest_films = st.session_state.mongo_queries.query_10_longest_film_by_genre()
                if longest_films:
                    st.write("Film le plus long par genre :")
                    st.table(pd.DataFrame(longest_films))
                else:
                    st.warning("Aucun résultat trouvé.")
            
            elif query_num == 11:
                count = st.session_state.mongo_queries.query_11_create_high_rated_high_revenue_view()
                st.success(f"Vue créée avec {count} films ayant une note > 80 et des revenus > 50M.")
            
            elif query_num == 12:
                corr, p_value, df = st.session_state.mongo_queries.query_12_runtime_revenue_correlation()
                if df is not None:
                    st.success(f"Coefficient de corrélation entre durée et revenus : {corr:.4f} (p-value: {p_value:.4f})")
                    
                    # Créer un scatter plot
                    fig, ax = plt.subplots(figsize=(10, 6))
                    sns.scatterplot(data=df, x='Runtime (Minutes)', y='Revenue (Millions)', ax=ax)
                    ax.set_title('Corrélation entre durée et revenus des films')
                    
                    # Ajouter une ligne de tendance
                    sns.regplot(data=df, x='Runtime (Minutes)', y='Revenue (Millions)', 
                                scatter=False, ci=None, ax=ax, color='red')
                    
                    st.pyplot(fig)
                else:
                    st.warning("Données insuffisantes pour calculer la corrélation.")
            
            elif query_num == 13:
                avg_runtime_by_decade, fig = st.session_state.mongo_queries.query_13_average_runtime_by_decade()
                if avg_runtime_by_decade is not None:
                    st.write("Durée moyenne des films par décennie :")
                    st.table(avg_runtime_by_decade)
                    st.pyplot(fig)
                else:
                    st.warning("Données insuffisantes pour analyser la durée par décennie.")
            
            elif query_num == 27:
                films_with_common_genres = st.session_state.mongo_queries.query_27_films_with_common_genres_different_directors()
                if films_with_common_genres:
                    st.write("Films avec des genres communs mais des réalisateurs différents :")
                    
                    # Créer un DataFrame pour l'affichage
                    df = pd.DataFrame(films_with_common_genres, columns=['Film 1', 'Film 2', 'Genres communs'])
                    st.table(df.head(20))  # Limiter à 20 lignes pour la lisibilité
                    
                    st.info(f"Total trouvé : {len(films_with_common_genres)} paires de films (limité à 20 pour l'affichage)")
                else:
                    st.warning("Aucune paire de films trouvée.")

# Page Neo4j Requêtes
elif page == "Neo4j - Requêtes":
    st.header("Requêtes Neo4j")
    
    if not st.session_state.neo4j_connector or not st.session_state.neo4j_connector.graph:
        st.warning("Vous devez d'abord configurer la connexion à Neo4j!")
    elif not queries_imported:
        st.warning("Le module de requêtes Neo4j n'a pas été importé correctement.")
    else:
        # S'assurer que neo4j_queries est instancié
        if st.session_state.neo4j_queries is None:
            st.session_state.neo4j_queries = Neo4jQueries(st.session_state.neo4j_connector)
        
        # Liste des requêtes disponibles
        query_options = [
            "14. Acteur avec le plus de films",
            "15. Acteurs ayant joué avec Anne Hathaway",
            "16. Acteur avec le plus de revenus",
            "17. Moyenne des votes",
            "18. Genre le plus représenté",
            "19. Films des acteurs ayant joué avec vous",
            "20. Réalisateur avec le plus d'acteurs",
            "21. Films les plus connectés",
            "22. 5 acteurs avec le plus de réalisateurs",
            "23. Recommandation de film pour un acteur",
            "24. Relation d'influence entre réalisateurs",
            "25. Chemin le plus court entre deux acteurs",
            "26. Analyse des communautés d'acteurs",
            "28. Recommandation basée sur les préférences d'un acteur",
            "29. Relation de concurrence entre réalisateurs",
            "30. Analyse des collaborations réalisateur-acteur"
        ]
        
        selected_query = st.selectbox("Sélectionnez une requête", query_options)
        query_num = int(selected_query.split('.')[0])
        
        # Afficher les champs spécifiques en fonction de la requête sélectionnée
        if query_num == 19:
            team_member = st.text_input("Nom du membre de l'équipe")
        elif query_num == 23 or query_num == 28:
            actor_name = st.text_input("Nom de l'acteur")
        elif query_num == 25:
            actor1 = st.text_input("Premier acteur")
            actor2 = st.text_input("Deuxième acteur")
        
        if st.button("Exécuter la requête"):
            # Exécuter la requête sélectionnée
            if query_num == 14:
                actor, count = st.session_state.neo4j_queries.query_14_actor_with_most_films()
                if actor:
                    st.success(f"L'acteur ayant joué dans le plus grand nombre de films est '{actor}' avec {count} films.")
                else:
                    st.warning("Aucun résultat trouvé.")
            
            elif query_num == 15:
                actors = st.session_state.neo4j_queries.query_15_actors_played_with_anne_hathaway()
                if actors:
                    st.write("Acteurs ayant joué avec Anne Hathaway :")
                    
                    # Créer un DataFrame pour l'affichage
                    df = pd.DataFrame(actors)
                    st.dataframe(df)
                else:
                    st.warning("Aucun acteur n'a joué avec Anne Hathaway ou elle n'est pas dans la base.")
            
            elif query_num == 16:
                actor, revenue = st.session_state.neo4j_queries.query_16_actor_with_highest_revenue()
                if actor:
                    st.success(f"L'acteur ayant joué dans des films totalisant le plus de revenus est '{actor}' avec {revenue:.2f} millions de dollars.")
                else:
                    st.warning("Aucun résultat trouvé.")
            
            elif query_num == 17:
                avg_votes = st.session_state.neo4j_queries.query_17_average_votes()
                st.success(f"La moyenne des votes est de {avg_votes:.2f}.")
            
            elif query_num == 18:
                genre, count = st.session_state.neo4j_queries.query_18_most_represented_genre()
                if genre:
                    st.success(f"Le genre le plus représenté est '{genre}' avec {count} films.")
                else:
                    st.warning("Aucun résultat trouvé ou pas de nœuds Genre.")
            
            elif query_num == 19:
                if not team_member:
                    st.warning("Veuillez entrer le nom d'un membre de l'équipe.")
                else:
                    films = st.session_state.neo4j_queries.query_19_films_with_your_costars(team_member)
                    if films:
                        st.write(f"Films des acteurs ayant joué avec {team_member} :")
                        st.dataframe(pd.DataFrame(films))
                    else:
                        st.warning(f"Aucun film trouvé ou {team_member} n'est pas dans la base.")
            
            elif query_num == 20:
                director, count = st.session_state.neo4j_queries.query_20_director_with_most_actors()
                if director:
                    st.success(f"Le réalisateur ayant travaillé avec le plus d'acteurs est '{director}' avec {count} acteurs.")
                else:
                    st.warning("Aucun résultat trouvé.")
            
            elif query_num == 21:
                films = st.session_state.neo4j_queries.query_21_most_connected_films()
                if films:
                    st.write("Films les plus connectés (avec le plus d'acteurs en commun) :")
                    
                    # Créer un DataFrame pour l'affichage
                    df = pd.DataFrame(films)
                    st.dataframe(df)
                else:
                    st.warning("Aucun film connecté trouvé.")
            
            elif query_num == 22:
                actors = st.session_state.neo4j_queries.query_22_actors_with_most_directors()
                if actors:
                    st.write("Acteurs ayant joué avec le plus de réalisateurs différents :")
                    
                    # Créer un DataFrame pour l'affichage
                    df = pd.DataFrame(actors)
                    st.dataframe(df)
                else:
                    st.warning("Aucun résultat trouvé.")
            
            elif query_num == 23:
                if not actor_name:
                    st.warning("Veuillez entrer le nom d'un acteur.")
                else:
                    recommendations = st.session_state.neo4j_queries.query_23_recommend_film_for_actor(actor_name)
                    if recommendations:
                        st.write(f"Films recommandés pour {actor_name} :")
                        st.dataframe(pd.DataFrame(recommendations))
                    else:
                        st.warning(f"Aucune recommandation trouvée pour {actor_name}.")
            
            elif query_num == 24:
                count = st.session_state.neo4j_queries.query_24_create_influence_relationships()
                st.success(f"{count} relations d'influence créées entre réalisateurs.")
            
            elif query_num == 25:
                if not actor1 or not actor2:
                    st.warning("Veuillez entrer les noms des deux acteurs.")
                else:
                    path = st.session_state.neo4j_queries.query_25_shortest_path_between_actors(actor1, actor2)
                    if path:
                        st.write(f"Chemin le plus court entre {actor1} et {actor2} :")
                        
                        # Afficher le chemin sous forme de liste
                        path_display = []
                        for i, node in enumerate(path):
                            if node.get('type') == 'Actor':
                                path_display.append(f"👤 {node.get('name')}")
                            elif node.get('type') == 'Film':
                                path_display.append(f"🎬 {node.get('title')}")
                            
                            if i < len(path) - 1:
                                path_display.append("→")
                        
                        st.markdown(" ".join(path_display))
                    else:
                        st.warning(f"Aucun chemin trouvé entre {actor1} et {actor2}.")
            
            elif query_num == 26:
                df_communities, graph = st.session_state.neo4j_queries.query_26_actor_communities()
                if df_communities is not None:
                    st.write("Communautés d'acteurs détectées :")
                    st.dataframe(df_communities)
                    
                    # Ajouter un graphique simple pour visualiser
                    if graph:
                        st.info("Une analyse plus détaillée des communautés d'acteurs a été effectuée. Voir le rapport pour les visualisations complètes.")
                else:
                    st.warning("Impossible d'analyser les communautés d'acteurs.")
            
            elif query_num == 28:
                if not actor_name:
                    st.warning("Veuillez entrer le nom d'un acteur.")
                else:
                    recommendations = st.session_state.neo4j_queries.query_28_recommend_films_based_on_actor_preferences(actor_name)
                    if recommendations:
                        st.write(f"Films recommandés basés sur les préférences de {actor_name} :")
                        st.dataframe(pd.DataFrame(recommendations))
                    else:
                        st.warning(f"Aucune recommandation trouvée basée sur {actor_name}.")
            
            elif query_num == 29:
                count = st.session_state.neo4j_queries.query_29_create_competition_relationship()
                st.success(f"{count} relations de concurrence créées entre réalisateurs.")
            
            elif query_num == 30:
                df_collaborations, df_commercial = st.session_state.neo4j_queries.query_30_analyze_director_actor_collaborations()
                if df_collaborations is not None:
                    st.write("Collaborations fréquentes entre réalisateurs et acteurs :")
                    st.dataframe(df_collaborations)
                    
                    st.write("Analyse commerciale des collaborations :")
                    st.dataframe(df_commercial)
                else:
                    st.warning("Aucune collaboration fréquente trouvée.")

# Page Visualisations
elif page == "Visualisations":
    st.header("Visualisations")
    
    if ((not st.session_state.mongo_connector or not st.session_state.mongo_connector.client) and
        (not st.session_state.neo4j_connector or not st.session_state.neo4j_connector.graph)):
        st.warning("Vous devez d'abord configurer au moins une connexion aux bases de données!")
    elif not queries_imported:
        st.warning("Les modules de requêtes n'ont pas été importés correctement.")
    else:
        # Onglets pour les visualisations MongoDB et Neo4j
        tab1, tab2 = st.tabs(["Visualisations MongoDB", "Visualisations Neo4j"])
        
        with tab1:
            if not st.session_state.mongo_connector or not st.session_state.mongo_connector.client:
                st.warning("Vous devez d'abord configurer la connexion à MongoDB!")
            else:
                # S'assurer que mongo_queries est instancié
                if st.session_state.mongo_queries is None:
                    st.session_state.mongo_queries = MongoDBQueries(st.session_state.mongo_connector)
                
                # Options de visualisation MongoDB
                mongo_viz_options = [
                    "Histogramme des films par année",
                    "Distribution des genres",
                    "Corrélation durée/revenus",
                    "Évolution de la durée moyenne par décennie",
                    "Top réalisateurs par nombre de films"
                ]
                
                selected_mongo_viz = st.selectbox("Sélectionnez une visualisation", mongo_viz_options)
                
                if st.button("Générer la visualisation MongoDB"):
                    if selected_mongo_viz == "Histogramme des films par année":
                        fig = st.session_state.mongo_queries.query_4_films_per_year_histogram()
                        if fig:
                            st.pyplot(fig)
                    
                    elif selected_mongo_viz == "Distribution des genres":
                        # Récupérer les genres et créer un graphique
                        genres = st.session_state.mongo_queries.query_5_available_genres()
                        
                        if genres:
                            # Compter les films par genre
                            genre_counts = {}
                            
                            # Cette requête est simplifiée et pourrait être remplacée par une méthode dédiée
                            films_data = list(st.session_state.mongo_connector.films.find({}, {"genre": 1}))
                            
                            for film in films_data:
                                if "genre" in film and film["genre"]:
                                    film_genres = [g.strip() for g in film["genre"].split(",")]
                                    for g in film_genres:
                                        genre_counts[g] = genre_counts.get(g, 0) + 1
                            
                            # Créer un DataFrame et trier
                            df_genres = pd.DataFrame(list(genre_counts.items()), columns=["Genre", "Count"])
                            df_genres = df_genres.sort_values("Count", ascending=False)
                            
                            # Créer le graphique
                            fig, ax = plt.subplots(figsize=(12, 6))
                            sns.barplot(data=df_genres, x="Genre", y="Count", ax=ax)
                            ax.set_title("Nombre de films par genre")
                            ax.set_xlabel("Genre")
                            ax.set_ylabel("Nombre de films")
                            plt.xticks(rotation=45, ha='right')
                            plt.tight_layout()
                            
                            st.pyplot(fig)
                        else:
                            st.warning("Aucun genre trouvé.")
                    
                    elif selected_mongo_viz == "Corrélation durée/revenus":
                        corr, p_value, df = st.session_state.mongo_queries.query_12_runtime_revenue_correlation()
                        if df is not None:
                            st.write(f"Coefficient de corrélation : {corr:.4f} (p-value: {p_value:.4f})")
                            
                            # Créer un scatter plot
                            fig, ax = plt.subplots(figsize=(10, 6))
                            sns.scatterplot(data=df, x='Runtime (Minutes)', y='Revenue (Millions)', ax=ax)
                            ax.set_title('Corrélation entre durée et revenus des films')
                            
                            # Ajouter une ligne de tendance
                            sns.regplot(data=df, x='Runtime (Minutes)', y='Revenue (Millions)', 
                                      scatter=False, ci=None, ax=ax, color='red')
                            
                            st.pyplot(fig)
                        else:
                            st.warning("Données insuffisantes pour calculer la corrélation.")
                    
                    elif selected_mongo_viz == "Évolution de la durée moyenne par décennie":
                        avg_runtime_by_decade, fig = st.session_state.mongo_queries.query_13_average_runtime_by_decade()
                        if avg_runtime_by_decade is not None:
                            st.table(avg_runtime_by_decade)
                            st.pyplot(fig)
                        else:
                            st.warning("Données insuffisantes pour analyser la durée par décennie.")
                    
                    elif selected_mongo_viz == "Top réalisateurs par nombre de films":
                        # Récupérer les réalisateurs et le nombre de films
                        directors_data = list(st.session_state.mongo_connector.films.aggregate([
                            {"$group": {"_id": "$Director", "count": {"$sum": 1}}},
                            {"$sort": {"count": -1}},
                            {"$limit": 15}
                        ]))
                        
                        if directors_data:
                            # Créer un DataFrame
                            df_directors = pd.DataFrame(directors_data)
                            df_directors.columns = ["Director", "Films"]
                            
                            # Créer le graphique
                            fig, ax = plt.subplots(figsize=(12, 6))
                            sns.barplot(data=df_directors, x="Director", y="Films", ax=ax)
                            ax.set_title("Top 15 réalisateurs par nombre de films")
                            ax.set_xlabel("Réalisateur")
                            ax.set_ylabel("Nombre de films")
                            plt.xticks(rotation=45, ha='right')
                            plt.tight_layout()
                            
                            st.pyplot(fig)
                        else:
                            st.warning("Aucun réalisateur trouvé.")
        
        with tab2:
            if not st.session_state.neo4j_connector or not st.session_state.neo4j_connector.graph:
                st.warning("Vous devez d'abord configurer la connexion à Neo4j!")
            else:
                # S'assurer que neo4j_queries est instancié
                if st.session_state.neo4j_queries is None:
                    st.session_state.neo4j_queries = Neo4jQueries(st.session_state.neo4j_connector)
                
                st.info("Les visualisations Neo4j sont mieux rendues dans Neo4j Browser. Cette section montre des aperçus simplifiés.")
                
                # Options de visualisation Neo4j
                neo4j_viz_options = [
                    "Top acteurs par nombre de films",
                    "Statistiques des acteurs",
                    "Collaborations réalisateur-acteur"
                ]
                
                selected_neo4j_viz = st.selectbox("Sélectionnez une visualisation", neo4j_viz_options)
                
                if st.button("Générer la visualisation Neo4j"):
                    if selected_neo4j_viz == "Top acteurs par nombre de films":
                        # Exécuter une requête pour obtenir les top acteurs
                        top_actors_query = """
                        MATCH (a:Actor)-[:A_JOUE]->(f:Film)
                        WITH a.name AS actor, count(f) AS film_count
                        ORDER BY film_count DESC
                        LIMIT 15
                        RETURN actor, film_count
                        """
                        
                        try:
                            top_actors = st.session_state.neo4j_connector.graph.run(top_actors_query).data()
                            
                            if top_actors:
                                # Créer un DataFrame
                                df_top_actors = pd.DataFrame(top_actors)
                                
                                # Créer le graphique
                                fig, ax = plt.subplots(figsize=(12, 6))
                                sns.barplot(data=df_top_actors, x="actor", y="film_count", ax=ax)
                                ax.set_title("Top 15 acteurs par nombre de films")
                                ax.set_xlabel("Acteur")
                                ax.set_ylabel("Nombre de films")
                                plt.xticks(rotation=45, ha='right')
                                plt.tight_layout()
                                
                                st.pyplot(fig)
                            else:
                                st.warning("Aucun acteur trouvé.")
                        except Exception as e:
                            st.error(f"Erreur lors de l'exécution de la requête: {e}")
                    
                    elif selected_neo4j_viz == "Statistiques des acteurs":
                        # Requête pour obtenir des statistiques sur les acteurs
                        actors_stats_query = """
                        MATCH (a:Actor)-[:A_JOUE]->(f:Film)
                        WITH a, count(f) AS film_count
                        RETURN 
                            min(film_count) AS min_films,
                            max(film_count) AS max_films,
                            avg(film_count) AS avg_films,
                            count(a) AS total_actors
                        """
                        
                        try:
                            stats = st.session_state.neo4j_connector.graph.run(actors_stats_query).data()[0]
                            
                            # Afficher les statistiques
                            st.write("Statistiques des acteurs :")
                            st.write(f"Nombre total d'acteurs : {stats['total_actors']}")
                            st.write(f"Nombre minimum de films par acteur : {stats['min_films']}")
                            st.write(f"Nombre maximum de films par acteur : {stats['max_films']}")
                            st.write(f"Nombre moyen de films par acteur : {stats['avg_films']:.2f}")
                            
                            # Distribution des acteurs par nombre de films
                            distribution_query = """
                            MATCH (a:Actor)-[:A_JOUE]->(f:Film)
                            WITH a, count(f) AS film_count
                            RETURN film_count, count(a) AS actor_count
                            ORDER BY film_count
                            """
                            
                            distribution = st.session_state.neo4j_connector.graph.run(distribution_query).data()
                            
                            if distribution:
                                df_dist = pd.DataFrame(distribution)
                                
                                # Créer le graphique
                                fig, ax = plt.subplots(figsize=(12, 6))
                                sns.barplot(data=df_dist, x="film_count", y="actor_count", ax=ax)
                                ax.set_title("Distribution des acteurs par nombre de films")
                                ax.set_xlabel("Nombre de films")
                                ax.set_ylabel("Nombre d'acteurs")
                                plt.tight_layout()
                                
                                st.pyplot(fig)
                        except Exception as e:
                            st.error(f"Erreur lors de l'exécution de la requête: {e}")
                    
                    elif selected_neo4j_viz == "Collaborations réalisateur-acteur":
                        # Cette visualisation est complexe, nous utilisons un aperçu simplifié
                        df_collaborations, df_commercial = st.session_state.neo4j_queries.query_30_analyze_director_actor_collaborations(min_collaborations=3)
                        
                        if df_collaborations is not None:
                            st.write("Top collaborations entre réalisateurs et acteurs :")
                            st.dataframe(df_collaborations)
                            
                            if df_commercial is not None:
                                # Créer un graphique des revenus moyens par collaboration
                                if 'avg_revenue' in df_commercial.columns:
                                    df_plot = df_commercial.sort_values('avg_revenue', ascending=False).head(10)
                                    
                                    fig, ax = plt.subplots(figsize=(12, 6))
                                    bars = sns.barplot(data=df_plot, x='director', y='avg_revenue', ax=ax)
                                    
                                    # Ajouter les noms des acteurs
                                    for i, bar in enumerate(bars.patches):
                                        bars.text(bar.get_x() + bar.get_width()/2., 
                                                  bar.get_height() + 5,
                                                  df_plot.iloc[i]['actor'],
                                                  ha='center', va='bottom', rotation=0, size=8)
                                    
                                    ax.set_title("Top 10 collaborations réalisateur-acteur par revenus moyens")
                                    ax.set_xlabel("Réalisateur")
                                    ax.set_ylabel("Revenus moyens (millions $)")
                                    plt.xticks(rotation=45, ha='right')
                                    plt.tight_layout()
                                    
                                    st.pyplot(fig)
                        else:
                            st.warning("Aucune collaboration fréquente trouvée.")

# Page À propos
elif page == "À propos":
    st.header("À propos du projet")
    
    st.subheader("Équipe")
    st.write("Votre nom et les membres de votre équipe")
    
    st.subheader("Description du projet")
    st.write("""
    Ce projet a été réalisé dans le cadre du cours "NoSQL Databases" à ESIEA en 2024-2025.
    
    L'objectif était d'explorer deux types de bases de données NoSQL :
    - MongoDB (orientée document)
    - Neo4j (orientée graphe)
    
    et de développer une application Python capable d'interagir avec ces bases de données
    pour répondre à diverses questions.
    """)
    
    st.subheader("Fonctionnalités implémentées")
    st.write("""
    1. Connexion aux deux bases de données NoSQL
    2. Import des données de films depuis un fichier JSON
    3. Création de nœuds et relations dans Neo4j basés sur les données MongoDB
    4. Exécution de requêtes complexes pour répondre aux questions du projet
    5. Visualisation des résultats avec Matplotlib, Seaborn et Streamlit
    """)
    
    st.subheader("Technologies utilisées")
    st.write("""
    - **Python** : Langage de programmation principal
    - **MongoDB** : Base de données orientée document
    - **Neo4j** : Base de données orientée graphe
    - **Streamlit** : Framework pour l'interface utilisateur
    - **Pandas** : Manipulation de données
    - **Matplotlib et Seaborn** : Visualisation de données
    """)

# Pied de page
st.sidebar.markdown("---")
st.sidebar.markdown("© 2024-2025 - Projet NoSQL ESIEA")