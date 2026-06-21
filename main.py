# main.py
# Point d'entree de l'application : interface graphique Tkinter et logique
# du jeu de Nim (deroulement d'une partie, tour par tour).

import time
import tkinter as tk
from tkinter import messagebox, ttk

from audio import jouer_son
from board_view import dessiner_plateau
from database import initialiser_bdd, enregistrer_partie
from enemy import ia_jouer
from stats_view import ouvrir_statistiques
from player import (
    creer_joueur,
    lister_joueurs,
)

from settings import (
    PILES_PAR_DEFAUT,
    NIVEAUX_IA,
    COULEUR_FOND,
    COULEUR_PANNEAU,
    COULEUR_PLATEAU,
    COULEUR_TEXTE,
    COULEUR_TEXTE_SECONDAIRE,
    COULEUR_ACCENT,
)


# --------------------------------------------------------------------------
# Etat global de la partie en cours
# (variables simples, pas de programmation orientee objet)
# --------------------------------------------------------------------------

piles = []                 # liste des piles, ex : [3, 5, 7]
piles_depart = []          # copie des piles au debut de la partie (pour la BDD)
joueurs_partie = []        # [nom_joueur_humain, nom_adversaire]
index_tour = 0             # 0 ou 1 : a qui le tour ?
partie_active = False
heure_debut = 0.0


# --------------------------------------------------------------------------
# Fonctions utilitaires sur l'etat de la partie
# --------------------------------------------------------------------------

def mode_ia():
    """Renvoie True si la partie en cours est en mode Joueur contre IA."""
    return var_mode.get() == "JcIA"


def mode_jcj():
    """Renvoie True si la partie en cours est en mode Joueur contre Joueur."""
    return var_mode.get() == "JcJ"


def actualiser_controles_mode(*_):
    """Active ou desactive les controles selon le mode de jeu choisi."""
    if "combo_difficulte" not in globals():
        return

    if mode_jcj():
        combo_difficulte.configure(state="disabled")
        if "entry_adversaire" in globals():
            entry_adversaire.configure(state="normal")
    else:
        combo_difficulte.configure(state="readonly")
        if "entry_adversaire" in globals():
            entry_adversaire.configure(state="disabled")
            if var_adversaire.get().strip() == "" or var_adversaire.get().strip() == "Joueur 2":
                var_adversaire.set("IA")


def joueur_courant():
    """Renvoie le nom du joueur dont c'est le tour."""
    if not joueurs_partie:
        return ""
    return joueurs_partie[index_tour % 2]


def lire_configuration_piles():
    """Lit le champ de configuration des piles et renvoie une liste d'entiers.

    Leve une ValueError si le texte saisi n'est pas valide.
    """
    texte = var_config.get().strip()
    if texte == "":
        return list(PILES_PAR_DEFAUT)

    valeurs = []
    for morceau in texte.split(","):
        morceau = morceau.strip()
        if morceau == "":
            continue
        valeur = int(morceau)   # leve ValueError si ce n'est pas un nombre
        if valeur <= 0:
            raise ValueError("Les piles doivent contenir au moins un objet.")
        valeurs.append(valeur)

    if len(valeurs) == 0:
        raise ValueError("Il faut au moins une pile.")
    return valeurs


# --------------------------------------------------------------------------
# Gestion des joueurs (partie gauche de l'interface)
# --------------------------------------------------------------------------

def rafraichir_liste_joueurs():
    """Met a jour les menus deroulants avec la liste actuelle des joueurs."""
    noms = lister_joueurs()
    combo_joueur["values"] = noms
    combo_stats["values"] = noms


def action_creer_profil():
    """Appelee par le bouton 'Creer'. Cree un nouveau profil joueur."""
    nom = var_nouveau_joueur.get().strip()
    if nom == "":
        messagebox.showwarning("Profil joueur", "Saisis un nom de joueur.")
        return

    if creer_joueur(nom):
        var_nouveau_joueur.set("")
        rafraichir_liste_joueurs()
        var_joueur.set(nom)
        messagebox.showinfo("Profil joueur", "Le joueur '" + nom + "' a ete cree.")
    else:
        messagebox.showerror("Profil joueur", "Impossible de creer le joueur (verifie la base de donnees).")


def action_ouvrir_tableau_de_bord():
    """Ouvre le tableau de bord pour le joueur selectionne."""
    nom = var_joueur_stats.get().strip()
    if nom == "":
        messagebox.showwarning("Statistiques", "Selectionne un joueur.")
        return

    ouvrir_statistiques(fenetre, nom)


