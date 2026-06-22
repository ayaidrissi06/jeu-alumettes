# enemy.py
# Intelligence artificielle du jeu de Nim.
# 4 niveaux de difficulte, du plus simple (hasard) au plus fort (imbattable).

import random


def coups_possibles(allumettes):
    """Renvoie la liste de tous les coups jouables : (index_allumette, quantite)."""
    coups = []
    for index in range(len(allumettes)):
        for quantite in range(1, allumettes[index] + 1):
            coups.append((index, quantite))
    return coups


def coup_aleatoire(allumettes):
    """Niveau 1 : choisit un coup totalement au hasard parmi les coups possibles."""
    allumettes_non_vides = [i for i in range(len(allumettes)) if allumettes[i] > 0]
    allumette_choisie = random.choice(allumettes_non_vides)
    quantite = random.randint(1, allumettes[allumette_choisie])
    return allumette_choisie, quantite


def coup_heuristique(allumettes):
    """Niveau 2 : regle simple, on attaque toujours la plus grande pile
    en en retirant une quantite moderee (entre 1 et la moitie)."""
    plus_grande = allumettes.index(max(allumettes))
    quantite_max = max(1, allumettes[plus_grande] // 2)
    return plus_grande, random.randint(1, quantite_max)


def position_est_gagnante(allumettes, memo):
    """
    Fonction recursive (algorithme minimax) qui dit si la position est
    gagnante pour le joueur qui doit jouer maintenant.

    Principe : une position est gagnante s'il existe AU MOINS UN coup qui
    place l'adversaire dans une position perdante. Une position ou toutes
    les allumettes sont vides est perdante (le joueur ne peut plus jouer).

    Le dictionnaire 'memo' sert a ne pas recalculer deux fois le meme etat
    (sinon le calcul serait beaucoup trop long).
    """
    etat = tuple(allumettes)

    if etat in memo:
        return memo[etat]

    if sum(etat) == 0:
        memo[etat] = False
        return False

    for index, quantite in coups_possibles(list(etat)):
        nouvelles_allumettes = list(etat)
        nouvelles_allumettes[index] -= quantite
        if not position_est_gagnante(nouvelles_allumettes, memo):
            memo[etat] = True
            return True

    memo[etat] = False
    return False


def coup_minimax(allumettes):
    """Niveau 3 : explore les coups possibles et joue celui qui laisse
    l'adversaire dans une position perdante, si un tel coup existe."""
    memo = {}
    for index, quantite in coups_possibles(allumettes):
        nouvelles_allumettes = allumettes[:]
        nouvelles_allumettes[index] -= quantite
        if not position_est_gagnante(nouvelles_allumettes, memo):
            return index, quantite

    # Aucun coup parfait trouve (position deja perdante) : on joue au hasard
    return coup_aleatoire(allumettes)


def coup_nim_sum(allumettes):
    """
    Niveau 4 : strategie mathematique optimale du jeu de Nim, basee sur
    le "nim-sum" (XOR de toutes les allumettes).

    - Si le nim-sum vaut 0, la position est perdante pour celui qui doit
      jouer : aucun coup ne sera meilleur qu'un autre, on joue au hasard.
    - Sinon, il existe toujours un coup qui ramene le nim-sum a 0. On
      cherche une pile telle que (pile XOR nim_sum) < pile, et on retire
      la difference de cette pile.
    """
    nim_sum = 0
    for valeur in allumettes:
        nim_sum = nim_sum ^ valeur

    if nim_sum == 0:
        return coup_aleatoire(allumettes)

    for index, valeur in enumerate(allumettes):
        cible = valeur ^ nim_sum
        if cible < valeur:
            return index, valeur - cible

    return coup_aleatoire(allumettes)


def ia_jouer(allumettes, niveau):
    """Point d'entree principal de l'IA : choisit un coup selon le niveau."""
    if sum(allumettes) == 0:
        return 0, 0

    if niveau == 1:
        return coup_aleatoire(allumettes)
    if niveau == 2:
        return coup_heuristique(allumettes)
    if niveau == 3:
        return coup_minimax(allumettes)

    return coup_nim_sum(allumettes)