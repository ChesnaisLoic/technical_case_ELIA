# Cas technique : ELIA

CHESNAIS Loïc - Candidature au poste de Data Engineer

## 1. Set up a local postgreSQL server using a Docker container

J'ai choisi d'utiliser l'outil docker compose. Cela me permet de mettre en place PostgreSQL ainsi que Adminer (outil de gestion de base de données) en une seule commande.  
J'en ai profité pour mettre en place un fichier d'environnement ".env" qui n'est pas présent sur le dépot par soucis de sécurité. Un fichier ".env.example" est présent pour indiquer les noms des variabes à définir.

Le fichier est "docker-compose.yaml", afin de démarrer les deux containers vous devez entrer la commande suivante :  

```
docker compose up -d
```

## 2. Implement a Python script that retrieves two datasets for September 2024 and stores the retrieved data in two SQL tables within a postgreSQL database  

J'ai décidé d'utiliser l'architecture "ETL" (Extract-Transform-Load), ce qui me permet de séparer la logique de mon script python en 3 modules.

- Extract
  - En parcourant les deux API, j'ai pu trouver le moyen de placer des filtres dans ma requête me permettant d'isoler les données du mois de septembre,
  - J'ai également décidé d'utiliser le TimeZone UTC car c'est un standard mondialement reconnu, cela me permet d'uniformiser les données et d'éviter les erreurs de conversion liées aux fuseaux horaires.
- Transform
  - Dans ce cas pratique, ce module peut être considéré comme optionnel. J'ai néanmoins profité de cette occasion pour explorer le jeu de données via la bibliothèque Pandas (code commenté car non nécessaire à l'exécution du programme),
  - J'ai également appliqué une conversion de type sur la colonne datetime qui n'était pas reconnue comme étant une date.
- Load
  - Dans ce module, je commence par charger le fichier csv transformé, je m'assure via SQLAlchemy que les différentes tables du projet soient bien créées (je le fais si ce n'est pas le cas) et ensuite j'insère les données dans les différentes tables,
  - Les arguments "method" et "chunksize" de la méthode "to_sql" m'ont permis d'apporter une couche d'optimisation améliorant la vitesse d'exécution des requêtes SQL d'insertion,
  - Le fait de vérifier que les tables soient bien créées peut être considéré comme une première couche d'automatisation du projet. Si l'on ajoute l'exécution de ce script dans un container couplé à la création de la base de données, on pourrait facilement déployer ce projet sans effectuer de réglages manuels.

J'ai pris la liberté d'exporter les fichiers résultants des modules "Extract" et "Transform". Ces fichiers pourront ensuite être surveillés afin de valider ou déboguer le programme.  
Dans une logique de débogage j'ai ajouté quelques logs.

Dans la création des bases de données dans le module Load, j'ai fait le choix d'ajouter un entier en clé primaire. C'est un choix discutable car le sujet implique l'utilisation d'une base de données relationnelle. On aurait pu utiliser l'extension TimescaleDB car nos données sont des séries temporelles ou encore choisir MongoDB (ou tout autre outil NoSQL).

Afin d'exécuter le programme il faut :

- s'assurer le fichier ".env" existe et que les variables soient identiques à celles de la base de données,
- utiliser la version de Python 3.11.

Ensuite il faut exécuter les commandes suivantes :

```shell
# Installation de pipenv, un gestionnaire d'environnement virtuel
pip install pipenv

# Installation des biliothèques du projet
pipenv install

# Il faudra préalablement choisir l'environnement virtuel venant d'être créé
py main.py
```

## 3. Write an SQL query that aggregates the aFRR volumes up and down from 1min to 15min granularity and stores the result in a third SQL table

Pour cette partie, nous pourrons utiliser la table "aggregated_volumes_up_down_per_quarter-hour" créée dans la deuxième question.

La requête SQL est la suivante:

```sql
INSERT INTO "aggregated_volumes_up_down_per_quarter-hour" (datetime, afrrvolumeup, afrrvolumedown)
SELECT date_trunc('hour', datetime) + INTERVAL '15 minutes' * FLOOR(EXTRACT(minute FROM datetime) / 15) as interval_15min, SUM(afrrvolumeup) as sum_afrrvolumeup, SUM(afrrvolumedown) as sum_afrrvolumedown
FROM current_system_imbalance
GROUP BY interval_15min
ORDER BY interval_15min;
```

Cette requête nous permet de regrouper par tranche de 15 minutes les sommes des valeurs aFRR+ et aFRR-.  
Le nombre de lignes créées dans la table est le même que dans celle où les valeurs sont entrées toutes les 15 minutes.

## 4. Write an SQL query that calculates, for the day 05/09/2024, the revenue in € from the aFRR up and down markets using the 15min imbalance price and the aggregated data from the previous step

La requête SQL est la suivante:

```sql
SELECT
  ROUND(SUM(afrrvolumeup * (imbalanceprice / 4)), 2) || ' €' AS revenue_up,
  ROUND(SUM(afrrvolumedown * (imbalanceprice / 4)), 2) || ' €' AS revenue_down,
  ROUND(SUM((afrrvolumeup + afrrvolumedown) * (imbalanceprice / 4)), 2) || ' €' as total_revenue
FROM "aggregated_volumes_up_down_per_quarter-hour" 
JOIN "imbalance_prices_per_quarter-hour"
  ON "aggregated_volumes_up_down_per_quarter-hour".datetime = "imbalance_prices_per_quarter-hour".datetime
WHERE "aggregated_volumes_up_down_per_quarter-hour".datetime::date = '2024-09-05';
```

Dans cette requête je divise imbalanceprice par 4 étant donné que cette colonne réprésente le prix en MWh alors que nous sommes en train de traiter des valeurs sur la base de 15 minutes (60/4 = 15).

Les trois résultats sont :

| Label  | Définition  | Valeur (en €)  |
|---|---|---|
|  revenue_up | la somme des produits entre afrrvolumeup et imbalanceprice  | 2 245 779.60 €  |
|  revenue_down | la somme des produits entre afrrvolumedown et imbalanceprice  | -1 729 880.75 €  |
|  total_revenue | la recette en € du marché aFRR  | 515 898.85 € |

Ces trois données concernent la journée du 05 septembre 2024.
