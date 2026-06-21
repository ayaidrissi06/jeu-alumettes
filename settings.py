# settings.py
# Ce fichier regroupe tous les reglages du jeu : config par defaut,
# parametres de connexion a la base de donnees, et couleurs de l'interface.
# Le but est de pouvoir tout modifier ici sans toucher au reste du code.

import os

# Configuration de depart des piles (jeu de Nim classique : 3, 5, 7 objets)
PILES_PAR_DEFAUT = [3, 5, 7]

# Niveaux de difficulte proposes pour l'IA
NIVEAUX_IA = [1, 2, 3, 4]

# Parametres de connexion a la base de donnees MySQL.
# os.getenv permet de definir ces valeurs autrement (variables d'environnement)
# sans avoir a modifier le code, par exemple sur un autre ordinateur.
DB_CONFIG = {
    "host": os.getenv("NIM_DB_HOST", "localhost"),
    "user": os.getenv("NIM_DB_USER", "root"),
    "password": os.getenv("NIM_DB_PASSWORD", ""),
    "database": os.getenv("NIM_DB_NAME", "jeupython"),
}

# Couleurs de l'interface. Le plateau reste vert et les allumettes
# gardent leur palette d'origine, le reste de l'UI change.
COULEUR_FOND = "#000000"
COULEUR_PANNEAU = "#262626"
COULEUR_PLATEAU = "#14532d"
COULEUR_ALLUMETTE = "#fbbf24"
COULEUR_TETE_ALLUMETTE = "#dc2626"
COULEUR_TEXTE = "#f8fafc"
COULEUR_TEXTE_SECONDAIRE = "#cbd5e1"
COULEUR_ACCENT = "#38bdf8"