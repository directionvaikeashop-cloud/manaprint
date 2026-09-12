# -*- coding: utf-8 -*-
"""
MANAPRINT — Générateur VIN CORSE ALALIA (format A4)

🍇 NÉ LE 10/09 (sceau Maeva) — LA GRAPPE DE RAISIN CORSE.
Un carton en hauteur : le panneau de bois « Vin Corse ALALIA · Terre de
caractère », la bouteille et le verre, la tête de Maure « CORSICA · ISULA
BELLA », les cinq pastilles B-I-N-G-O avec leurs plages, et une GRAPPE DE
TREIZE GRAINS qui porte les numéros. « Plus qu'un vin, une histoire… » à
gauche, « Santé ! » à droite.

RÈGLE — NEUF numéros, tous différents. LA COLONNE COMMANDE LA PLAGE
(sceau Maeva 10/09) : chaque grain tire dans la plage de la colonne où il
se trouve, exactement comme les cinq pastilles l'annoncent en tête —
  B : 1-15   ·   I : 16-30   ·   N : 31-45   ·   G : 46-60   ·   O : 61-75
La grappe compte DIX grains dessinés, mais NEUF seulement reçoivent un
numéro — celui du milieu de la 3e rangée reste vide (sceau Maeva 10/09) :
        ●  ●  ●        B · N · O
          ●  ●         I · G
        ●  ✗  ●        B · (vide) · O
          ●  ●         I · G
   soit deux B, deux I, UN SEUL N, deux G et deux O.
⚠️ Les cinq plages se suivent SANS TROU : tout le sac de 1 à 75 sert.
⚠️ Le sac du crieur va de 1 à 75.

⭐ CHAQUE GRAIN PORTE SA LETTRE au-dessus de son chiffre, comme sur le
   carton d'exemple de Maeva.

⚠️ Le carton est en HAUTEUR (ratio 0,8580) — 12 par feuille A4 (3 × 4),
   comme la planche que Maeva a dessinée.
"""
import io
import os as _os2
import random
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase.pdfmetrics import stringWidth as _lg_al

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

GRIS = colors.Color(0.42, 0.42, 0.42)
GRIS_CLAIR = colors.Color(0.62, 0.62, 0.62)


# ══ DEUX GAMMES COMMERCIALES (vision Maeva) ══════════════════════════
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

_RATIO_CARTON = 0.8580

# ═══ 🍇 LES NEUF GRAINS QUI REÇOIVENT UN NUMÉRO ═══ (x, y en fractions du carton ; n° de colonne)
#     colonne 0=B · 1=I · 2=N · 3=G · 4=O
# ⚠️⚠️ ATTENTION — les CINQ PASTILLES B·I·N·G·O de l'en-tête sont, elles
#    aussi, des cercles bien ronds : au premier relevé, trois d'entre elles
#    (I, N, G) s'étaient glissées dans la liste et recevaient un numéro.
#    Les VRAIS GRAINS sont tous SOUS la ligne des pastilles (y < 0,55).
# ⭐ 10/09 (sceau Maeva) : LE GRAIN DU MILIEU DE LA 3e RANGÉE RESTE VIDE.
#    Il est dessiné sur la grappe mais ne reçoit pas de numéro — c'est le
#    grain que Maeva a désigné, et on retombe ainsi sur les NEUF boules de
#    son carton d'exemple. La colonne N n'a donc qu'UN SEUL numéro.
#    ⚠️ Pour le remettre un jour : rajouter (0.5086, 0.2601, 2) en 3e rangée.
BOULES = [
    (0.3373, 0.5043, 0), (0.5027, 0.5039, 2), (0.6714, 0.5043, 4),   # rangée 1 : B · N · O
    (0.4191, 0.3810, 1), (0.5905, 0.3810, 3),                        # rangée 2 : I · G
    (0.3532, 0.2570, 0),                      (0.6705, 0.2598, 4),   # rangée 3 : B · ✗ · O
    (0.4359, 0.1470, 1), (0.5845, 0.1486, 3),                        # rangée 4 : I · G
]
DIAM_GRAIN = 0.1500
HAUT_GRAIN = 0.1270

