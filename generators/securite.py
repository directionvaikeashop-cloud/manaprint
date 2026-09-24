# -*- coding: utf-8 -*-
"""
MANAPRINT — Module de SÉCURITÉ ANTI-PHOTOCOPIE partagé (micro-impression)
==========================================================================
Utilisé par tous les générateurs de cartons. Deux protections :

1) cadre_micro()   : cadre intérieur de la carte en MICROTEXTE (~0,55 pt).
   À l'œil nu : un fin double trait. À la loupe x10 : le texte
   MANAPRINT*ORIGINAL* + le N° DE SÉRIE de la carte, répété.
   À la photocopie : les lettres sont détruites (trait gris flou).

2) chiffre_micro() : chiffres "billet de banque" — contour net + corps
   rempli de microtexte. De loin : un chiffre normal. À la loupe : du texte.
   À la photocopie : intérieur gris baveux, lettres détruites.

Vérification en salle : loupe de poche x10. Lettres nettes = ORIGINAL.
Optimisé gros volumes : les chiffres sont des "tampons" PDF (Form XObjects)
définis une fois par document puis réutilisés → fichiers légers, génération rapide.

IMPORTANT : chaque générateur importe ce module en mode "anti-panne" :
si ce fichier est absent, les jeux fonctionnent normalement, sans microtexte.
"""
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

# Police NORMALE (pas ExtraLight) pour le microtexte : traits plus nets à 0,5 pt
try:
    pdfmetrics.registerFont(TTFont("DJMICRO", "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"))
    POLICE_MICRO = "DJMICRO"
except Exception:
    POLICE_MICRO = "Helvetica"

GRIS_MICRO = colors.Color(0.42, 0.42, 0.42)      # cadre
ENCRE_REMPLISSAGE = colors.Color(0.25, 0.25, 0.25)  # intérieur des chiffres (soutenu)
MICRO_GENERIQUE = "MANAPRINT*ORIGINAL*"
_POLICE_RAPIDE = "DJLECO"  # la police de la gamme ÉCO -> rendu simple et rapide

# 🖨️ MODE BOUTIQUE RAPIDE (Maeva, juil. 2026) : cartons SANS microtexte pour les
# étagères boutique — le microtexte sature le processeur des imprimantes en
# impression directe (clé USB) : pause toutes les ~5 feuilles. En mode rapide,
# le cadre devient un fin trait simple et les chiffres sont pleins : PDF léger,
# impression d'une traite. La sécurité reste assurée par le QR unique + code.
# Interrupteur isolé par thread (chaque fabrication tourne dans son propre thread).
import threading as _threading
_mode_local = _threading.local()


def activer_mode_rapide(actif=True):
    """Active/désactive le mode boutique rapide pour le thread de fabrication courant."""
    _mode_local.rapide = bool(actif)


def mode_rapide_actif():
    return getattr(_mode_local, "rapide", False)


# SIGNATURE TUKEA (sceau Maeva, 05/08) — pour l'offre « PDF seul ».
# Le client emporte le fichier : il l'imprimera, et le photocopiera. Le QR
# de verification n'a plus de sens hors de nos machines ; a sa place, notre
# adresse. Chaque photocopie devient alors une petite publicite.
def activer_sans_qr(actif=True):
    """Supprime le QR des cartons, pour le thread courant.

    Utilise pour les tirages INTERNES (ravitaillement de la boutique,
    fabrique a l'enseigne d'un partenaire) : le QR n'y sert a rien, et
    sa place gagnee allege la page.
    """
    _mode_local.sans_qr = bool(actif)


def sans_qr_actif():
    return getattr(_mode_local, "sans_qr", False)


def activer_signature(actif=True):
    """Remplace le QR par la signature TUKEA, pour le thread courant."""
    _mode_local.signature = bool(actif)


def signature_active():
    return getattr(_mode_local, "signature", False)

# QR de vérification (anti-duplication) — anti-panne : optionnel
try:
    from generators import qr_verif as _qr
except Exception:
    try:
        import qr_verif as _qr
    except Exception:
        _qr = None


def _signature_a_la_place(c, x, y, taille):
    """Ecrit la signature TUKEA dans la case du QR, sur trois lignes
    ajustees a la largeur disponible. Tout au trait, presque pas d'encre."""
    from reportlab.lib import colors as _c
    from reportlab.pdfbase.pdfmetrics import stringWidth as _w
    lignes = ["by TUKEA", "89 22 23 05", "manaprint.app"]
    largeur = max(taille * 2.3, 26.0)
    c.saveState()
    c.setFillColor(_c.Color(0.42, 0.42, 0.42))
    t = 6.2
    while t > 3.4 and max(_w(s, "Helvetica-Bold", t) for s in lignes) > largeur:
        t -= 0.1
    interligne = t * 1.25
    haut = y + taille / 2 + interligne
    cx = x + taille / 2
    for i, s in enumerate(lignes):
        c.setFont("Helvetica-Bold" if i == 0 else "Helvetica", t)
        c.drawCentredString(cx, haut - i * interligne, s)
    c.restoreState()
    return True