def maj_statut(message=None):
    """Met a jour la barre de statut en bas de l'ecran."""
    if message is not None:
        var_statut.set(message)
        return

    if not partie_active:
        var_statut.set("Aucune partie en cours.")
        return

    var_statut.set(
        "Mode " + var_mode.get() +
        "  |  Tour de " + joueur_courant() +
        "  |  Objets restants : " + str(sum(piles))
    )


# --------------------------------------------------------------------------
# Deroulement de la partie
# --------------------------------------------------------------------------

def nouvelle_partie():
    """Demarre une nouvelle partie avec la configuration choisie."""
    global piles, piles_depart, joueurs_partie, index_tour, partie_active, heure_debut

    try:
        configuration = lire_configuration_piles()
    except ValueError:
        messagebox.showerror(
            "Configuration invalide",
            "La configuration des piles doit etre une suite de nombres "
            "entiers positifs separes par des virgules (ex : 3,5,7).",
        )
        return

    nom_joueur = var_joueur.get().strip() or "Joueur 1"
    if mode_ia():
        nom_adversaire = "IA"
    else:
        nom_adversaire = var_adversaire.get().strip() or "Joueur 2"

    if not mode_ia() and nom_joueur == nom_adversaire:
        messagebox.showerror(
            "Configuration invalide",
            "En mode JcJ, les deux joueurs doivent avoir des noms differents.",
        )
        return

    # On enregistre les profils en base s'ils n'existent pas encore
    creer_joueur(nom_joueur)
    if not mode_ia():
        creer_joueur(nom_adversaire)
    rafraichir_liste_joueurs()

    piles = configuration[:]
    piles_depart = configuration[:]
    joueurs_partie = [nom_joueur, nom_adversaire]
    index_tour = 0
    partie_active = True
    heure_debut = time.time()

    dessiner_plateau(plateau, piles)
    maj_statut()


def jouer_coup(index_pile, quantite):
    """Applique un coup (retirer 'quantite' objets de la pile 'index_pile')."""
    global index_tour

    if not partie_active:
        messagebox.showwarning("Partie", "Aucune partie n'est en cours.")
        return

    if index_pile < 0 or index_pile >= len(piles):
        jouer_son("erreur")
        messagebox.showerror("Coup invalide", "Ce numero de pile n'existe pas.")
        return

    if quantite < 1:
        jouer_son("erreur")
        messagebox.showerror("Coup invalide", "Il faut retirer au moins un objet.")
        return

    if quantite > piles[index_pile]:
        jouer_son("erreur")
        messagebox.showerror("Coup invalide", "Cette pile ne contient pas assez d'objets.")
        return

    piles[index_pile] -= quantite
    jouer_son("valide")
    dessiner_plateau(plateau, piles)

    # Condition de victoire : celui qui retire le dernier objet gagne
    if sum(piles) == 0:
        terminer_partie(joueur_courant())
        return

    index_tour += 1
    maj_statut()

    # Si c'est au tour de l'IA, on declenche son coup apres un court delai
    if mode_ia() and joueur_courant() == joueurs_partie[1]:
        fenetre.after(500, tour_ia)


def action_jouer_humain():
    """Appelee par le bouton 'Jouer'. Lit les champs et joue le coup du joueur humain."""
    if not partie_active:
        jouer_son("erreur")
        messagebox.showwarning("Partie", "Demarre d'abord une partie.")
        return

    if mode_ia() and joueur_courant() == joueurs_partie[1]:
        jouer_son("erreur")
        messagebox.showinfo("Partie", "C'est au tour de l'IA, patiente un instant.")
        return

    try:
        index_pile = int(var_pile.get()) - 1
        quantite = int(var_quantite.get())
    except ValueError:
        jouer_son("erreur")
        messagebox.showerror("Coup invalide", "Indique un numero de pile et une quantite valides.")
        return

    jouer_coup(index_pile, quantite)


def tour_ia():
    """Fait jouer l'IA selon le niveau de difficulte choisi."""
    if not partie_active or not mode_ia():
        return
    if joueur_courant() != joueurs_partie[1]:
        return

    niveau = int(var_difficulte.get())
    index_pile, quantite = ia_jouer(piles, niveau)
    jouer_coup(index_pile, quantite)


