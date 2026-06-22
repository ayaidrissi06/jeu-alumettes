# audio.py
# Gestion simple des effets sonores du jeu.

from pathlib import Path

try:
    import winsound
except ImportError:
    winsound = None


DOSSIER_PROJET = Path(__file__).resolve().parent

SONS = {
    "valide": Path("C:/Users/aya18/Desktop/projet python/assets/sounds/valide.wav"),
    "erreur": Path("C:/Users/aya18/Desktop/projet python/assets/sounds/erreur.wav"),
    "victoire": Path("C:/Users/aya18/Desktop/projet python/assets/sounds/victoire.wav"),
}


def jouer_son(nom):
    """Joue un effet sonore en arriere-plan si le systeme le permet."""
    if winsound is None:
        return

    chemin = SONS.get(nom)
    if chemin is None or not chemin.exists():
        return

    try:
        winsound.PlaySound(str(chemin), winsound.SND_FILENAME | winsound.SND_ASYNC)
    except Exception:
        pass