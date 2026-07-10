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

# QR de vérification (anti-duplication) — anti-panne : optionnel
try:
    from generators import qr_verif as _qr
except Exception:
    try:
        import qr_verif as _qr
    except Exception:
        _qr = None


def carton_qr(c, x, y, taille, evenement_id, serie, **options):
    """Dessine le QR de vérification si le module est disponible. Renvoie True/False.
    options : position_code="bas" (défaut) ou "droite"."""
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


def _form_chiffre(c, ch, police, taille, taille_micro, couleur):
    """Crée (une seule fois par document) le 'tampon' PDF d'un chiffre rempli
    de microtexte, avec contour net pour la lisibilité en salle."""
    nom = "mtx_%s_%s_%d_%s" % (ch, police, int(taille * 10), _cle_couleur(couleur))
    formes = getattr(c, "_formes_micro", None)
    if formes is None:
        formes = set()
        c._formes_micro = formes
    if nom in formes:
        return nom
    largeur = pdfmetrics.stringWidth(ch, police, taille)
    c.beginForm(nom, lowerx=-4, lowery=-taille * 0.30,
                upperx=largeur + 4, uppery=taille * 1.10)
    # 1) contour net du chiffre (lisibilité, façon billet)
    c.setStrokeColor(couleur)
    # contour un peu plus épais pour les polices grasses (Bold)
    epais = 0.016 if "Bold" in police else 0.010
    c.setLineWidth(max(0.3, taille * epais))
    t = c.beginText(0, 0)
    t.setFont(police, taille)
    t.setTextRenderMode(1)   # contour seulement
    t.textOut(ch)
    c.drawText(t)
    # 2) le chiffre devient un masque de découpe (mode de rendu 7)
    t = c.beginText(0, 0)
    t.setFont(police, taille)
    t.setTextRenderMode(7)
    t.textOut(ch)
    c.drawText(t)
    c._code.append('0 Tr')  # IMPORTANT : ReportLab laisse sinon le texte en mode invisible
    # 3) remplir le masque de lignes de microtexte
    l_base = pdfmetrics.stringWidth(MICRO_GENERIQUE, POLICE_MICRO, taille_micro)
    ligne = MICRO_GENERIQUE * (int(largeur * 1.6 / max(l_base, 0.1)) + 2)
    c.setFont(POLICE_MICRO, taille_micro)
    c.setFillColor(_encre_remplissage(couleur))
    interligne = taille_micro * 1.05
    yy = -taille * 0.25
    decal = 0.0
    while yy < taille * 1.05:
        c.drawString(-3 - (decal % 4), yy, ligne)
        yy += interligne
        decal += 1.3
    c.endForm()
    formes.add(nom)
    return nom


def chiffre_micro(c, texte, x_centre, y_bas, taille, couleur, police, taille_micro=None):
    """Dessine un nombre centré (équivalent drawCentredString) dont chaque
    chiffre est rempli de microtexte. taille >= 24 pt recommandé.

    ⚡ GAMME ÉCO (police fine DJLECO) : chiffres simples SANS remplissage
    microtexte -> PDF ultra-légers, impression RAPIDE (retour terrain).
    La sécurité ÉCO reste assurée par le cadre microtexte + le QR unique.
    🏦 GAMME PREMIUM (Bold) : chiffres "billet de banque" complets.
    🖨️ Mode boutique rapide : chiffres pleins pour TOUTES les gammes."""
    if police == _POLICE_RAPIDE or mode_rapide_actif():
        c.saveState()
        c.setFillColor(couleur)
        c.setFont(police, taille)
        c.drawCentredString(x_centre, y_bas, str(texte))
        c.restoreState()
        return
    if taille_micro is None:
        # taille du microtexte proportionnée au chiffre (0,45 à 0,70 pt)
        taille_micro = max(0.45, min(0.70, taille * 0.015))
    texte = str(texte)
    largeurs = [pdfmetrics.stringWidth(ch, police, taille) for ch in texte]
    x = x_centre - sum(largeurs) / 2.0
    for ch, lw in zip(texte, largeurs):
        nom = _form_chiffre(c, ch, police, taille, taille_micro, couleur)
        c.saveState()
        c.translate(x, y_bas)
        c.doForm(nom)
        c.restoreState()
        x += lw
