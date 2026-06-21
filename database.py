# database.py
# Gere la connexion a la base de donnees MySQL et l'enregistrement des parties.
# Toutes les fonctions qui touchent a la base sont protegees par des
# blocs try/except pour eviter que le programme ne plante en cas de probleme.

import mysql.connector
from mysql.connector import Error

from settings import DB_CONFIG


def connecter():
    """Ouvre une connexion vers la base de donnees MySQL.

    Renvoie l'objet connexion en cas de succes, ou None en cas d'echec.
    """
    try:
        return mysql.connector.connect(**DB_CONFIG)
    except Error as erreur:
        print("Erreur de connexion a la base de donnees :", erreur)
        return None


def initialiser_bdd():
    """Cree les tables 'joueurs' et 'parties' si elles n'existent pas encore."""
    connexion = connecter()
    if connexion is None:
        return False

    try:
        curseur = connexion.cursor()

        curseur.execute("""
            CREATE TABLE IF NOT EXISTS joueurs (
                id INT AUTO_INCREMENT PRIMARY KEY,
                nom VARCHAR(100) NOT NULL UNIQUE,
                parties_jouees INT NOT NULL DEFAULT 0,
                victoires INT NOT NULL DEFAULT 0,
                defaites INT NOT NULL DEFAULT 0,
                nuls INT NOT NULL DEFAULT 0,
                score INT NOT NULL DEFAULT 0
            )
        """)

        curseur.execute("""
            CREATE TABLE IF NOT EXISTS parties (
                id INT AUTO_INCREMENT PRIMARY KEY,
                joueur VARCHAR(100) NOT NULL,
                adversaire VARCHAR(100) NOT NULL,
                date_heure TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                duree_secondes INT NOT NULL,
                mode VARCHAR(10) NOT NULL,
                difficulte VARCHAR(10) NOT NULL,
                piles_depart VARCHAR(255) NOT NULL,
                piles_fin VARCHAR(255) NOT NULL,
                gagnant VARCHAR(100) NOT NULL,
                perdant VARCHAR(100) NOT NULL
            )
        """)

        connexion.commit()
        return True

    except Error as erreur:
        print("Erreur lors de la creation des tables :", erreur)
        return False

    finally:
        curseur.close()
        connexion.close()


def ajouter_joueur_si_absent(curseur, nom):
    """Insere un joueur dans la table s'il n'y est pas deja."""
    curseur.execute(
        "INSERT IGNORE INTO joueurs (nom) VALUES (%s)",
        (nom,)
    )


def enregistrer_partie(joueur, adversaire, duree, mode, difficulte,
                        piles_depart, piles_fin, gagnant, perdant,
                        match_nul=False):
    """Enregistre une partie terminee et met a jour les statistiques cumulees."""
    connexion = connecter()
    if connexion is None:
        return False

    try:
        curseur = connexion.cursor()

        ajouter_joueur_si_absent(curseur, joueur)
        ajouter_joueur_si_absent(curseur, adversaire)

        curseur.execute("""
            INSERT INTO parties
                (joueur, adversaire, duree_secondes, mode, difficulte,
                 piles_depart, piles_fin, gagnant, perdant)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            joueur, adversaire, duree, mode, str(difficulte),
            str(piles_depart), str(piles_fin), gagnant, perdant
        ))

        if match_nul:
            # Cas rare en JcJ : aucune victoire/defaite, juste 1 point chacun
            for nom in (joueur, adversaire):
                curseur.execute("""
                    UPDATE joueurs
                    SET parties_jouees = parties_jouees + 1,
                        nuls = nuls + 1,
                        score = score + 1
                    WHERE nom = %s
                """, (nom,))
        else:
            curseur.execute("""
                UPDATE joueurs
                SET parties_jouees = parties_jouees + 1,
                    victoires = victoires + 1,
                    score = score + 3
                WHERE nom = %s
            """, (gagnant,))

            curseur.execute("""
                UPDATE joueurs
                SET parties_jouees = parties_jouees + 1,
                    defaites = defaites + 1
                WHERE nom = %s
            """, (perdant,))

        connexion.commit()
        return True

    except Error as erreur:
        print("Erreur lors de l'enregistrement de la partie :", erreur)
        return False

    finally:
        curseur.close()
        connexion.close()