# -*- coding: utf-8 -*-
"""
MANAPRINT — Générateur WOW 6 BOULES (format A4)
12 cartes par feuille A4 (3 colonnes × 4 rangées).
Chaque carte : grille 3×3 avec 6 numéros UNIQUES tirés de 30-59
et 3 cases vides FIXES (fidèle au modèle) :
  (rangée 0, col 2) haut-droite · (rangée 1, col 0) milieu-gauche · (rangée 2, col 1) bas-milieu
Le QR de vérification se niche dans la case vide du bas-milieu.
En-tête 2 lignes : titre + « Carte N° 54001 » (fidèle au modèle).
Couleur arc-en-ciel (par carte) ou gris (N&B). Chiffres en gris (2 gammes ÉCO/PREMIUM).
"""
import io
import random
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

# SÉCURITÉ ANTI-PHOTOCOPIE (microtexte) — anti-panne : si le module securite
# est absent, les cartons sortent normalement, simplement sans microtexte.
try:
    from generators import securite as _sec
except Exception:
    try:
        import securite as _sec
    except Exception:
        _sec = None


try:
    pdfmetrics.registerFont(TTFont("DJL", "/usr/share/fonts/truetype/dejavu/DejaVuSans-ExtraLight.ttf"))
    POLICE = "DJL"
except Exception:
    POLICE = "Helvetica"

RAINBOW = [
    "#E53935", "#FB8C00", "#F9A825", "#43A047", "#00ACC1",
    "#1E88E5", "#3949AB", "#8E24AA", "#D81B60", "#6D4C41",
]
GRIS = colors.Color(0.42, 0.42, 0.42)
GRIS40 = colors.Color(0.60, 0.60, 0.60)
GRIS_CLAIR = colors.Color(0.80, 0.80, 0.80)


# ══ DEUX GAMMES COMMERCIALES (vision Maeva) ══════════════════════════
# ÉCO      : écriture fine DejaVu ExtraLight, gris 0,50 — économie de toner
# PREMIUM  : écriture grasse Helvetica-Bold, gris 0,55 — style P15
from reportlab.pdfbase import pdfmetrics as _pm
from reportlab.pdfbase.ttfonts import TTFont as _TF
try:
    _pm.registerFont(_TF("DJLECO", "/usr/share/fonts/truetype/dejavu/DejaVuSans-ExtraLight.ttf"))
    _POLICE_ECO = "DJLECO"
except Exception:
    _POLICE_ECO = "Helvetica"
_GRIS_ECO = colors.Color(0.50, 0.50, 0.50)
_POLICE_P15 = "Helvetica-Bold"
_GRIS_P15 = colors.Color(0.55, 0.55, 0.55)

def _style_chiffres(style):
    """Retourne (police, gris) des chiffres selon la gamme choisie."""
    if str(style).lower() in ("p15", "premium"):
        return _POLICE_P15, _GRIS_P15
    return _POLICE_ECO, _GRIS_ECO
# ═════════════════════════════════════════════════════════════════════

PAGE_W, PAGE_H = A4
PLAGE = (30, 59)                       # les boules du WOW 6
VIDES = {(0, 2), (1, 0), (2, 1)}       # cases vides FIXES (fidèle au modèle)
CASE_QR = (2, 1)                       # le QR vit dans la case vide bas-milieu

# ═══ 💥 LE WOW ! À SIX CERCLES (sceau Maeva 14/08) ═══
# « VOTRE JEU WOW ! — 6 BOULES » : la même explosion de bande dessinée
# que WOW 4, mais six grands cercles — trois en haut, trois en bas.
_RATIO_WOW6 = 1.5018
CERCLES = [[0.2552, 0.7992], [0.5037, 0.798], [0.7476, 0.7992], [0.2642, 0.2509], [0.5121, 0.2506], [0.7704, 0.2505]]
DIAM_CERCLE = 0.179
import os as _os2
from reportlab.pdfbase.pdfmetrics import stringWidth as _lg_w6


def _choisir_image(motif_img, ratio_attendu):
    """Retrouve le dessin, quel que soit son nom de fichier."""
    dossier = _os2.path.dirname(_os2.path.abspath(__file__))
    exact = _os2.path.join(dossier, motif_img + ".png")
    candidats = []
    try:
        for f in _os2.listdir(dossier):
            if motif_img in f and f.lower().endswith(".png"):
                candidats.append(_os2.path.join(dossier, f))
    except Exception:
        return exact
    if not candidats:
        return exact
    meilleur, ecart = candidats[0], 9e9
    for chemin in candidats:
        try:
            from PIL import Image as _Im
            with _Im.open(chemin) as im:
                e = abs(im.width / float(im.height) - ratio_attendu)
        except Exception:
            continue
        if e < ecart:
            meilleur, ecart = chemin, e
    return meilleur


_IMAGE_WOW6 = _choisir_image("wow6_bd", _RATIO_WOW6)


# 14/08 : le dessin est en PAYSAGE (ratio 1,50) — on passe de 12 cartes
# a 8 cartes-plaques (2 colonnes x 4 rangees).
COLS_PAGE = 2
ROWS_PAGE = 4
MARGIN_X = 8 * mm
MARGIN_TOP = 8 * mm
MARGIN_BOT = 8 * mm
GUTTER_X = 4 * mm
GUTTER_Y = 4 * mm

CARD_W = (PAGE_W - 2 * MARGIN_X - (COLS_PAGE - 1) * GUTTER_X) / COLS_PAGE
CARD_H = (PAGE_H - MARGIN_TOP - MARGIN_BOT - (ROWS_PAGE - 1) * GUTTER_Y) / ROWS_PAGE


