# -*- coding: utf-8 -*-
"""
MANAPRINT — Générateur PAPEARI (format A4 PAYSAGE)

🎊 NÉ LE 14/08 (sceau Maeva) : LA GUIRLANDE DE BINGO. Six anneaux
suspendus sous les lettres B · I · N · N · G · O, des étoiles et des
serpentins qui dansent autour.

⚠️ RÈGLE (relevée sur le carton BORABORA de Maeva : 2 · 16 · 44 · 36 ·
52 · 63) : six numéros, un par lettre —
  B : 1-15 · I : 16-30 · N ×2 : 31-45 · G : 46-60 · O : 61-75
⚠️ LES DEUX N sont tirés ensemble et triés : jamais le même deux fois.

8 cartes par feuille A4 paysage (2 colonnes × 4 rangées).
"""
import io
import random
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4, landscape
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

PAGE_W, PAGE_H = landscape(A4)
# Les 5 boules de TAHAA : (plage, position) — haut: coins + centre, bas: centre-gauche/droit
# 🎈 LES CINQ BALLONS : deux N, un G, deux O
#    ⚠️ ce ne sont que TROIS familles — les deux N sont tirés ensemble,
#    les deux O aussi, pour qu'ils ne se répètent jamais.
# 🎊 LES SIX ANNEAUX : B · I · N · N · G · O
#    ⚠️ les DEUX N sont tirés ensemble pour ne jamais se répéter.
FAMILLES = [((1, 15), 1), ((16, 30), 1), ((31, 45), 2),
            ((46, 60), 1), ((61, 75), 1)]
BOULES = [((1, 15), 0, 0), ((16, 30), 0, 0), ((31, 45), 0, 0),
          ((31, 45), 0, 0), ((46, 60), 0, 0), ((61, 75), 0, 0)]

# ═══ 🐛 LA CHENILLE (sceau Maeva 13/08) ═══
# « VOTRE JEU TAHAA 75 — DE 5 BOULES » : une chenille rieuse, ses CINQ
# ANNEAUX en ligne, l'herbe et les feuilles autour.
# ⚠️ Les numéros ne se lisent plus sur deux rangées mais EN LIGNE, dans
# les anneaux — mesurés au pixel sur l'image elle-même.
_RATIO_CHENILLE = 1.9697
ANNEAUX = [(0.2174, 0.3025), (0.3488, 0.3031), (0.4892, 0.3032), (0.623, 0.3032), (0.7601, 0.304), (0.8953, 0.3041)]

# ⭐ 14/08 (sceau Maeva : « je veux juste que le lien entre les lettres et
# les bulles se voie ») : LES SIX FICELLES.
# Elle a aimé le carton nettoyé, mais les anneaux semblaient flotter.
# Chaque lettre laisse donc pendre SA ficelle jusqu'à SA bulle — dessinée
# PAR LE PDF, pas par l'image : elle suit chaque paire au pixel près et
# ne coûte presque rien en encre.
# ⚠️ elle ondule légèrement (courbe de Bézier) : une ficelle droite ferait
# raide, une ficelle qui serpente fait vivante.
BAS_LETTRES = [[0.2243, 0.5959], [0.3454, 0.5959], [0.4938, 0.6049], [0.6297, 0.6062], [0.7597, 0.5959], [0.8955, 0.5959]]
DIAM_AN = 0.1235
import os as _os2
from reportlab.pdfbase.pdfmetrics import stringWidth as _lg_t


def _choisir_image(motif, ratio_attendu):
    """🛟 Retrouve le dessin, quel que soit son nom de fichier."""
    dossier = _os2.path.dirname(_os2.path.abspath(__file__))
    exact = _os2.path.join(dossier, motif + ".png")
    candidats = []
    try:
        for f in _os2.listdir(dossier):
            if motif in f and f.lower().endswith(".png"):
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


_IMAGE_CHENILLE = _choisir_image("papeari_bingo", _RATIO_CHENILLE)