LETTRES = "BINGO"
# 🍇 la plage de chaque colonne — elles sont IMPRIMÉES en tête du carton
PLAGES = [(1, 15), (16, 30), (31, 45), (46, 60), (61, 75)]


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


_IMAGE_CARTON = _choisir_image("alalia_grappe", _RATIO_CARTON)

PAGE_W, PAGE_H = A4
MARGIN_X = 5 * mm
MARGIN_TOP = 5 * mm
MARGIN_BOT = 5 * mm
GUTTER_X = 2 * mm
GUTTER_Y = 2 * mm
# ⚠️ ON RESPECTE LE RATIO : les deux côtés ensemble, puis on centre.
COLS_PAGE = 3
ROWS_PAGE = 4
_DISPO_W = (PAGE_W - 2 * MARGIN_X - (COLS_PAGE - 1) * GUTTER_X) / COLS_PAGE
_DISPO_H = (PAGE_H - MARGIN_TOP - MARGIN_BOT - (ROWS_PAGE - 1) * GUTTER_Y) / ROWS_PAGE
CARD_W = min(_DISPO_W, _DISPO_H * _RATIO_CARTON)
CARD_H = CARD_W / _RATIO_CARTON
_TOTAL_W = COLS_PAGE * CARD_W + (COLS_PAGE - 1) * GUTTER_X
_TOTAL_H = ROWS_PAGE * CARD_H + (ROWS_PAGE - 1) * GUTTER_Y
MARGE_G = (PAGE_W - _TOTAL_W) / 2
MARGE_B = MARGIN_BOT + max(0, (PAGE_H - MARGIN_TOP - MARGIN_BOT - _TOTAL_H) / 2)


def _gen_carte(rng):
    """🍇 Treize numéros, tous différents.

    On tire COLONNE PAR COLONNE : chaque colonne a sa plage à elle, et tous
    ses grains sont tirés d'un seul coup — deux grains d'une même colonne ne
    peuvent donc jamais porter le même chiffre. Les numéros d'une colonne
    sont TRIÉS du haut vers le bas.
    """
    par_colonne = {}
    for i, (x, y, co) in enumerate(BOULES):
        par_colonne.setdefault(co, []).append(i)
    valeurs = [None] * len(BOULES)
    for co, postes in par_colonne.items():
        lo, hi = PLAGES[co]
        # ⚠️ du PLUS PETIT EN HAUT au plus grand en bas, comme sur tous les
        #    autres cartons de la maison : on trie le tirage en ordre
        #    croissant et on descend la colonne (y décroissant).
        tirage = sorted(rng.sample(range(lo, hi + 1), len(postes)))
        for poste, v in zip(sorted(postes, key=lambda p: -BOULES[p][1]), tirage):
            valeurs[poste] = v
    return valeurs