def carton_qr(c, x, y, taille, evenement_id, serie, **options):
    """Dessine le QR de vérification si le module est disponible. Renvoie True/False.
    options : position_code="bas" (défaut) ou "droite".
    En mode SIGNATURE (offre « PDF seul »), la signature TUKEA prend la
    place du QR : le fichier part chez le client, la copie fait la publicite."""
    if sans_qr_actif():
        return False          # tirage de la maison : pas de QR du tout
    if signature_active():
        try:
            return _signature_a_la_place(c, x, y, taille)
        except Exception:
            return False
    if _qr is None:
        return False
    try:
        return _qr.dessiner_qr(c, x, y, taille, evenement_id, serie, **options)
    except Exception:
        return False



def _chaine_serie(serie):
    """Texte de sécurité unique par carte (contient le N° de série)."""
    try:
        return "MANAPRINT*ORIGINAL*%06d*" % int(serie)
    except Exception:
        return MICRO_GENERIQUE


def ligne_micro(c, x, y, longueur, serie, taille=0.55, angle=0, couleur=GRIS_MICRO):
    """Trace une ligne de microtexte de la longueur demandée (points PDF).
    🖨️ Mode boutique rapide : un fin trait simple à la place (même allure à
    l'œil nu, mille fois plus léger pour le processeur de l'imprimante)."""
    if mode_rapide_actif():
        c.saveState()
        c.setStrokeColor(couleur)
        c.setLineWidth(0.3)
        c.translate(x, y)
        if angle:
            c.rotate(angle)
        c.line(0, taille * 0.35, longueur, taille * 0.35)
        c.restoreState()
        return
    base = _chaine_serie(serie)
    l_base = pdfmetrics.stringWidth(base, POLICE_MICRO, taille)
    if l_base <= 0 or longueur <= 0:
        return
    nrep = int(longueur / l_base) + 1
    texte = base * nrep
    ncar = max(1, int(len(texte) * longueur / (l_base * nrep)))
    c.saveState()
    c.setFont(POLICE_MICRO, taille)
    c.setFillColor(couleur)
    c.translate(x, y)
    if angle:
        c.rotate(angle)
    c.drawString(0, 0, texte[:ncar])
    c.restoreState()


def cadre_micro(c, x0, y0, largeur, hauteur, serie,
                retrait=1.5 * mm, taille=0.70, couleur=GRIS_MICRO):
    """Cadre intérieur en microtexte sur les 4 côtés d'une carte."""
    d = retrait
    ligne_micro(c, x0 + d, y0 + d - 0.4, largeur - 2 * d, serie, taille, 0, couleur)    # bas
    ligne_micro(c, x0 + d, y0 + hauteur - d, largeur - 2 * d, serie, taille, 0, couleur)  # haut
    ligne_micro(c, x0 + d + 0.4, y0 + d, hauteur - 2 * d, serie, taille, 90, couleur)   # gauche
    ligne_micro(c, x0 + largeur - d, y0 + d, hauteur - 2 * d, serie, taille, 90, couleur)  # droite


def _cle_couleur(couleur):
    try:
        r, g, b = couleur.rgb()
        return "%02x%02x%02x" % (int(r * 255), int(g * 255), int(b * 255))
    except Exception:
        return "x"


def _encre_remplissage(couleur):
    """Encre du microtexte intérieur : la couleur du chiffre, assombrie de 55 %
    pour compenser les vides de la trame (réglage validé sur le style P15)."""
    try:
        r, g, b = couleur.rgb()
        return colors.Color(r * 0.45, g * 0.45, b * 0.45)
    except Exception:
        return ENCRE_REMPLISSAGE


def _form_chiffre(c, ch, police, taille, taille_micro, couleur, epaisseur=None):
    """Crée (une seule fois par document) le 'tampon' PDF d'un chiffre rempli
    de microtexte, avec contour net pour la lisibilité en salle.

    ⭐⭐ 23/09 (sceau Maeva : « renforce le gras, on ne change pas
    l'écriture ») : `epaisseur` permet à un jeu de demander un CONTOUR PLUS
    ÉPAIS sans toucher à la police. Le trait est centré sur le dessin de la
    lettre : il l'épaissit vers l'intérieur ET vers l'extérieur, donc on
    obtient un gras sans déformer Latin Modern. C'est la seule façon de
    grossir le trait sans changer d'écriture.
    ⚠️⚠️ L'ÉPAISSEUR ENTRE DANS LE NOM DU TAMPON. Chaque chiffre n'est
    dessiné qu'UNE fois par document puis réutilisé : sans ça, un jeu à
    contour fin et un jeu à contour gras se partageraient le même tampon et
    le second prendrait l'épaisseur du premier. NE PAS RETIRER DU NOM.
    ⚠️ Valeur par défaut inchangée : tous les jeux qui n'en demandent pas
    gardent exactement le rendu d'avant.
    """
    epais = (0.016 if "Bold" in police else 0.010) if epaisseur is None else float(epaisseur)
    nom = "mtx_%s_%s_%d_%s_%d"
