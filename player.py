# player.py
# Gere les profils joueurs : creation, liste, statistiques individuelles,
# classement general et historique des parties.

from sqlite3 import Cursor

from mysql.connector import Error

from database import connecter

# Statistiques par defaut pour un joueur qui n'existe pas encore dans la base.
STATS_PAR_DEFAUT = {
    "nom": "",
    "parties_jouees": 0,
    "victoires": 0,
    "defaites": 0,
    "nuls": 0,
    "score": 0,
}


def creer_joueur(nom):
    """Cree un nouveau profil joueur. Renvoie True si l'operation a reussi."""
    nom = nom.strip()
    if nom == "":
        return False

    connexion = connecter()
    if connexion is None:
        return False

    try:
        cursor = connexion.cursor() # crée un "curseur" : c'est l'objet qui permet d'envoyer des requêtes SQL et de récupérer leurs résultats.
        cursor.execute("INSERT IGNORE INTO joueurs (nom) VALUES (%s)", (nom,))
        connexion.commit()
        return True
    except Error as erreur:
        print("Erreur lors de la creation du joueur :", erreur)
        return False
    finally:
        cursor.close()
        connexion.close()


def lister_joueurs():
    """Renvoie la liste des noms de tous les joueurs enregistres."""
    connexion = connecter()
    if connexion is None:
        return []

    try:
        cursor = connexion.cursor()
        cursor.execute("SELECT nom FROM joueurs ORDER BY nom ASC")
        lignes = cursor.fetchall()
        return [ligne[0] for ligne in lignes]
    except Error as erreur:
        print("Erreur lors de la lecture des joueurs :", erreur)
        return []
    finally:
        cursor.close()
        connexion.close()


def obtenir_stats(nom):
    """Renvoie un dictionnaire avec les statistiques cumulees d'un joueur."""
    connexion = connecter()
    if connexion is None:
        return dict(STATS_PAR_DEFAUT, nom=nom)

    try:
        cursor = connexion.cursor(dictionary=True)
        cursor.execute("SELECT * FROM joueurs WHERE nom = %s", (nom,))
        resultat = cursor.fetchone()
        if resultat:
            return resultat
        return dict(STATS_PAR_DEFAUT, nom=nom)
    except Error as erreur:
        print("Erreur lors de la lecture des statistiques :", erreur)
        return dict(STATS_PAR_DEFAUT, nom=nom)
    finally:
        cursor.close()
        connexion.close()


def obtenir_classement(limite=10):
    """Renvoie les meilleurs joueurs, tries par score puis par victoires."""
    connexion = connecter()
    if connexion is None:
        return []

    try:
        cursor = connexion.cursor(dictionary=True)
        cursor.execute("""
            SELECT nom, score, victoires, defaites, nuls, parties_jouees
            FROM joueurs
            ORDER BY score DESC, victoires DESC
            LIMIT %s
        """, (limite,))
        return cursor.fetchall()
    except Error as erreur:
        print("Erreur lors de la lecture du classement :", erreur)
        return []
    finally:
        cursor.close()
        connexion.close()


def obtenir_historique(nom, limite=15):
    """Renvoie les dernieres parties jouees par un joueur (en tant que joueur ou adversaire)."""
    connexion = connecter()
    if connexion is None:
        return []

    try:
        cursor = connexion.cursor(dictionary=True)
        cursor.execute("""
            SELECT date_heure, mode, difficulte, gagnant, perdant, duree_secondes
            FROM parties
            WHERE joueur = %s OR adversaire = %s
            ORDER BY date_heure DESC
            LIMIT %s
        """, (nom, nom, limite))
        return cursor.fetchall()
    except Error as erreur:
        print("Erreur lors de la lecture de l'historique :", erreur)
        return []
    finally:
        cursor.close()
        connexion.close()