def _dessiner_carton(c, x0, y0, nums, serie, style="eco"):
    police_ch, gris_ch = _style_chiffres(style)
    _pw = CARD_W - 0.4 * mm
    _ph = CARD_H - 0.4 * mm
    _px = x0 + (CARD_W - _pw) / 2
    _py = y0 + 0.2 * mm
    if _os2.path.exists(_IMAGE_CARTON):
        try:
            c.drawImage(_IMAGE_CARTON, _px, _py, _pw, _ph, mask="auto")
        except Exception:
            pass

    # LA POLICE DES CHIFFRES : « Helvetica-Bold » — le gras plutôt que la
    # taille, les chiffres se voient de loin.
    # ⚠️ le grain porte SA LETTRE au-dessus du chiffre : le chiffre n'a donc
    #    que les deux tiers du bas du grain, et la lettre le tiers du haut.
    _POLICE_NUM = "Helvetica-Bold"
    _lg_g = _pw * DIAM_GRAIN
    _ht_g = _ph * HAUT_GRAIN
    # ⭐ 10/09 (sceau Maeva) : LETTRE RÉTRÉCIE, CHIFFRE AU MAXIMUM.
    #    La lettre n'est qu'un repère — elle passe à 0,30 de la taille du
    #    chiffre et se serre tout en haut du grain. Le chiffre récupère la
    #    place ainsi libérée : 0,78 de la largeur du grain et 0,56 de sa
    #    hauteur, soit 17 pt au lieu de 14.
    _t_num = 40.0
    while _t_num > 6 and (_lg_al("88", _POLICE_NUM, _t_num) > _lg_g * 0.78
                          or _t_num * 0.72 > _ht_g * 0.56):
        _t_num -= 0.5
    _t_let = max(3.0, _t_num * 0.30)

    for i, (fx, fy, co) in enumerate(BOULES):
        _cx = _px + fx * _pw
        _cy = _py + fy * _ph
        # ① la LETTRE, dans le haut du grain
        c.setFillColor(gris_ch)
        c.setFont("Helvetica-Bold", _t_let)
        c.drawCentredString(_cx, _cy + _ht_g * 0.27, LETTRES[co])
        # ② le CHIFFRE, dessous
        c.setFont(_POLICE_NUM, _t_num)
        c.drawCentredString(_cx, _cy - _ht_g * 0.08 - _t_num * 0.34, str(nums[i]))

    # ═══ LA SÉRIE, SOUS LE MOT « SANTÉ ! » (sceau Maeva 10/09) ═══
    #    Mesuré sur le dessin : le mot occupe x 0,68→0,98 et descend jusqu'à
    #    y 0,151 ; la bande y 0,073→0,073 est libre juste en dessous.
    c.setFillColor(gris_ch)
    _tb = 8.0
    _bl = "N\u00b0 %05d" % serie
    while _tb > 3.0 and _lg_al(_bl, "Helvetica-Bold", _tb) > _pw * 0.26:
        _tb -= 0.25
    c.setFont("Helvetica-Bold", _tb)
    c.drawCentredString(_px + 0.8323 * _pw, _py + 0.0530 * _ph, _bl)


def generer_pdf(nb_cartes=12, serie_start=1, theme="", couleur=True,
                nom_evenement="", titre_jeu="", couleur_perso="", date_lieu="",
                telephone="", style="eco", evenement_id="", page_start=1):
    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=A4, pageCompression=1)
    rng = random.Random()
    nb_cartes = max(1, min(int(nb_cartes), 10000))
    par_page = COLS_PAGE * ROWS_PAGE
    nb_pages = (nb_cartes + par_page - 1) // par_page
    serie = int(serie_start)
    no_page = max(1, int(page_start))
    faits = 0
    for _ in range(nb_pages):
        # ⭐ le numéro de page AU CENTRE, en haut (règle Maeva 03/09)
        if nom_evenement:
            c.setFillColor(colors.black); c.setFont("Helvetica-Bold", 8)
            c.drawString(MARGIN_X, PAGE_H - 4 * mm, nom_evenement)
        c.setFillColor(GRIS_CLAIR); c.setFont("Helvetica-Bold", 7)
        c.drawCentredString(PAGE_W / 2, PAGE_H - 4 * mm, "Page %d" % no_page)
        for row in range(ROWS_PAGE):
            for col_i in range(COLS_PAGE):
                if faits >= nb_cartes:
                    break
                x0 = MARGE_G + col_i * (CARD_W + GUTTER_X)
                y0 = MARGE_B + (ROWS_PAGE - 1 - row) * (CARD_H + GUTTER_Y)
                _dessiner_carton(c, x0, y0, _gen_carte(rng), serie, style)
                serie += 1
                faits += 1
        c.showPage()
        no_page += 1
    c.save()
    buf.seek(0)
    return buf
