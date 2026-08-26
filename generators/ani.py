# -*- coding: utf-8 -*-
"""
MANAPRINT — Générateur TEAHUPOO (format A4)

🌊 REBAPTISÉ LE 14/08 (sceau Maeva) : l'ancien « ANI » devient TEAHUPOO.
Une surfeuse dans la vague, l'écume tout autour, et neuf bulles
numérotées de 1 à 9.

RÈGLE INCHANGÉE : neuf numéros, trois par lettre —
  A : 61-70 · N : 71-80 · I : 81-90
⚠️ Ce sont les dizaines hautes, fidèles au modèle d'origine.

8 cartes par feuille A4 (2 colonnes × 4 rangées).
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
LETTRES = "ANI"
# (min, max) par lettre — A N I (les dizaines hautes)
PLAGES = [(61, 70), (71, 80), (81, 90)]

# ═══ 🌊 LA VAGUE ET SES NEUF BULLES (sceau Maeva 14/08) ═══
# « TEAHUPOO — 9 BOULES » : une surfeuse dans le tube, l'écume partout,
# et neuf bulles numérotées de 1 à 9 par des pastilles noires.
# ⚠️ L'ORDRE suit les pastilles : 3 en haut · 4 au milieu · 2 en bas.
_RATIO_VAGUE = 1.5018
BULLES = [[0.363, 0.6294], [0.5181, 0.6295], [0.6729, 0.6293], [0.2871, 0.4157], [0.4407, 0.4156], [0.5987, 0.4156], [0.7536, 0.4155], [0.3985, 0.1949], [0.65, 0.1946]]
LARG_BULLE = 0.1166
HAUT_BULLE = 0.1832
import os as _os2
from reportlab.pdfbase.pdfmetrics import stringWidth as _lg_te


def _choisir_image(motif_img, ratio_attendu):
    """🛟 Retrouve le dessin, quel que soit son nom de fichier."""
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


_IMAGE_VAGUE = _choisir_image("teahu_vague", _RATIO_VAGUE)


# ⚠️ 14/08 : le dessin est en PAYSAGE (ratio 1,50) — on passe de 12 cartes
# à 8 cartes-plaques (2 colonnes × 4 rangées).
COLS_PAGE = 2
ROWS_PAGE = 4
MARGIN_X = 8 * mm
MARGIN_TOP = 10 * mm
MARGIN_BOT = 8 * mm
GUTTER_X = 4 * mm
GUTTER_Y = 4 * mm

CARD_W = (PAGE_W - 2 * MARGIN_X - (COLS_PAGE - 1) * GUTTER_X) / COLS_PAGE
CARD_H = (PAGE_H - MARGIN_TOP - MARGIN_BOT - (ROWS_PAGE - 1) * GUTTER_Y) / ROWS_PAGE
HDR_H = 6 * mm           # bande d'en-tête T | E | A
PIED_H = 4.4 * mm        # bande N° SERIE
ZONE_QR_H = 15 * mm      # bande basse réservée au QR de vérification


def _gen_carte(rng):
    """9 numéros : 3 par lettre, chacun dans sa plage, empilés triés."""
    return [sorted(rng.sample(range(pmin, pmax + 1), 3)) for pmin, pmax in PLAGES]


def _dessiner_carte(c, x0, y0, cols_nums, couleur_hex, serie, titre_jeu="", telephone="", style="eco", evenement_id=""):
    police_ch, gris_ch = _style_chiffres(style)
    col = colors.HexColor(couleur_hex)

    # ⚠️⚠️ 14/08 : ni cadre, ni microtexte, ni QR — comme les autres jeux
    # habillés. Maeva veut le carton net.

    # ═══ 🌊 LA PLAQUE À LA VAGUE ═══
    # ⚠️ PAS de preserveAspectRatio : on VEUT l'étirer pour qu'elle épouse
    # la carte. Les neuf bulles suivent, chacune à sa place.
    _pw = CARD_W - 0.6 * mm
    _ph = CARD_H - 0.6 * mm
    _px = x0 + (CARD_W - _pw) / 2
    _py = y0 + 0.3 * mm
    if _os2.path.exists(_IMAGE_VAGUE):
        try:
            c.drawImage(_IMAGE_VAGUE, _px, _py, _pw, _ph, mask="auto")
        except Exception:
            pass

    # ⭐⭐ LA POLICE DES CHIFFRES : « Helvetica-Bold » (sceau Maeva 14/08).
    # Le secret n'est pas la taille, c'est LE GRAS — 58 % de chair contre
    # 24 % pour DJLECO : les chiffres se voient de loin.
    _POLICE_NUM = "Helvetica-Bold"
    _lg_b = _pw * LARG_BULLE
    _ht_b = _ph * HAUT_BULLE
    _t_num = 34.0
    while _t_num > 6 and (_lg_te("88", _POLICE_NUM, _t_num) > _lg_b * 0.86
                          or _t_num * 0.72 > _ht_b * 0.58):
        _t_num -= 0.5

    # ═══ les NEUF numéros, dans les bulles de la vague ═══
    # ⚠️ `carte` donne trois colonnes A · N · I de trois numéros triés.
    # On les aplatit dans l'ordre des pastilles 1 à 9.
    _plat = [v for colonne in cols_nums for v in colonne]
    for _k, _n in enumerate(_plat[:9]):
        _bx, _by = BULLES[_k]
        _nx = _px + _bx * _pw
        _ny = _py + _by * _ph - _t_num * 0.34
        if _sec:
            _sec.chiffre_micro(c, _n, _nx, _ny, _t_num, gris_ch, _POLICE_NUM)
        else:
            c.setFillColor(gris_ch)
            c.setFont(_POLICE_NUM, _t_num)
            c.drawCentredString(_nx, _ny, str(_n))

    # ═══ 🎫 LE BANDEAU, au PIED de la carte ═══
    # ⚠️ la pastille « 9 BOULES » du dessin est trop courte : le numéro de
    # série la chevauchait. On l'écrit donc au pied, dans sa propre
    # pastille aux bouts ronds.
    _bl = "N\u00b0 %05d" % serie
    if telephone:
        _bl += "   \u2605   " + telephone
    _tb = 7.5
    while _tb > 3.4 and _lg_te(_bl, "Helvetica-Bold", _tb) > _pw * 0.30:
        _tb -= 0.25
    _bh = _tb * 1.68
    _bw = _lg_te(_bl, "Helvetica-Bold", _tb) + _bh * 1.4
    _bx = _px + _pw * 0.520 - _bw / 2
    _by = _py + _ph * 0.022
    c.setStrokeColor(gris_ch); c.setLineWidth(0.7)
    c.setFillColor(colors.white)
    c.roundRect(_bx, _by, _bw, _bh, _bh / 2.0, stroke=1, fill=1)
    c.setFillColor(gris_ch)
    c.setFont("Helvetica-Bold", _tb)
    c.drawCentredString(_px + _pw * 0.520, _by + _bh * 0.30, _bl)


def generer_pdf(nb_cartes=12, serie_start=1, theme="", couleur=True,
                nom_evenement="", titre_jeu="", couleur_perso="", date_lieu="", telephone="",
                style="eco", evenement_id="", page_start=1):
    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=A4, pageCompression=1)

    nb_cartes = max(1, min(int(nb_cartes), 10000))
    par_page = COLS_PAGE * ROWS_PAGE
    nb_pages = (nb_cartes + par_page - 1) // par_page

    rng = random.Random(931100 + int(serie_start))
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
                      telephone="89.22.23.05")
    with open("test_ani.pdf", "wb") as f:
        f.write(pdf.read())
    print("ANI généré")