def _gen_carte(rng):
    """6 numéros uniques (30-59) placés dans les 6 cases pleines (ordre aléatoire)."""
    nums = rng.sample(range(PLAGE[0], PLAGE[1] + 1), 6)
    grille = {}
    k = 0
    for r in range(3):
        for cc in range(3):
            if (r, cc) in VIDES:
                continue
            grille[(r, cc)] = nums[k]
            k += 1
    return grille


def _dessiner_carte(c, x0, y0, grille, couleur_hex, serie, titre_jeu="", telephone="", style="eco", evenement_id=""):
    police_ch, gris_ch = _style_chiffres(style)
    col = colors.HexColor(couleur_hex)

    # 14/08 : ni cadre, ni microtexte, ni QR — comme les autres jeux
    # habilles. Maeva veut le carton net.

    # ═══ LA PLAQUE AU WOW ! ═══
    # PAS de preserveAspectRatio : on VEUT l'etirer pour qu'elle epouse
    # la carte. Les six cercles suivent, chacun a sa place.
    _pw = CARD_W - 0.6 * mm
    _ph = CARD_H - 0.6 * mm
    _px = x0 + (CARD_W - _pw) / 2
    _py = y0 + 0.3 * mm
    if _os2.path.exists(_IMAGE_WOW6):
        try:
            c.drawImage(_IMAGE_WOW6, _px, _py, _pw, _ph, mask="auto")
        except Exception:
            pass

    # LA POLICE DES CHIFFRES : « Helvetica-Bold » (sceau Maeva 14/08).
    # Le secret n'est pas la taille, c'est LE GRAS — 58 % de chair contre
    # 24 % pour DJLECO : les chiffres se voient de loin.
    _POLICE_NUM = "Helvetica-Bold"
    _dia = _pw * DIAM_CERCLE
    _t_num = 48.0
    while _t_num > 6 and (_lg_w6("88", _POLICE_NUM, _t_num) > _dia * 0.72
                          or _t_num * 0.72 > _dia * 0.62):
        _t_num -= 0.5

    # ═══ les SIX numeros, dans les cercles du WOW ═══
    # `grille` est un DICTIONNAIRE {(rangee, colonne): numero} — les trois
    # cases vides n'y figurent pas. On lit dans l'ordre naturel.
    _plat = [grille[(r, cc)] for r in range(3) for cc in range(3)
             if (r, cc) in grille]
    for _k, _n in enumerate(_plat[:6]):
        _bx, _by = CERCLES[_k]
        _nx = _px + _bx * _pw
        _ny = _py + _by * _ph - _t_num * 0.34
        if _sec:
            _sec.chiffre_micro(c, _n, _nx, _ny, _t_num, gris_ch, _POLICE_NUM)
        else:
            c.setFillColor(gris_ch)
            c.setFont(_POLICE_NUM, _t_num)
            c.drawCentredString(_nx, _ny, str(_n))

    # ═══ LE BANDEAU, ecrit dans sa pastille (deja creuse au dessin) ═══
    c.setFillColor(gris_ch)
    _bl = "N\u00b0 %05d" % serie
    if telephone:
        _bl += "        \u2605        " + telephone
    _tb = 9.0
    while _tb > 3.4 and _lg_w6(_bl, "Helvetica-Bold", _tb) > _pw * 0.42:
        _tb -= 0.25
    c.setFont("Helvetica-Bold", _tb)
    c.drawCentredString(_px + _pw * 0.510, _py + _ph * 0.036, _bl)


def generer_pdf(nb_cartes=12, serie_start=1, theme="", couleur=True,
                nom_evenement="", titre_jeu="", couleur_perso="", date_lieu="", telephone="",
                style="eco", evenement_id="", page_start=1):
    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=A4, pageCompression=1)

    nb_cartes = max(1, min(int(nb_cartes), 10000))
    par_page = COLS_PAGE * ROWS_PAGE
    nb_pages = (nb_cartes + par_page - 1) // par_page

    rng = random.Random()   # graine fraîche : cartes uniques à chaque génération
    serie = int(serie_start)
    # 📄 la page continue d'une rame à l'autre (sceau Maeva 12/08)
    no_page = max(1, int(page_start))
    faites = 0

    for _ in range(nb_pages):
        # en-tête de page
        if nom_evenement:
            c.setFillColor(colors.black); c.setFont(POLICE, 9)
            c.drawCentredString(PAGE_W / 2, PAGE_H - 5 * mm, nom_evenement)
        c.setFillColor(GRIS_CLAIR); c.setFont(POLICE, 6)
        c.drawCentredString(PAGE_W / 2, PAGE_H - 7.2 * mm, "%03d" % no_page)

        for row in range(ROWS_PAGE):
            for col_i in range(COLS_PAGE):
                if faites >= nb_cartes:
                    break
                x0 = MARGIN_X + col_i * (CARD_W + GUTTER_X)
                y0 = MARGIN_BOT + (ROWS_PAGE - 1 - row) * (CARD_H + GUTTER_Y)
                grille = _gen_carte(rng)
                coul = (couleur_perso if (couleur and couleur_perso)
                        else RAINBOW[(serie - 1) % len(RAINBOW)] if couleur else "#9A9A9A")
                _dessiner_carte(c, x0, y0, grille, coul, serie, titre_jeu, telephone, style=style, evenement_id=evenement_id)
                serie += 1
                faites += 1

        c.showPage()
        no_page += 1

    c.save()
    buf.seek(0)
    return buf


if __name__ == "__main__":
    pdf = generer_pdf(nb_cartes=12, couleur=True,
                      nom_evenement="ASSOCIATION TE MANU", titre_jeu="BOUTIQUE RAIATEA",
                      serie_start=54001, telephone="87 04 82 21")
    with open("test_wow6.pdf", "wb") as f:
        f.write(pdf.read())
    print("WOW 6 boules généré")