# ⚠️ 13/08 : 8 cartes par feuille au lieu de 18 (décision Maeva). La
# chenille est LARGE (ratio 2,30) : moins de cartes, mais des chiffres
# qu'on lit à bout de bras — 26 pt au lieu de 14.
COLS_PAGE = 2
ROWS_PAGE = 4
MARGIN_X = 8 * mm
MARGIN_TOP = 9 * mm
MARGIN_BOT = 7 * mm
GUTTER_X = 5 * mm
GUTTER_Y = 3 * mm

CARD_W = (PAGE_W - 2 * MARGIN_X - (COLS_PAGE - 1) * GUTTER_X) / COLS_PAGE
CARD_H = (PAGE_H - MARGIN_TOP - MARGIN_BOT - (ROWS_PAGE - 1) * GUTTER_Y) / ROWS_PAGE


def _gen_carte(rng):
    """🎈 Cinq numéros : deux N, un G, deux O.

    ⚠️ Les deux numéros d'une même lettre sont tirés ENSEMBLE et triés :
    ils ne peuvent donc jamais être identiques, et se lisent dans l'ordre.
    """
    nums = []
    for (pmin, pmax), combien in FAMILLES:
        nums += sorted(rng.sample(range(pmin, pmax + 1), combien))
    return nums


def _dessiner_carte(c, x0, y0, nums, couleur_hex, serie, titre_jeu="", telephone="", style="eco", evenement_id=""):
    police_ch, gris_ch = _style_chiffres(style)
    col = colors.HexColor(couleur_hex)

    # ⚠️⚠️ 13/08 : ni cadre, ni microtexte, ni QR — comme WIN, KAI, SUN,
    # WIZ et RAI. Maeva veut le carton net.

    # ═══ 🐛 LA CHENILLE ═══
    # ⚠️ PAS de preserveAspectRatio : on VEUT l'étirer pour qu'elle épouse
    # la carte. Les cinq anneaux suivent, chacun à sa place.
    BANDE_PIED = 4.0 * mm
    _pw = CARD_W - 0.8 * mm
    _ph = CARD_H - 0.8 * mm - BANDE_PIED
    _px = x0 + (CARD_W - _pw) / 2
    _py = y0 + BANDE_PIED + 0.4 * mm
    if _os2.path.exists(_IMAGE_CHENILLE):
        try:
            c.drawImage(_IMAGE_CHENILLE, _px, _py, _pw, _ph, mask="auto")
        except Exception:
            pass

    # ⚠️ la taille se calcule DEPUIS l'anneau, jamais en dur.
    _dia = _pw * DIAM_AN
    _t_num = 40.0
    while _t_num > 6 and (_lg_t("88", police_ch, _t_num) > _dia * 0.78
                          or _t_num * 0.72 > _dia * 0.66):
        _t_num -= 0.5

    # ═══ les CINQ numéros, dans les anneaux ═══
    # ═══ 🎀 LES FICELLES : de chaque lettre à sa bulle ═══
    c.saveState()
    try:
        c.setStrokeColor(gris_ch)
        c.setLineWidth(0.9)
        for _k in range(min(len(BAS_LETTRES), len(ANNEAUX))):
            _lx, _ly = BAS_LETTRES[_k]
            _ax, _ay = ANNEAUX[_k]
            _x1 = _px + _lx * _pw
            _y1 = _py + _ly * _ph
            _x2 = _px + _ax * _pw
            # ⚠️⚠️ LE PIÈGE : DIAM_AN est une fraction de la LARGEUR,
            # mais _ay est une fraction de la HAUTEUR. La carte étant
            # deux fois plus large que haute, il faut CONVERTIR — sinon
            # la ficelle s'arrête bien trop tôt.
            _rayon_h = DIAM_AN * _RATIO_CHENILLE * 0.575 * 1.15
            _y2 = _py + (_ay + _rayon_h) * _ph
            if _y2 >= _y1:
                continue
            _dy = (_y2 - _y1)
            _ond = _pw * 0.006
            c.bezier(_x1, _y1,
                     _x1 - _ond, _y1 + _dy * 0.34,
                     _x2 + _ond, _y1 + _dy * 0.68,
                     _x2, _y2)
            # le petit nœud, là où la ficelle touche la bulle
            c.circle(_x2, _y2, _pw * 0.0045, stroke=1, fill=0)
    finally:
        c.restoreState()

    for _i, _val in enumerate(nums[:6]):
        _ax, _ay = ANNEAUX[_i]
        _nx = _px + _ax * _pw
        _ny = _py + _ay * _ph - _t_num * 0.34
        if _sec:
            _sec.chiffre_micro(c, _val, _nx, _ny, _t_num, gris_ch, police_ch)
        else:
            c.setFillColor(gris_ch)
            c.setFont(police_ch, _t_num)
            c.drawCentredString(_nx, _ny, str(_val))

    # ═══ 🎫 LE BANDEAU AUX BOUTS RONDS, en pied ═══
    _ligne = "N\u00b0 %05d" % serie
    if telephone:
        _ligne += "  \u00b7  " + telephone
    _t_l = 5.2
    while _t_l > 3.2 and _lg_t(_ligne, POLICE, _t_l) > CARD_W - 9.0 * mm:
        _t_l -= 0.25
    _bh = _t_l * 1.72
    _bw = min(_lg_t(_ligne, POLICE, _t_l) + _bh * 1.30, CARD_W - 2.0 * mm)
    _bx = x0 + (CARD_W - _bw) / 2
    _by = y0 + 0.5 * mm
    _plein = couleur_hex not in ("#9A9A9A", "#999999")
    c.setStrokeColor(col)
    c.setLineWidth(0.6)
    if _plein:
        c.setFillColor(col)
        c.roundRect(_bx, _by, _bw, _bh, _bh / 2.0, stroke=1, fill=1)
        c.setFillColor(colors.white)
    else:
        c.roundRect(_bx, _by, _bw, _bh, _bh / 2.0, stroke=1, fill=0)
        c.setFillColor(col)
    c.setFont(POLICE, _t_l)
    c.drawCentredString(x0 + CARD_W / 2, _by + _bh * 0.32, _ligne)


