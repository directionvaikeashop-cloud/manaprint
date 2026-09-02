# -*- coding: utf-8 -*-
"""
MANAPRINT — Générateur BGO TIKI (format A4)

🗿 NÉ LE 27/08 (sceau Maeva) — LE FRÈRE HABILLÉ DE « BGO 5 BOULES ».
Une languette « CRÉATION TUKEA · 89 22 23 05 » : cinq tikis assis dans les
feuillages, chacun tenant une bulle blanche dans la bouche, une fleur de lys
en haut à gauche, l'étoile « 5 BOULES » en haut à droite.

RÈGLE — LA MÊME QUE BGO 5 BOULES, rien n'a bougé :
  tiki 1 · B : 1-15   ┐ les deux B, triés du plus petit au plus grand
  tiki 2 · B : 1-15   ┘
  tiki 3 · G : 46-60
  tiki 4 · O : 61-75  ┐ les deux O, triés du plus petit au plus grand
  tiki 5 · O : 61-75  ┘
⚠️ Les deux numéros d'une même lettre sont tirés D'UN COUP (`rng.sample`)
   pour être toujours différents, puis TRIÉS — le petit à gauche.
⚠️ LE SAC DU CRIEUR SAUTE LE 16-45 : il ne contient que 1-15 et 46-75.
   (identique à `bgo5` dans app.py — ne pas y toucher.)

⚠️ Le dessin est une LANGUETTE (ratio 1,5317) — 8 cartes par feuille A4
   (2 colonnes × 4 rangées, sceau Maeva 28/08 : elle a choisi les chiffres à
   20 pt, le maximum possible avec ce dessin, plutôt que 10 cartes à 17 pt). Le ratio commande : on calcule les deux côtés
   ENSEMBLE et on centre dans les deux sens, sinon les tikis s'écrasent.
⚠️ Le dessin fourni portait « Ô » (accent) sous le 4e tiki alors que le 5e
   portait « O » : le O propre du 5e a été RECOPIÉ à la place, pas redessiné.
⭐⭐ DESSIN REFAIT PAR MAEVA LE 28/08 pour l'économie de toner : tout est
   passé en CONTOURS, plus un seul aplat — le dessin est tombé de 12,90 % à
   7,33 % d'encre, mieux que la version ÉCO que j'avais fabriquée (9,08 %).
   Ses bulles ont aussi grossi de 13 %, les chiffres y gagnent.
⚠️ `bgo_tiki_eco.png` reste FACULTATIF : s'il n'est pas téléversé, la gamme
   ÉCO utilise simplement le même dessin (repli automatique, jamais de carton
   vide). Le trait est fin PARTOUT — la moitié fait 2 px, soit 0,13 mm à
   l'impression : l'amincir le ferait disparaître, et le creuser vide le
   regard des tikis.
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
from reportlab.pdfbase.pdfmetrics import stringWidth as _lg_tk

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

# ═══ 🗿 LES CINQ BULLES, de gauche à droite ═══
# (relevées sur le dessin recadré — fractions de la carte, repère bas-gauche)
_RATIO_TIKI = 1.5317
BULLES = [
    [0.1082, 0.2177],
    [0.3004, 0.2172],
    [0.4907, 0.2172],
    [0.6800, 0.2172],
    [0.8704, 0.2172],
]
LARG_BULLE = 0.0944
HAUT_BULLE = 0.1580

# 🗿 la plage de chaque tiki + le groupe de lettre auquel il appartient.
# Les tikis d'un même groupe sont tirés ENSEMBLE puis triés.
GROUPES = [
    ((0, 1), (1, 15)),      # les deux B
    ((2,),   (46, 60)),     # le G, tout seul
    ((3, 4), (61, 75)),     # les deux O
]
# le sac du crieur : 1-15 et 46-75 — LE 16-45 N'EXISTE PAS dans ce jeu
SAC = [n for n in range(1, 16)] + [n for n in range(46, 76)]

# la bande blanche sous les tikis accueille le numéro de série
_SERIE_X = 0.8286
_SERIE_Y = 0.0481
_SERIE_LARG = 0.157


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


# ⭐⭐ DEUX DESSINS, UN PAR GAMME (sceau Maeva 27/08) — le trait des tikis
# est fin partout, il n'y a AUCUN aplat à creuser : le seul levier d'économie
# de toner est d'ALLÉGER LE TRAIT. La version ÉCO est le même dessin à 70 %
# de noir — le dessin reste franc et coûte 30 % d'encre en moins.
def _img(nom):
    d = _os2.path.dirname(_os2.path.abspath(__file__))
    return _os2.path.join(d, nom + ".png")


_IMAGE_TIKI = _img("bgo_tiki")               # PREMIUM — trait plein
_IMAGE_TIKI_ECO = _img("bgo_tiki_eco")       # ÉCO — trait allégé à 70 %
if not _os2.path.exists(_IMAGE_TIKI):
    _IMAGE_TIKI = _choisir_image("bgo_tiki", _RATIO_TIKI)
if not _os2.path.exists(_IMAGE_TIKI_ECO):
    _IMAGE_TIKI_ECO = _IMAGE_TIKI            # repli : jamais de carton vide

PAGE_W, PAGE_H = A4
MARGIN_X = 6 * mm
MARGIN_TOP = 6 * mm
MARGIN_BOT = 6 * mm
GUTTER_X = 3 * mm
GUTTER_Y = 2 * mm
# ⚠️ ON RESPECTE LE RATIO : les deux côtés se calculent ENSEMBLE, sinon les
# tikis s'aplatissent. On centre ensuite dans les deux sens.
COLS_PAGE = 2
ROWS_PAGE = 4
_DISPO_W = (PAGE_W - 2 * MARGIN_X - (COLS_PAGE - 1) * GUTTER_X) / COLS_PAGE
_DISPO_H = (PAGE_H - MARGIN_TOP - MARGIN_BOT - (ROWS_PAGE - 1) * GUTTER_Y) / ROWS_PAGE
CARD_W = min(_DISPO_W, _DISPO_H * _RATIO_TIKI)
CARD_H = CARD_W / _RATIO_TIKI
_TOTAL_W = COLS_PAGE * CARD_W + (COLS_PAGE - 1) * GUTTER_X
_TOTAL_H = ROWS_PAGE * CARD_H + (ROWS_PAGE - 1) * GUTTER_Y
MARGE_G = (PAGE_W - _TOTAL_W) / 2
MARGE_B = MARGIN_BOT + max(0, (PAGE_H - MARGIN_TOP - MARGIN_BOT - _TOTAL_H) / 2)


def _gen_carte(rng):
    """🗿 Cinq numéros, un par tiki.

    Les tikis d'une même lettre (les deux B, les deux O) sont tirés d'un
    SEUL coup dans leur plage puis TRIÉS : jamais deux fois le même chiffre,
    et le petit se pose toujours à gauche — comme sur BGO 5 boules.
    """
    nums = [None] * 5
    for cases, (lo, hi) in GROUPES:
        tirage = sorted(rng.sample(range(lo, hi + 1), len(cases)))
        for case, n in zip(cases, tirage):
            nums[case] = n
    return nums


def _dessiner_carte(c, x0, y0, nums, couleur_hex, serie, telephone="",
                    style="eco", evenement_id=""):
    police_ch, gris_ch = _style_chiffres(style)

    # ═══ LA LANGUETTE AUX CINQ TIKIS ═══
    _pw = CARD_W - 0.6 * mm
    _ph = CARD_H - 0.6 * mm
    _px = x0 + (CARD_W - _pw) / 2
    _py = y0 + 0.3 * mm
    # le dessin suit la gamme : trait plein en PREMIUM, trait allégé en ÉCO
    _img_carte = (_IMAGE_TIKI if str(style).lower() in ("p15", "premium")
                  else _IMAGE_TIKI_ECO)
    if _os2.path.exists(_img_carte):
        try:
            c.drawImage(_img_carte, _px, _py, _pw, _ph, mask="auto")
        except Exception:
            pass

    # LA POLICE DES CHIFFRES : « Helvetica-Bold » — le gras plutôt que la
    # taille, les chiffres se voient de loin.
    _POLICE_NUM = "Helvetica-Bold"
    _lg_b = _pw * LARG_BULLE
    _ht_b = _ph * HAUT_BULLE
    _t_num = 48.0
    while _t_num > 6 and (_lg_tk("88", _POLICE_NUM, _t_num) > _lg_b * 0.86
                          or _t_num * 0.72 > _ht_b * 0.72):
        _t_num -= 0.5

    for _k, _n in enumerate(nums[:5]):
        _bx, _by = BULLES[_k]
        _nx = _px + _bx * _pw
        _ny = _py + _by * _ph - _t_num * 0.34
        c.setFillColor(gris_ch)
        c.setFont(_POLICE_NUM, _t_num)
        c.drawCentredString(_nx, _ny, str(_n))

    # ═══ LA SÉRIE, dans la bande blanche sous les tikis ═══
    c.setFillColor(colors.black)
    _tb = 9.0
    _bl = "S\u00c9RIE : %03d" % serie
    while _tb > 3.0 and _lg_tk(_bl, "Helvetica-Bold", _tb) > _pw * _SERIE_LARG:
        _tb -= 0.25
    c.setFont("Helvetica-Bold", _tb)
    c.drawCentredString(_px + _SERIE_X * _pw,
                        _py + _SERIE_Y * _ph - _tb * 0.34, _bl)


def generer_pdf(nb_cartes=8, serie_start=1, theme="", couleur=True,
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
    faites = 0
    for _ in range(nb_pages):
        if nom_evenement:
            c.setFillColor(colors.black); c.setFont("Helvetica-Bold", 9)
            c.drawCentredString(PAGE_W / 2, PAGE_H - 5 * mm, nom_evenement)
        c.setFillColor(GRIS_CLAIR); c.setFont("Helvetica", 5)
        c.drawRightString(PAGE_W - 6 * mm, PAGE_H - 5 * mm, "Page %d" % no_page)
        for row in range(ROWS_PAGE):
            for col_i in range(COLS_PAGE):
                if faites >= nb_cartes:
                    break
                x0 = MARGE_G + col_i * (CARD_W + GUTTER_X)
                y0 = MARGE_B + (ROWS_PAGE - 1 - row) * (CARD_H + GUTTER_Y)
                coul = (couleur_perso or "#000000") if couleur else "#000000"
                _dessiner_carte(c, x0, y0, _gen_carte(rng), coul, serie,
                                telephone, style, evenement_id)
                serie += 1
                faites += 1
        c.showPage()
        no_page += 1
    c.save()
    buf.seek(0)
    return buf
