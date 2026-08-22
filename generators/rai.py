# -*- coding: utf-8 -*-
"""
MANAPRINT — Générateur RAI (format A4)
12 cartes par feuille A4 (3 colonnes × 4 rangées).
Chaque carte : en-tête « Le jeu RAI … » + « Carte N° 030001 »
(fidèle au modèle), puis une grille 3×3 de 8 BOULES par familles de DIX :
  colonne 1 = 30-39 (×3) · colonne 2 = 40-49 (×2) · colonne 3 = 50-59 (×3)
(numéros distincts par colonne, ordre LIBRE — fidèle au modèle)
La case CENTRALE est libérée pour le QR de vérification (décision Maeva).
Tirage compact 30-59 !
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
# Les 3 familles de DIX (fidèle au modèle)
COLONNES = [(30, 39), (40, 49), (50, 59)]

# ═══ ☁️ LES NEUF NUAGES (sceau Maeva 13/08) ═══
# « VOTRE JEU RAI — LE CIEL » : neuf nuages en 3×3, portés par un ciel de
# vent et de petits nuages. Ils remplacent les traits de grille.
# ⚠️ RAI n'a que HUIT boules : le nuage du CENTRE accueille donc le
# numéro de série — la case libérée trouve enfin son usage.
_RATIO_NUAGES = 0.9982
NUAGES = [[0.1907, 0.6921], [0.4993, 0.6979], [0.8077, 0.6899], [0.1919, 0.4454], [0.5006, 0.4478], [0.8089, 0.446], [0.1932, 0.1967], [0.5004, 0.1957], [0.8083, 0.1962]]
LARG_NU = 0.2909
HAUT_NU = 0.2321
import os as _os2
from reportlab.pdfbase.pdfmetrics import stringWidth as _lg_r


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


_IMAGE_NUAGES = _choisir_image("rai_nuages", _RATIO_NUAGES)


COLS_PAGE = 3
ROWS_PAGE = 4
MARGIN_X = 8 * mm
MARGIN_TOP = 10 * mm
MARGIN_BOT = 8 * mm
GUTTER_X = 4 * mm
GUTTER_Y = 4 * mm

CARD_W = (PAGE_W - 2 * MARGIN_X - (COLS_PAGE - 1) * GUTTER_X) / COLS_PAGE
CARD_H = (PAGE_H - MARGIN_TOP - MARGIN_BOT - (ROWS_PAGE - 1) * GUTTER_Y) / ROWS_PAGE
HDR_H = 11 * mm          # les deux lignes d'en-tête + le QR


def _gen_carte(rng):
    """8 boules : 3 + 2 + 3 distincts par famille de dix, ordre LIBRE.
    La colonne du milieu libère sa case centrale pour le QR (décision Maeva)."""
    return [rng.sample(range(pmin, pmax + 1), n)
            for (pmin, pmax), n in zip(COLONNES, (3, 2, 3))]


def _dessiner_carte(c, x0, y0, cols_nums, couleur_hex, serie, titre_jeu="", telephone="", style="eco", evenement_id=""):
    police_ch, gris_ch = _style_chiffres(style)
    col = colors.HexColor(couleur_hex)
    cell_w = CARD_W / 3

    # ⚠️⚠️ 13/08 : ni cadre, ni microtexte, ni QR — comme WIN, KAI, SUN, WIZ.

    # ═══ ☁️ LA PLAQUE AU CIEL ═══
    # ⚠️ PAS de preserveAspectRatio : on VEUT l'étirer pour qu'elle épouse
    # la carte. Les neuf nuages suivent, chacun à sa place.
    BANDE_PIED = 4.5 * mm
    _pw = CARD_W - 0.8 * mm
    _ph = CARD_H - 1.0 * mm - BANDE_PIED
    _px = x0 + (CARD_W - _pw) / 2
    _py = y0 + BANDE_PIED + 0.5 * mm
    if _os2.path.exists(_IMAGE_NUAGES):
        try:
            c.drawImage(_IMAGE_NUAGES, _px, _py, _pw, _ph, mask="auto")
        except Exception:
            pass

    # ⚠️ la taille se calcule DEPUIS le nuage, jamais en dur. Le nuage est
    # bombé : le chiffre ne peut occuper que son ventre, pas ses bords.
    _nw = _pw * LARG_NU
    _nh = _ph * HAUT_NU
    _t_num = 44.0
    while _t_num > 8 and (_lg_r("88", police_ch, _t_num) > _nw * 0.60
                          or _t_num * 0.72 > _nh * 0.56):
        _t_num -= 0.5

    # ═══ les HUIT numéros, dans leurs nuages ═══
    # ⚠️ cols_nums donne les COLONNES (3, 2, 3). On les range dans la
    # grille 3×3 en LAISSANT LE CENTRE LIBRE — il portera la série.
    _grille = [
        [cols_nums[0][0], cols_nums[1][0], cols_nums[2][0]],
        [cols_nums[0][1], None,            cols_nums[2][1]],
        [cols_nums[0][2], cols_nums[1][1], cols_nums[2][2]],
    ]
    for _r in range(3):
        for _c2 in range(3):
            _val = _grille[_r][_c2]
            if _val is None:
                continue
            _nx0, _ny0 = NUAGES[_r * 3 + _c2]
            _nx = _px + _nx0 * _pw
            _ny = _py + _ny0 * _ph - _t_num * 0.34
            if _sec:
                _sec.chiffre_micro(c, _val, _nx, _ny, _t_num, gris_ch, police_ch)
            else:
                c.setFillColor(gris_ch)
                c.setFont(police_ch, _t_num)
                c.drawCentredString(_nx, _ny, str(_val))

    # ⭐ LE NUAGE DU CENTRE porte le numéro de série
    _cx0, _cy0 = NUAGES[4]
    _t_s = _t_num * 0.44
    c.setFillColor(col)
    c.setFont(POLICE, _t_s)
    c.drawCentredString(_px + _cx0 * _pw, _py + _cy0 * _ph - _t_s * 0.34,
                        "N\u00b0 %05d" % serie)

    # ═══ 🎫 LE BANDEAU AUX BOUTS RONDS, en pied ═══
    _ligne = "RAI"
    if titre_jeu and titre_jeu.strip().upper() != "RAI":
        _ligne = titre_jeu.strip()
    if telephone:
        _ligne += "  \u00b7  " + telephone
    _t_l = 5.4
    while _t_l > 3.2 and _lg_r(_ligne, POLICE, _t_l) > CARD_W - 9.0 * mm:
        _t_l -= 0.25
    _bh = _t_l * 1.72
    _bw = min(_lg_r(_ligne, POLICE, _t_l) + _bh * 1.30, CARD_W - 2.0 * mm)
    _bx = x0 + (CARD_W - _bw) / 2
    _by = y0 + 0.7 * mm
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


def generer_pdf(nb_cartes=12, serie_start=1, theme="", couleur=True,
                nom_evenement="", titre_jeu="", couleur_perso="", date_lieu="", telephone="",
                style="eco", evenement_id="", page_start=1):
    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=A4, pageCompression=1)

    nb_cartes = max(1, min(int(nb_cartes), 10000))
    par_page = COLS_PAGE * ROWS_PAGE
    nb_pages = (nb_cartes + par_page - 1) // par_page

    rng = random.Random(937000 + int(serie_start))
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
                cols_nums = _gen_carte(rng)
                coul = (couleur_perso if (couleur and couleur_perso)
                        else RAINBOW[(serie - 1) % len(RAINBOW)] if couleur else "#9A9A9A")
                _dessiner_carte(c, x0, y0, cols_nums, coul, serie, titre_jeu, telephone,
                                style=style, evenement_id=evenement_id)
                serie += 1
                faites += 1

        c.showPage()
        no_page += 1

    c.save()
    buf.seek(0)
    return buf


if __name__ == "__main__":
    pdf = generer_pdf(nb_cartes=12, couleur=True,
                      nom_evenement="ASSOCIATION TE MANU", titre_jeu="Grand Loto",
                      telephone="89 22 23 05")
    with open("test_rai.pdf", "wb") as f:
        f.write(pdf.read())
    print("RAI généré")
