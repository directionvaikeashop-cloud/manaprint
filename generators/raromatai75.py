# -*- coding: utf-8 -*-
"""
MANAPRINT — Générateur RAROMATAI 75 (feuille A4, deux grilles)

🌴 NÉ LE 03/09 (sceau Maeva) — LE CARTON DE RANIHEI SISTERS & SHOP.
Cocotier et motu en tête, « RAROMATAI 75 », DEUX GRILLES BINGO empilées —
chacune avec son « Série ___ » — un bandeau tressé entre les deux, et
« Bonne chance ! » entre deux hibiscus au pied.

RÈGLE — les cinq colonnes et leur plage (elles sont IMPRIMÉES sur le carton) :
  B : 1-15   ·   I : 16-30   ·   N : 31-45   ·   G : 46-60   ·   O : 61-75
⚠️ Les cinq plages se suivent SANS TROU : tout le sac de 1 à 75 sert.
⚠️ Le sac du crieur va de 1 à 75.

⚠️⚠️ ON NE REMPLIT PAS TOUTE LA GRILLE. Seules les cases marquées d'un ÎLOT
   reçoivent un numéro — les autres restent blanches. Le motif est relevé
   sur le dessin, il n'a pas à être deviné :
        L1 :  B  ·  N  ·  O
        L2 :  ·  I  ·  G  ·
        L3 :  B  ·  ✎  ·  O      (✎ = la case « Série », au centre)
        L4 :  ·  I  ·  G  ·
        L5 :  B  ·  N  ·  O
   Soit DOUZE numéros par grille : trois B, deux I, deux N, deux G, trois O.
   Les numéros d'une même colonne sont TRIÉS du haut vers le bas.

⚠️⚠️ CE JEU EST UNE FEUILLE, pas un carton qu'on répète : le dessin porte
   DEUX grilles. Une page du PDF = une feuille = DEUX cartons. D'où
   `cartes_par_feuille = 2` et une seule image par page.
⚠️ La feuille est en PORTRAIT (ratio 0,6375) — centrée sur un A4 debout.

⭐ NUMÉROTATION (règle de la maison) : le NUMÉRO DE SÉRIE va sur le trait du
   « Série ___ » de chaque grille, et le NUMÉRO DE PAGE au CENTRE, en haut.
   ⚠️ Sur ce carton, CHAQUE GRILLE porte DEUX mentions « Série ___ » : une
      en tête et une au centre de la grille. Le PDF écrit le numéro AUX DEUX
      endroits. Les quatre numéros écrits en dur sur le dessin ont été
      effacés ; le mot « Série » et les traits sont gardés.
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
from reportlab.pdfbase.pdfmetrics import stringWidth as _lg_rm

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

_RATIO_FEUILLE = 0.6809

# ═══ 🌴 LES DEUX GRILLES ═══ (fractions de la feuille, repère bas-gauche)
COLONNES = [0.1269, 0.3153, 0.5041, 0.6930, 0.8808]      # B · I · N · G · O
GRILLES = [
    [0.7181, 0.6617, 0.6042, 0.5471, 0.4902],            # grille du HAUT
    [0.2687, 0.2112, 0.1540, 0.0965, 0.0398],            # grille du BAS
]
LARG_CASE = 0.1855
HAUT_CASE = 0.0492

# 🌴 la plage de chaque colonne — elles sont IMPRIMÉES sur le carton
PLAGES = [(1, 15), (16, 30), (31, 45), (46, 60), (61, 75)]

# 🌴 LES CASES QUI REÇOIVENT UN NUMÉRO : (ligne, colonne). Douze au total.
CASES = [
    (0, 0), (0, 2), (0, 4),    # L1 : B · N · O
    (1, 1), (1, 3),            # L2 : I · G
    (2, 0), (2, 4),            # L3 : B · O
    (3, 1), (3, 3),            # L4 : I · G
    (4, 0), (4, 2), (4, 4),    # L5 : B · N · O
]

# ⭐⭐ 03/09 (sceau Maeva) : LE CHIFFRE S'ÉCARTE DE SON ÎLOT.
#    Mesuré sur le dessin : l'îlot occupe la GAUCHE de la case pour B, I, N
#    et G (de 1 % à 35 %), et la DROITE pour le O (de 67 % à 96 %).
#    Le chiffre part donc DANS L'AUTRE SENS : vers la DROITE pour B·I·N·G,
#    vers la GAUCHE pour O. L'îlot et le chiffre se tournent le dos, chacun
#    dans son coin de case.
#      B·I·N·G : centre du chiffre à 62 % de la case
#      O       : centre du chiffre à 38 %
# ⚠️ ces valeurs sont en fraction de la CASE, pas de la feuille : elles sont
#    donc multipliées par LARG_CASE au moment du tracé.
DECALAGE_X = [+0.12, +0.12, +0.12, +0.12, -0.12]   # B · I · N · G · O

# ⭐ les places du numéro de série : DEUX par grille — en tête, et au centre
# ⚠️ dans la case du CENTRE, le mot « Série » est juste au-dessus du trait :
#    le numéro s'écrit dans l'étroit espace entre les deux, et en plus petit.
SERIE = [
    [(0.3306, 0.8279), (0.5036, 0.5880)],   # grille du HAUT  : tête · centre
    [(0.3306, 0.3763), (0.5036, 0.1372)],   # grille du BAS   : tête · centre
]
SERIE_LARG = 0.150
SERIE_LARG_CENTRE = 0.085


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


_IMAGE_FEUILLE = _choisir_image("raromatai75_feuille", _RATIO_FEUILLE)

PAGE_W, PAGE_H = A4
MARGIN_X = 5 * mm
MARGIN_Y = 5 * mm
CARTES_PAR_FEUILLE = 2
# ⚠️ ON RESPECTE LE RATIO : les deux côtés ensemble, puis on centre.
_DISPO_W = PAGE_W - 2 * MARGIN_X
_DISPO_H = PAGE_H - 2 * MARGIN_Y
CARD_W = min(_DISPO_W, _DISPO_H * _RATIO_FEUILLE)
CARD_H = CARD_W / _RATIO_FEUILLE
MARGE_G = (PAGE_W - CARD_W) / 2
MARGE_B = (PAGE_H - CARD_H) / 2


def _gen_carte(rng):
    """🌴 Douze numéros pour UNE grille, tous différents.

    On tire COLONNE PAR COLONNE : chaque colonne a sa plage à elle, et ses
    cases sont tirées d'un seul coup pour ne jamais porter le même chiffre.
    Les numéros d'une colonne sont TRIÉS du haut vers le bas.
    """
    par_colonne = {}
    for (li, co) in CASES:
        par_colonne.setdefault(co, []).append(li)
    valeurs = {}
    for co, lignes in par_colonne.items():
        lo, hi = PLAGES[co]
        tirage = sorted(rng.sample(range(lo, hi + 1), len(lignes)))
        for li, v in zip(sorted(lignes), tirage):
            valeurs[(li, co)] = v
    return valeurs


def _dessiner_feuille(c, grilles, serie_debut, style="eco"):
    """🌴 Une feuille : le dessin, puis les 24 numéros et les deux séries."""
    police_ch, gris_ch = _style_chiffres(style)
    _px, _py = MARGE_G, MARGE_B
    _pw, _ph = CARD_W, CARD_H
    if _os2.path.exists(_IMAGE_FEUILLE):
        try:
            c.drawImage(_IMAGE_FEUILLE, _px, _py, _pw, _ph, mask="auto")
        except Exception:
            pass

    # LA POLICE DES CHIFFRES : « Helvetica-Bold » — le gras plutôt que la
    # taille, les chiffres se voient de loin.
    # ⭐ 03/09 (sceau Maeva) : la taille est FIXÉE À 25 pt. Les deux
    #    garde-fous restent en place — si la case rétrécissait un jour, la
    #    taille redescendrait toute seule au lieu de déborder.
    _POLICE_NUM = "Helvetica-Bold"
    _lg_c = _pw * LARG_CASE
    _ht_c = _ph * HAUT_CASE
    _t_num = 25.0
    while _t_num > 6 and (_lg_rm("88", _POLICE_NUM, _t_num) > _lg_c * 0.90
                          or _t_num * 0.72 > _ht_c * 0.82):
        _t_num -= 0.5

    for ig, valeurs in enumerate(grilles):
        LIG = GRILLES[ig]
        for (li, co), valeur in valeurs.items():
            _nx = _px + (COLONNES[co] + DECALAGE_X[co] * LARG_CASE) * _pw
            _ny = _py + LIG[li] * _ph - _t_num * 0.34
            c.setFillColor(gris_ch)
            c.setFont(_POLICE_NUM, _t_num)
            c.drawCentredString(_nx, _ny, str(valeur))

    # ═══ LES DEUX SÉRIES, sur leur trait ═══
    for k, places in enumerate(SERIE):
        _bl = "%03d" % (serie_debut + k)
        _tb = 16.0
        while _tb > 3.2 and _lg_rm(_bl, "Helvetica-Bold", _tb) > _pw * SERIE_LARG:
            _tb -= 0.25
        c.setFillColor(colors.black)
        for i, (sx, sy) in enumerate(places):   # en tête ET au centre
            _t = _tb
            if i == 1:                          # la case du centre est étroite
                _t = 11.0
                while _t > 3.2 and _lg_rm(_bl, "Helvetica-Bold", _t) > _pw * SERIE_LARG_CENTRE:
                    _t -= 0.25
            c.setFont("Helvetica-Bold", _t)
            c.drawCentredString(_px + sx * _pw, _py + sy * _ph, _bl)


def generer_pdf(nb_cartes=2, serie_start=1, theme="", couleur=True,
                nom_evenement="", titre_jeu="", couleur_perso="", date_lieu="",
                telephone="", style="eco", evenement_id="", page_start=1):
    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=A4, pageCompression=1)
    rng = random.Random()
    nb_cartes = max(1, min(int(nb_cartes), 10000))
    nb_pages = (nb_cartes + CARTES_PAR_FEUILLE - 1) // CARTES_PAR_FEUILLE
    serie = int(serie_start)
    no_page = max(1, int(page_start))
    for _ in range(nb_pages):
        # ⭐ le numéro de page AU CENTRE, en haut (règle Maeva 03/09)
        if nom_evenement:
            c.setFillColor(colors.black); c.setFont("Helvetica-Bold", 9)
            c.drawString(MARGIN_X, PAGE_H - 4 * mm, nom_evenement)
        c.setFillColor(GRIS_CLAIR); c.setFont("Helvetica-Bold", 7)
        c.drawCentredString(PAGE_W / 2, PAGE_H - 4 * mm, "Page %d" % no_page)
        _dessiner_feuille(c, [_gen_carte(rng) for _ in range(CARTES_PAR_FEUILLE)],
                          serie, style)
        serie += CARTES_PAR_FEUILLE
        c.showPage()
        no_page += 1
    c.save()
    buf.seek(0)
    return buf
