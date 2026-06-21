# board_view.py
# Dessin du plateau de jeu et des allumettes.

from settings import COULEUR_ALLUMETTE, COULEUR_TETE_ALLUMETTE, COULEUR_TEXTE


def dessiner_allumette(canvas, x, y):
    """Dessine une allumette realiste centree en (x, y)."""
    canvas.create_oval(
        x - 8, y + 2, x + 8, y + 6,
        fill="#0b3d1f", outline="",
    )

    canvas.create_rectangle(
        x - 4, y - 42, x + 4, y,
        fill=COULEUR_ALLUMETTE, outline="#b40909", width=1,
    )

    canvas.create_line(
        x - 2, y - 39, x - 2, y - 4,
        fill="#fde68a", width=1,
    )

    canvas.create_oval(
        x - 7, y - 51, x + 7, y - 38,
        fill=COULEUR_TETE_ALLUMETTE, outline="#7f751d", width=1,
    )

    canvas.create_oval(
        x - 4, y - 49, x - 1, y - 46,
        fill="#fca5a5", outline="",
    )


def dessiner_plateau(canvas, piles):
    """Dessine les piles d'allumettes sur le Canvas."""
    canvas.delete("all")
    largeur = int(canvas["width"])
    hauteur = int(canvas["height"])

    if not piles:
        canvas.create_text(
            largeur // 2, hauteur // 2,
            text="Clique sur 'Nouvelle partie' pour commencer",
            fill=COULEUR_TEXTE, font=("Segoe UI", 13, "bold"),
        )
        return

    nb_piles = len(piles)
    espace_colonne = largeur // (nb_piles + 1)

    for index in range(nb_piles):
        x = espace_colonne * (index + 1)

        canvas.create_text(
            x, 22, text="Pile " + str(index + 1),
            fill=COULEUR_TEXTE, font=("Segoe UI", 11, "bold"),
        )

        y_base = hauteur - 40
        for niveau in range(piles[index]):
            decalage = (niveau % 3 - 1) * 6
            y = y_base - niveau * 19
            dessiner_allumette(canvas, x + decalage, y)

        canvas.create_text(
            x, hauteur - 12, text=str(piles[index]),
            fill=COULEUR_TEXTE, font=("Segoe UI", 12, "bold"),
        )