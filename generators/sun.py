# -*- coding: utf-8 -*-
"""
MANAPRINT — Générateur SUN 8 BOULES (format A4)
12 cartes par feuille A4 (3 colonnes × 4 rangées).
Chaque carte : grille 3×3. 8 numéros + 1 case vide (position aléatoire dans la
colonne du milieu). Numéro de série EN PIED sous la carte.
Colonnes : col1 = 1-8, col2 = 9-16, col3 = 17-24.
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
# (min, max) par colonne — SUN 8 boules
PLAGES = [(1, 8), (9, 16), (17, 24)]

# ═══ ☀️ LA PLAQUE AU SOLEIL (sceau Maeva 13/08) ═══
# « VOTRE JEU SUN — AVEC 8 BOULES » : un soleil rieur, et HUIT BULLES en
# couronne autour de lui, reliées par ses rayons.
# ⚠️ Les numéros ne se lisent plus en grille 3×3 mais EN COURONNE, comme
# le dessin le demande — mesuré au pixel sur l'image elle-même.
_RATIO_PLAQUE = 1.0
BULLES = [[0.496, 0.759], [0.239, 0.714], [0.132, 0.482], [0.193, 0.235], [0.489, 0.129], [0.792, 0.235], [0.853, 0.482], [0.746, 0.714]]
import os as _os2
from reportlab.pdfbase.pdfmetrics import stringWidth as _lg_s


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


_IMAGE_PLAQUE = _choisir_image("sun_plaque", _RATIO_PLAQUE)

COLS_PAGE = 3
ROWS_PAGE = 4
MARGIN_X = 8 * mm
MARGIN_TOP = 8 * mm
MARGIN_BOT = 8 * mm
GUTTER_X = 4 * mm
GUTTER_Y = 4 * mm

CARD_W = (PAGE_W - 2 * MARGIN_X - (COLS_PAGE - 1) * GUTTER_X) / COLS_PAGE
CARD_H = (PAGE_H - MARGIN_TOP - MARGIN_BOT - (ROWS_PAGE - 1) * GUTTER_Y) / ROWS_PAGE


def _gen_carte(rng):
    """8 numéros : col1 = 3 nums, col3 = 3 nums, col2 = 2 nums (1 case vide aléatoire).
    La case vide est dans la colonne du milieu, sur une rangée tirée au hasard."""
    col1 = sorted(rng.sample(range(PLAGES[0][0], PLAGES[0][1] + 1), 3))
    col3 = sorted(rng.sample(range(PLAGES[2][0], PLAGES[2][1] + 1), 3))
    col2_nums = sorted(rng.sample(range(PLAGES[1][0], PLAGES[1][1] + 1), 2))
    # position de la case vide dans la colonne du milieu (rangée 0, 1 ou 2)
    vide = 2  # case vide TOUJOURS en bas-milieu : elle accueille le QR de sécurité
    col2 = []
    it = iter(col2_nums)
    for r in range(3):
        col2.append(None if r == vide else next(it))
    grille = [
        [col1[0], col2[0], col3[0]],
        [col1[1], col2[1], col3[1]],
        [col1[2], col2[2], col3[2]],
    ]
    return grille


# 🎲 LES PETITS NUMÉROS EN VRAIS DÉS (sceau Maeva 30/07) : 1-6 = un dé à
# points ; 7, 8, 9 = DEUX dés dont les points s'additionnent (7=4+3, 8=4+4,
# 9=5+4) ; à partir de 10, le chiffre reste roi (un dé ne sait pas dire 47).
_DECOMP_DES = {7: (4, 3), 8: (4, 4), 9: (5, 4)}


def _un_de(c, cx, cy, t, valeur, col, gris_ch):
    """Un vrai dé : carré arrondi blanc bordé couleur, points gris disposés
    comme sur les dés du commerce."""
    r = t / 2.0
    c.setStrokeColor(col); c.setLineWidth(1.1)
    c.setFillColor(colors.white)
    c.roundRect(cx - r, cy - r, t, t, t * 0.18, stroke=1, fill=1)
    q = t * 0.26
    pos = {1: [(0, 0)], 2: [(-q, q), (q, -q)], 3: [(-q, q), (0, 0), (q, -q)],
           4: [(-q, q), (q, q), (-q, -q), (q, -q)],
           5: [(-q, q), (q, q), (0, 0), (-q, -q), (q, -q)],
           6: [(-q, q), (q, q), (-q, 0), (q, 0), (-q, -q), (q, -q)]}[valeur]
    c.setFillColor(gris_ch)
    for dx, dy in pos:
        c.circle(cx + dx, cy + dy, t * 0.085, stroke=0, fill=1)


def _dessine_des(c, valeur, cx, cy, col, gris_ch):
    if valeur <= 6:
        _un_de(c, cx, cy, 11.5 * mm, valeur, col, gris_ch)
    else:
        a, b = _DECOMP_DES[valeur]
        _un_de(c, cx - 4.4 * mm, cy, 7.8 * mm, a, col, gris_ch)
        _un_de(c, cx + 4.4 * mm, cy, 7.8 * mm, b, col, gris_ch)


def _dessiner_carte(c, x0, y0, grille, couleur_hex, serie, titre_jeu="", telephone="", style="eco", evenement_id="", des=False):
    police_ch, gris_ch = _style_chiffres(style)
    col = colors.HexColor(couleur_hex)
    ncols = 3

    # Bordure carte
    c.setStrokeColor(col); c.setLineWidth(0.8)
    # ═══ ☀️ LA PLAQUE N'EST QUE POUR SUN NORMAL (sceau Maeva 13/08) ═══
    # ⚠️⚠️ « ce travail seulement pour le SUN normale ». SUN CASINO
    # (des=True) garde son ANCIEN visage : son cadre, sa grille 3×3 à
    # traits, ses dés, son QR et son microtexte.
    _plaque = not des

    if not _plaque:
        # ⚠️ SUN CASINO : sa bordure et sa protection, comme avant
        c.setStrokeColor(col); c.setLineWidth(0.8)
        c.roundRect(x0, y0, CARD_W, CARD_H, 1.5 * mm, stroke=1, fill=0)
        if _sec:
            _sec.cadre_micro(c, x0, y0, CARD_W, CARD_H, serie, retrait=1.0 * mm)
        # son en-tête d'origine
        _hdr = y0 + CARD_H - 4 * mm
        _t = "SUN 8 boules"
        if titre_jeu and titre_jeu.strip().upper() != _t.upper():
            _t += "  \u2014  " + titre_jeu.strip()
        if telephone:
            _t += " " + telephone
        c.setFillColor(col); c.setFont(POLICE, 5.5)
        c.drawCentredString(x0 + CARD_W / 2, _hdr, _t[:60])
        # sa grille 3×3 à traits
        _gt = _hdr - 2.5 * mm
        _gb = y0 + 5.5 * mm
        _cw = CARD_W / 3
        _rh = (_gt - _gb) / 3
        c.setStrokeColor(GRIS_CLAIR); c.setLineWidth(0.3)
        for _i in range(1, 3):
            c.line(x0 + _i * _cw, _gb, x0 + _i * _cw, _gt)
            c.line(x0 + 1.5 * mm, _gt - _i * _rh, x0 + CARD_W - 1.5 * mm, _gt - _i * _rh)
        # ses chiffres (ou ses dés) dans les neuf cases
        for _r in range(3):
            for _c2 in range(3):
                _v = grille[_r][_c2]
                if _v is None:
                    continue
                _cx = x0 + (_c2 + 0.5) * _cw
                _cy = _gt - (_r + 0.5) * _rh
                if des and _v <= 9:
                    _dessine_des(c, _v, _cx, _cy, col, gris_ch)
                elif _sec:
                    _sec.chiffre_micro(c, _v, _cx, _cy - 11, 32, gris_ch, police_ch)
                else:
                    c.setFillColor(gris_ch); c.setFont(police_ch, 32)
                    c.drawCentredString(_cx, _cy - 11, str(_v))
        # son QR dans la case vide du bas-milieu
        if _sec and evenement_id:
            try:
                _q = 12.5 * mm
                _sec.carton_qr(c, x0 + 1.5 * _cw - _q / 2, _gb + _rh / 2 - _q / 2,
                               _q, evenement_id, serie)
            except Exception:
                pass
        # son pied
        c.setFillColor(GRIS_CLAIR); c.setFont(POLICE, 4.5)
        c.drawString(x0 + 2 * mm, y0 + 2 * mm, "N\u00b0 S\u00c9RIE")
        c.setFillColor(col); c.setFont(POLICE, 7)
        c.drawRightString(x0 + CARD_W - 2 * mm, y0 + 2 * mm, "%06d" % serie)
        return

    # ⚠️ SUN NORMAL : ni cadre, ni microtexte, ni QR. Le carton est net.

    # ═══ ☀️ LA PLAQUE AU SOLEIL, ET SES HUIT BULLES ═══
    # ⚠️ PAS de preserveAspectRatio : on VEUT l'étirer pour qu'elle épouse
    # la carte. Les huit bulles suivent, chacune à sa place.
    # ⚠️ 13/08 : une bande est RÉSERVÉE en bas pour le bandeau, sinon il
    # couvrait la bulle du bas. La plaque monte d'autant.
    BANDE_PIED = 5.0 * mm
    _pw = CARD_W - 0.8 * mm
    _ph = CARD_H - 1.0 * mm - BANDE_PIED
    _px = x0 + (CARD_W - _pw) / 2
    _py = y0 + BANDE_PIED + 0.5 * mm
    if _os2.path.exists(_IMAGE_PLAQUE):
        try:
            c.drawImage(_IMAGE_PLAQUE, _px, _py, _pw, _ph, mask="auto")
        except Exception:
            pass

    # ⚠️ la taille se calcule DEPUIS la bulle : deux bulles voisines sont
    # séparées d'environ 0,24 de la largeur, le chiffre ne doit pas
    # déborder de la sienne.
    # ⚠️ la bulle mesure 0,158 de la largeur de la plaque. Le chiffre doit
    # tenir DEDANS : « 88 » ne peut pas dépasser 0,74 du diamètre, et sa
    # hauteur 0,58 — sinon il déborde par le haut, comme le « 3 » l'a fait.
    _dia = _pw * 0.2388
    _t_num = 30.0
    while _t_num > 6 and (_lg_s("88", police_ch, _t_num) > _dia * 0.74
                          or _t_num * 0.72 > _dia * 0.58):
        _t_num -= 0.5

    # ═══ les HUIT numéros, dans leurs bulles ═══
    # On aplatit la grille (elle porte 8 numéros et une case vide) et on
    # les pose dans l'ordre de la couronne, en partant du bas.
    _plat = [v for rang in grille for v in rang if v is not None]
    for _i, _val in enumerate(_plat[:8]):
        _bx, _by = BULLES[_i]
        _nx = _px + _bx * _pw
        _ny = _py + _by * _ph - _t_num * 0.34
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
    _t_l = 5.4
    while _t_l > 3.2 and _lg_s(_ligne, POLICE, _t_l) > CARD_W - 9.0 * mm:
        _t_l -= 0.25
    _bh = _t_l * 1.72
    _bw = min(_lg_s(_ligne, POLICE, _t_l) + _bh * 1.30, CARD_W - 2.0 * mm)
    _bbx = x0 + (CARD_W - _bw) / 2
    _bby = y0 + 0.8 * mm
    _plein = couleur_hex not in ("#9A9A9A", "#999999")
    c.setStrokeColor(col)
    c.setLineWidth(0.6)
    if _plein:
        c.setFillColor(col)
        c.roundRect(_bbx, _bby, _bw, _bh, _bh / 2.0, stroke=1, fill=1)
        c.setFillColor(colors.white)
    else:
        c.roundRect(_bbx, _bby, _bw, _bh, _bh / 2.0, stroke=1, fill=0)
        c.setFillColor(col)
    c.setFont(POLICE, _t_l)
    c.drawCentredString(x0 + CARD_W / 2, _bby + _bh * 0.32, _ligne)


def generer_pdf(nb_cartes=12, serie_start=1, theme="", couleur=True,
                nom_evenement="", titre_jeu="", couleur_perso="", date_lieu="", telephone="",
                style="eco", evenement_id="", des=False, page_start=1):
    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=A4, pageCompression=1)

    nb_cartes = max(1, min(int(nb_cartes), 10000))
    par_page = COLS_PAGE * ROWS_PAGE
    nb_pages = (nb_cartes + par_page - 1) // par_page

    rng = random.Random(500000 + int(serie_start))
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
                _dessiner_carte(c, x0, y0, grille, coul, serie, titre_jeu, telephone, style=style, evenement_id=evenement_id, des=des)
                serie += 1
                faites += 1

        c.showPage()
        no_page += 1

    c.save()
    buf.seek(0)
    return buf


def generer_pdf_casino(**kw):
    """🎲 SUN CASINO — le jumeau où les numéros 1-9 vivent en vrais dés."""
    kw["des"] = True
    return generer_pdf(**kw)


if __name__ == "__main__":
    pdf = generer_pdf(nb_cartes=12, couleur=True,
                      nom_evenement="ASSOCIATION TE MANU", titre_jeu="Le jeux SUN pour 8 boules",
                      telephone="89.22.23.05")
    with open("test_sun.pdf", "wb") as f:
        f.write(pdf.read())
    print("SUN 8 boules généré")