def terminer_partie(gagnant):
    """Cloture la partie : calcule la duree, enregistre le resultat en base."""
    global partie_active

    partie_active = False
    duree = int(time.time() - heure_debut) if heure_debut else 0

    nom_joueur = joueurs_partie[0]
    nom_adversaire = joueurs_partie[1]
    perdant = nom_adversaire if gagnant == nom_joueur else nom_joueur
    difficulte = var_difficulte.get() if mode_ia() else "N/A"

    enregistrer_partie(
        nom_joueur, nom_adversaire, duree, var_mode.get(), difficulte,
        piles_depart, piles[:], gagnant, perdant,
    )

    jouer_son("victoire")
    maj_statut("Partie terminee. Vainqueur : " + gagnant)
    messagebox.showinfo("Fin de partie", gagnant + " remporte la partie !")


# --------------------------------------------------------------------------
# Construction de l'interface
# --------------------------------------------------------------------------

def appliquer_theme():
    style = ttk.Style()
    try:
        style.theme_use("clam")
    except tk.TclError:
        pass
    style.configure("TCombobox", padding=4)


def construire_interface():
    global plateau, var_statut, var_mode, var_difficulte, var_config
    global var_joueur, var_adversaire, var_joueur_stats, var_nouveau_joueur
    global var_pile, var_quantite, combo_joueur, combo_stats, combo_difficulte, entry_adversaire

    appliquer_theme()

    conteneur = tk.Frame(fenetre, bg=COULEUR_FOND)
    conteneur.pack(fill="both", expand=True)

    # --- Titre ---
    tk.Label(
        conteneur, text="Jeu de Nim",
        bg=COULEUR_FOND, fg=COULEUR_TEXTE, font=("Segoe UI", 20, "bold"),
    ).pack(anchor="w", padx=18, pady=(18, 0))
    tk.Label(
        conteneur, text="Retire le dernier objet pour gagner la partie !",
        bg=COULEUR_FOND, fg=COULEUR_TEXTE_SECONDAIRE, font=("Segoe UI", 10),
    ).pack(anchor="w", padx=18, pady=(2, 10))

    corps = tk.Frame(conteneur, bg=COULEUR_FOND)
    corps.pack(fill="both", expand=True, padx=18, pady=4)

    panneau_gauche = tk.Frame(corps, bg=COULEUR_PANNEAU, padx=14, pady=14)
    panneau_gauche.pack(side="left", fill="y", padx=(0, 12))

    panneau_droit = tk.Frame(corps, bg=COULEUR_PANNEAU, padx=14, pady=14)
    panneau_droit.pack(side="left", fill="both", expand=True)

    # ----- Variables Tkinter -----
    var_nouveau_joueur = tk.StringVar()
    var_joueur = tk.StringVar()
    var_adversaire = tk.StringVar()
    var_joueur_stats = tk.StringVar()
    var_mode = tk.StringVar(value="JcIA")
    var_difficulte = tk.StringVar(value="3")
    var_config = tk.StringVar(value=",".join(str(v) for v in PILES_PAR_DEFAUT))
    var_pile = tk.StringVar(value="1")
    var_quantite = tk.StringVar(value="1")
    var_statut = tk.StringVar(value="Bienvenue ! Cree un joueur puis lance une partie.")

    # ----- Section "Joueurs" -----
    cadre_joueurs = tk.LabelFrame(panneau_gauche, text="Joueurs", bg=COULEUR_PANNEAU, fg=COULEUR_TEXTE)
    cadre_joueurs.pack(fill="x", pady=(0, 14))

    ligne1 = tk.Frame(cadre_joueurs, bg=COULEUR_PANNEAU)
    ligne1.pack(fill="x", pady=6, padx=8)
    tk.Entry(ligne1, textvariable=var_nouveau_joueur, width=16).pack(side="left", fill="x", expand=True)
    tk.Button(ligne1, text="Creer", command=action_creer_profil,
              bg=COULEUR_ACCENT, relief="flat").pack(side="left", padx=(6, 0))

    tk.Label(cadre_joueurs, text="Joueur 1 (toi)", bg=COULEUR_PANNEAU, fg=COULEUR_TEXTE_SECONDAIRE).pack(anchor="w", padx=8)
    combo_joueur = ttk.Combobox(cadre_joueurs, textvariable=var_joueur, state="readonly")
    combo_joueur.pack(fill="x", padx=8, pady=(2, 8))

    tk.Label(cadre_joueurs, text="Adversaire (si JcJ)", bg=COULEUR_PANNEAU, fg=COULEUR_TEXTE_SECONDAIRE).pack(anchor="w", padx=8)
    entry_adversaire = tk.Entry(cadre_joueurs, textvariable=var_adversaire)
    entry_adversaire.pack(fill="x", padx=8, pady=(2, 8))

    tk.Label(cadre_joueurs, text="Voir les stats de", bg=COULEUR_PANNEAU, fg=COULEUR_TEXTE_SECONDAIRE).pack(anchor="w", padx=8)
    combo_stats = ttk.Combobox(cadre_joueurs, textvariable=var_joueur_stats, state="readonly")
    combo_stats.pack(fill="x", padx=8, pady=(2, 8))

    tk.Button(cadre_joueurs, text="Tableau de bord", command=action_ouvrir_tableau_de_bord,
              bg=COULEUR_ACCENT, relief="flat").pack(fill="x", padx=8, pady=(4, 8))

    # ----- Section "Partie" -----
    cadre_partie = tk.LabelFrame(panneau_gauche, text="Nouvelle partie", bg=COULEUR_PANNEAU, fg=COULEUR_TEXTE)
    cadre_partie.pack(fill="x")

    tk.Label(cadre_partie,
              text="Mode de jeu", 
              bg=COULEUR_PANNEAU,
                fg=COULEUR_TEXTE_SECONDAIRE).pack(anchor="w", padx=8)
    
    ttk.Combobox(cadre_partie, 
                 textvariable=var_mode,
                   state="readonly",
                 values=["JcJ", "JcIA"]).pack(fill="x", padx=8, pady=(2, 8))

    tk.Label(cadre_partie, text="Difficulte de l'IA", bg=COULEUR_PANNEAU, fg=COULEUR_TEXTE_SECONDAIRE).pack(anchor="w", padx=8)
    combo_difficulte = ttk.Combobox(cadre_partie, textvariable=var_difficulte, state="readonly",
                                     values=[str(n) for n in NIVEAUX_IA])
    combo_difficulte.pack(fill="x", padx=8, pady=(2, 8))
    var_mode.trace_add("write", actualiser_controles_mode)
    actualiser_controles_mode()

    tk.Label(cadre_partie, text="Piles (separees par des virgules)", bg=COULEUR_PANNEAU, fg=COULEUR_TEXTE_SECONDAIRE).pack(anchor="w", padx=8)
    tk.Entry(cadre_partie, textvariable=var_config).pack(fill="x", padx=8, pady=(2, 8))

    tk.Button(cadre_partie, text="Nouvelle partie", command=nouvelle_partie,
              bg=COULEUR_ACCENT, relief="flat").pack(fill="x", padx=8, pady=(6, 10))

    plateau = tk.Canvas(panneau_droit, bg=COULEUR_PLATEAU, width=560, height=420, highlightthickness=0)
    plateau.pack(pady=(0, 12))

    controles = tk.Frame(panneau_droit, bg=COULEUR_PANNEAU)
    controles.pack(fill="x")

    tk.Label(controles, text="Pile", bg=COULEUR_PANNEAU, fg=COULEUR_TEXTE_SECONDAIRE).grid(row=0, column=0, padx=4)
    tk.Entry(controles, textvariable=var_pile, width=6).grid(row=1, column=0, padx=4)

    tk.Label(controles, text="Quantite", bg=COULEUR_PANNEAU, fg=COULEUR_TEXTE_SECONDAIRE).grid(row=0, column=1, padx=4)
    tk.Entry(controles, textvariable=var_quantite, width=6).grid(row=1, column=1, padx=4)

    tk.Button(controles, text="Jouer", command=action_jouer_humain,
              bg=COULEUR_ACCENT, relief="flat").grid(row=1, column=2, padx=10)

 
    tk.Label(conteneur, textvariable=var_statut, bg=COULEUR_FOND, fg=COULEUR_TEXTE_SECONDAIRE,
              font=("Segoe UI", 10, "bold")).pack(anchor="w", padx=18, pady=(8, 16))

    actualiser_controles_mode()
    dessiner_plateau(plateau, piles)



def lancer_application():
    global fenetre

    fenetre = tk.Tk()
    fenetre.title("Jeu de Nim")
    fenetre.geometry("980x680")
    fenetre.configure(bg=COULEUR_FOND)

    construire_interface()

    if not initialiser_bdd():
        messagebox.showwarning(
            "Base de donnees",
            "Impossible de se connecter a MySQL. Verifie tes identifiants "
            "dans settings.py (le jeu fonctionne quand meme, mais les "
            "parties ne seront pas sauvegardees).",
        )

    rafraichir_liste_joueurs()
    fenetre.mainloop()


if __name__ == "__main__":
    lancer_application()