def generer_pdf(nb_cartes=18, serie_start=1, theme="", couleur=True,
                nom_evenement="", titre_jeu="", couleur_perso="", date_lieu="", telephone="",
                style="eco", evenement_id="", page_start=1):
    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=landscape(A4), pageCompression=1)

    nb_cartes = max(1, min(int(nb_cartes), 10000))
    par_page = COLS_PAGE * ROWS_PAGE
    nb_pages = (nb_cartes + par_page - 1) // par_page

    rng = random.Random(931800 + int(serie_start))
    serie = int(serie_start)
    # 📄 la page continue d'une rame à l'autre (sceau Maeva 12/08)
    no_page = max(1, int(page_start))
    faites = 0

    for _ in range(nb_pages):
        # en-tête de page
        if nom_evenement:
            c.setFillColor(colors.black); c.setFont(POLICE, 8)
            c.drawCentredString(PAGE_W / 2, PAGE_H - 4 * mm, nom_evenement)
        c.setFillColor(GRIS_CLAIR); c.setFont(POLICE, 6)
        c.drawCentredString(PAGE_W / 2, PAGE_H - 6.4 * mm, "%03d" % no_page)

        for row in range(ROWS_PAGE):
            for col_i in range(COLS_PAGE):
                if faites >= nb_cartes:
                    break
                x0 = MARGIN_X + col_i * (CARD_W + GUTTER_X)
                y0 = MARGIN_BOT + (ROWS_PAGE - 1 - row) * (CARD_H + GUTTER_Y)
                nums = _gen_carte(rng)
                coul = (couleur_perso if (couleur and couleur_perso)
                        else RAINBOW[(serie - 1) % len(RAINBOW)] if couleur else "#9A9A9A")
                _dessiner_carte(c, x0, y0, nums, coul, serie, titre_jeu, telephone,
                                style=style, evenement_id=evenement_id)
                serie += 1
                faites += 1

        c.showPage()
        no_page += 1

    c.save()
    buf.seek(0)
    return buf


if __name__ == "__main__":
    pdf = generer_pdf(nb_cartes=18, couleur=True,
                      nom_evenement="ASSOCIATION TE MANU", titre_jeu="Grand Loto",
                      telephone="87 04 32 21")
    with open("test_tahaa.pdf", "wb") as f:
        f.write(pdf.read())
    print("TAHAA généré")
