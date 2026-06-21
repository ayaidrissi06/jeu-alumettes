# stats_view.py
# Fenetre secondaire avec statistiques, classement et historique.

import tkinter as tk
from tkinter import ttk

from player import obtenir_stats, obtenir_classement, obtenir_historique
from settings import COULEUR_FOND, COULEUR_PANNEAU, COULEUR_TEXTE, COULEUR_TEXTE_SECONDAIRE


def ouvrir_statistiques(fenetre_parent, nom_joueur):
    """Ouvre une fenetre avec les statistiques du joueur."""
    nom = nom_joueur.strip()
    if nom == "":
        return False

    stats = obtenir_stats(nom)
    classement = obtenir_classement(10)
    historique = obtenir_historique(nom, 12)

    fenetre_stats = tk.Toplevel(fenetre_parent)
    fenetre_stats.title("Statistiques de " + nom)
    fenetre_stats.configure(bg=COULEUR_FOND)
    fenetre_stats.geometry("950x600")

    tk.Label(
        fenetre_stats, text="Statistiques de " + nom,
        bg=COULEUR_FOND, fg=COULEUR_TEXTE, font=("Segoe UI", 16, "bold"),
    ).pack(anchor="w", padx=16, pady=12)

    total = stats.get("parties_jouees", 0) or 0
    victoires = stats.get("victoires", 0) or 0
    defaites = stats.get("defaites", 0) or 0
    nuls = stats.get("nuls", 0) or 0
    score = stats.get("score", 0) or 0
    taux_victoire = round((victoires / total) * 100, 1) if total else 0

    resume = (
        "Parties jouees : " + str(total) +
        "   |   Victoires : " + str(victoires) +
        "   |   Defaites : " + str(defaites) +
        "   |   Nuls : " + str(nuls) +
        "   |   Taux de victoire : " + str(taux_victoire) + "%" +
        "   |   Score : " + str(score)
    )
    tk.Label(
        fenetre_stats, text=resume, bg=COULEUR_PANNEAU, fg=COULEUR_TEXTE,
        font=("Segoe UI", 10, "bold"), padx=10, pady=10,
    ).pack(fill="x", padx=16, pady=(0, 12))

    zone = tk.Frame(fenetre_stats, bg=COULEUR_FOND)
    zone.pack(fill="both", expand=True, padx=16, pady=(0, 16))
    zone.columnconfigure(0, weight=1)
    zone.columnconfigure(1, weight=1)

    cadre_classement = tk.LabelFrame(zone, text="Classement", bg=COULEUR_FOND, fg=COULEUR_TEXTE)
    cadre_classement.grid(row=0, column=0, sticky="nsew", padx=(0, 8))

    arbre_classement = ttk.Treeview(
        cadre_classement,
        columns=("nom", "score", "v", "d", "n", "p"),
        show="headings", height=12,
    )
    entetes = [("nom", "Nom", 110), ("score", "Score", 60), ("v", "V", 50),
               ("d", "D", 50), ("n", "N", 50), ("p", "Parties", 70)]
    for cle, titre, largeur in entetes:
        arbre_classement.heading(cle, text=titre)
        arbre_classement.column(cle, width=largeur, anchor="center")
    arbre_classement.pack(fill="both", expand=True, padx=8, pady=8)

    for ligne in classement:
        arbre_classement.insert("", "end", values=(
            ligne["nom"], ligne["score"], ligne["victoires"],
            ligne["defaites"], ligne["nuls"], ligne["parties_jouees"],
        ))

    cadre_historique = tk.LabelFrame(zone, text="Historique", bg=COULEUR_FOND, fg=COULEUR_TEXTE)
    cadre_historique.grid(row=0, column=1, sticky="nsew", padx=(8, 0))

    arbre_historique = ttk.Treeview(
        cadre_historique,
        columns=("date", "mode", "diff", "gagnant", "duree"),
        show="headings", height=12,
    )
    entetes_hist = [("date", "Date", 140), ("mode", "Mode", 60), ("diff", "Niveau", 60),
                     ("gagnant", "Gagnant", 100), ("duree", "Duree", 70)]
    for cle, titre, largeur in entetes_hist:
        arbre_historique.heading(cle, text=titre)
        arbre_historique.column(cle, width=largeur, anchor="center")
    arbre_historique.pack(fill="both", expand=True, padx=8, pady=8)

    for ligne in historique:
        arbre_historique.insert("", "end", values=(
            ligne["date_heure"], ligne["mode"], ligne["difficulte"],
            ligne["gagnant"], str(ligne["duree_secondes"]) + "s",
        ))

    return True