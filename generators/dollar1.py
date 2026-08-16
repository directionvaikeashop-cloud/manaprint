# -*- coding: utf-8 -*-
"""
MANAPRINT — Générateur 1 DOLLAR (format A4)

💵 NÉ LE 13/08 (sceau Maeva) : LE BILLET D'UN DOLLAR. Son cadre gravé —
« FEDERAL RESERVE NOTE », les quatre « 1 » dans leurs médaillons, les
rameaux — occupe le carton, et les NEUF numéros se rangent dedans.

RÈGLE, relevée sur la planche de Maeva :
  • QUATRE colonnes de deux : 1-15 · 16-30 · 46-60 · 61-75
  • UN numéro au CENTRE : 31-45
Ils se lisent en deux rangées de quatre, le centre entre les deux —
la même croix que le loto, en plus resserré.

10 billets par feuille A4 (2 colonnes × 5 rangées).
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


import os as _os
_PIECE_IMG = None


def _charger_piece():
    """La pièce de 100 francs de Maeva (découpée en disque), pâlie une fois
    pour que le chiffre reste roi. Anti-panne : boule à double cercle."""
    global _PIECE_IMG
    if _PIECE_IMG is not None:
        return _PIECE_IMG
    try:
        from PIL import Image as _Image
        chemin = _os.path.join(_os.path.dirname(_os.path.abspath(__file__)), "francs_piece.png")
        brut = _Image.open(chemin)
        if brut.mode in ("RGBA", "LA", "P"):
            brut = brut.convert("RGBA")
            fondb = _Image.new("RGBA", brut.size, (255, 255, 255, 255))
            brut = _Image.alpha_composite(fondb, brut)
        img = brut.convert("L")
        img = img.point(lambda p: int(255 - (255 - p) * 0.34))
        _PIECE_IMG = img.convert("RGB")
    except Exception:
        _PIECE_IMG = False
    return _PIECE_IMG


PAGE_W, PAGE_H = A4
# 💵 LE BILLET DE MAEVA — les numéros vivent dans son vide central.
_RATIO_BILLET = 1.8713
ZONE = (0.145, 0.855, 0.215, 0.8)   # x0, x1, y0, y1
# 💵 les quatre colonnes du billet, et son centre
COLONNES1D = [(1, 15), (16, 30), (46, 60), (61, 75)]
CENTRE1D = (31, 45)
import os as _os2
from reportlab.pdfbase.pdfmetrics import stringWidth as _lg5


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


# ⚡ 13/08 (sceau Maeva : « un gras gris pour économiser du toner ») :
# ⚠️ les CHIFFRES étaient déjà en gris 50 % — les éclaircir n'aurait rendu
# que 0,29 point. Le vrai gisement était LE DESSIN : à lui seul il coûtait
# 3,99 % sur les 4,28 % de la planche (les fibres du corail, les fleurs,
# le rameur). Il a donc été ÉCLAIRCI dans l'image (facteur 0,42 → 0,28) :
# l'encre du billet tombe à 2,74 % et le relief reste net.
_IMAGE_BILLET = _choisir_image("billet1d", _RATIO_BILLET)

# ⭐ LA POLICE QUI GROSSIT : condensée grasse — plus étroite qu'une grasse
# ordinaire, donc elle monte plus haut à place égale.
_POLICE_GROS = ""
try:
    from reportlab.pdfbase import pdfmetrics as _pm5
    from reportlab.pdfbase.ttfonts import TTFont as _TF5
    _pm5.registerFont(_TF5("D1GROS",
        "/usr/share/fonts/truetype/dejavu/DejaVuSansCondensed-Bold.ttf"))
    _POLICE_GROS = "D1GROS"
except Exception:
    _POLICE_GROS = ""


def _gen_billet(rng):
    """💵 Les neuf numéros : deux par colonne, un au centre.

    ⚠️ Les deux numéros d'une colonne sont TRIÉS : le plus petit en haut,
    le plus grand en bas — c'est ce que montre la planche de Maeva.
    """
    haut, bas = [], []
    for pmin, pmax in COLONNES1D:
        deux = sorted(rng.sample(range(pmin, pmax + 1), 2))
        haut.append(deux[0])
        bas.append(deux[1])
    centre = rng.randint(CENTRE1D[0], CENTRE1D[1])
    return haut, centre, bas


COLS_PAGE = 2
ROWS_PAGE = 5            # 10 billets par feuille (sceau Maeva 13/08)
MARGIN_X = 8 * mm
MARGIN_TOP = 9 * mm
MARGIN_BOT = 8 * mm
GUTTER_X = 4 * mm
GUTTER_Y = 4 * mm
CARD_W = (PAGE_W - 2 * MARGIN_X - (COLS_PAGE - 1) * GUTTER_X) / COLS_PAGE
CARD_H = (PAGE_H - MARGIN_TOP - MARGIN_BOT - (ROWS_PAGE - 1) * GUTTER_Y) / ROWS_PAGE

NB_NUMS = 7
# le billet modèle YAKARI (47/67 haut · 49/84/71 milieu · 50/75 bas) :
# colonne GAUCHE = 3 triés dans 46-60 (haut, milieu, bas), colonne DROITE =
# 3 triés dans 61-75 (haut, milieu, bas), CENTRE = 1 dans 76-90
POSITIONS = [(0.22, 0.73), (0.22, 0.47), (0.22, 0.21), (0.78, 0.73), (0.78, 0.47), (0.78, 0.21), (0.50, 0.47)]
PIECE_MM = 16.0        # diamètre de chaque pièce de 100 F
MEDAILLON_MM = 4.9     # rayon du médaillon blanc au coeur de la pièce
TAILLE_CHIFFRE = 19


def _dessiner_carte(c, x0, y0, nums, couleur_hex, serie, titre_jeu="", telephone="", style="eco", evenement_id=""):
    police_ch, gris_ch = _style_chiffres(style)
    col = colors.HexColor(couleur_hex)

    # ═══ 💵 LE BILLET DE CINQ CENTS FRANCS ═══
    # Le dessin de Maeva occupe tout le carton ; les dix numéros se
    # rangent dans son grand vide central, en deux rangées de cinq.
    haut, centre, bas = nums
    iw = CARD_W - 1.5 * mm
    ih = iw / _RATIO_BILLET
    if ih > CARD_H - 1.5 * mm:
        ih = CARD_H - 1.5 * mm
        iw = ih * _RATIO_BILLET
    px = x0 + (CARD_W - iw) / 2
    py = y0 + (CARD_H - ih) / 2
    if _os2.path.exists(_IMAGE_BILLET):
        try:
            c.drawImage(_IMAGE_BILLET, px, py, iw, ih, mask="auto",
                        preserveAspectRatio=True)
        except Exception:
            pass

    # la zone libre du billet
    zx = px + ZONE[0] * iw
    zw = (ZONE[1] - ZONE[0]) * iw
    zy = py + ZONE[2] * ih
    zh = (ZONE[3] - ZONE[2]) * ih

    # ⚠️ le chiffre se cale sur SA case : cinq par rangée, deux rangées,
    # et une bande au milieu pour le numéro de série.
    # ⚠️ QUATRE numéros par rangée, plus le centre entre les deux — mais
    # le centre mord sur la largeur : on réserve sa colonne au milieu.
    LARG_CENTRE = zw * 0.16
    place = (zw - LARG_CENTRE) / 4.0
    etage = zh / 2.6
    # ⭐ 13/08 (sceau Maeva : « cherche une écriture qui donne un effet de
    # chiffre grossi ») : LA CONDENSÉE GRASSE, ÉTIRÉE EN HAUTEUR.
    # C'est la LARGEUR qui bride ce billet — cinq numéros par rangée dans
    # 59 mm. La condensée est plus étroite (25 pt au lieu de 22,5), et il
    # restait 9,7 mm de hauteur pour 6,3 utilisés : on étire donc le
    # chiffre verticalement. Il paraît bien plus gros SANS prendre un
    # millimètre de large en plus.
    ETIRE = 1.55
    police_ch = _POLICE_GROS or police_ch
    taille = 30.0
    while taille > 7 and (_lg5("88", police_ch, taille) > place * 0.80
                          or taille * 0.72 * ETIRE > etage * 0.94):
        taille -= 0.5

    y_haut = zy + zh - etage * 0.62 - taille * 0.34
    y_bas = zy + etage * 0.42 - taille * 0.34
    # les deux rangées de quatre, le centre les écartant au milieu
    for etg, ys in ((haut, y_haut), (bas, y_bas)):
        for k, n in enumerate(etg):
            # les deux de gauche collés à gauche, les deux de droite à droite
            if k < 2:
                nx = zx + (k + 0.5) * place
            else:
                nx = zx + LARG_CENTRE + (k + 0.5) * place
            c.saveState()
            try:
                c.translate(nx, ys)
                c.scale(1.0, ETIRE)
                if _sec:
                    _sec.chiffre_micro(c, n, 0, 0, taille, gris_ch, police_ch)
                else:
                    c.setFillColor(gris_ch)
                    c.setFont(police_ch, taille)
                    c.drawCentredString(0, 0, str(n))
            finally:
                c.restoreState()

    # 🎯 LE NUMÉRO DU CENTRE — plus petit, entre les deux rangées, comme
    # sur la planche de Maeva. Il ne prend qu'une taille réduite : sa
    # place est étroite, et il doit rester lisible sans écraser les autres.
    t_c = taille * 0.74
    cx_c = zx + 2 * place + LARG_CENTRE / 2
    cy_c = zy + zh / 2 - t_c * 0.34
    c.saveState()
    try:
        c.translate(cx_c, cy_c)
        c.scale(1.0, ETIRE)
        if _sec:
            _sec.chiffre_micro(c, centre, 0, 0, t_c, gris_ch, police_ch)
        else:
            c.setFillColor(gris_ch)
            c.setFont(police_ch, t_c)
            c.drawCentredString(0, 0, str(centre))
    finally:
        c.restoreState()

    # 🎫 le numéro de série, au pied du billet
    # ⚠️ 13/08 : il était au CENTRE et écrasait le neuvième numéro — sur
    # ce billet, le centre appartient au chiffre, pas à la série.
    c.setFillColor(col)
    c.setFont(POLICE, 5.0)
    c.drawString(px + iw * 0.055, py + ih * 0.055, "N\u00b0 %05d" % serie)

    # le téléphone, discret sous le billet
    if telephone:
        c.setFillColor(colors.Color(0.55, 0.55, 0.55))
        c.setFont(POLICE, 4.4)
        c.drawString(px + 2.0 * mm, py + 1.0 * mm, telephone)

    # 🎯 le QR, dans le coin bas-droit du vide central
    if _sec and evenement_id:
        try:
            # ⚠️ 13/08 : le QR mangeait le dernier numéro de la rangée du
            # bas. Il se pose désormais SUR LE RAMEUR, à droite du billet,
            # là où aucun chiffre ne vit.
            # ⚠️ le QR mordait le dernier numéro. Il se pose désormais SOUS
            # le billet, dans la marge du carton, où rien ne vit.
            _q = 7.0 * mm
            _sec.carton_qr(c, x0 + CARD_W - _q - 1.0 * mm, y0 + 0.6 * mm, _q,
                           evenement_id, serie, avec_code=False)
        except Exception:
            pass


def generer_pdf(nb_cartes=12, serie_start=1, theme="", couleur=True,
                nom_evenement="", titre_jeu="", couleur_perso="", date_lieu="", telephone="",
                style="eco", evenement_id="", motif="", page_start=1):
    telephone = (telephone or "").strip() or "89 22 23 05"
    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=A4, pageCompression=1)
    nb_cartes = max(1, min(int(nb_cartes), 10000))
    par_page = COLS_PAGE * ROWS_PAGE
    nb_pages = (nb_cartes + par_page - 1) // par_page
    rng = random.Random(963000 + int(serie_start))
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
                # 💵 les DIX numéros du billet : deux rangées de cinq
                nums = _gen_billet(rng)
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
