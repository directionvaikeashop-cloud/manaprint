# -*- coding: utf-8 -*-
"""
MANAPRINT — Générateur LOSANGE (format A4)
6 losanges/page (2×3) — 8 numéros par carte : flanc gauche 3 triés 1-30,
flanc droit 3 triés 46-75, haut+bas 2 triés 31-45. Texte central, QR, microtexte.
QR de sécurité · série · microtexte · Tèl par défaut 89 22 23 05.
"""
import io
import math
import random
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

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

RAINBOW = ["#E53935", "#FB8C00", "#F9A825", "#43A047", "#00ACC1",
           "#1E88E5", "#3949AB", "#8E24AA", "#D81B60", "#6D4C41"]
GRIS_CLAIR = colors.Color(0.80, 0.80, 0.80)
PALE = colors.Color(0.86, 0.86, 0.86)
PALE2 = colors.Color(0.90, 0.90, 0.90)

try:
    pdfmetrics.registerFont(TTFont("DJLECO", "/usr/share/fonts/truetype/dejavu/DejaVuSans-ExtraLight.ttf"))
    _POLICE_ECO = "DJLECO"
except Exception:
    _POLICE_ECO = "Helvetica"
_GRIS_ECO = colors.Color(0.50, 0.50, 0.50)


def _style_chiffres(style):
    if str(style).lower() in ("p15", "premium"):
        return "Helvetica-Bold", colors.Color(0.55, 0.55, 0.55)
    return _POLICE_ECO, _GRIS_ECO


PAGE_W, PAGE_H = A4
# ═══ 🔷 LE DAMIER DE HUIT LOSANGES (sceau Maeva 14/08) ═══
# « LOSANGE » : huit losanges en damier, chacun coiffé de SA LETTRE —
# B · I · I · N en haut, N · G · G · O en bas.
# ⭐ Ces lettres tombent EXACTEMENT sur la règle du jeu :
#   B + I + I  = les 3 numéros de 1-30  (le flanc gauche)
#   N + N      = les 2 numéros de 31-45 (le haut et le bas)
#   G + G + O  = les 3 numéros de 46-75 (le flanc droit)
_RATIO_LOSANGE = 1.5018
LOSANGES = [(0.249, 0.5951), (0.4356, 0.5949), (0.619, 0.5947), (0.8042, 0.5946), (0.2463, 0.253), (0.4376, 0.2525), (0.6207, 0.2524), (0.8073, 0.2503)]
LARG_LOS = 0.1494
HAUT_LOS = 0.2232
import os as _os2
from reportlab.pdfbase.pdfmetrics import stringWidth as _lg_lo


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


_IMAGE_LOSANGE = _choisir_image("losange_huit", _RATIO_LOSANGE)


# ⚠️ 14/08 : le dessin est en PAYSAGE (ratio 1,50) — on passe de 6 cartes
# à 8 cartes-plaques (2 colonnes × 4 rangées).
COLS_PAGE = 2
ROWS_PAGE = 4
MARGIN_X = 8 * mm
MARGIN_TOP = 9 * mm
MARGIN_BOT = 8 * mm
GUTTER_X = 4 * mm
GUTTER_Y = 4 * mm
CARD_W = (PAGE_W - 2 * MARGIN_X - (COLS_PAGE - 1) * GUTTER_X) / COLS_PAGE
CARD_H = (PAGE_H - MARGIN_TOP - MARGIN_BOT - (ROWS_PAGE - 1) * GUTTER_Y) / ROWS_PAGE

NB_NUMS = 8
TAILLE_CHIFFRE = 32
# positions en fraction de carte : (fx, fy) — haut, fg1, fd1, g, d, fg2, fd2, bas
POS = [(0.50, 0.770), (0.315, 0.615), (0.685, 0.615), (0.185, 0.465), (0.815, 0.465),
       (0.325, 0.330), (0.675, 0.330), (0.50, 0.180)]


def _gen_nums(rng):
    """8 numéros : gauche 3 triés 1-30, droite 3 triés 46-75, haut+bas 2 triés 31-45."""
    g = sorted(rng.sample(range(1, 31), 3))
    d = sorted(rng.sample(range(46, 76), 3))
    n = sorted(rng.sample(range(31, 46), 2))
    #      haut  fg1   fd1   g     d     fg2   fd2   bas
    return [n[0], g[0], d[0], g[1], d[1], g[2], d[2], n[1]]


def _dessiner_carte(c, x0, y0, nums, couleur_hex, serie, titre_jeu="", telephone="", style="eco", evenement_id=""):
    police_ch, gris_ch = _style_chiffres(style)
    col = colors.HexColor(couleur_hex)

    # ⚠️⚠️ 14/08 : ni cadre, ni microtexte, ni QR — comme les autres jeux
    # habillés. Maeva veut le carton net.

    # ═══ 🔷 LA PLAQUE AU DAMIER ═══
    # ⚠️ PAS de preserveAspectRatio : on VEUT l'étirer pour qu'elle épouse
    # la carte. Les huit losanges suivent, chacun à sa place.
    _pw = CARD_W - 0.6 * mm
    _ph = CARD_H - 0.6 * mm
    _px = x0 + (CARD_W - _pw) / 2
    _py = y0 + 0.3 * mm
    if _os2.path.exists(_IMAGE_LOSANGE):
        try:
            c.drawImage(_IMAGE_LOSANGE, _px, _py, _pw, _ph, mask="auto")
        except Exception:
            pass

    # ⭐⭐ LA POLICE DES CHIFFRES : « Helvetica-Bold » (sceau Maeva 14/08).
    # Le secret n'est pas la taille, c'est LE GRAS — 58 % de chair contre
    # 24 % pour DJLECO : les chiffres se voient de loin.
    # ⚠️ un LOSANGE se resserre vers ses pointes : le chiffre ne peut
    #    occuper que sa TAILLE, la bande large du milieu.
    _POLICE_NUM = "Helvetica-Bold"
    _lg_l = _pw * LARG_LOS
    _ht_l = _ph * HAUT_LOS
    _t_num = 34.0
    while _t_num > 6 and (_lg_lo("88", _POLICE_NUM, _t_num) > _lg_l * 0.62
                          or _t_num * 0.72 > _ht_l * 0.44):
        _t_num -= 0.5

    # ═══ les HUIT numéros, dans les losanges du damier ═══
    # ⚠️ `nums` arrive dans l'ordre : haut · fg1 · fd1 · g · d · fg2 · fd2 · bas
    # On le range sur les lettres du dessin : B·I·I·N (haut) · N·G·G·O (bas)
    #   B = fg1 · I = fg2 · I = g   · N = haut
    #   N = bas · G = fd1 · G = fd2 · O = d
    _h, _fg1, _fd1, _g, _d, _fg2, _fd2, _b = nums
    _plat = [_fg1, _fg2, _g, _h, _b, _fd1, _fd2, _d]
    for _k, _n in enumerate(_plat[:8]):
        _bx, _by = LOSANGES[_k]
        _nx = _px + _bx * _pw
        _ny = _py + _by * _ph - _t_num * 0.34
        if _sec:
            _sec.chiffre_micro(c, _n, _nx, _ny, _t_num, gris_ch, _POLICE_NUM)
        else:
            c.setFillColor(gris_ch)
            c.setFont(_POLICE_NUM, _t_num)
            c.drawCentredString(_nx, _ny, str(_n))

    # ═══ 🎫 LE BANDEAU, écrit dans sa pastille (déjà creuse au dessin) ═══
    c.setFillColor(gris_ch)
    _bl = "N\u00b0 %05d" % serie
    if telephone:
        _bl += "        \u2605        " + telephone
    _tb = 9.0
    while _tb > 3.4 and _lg_lo(_bl, "Helvetica-Bold", _tb) > _pw * 0.44:
        _tb -= 0.25
    c.setFont("Helvetica-Bold", _tb)
    c.drawCentredString(_px + _pw * 0.520, _py + _ph * 0.042, _bl)


def generer_pdf(nb_cartes=6, serie_start=1, theme="", couleur=True,
                nom_evenement="", titre_jeu="", couleur_perso="", date_lieu="", telephone="",
                style="eco", evenement_id="", motif="", page_start=1):
    telephone = (telephone or "").strip() or "89 22 23 05"
    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=A4, pageCompression=1)
    nb_cartes = max(1, min(int(nb_cartes), 10000))
    par_page = COLS_PAGE * ROWS_PAGE
    nb_pages = (nb_cartes + par_page - 1) // par_page
    rng = random.Random(979000 + int(serie_start))
    serie = int(serie_start)
    # 📄 la page continue d'une rame à l'autre (sceau Maeva 12/08)
    no_page = max(1, int(page_start))
    faites = 0
    for _ in range(nb_pages):
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
                nums = _gen_nums(rng)
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
    pdf = generer_pdf(nb_cartes=6, couleur=True, nom_evenement="TEST", telephone="89.22.23.05")
    with open("test_losange.pdf", "wb") as f:
        f.write(pdf.read())
    print("LOSANGE généré")
