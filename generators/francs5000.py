# -*- coding: utf-8 -*-
"""
MANAPRINT — Générateur 5000 FRANCS (format A4)

💵 NÉ LE 13/08 (sceau Maeva) : LE BILLET DE CINQ MILLE FRANCS, et sa
règle nouvelle — dessinée à la main par Maeva sur un schéma.

⚠️⚠️ CE JEU NE RESSEMBLE À AUCUN AUTRE : QUATRE numéros seulement, et
un MONTANT au centre vers lequel tout converge.

  24 ↘                      ↗ 13        haut-gauche : 1-15
       ↘   [ MONTANT ]   ↗              bas-gauche  : 16-25
  24 ↗                      ↘ 49        haut-droit  : 26-45
                                        bas-droit   : 46-65

Le MONTANT au centre — 5, 10, 20, 50 ou 100 francs — est ce que le
joueur gagne. Les quatre flèches y ramènent l'œil.

8 billets par feuille A4 (2 colonnes × 4 rangées).
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
_RATIO_BILLET = 1.7526
ZONE = (0.215, 0.7, 0.23, 0.79)   # x0, x1, y0, y1
# 💵 LES QUATRE COINS DU BILLET (schéma de Maeva, 13/08)
#    haut-gauche · bas-gauche · haut-droit · bas-droit
COINS5000 = [(1, 15), (16, 25), (26, 45), (46, 65)]

# 💰 CE QUE LE JOUEUR GAGNE — le montant qui trône au centre.
# ⚠️ 13/08 (sceau Maeva) : ils se suivent DE CINQ EN CINQ, sans saut :
# 5, 10, 15, 20… jusqu'à 100. Un vrai barème de loto, pas cinq paliers.
MONTANTS5000 = list(range(5, 105, 5))
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
_IMAGE_BILLET = _choisir_image("billet5000", _RATIO_BILLET)

# ⭐ LA POLICE QUI GROSSIT : condensée grasse — plus étroite qu'une grasse
# ordinaire, donc elle monte plus haut à place égale.
_POLICE_GROS = ""
try:
    from reportlab.pdfbase import pdfmetrics as _pm5
    from reportlab.pdfbase.ttfonts import TTFont as _TF5
    _pm5.registerFont(_TF5("F5000GROS",
        "/usr/share/fonts/truetype/dejavu/DejaVuSansCondensed-Bold.ttf"))
    _POLICE_GROS = "F5000GROS"
except Exception:
    _POLICE_GROS = ""


def _gen_billet(rng):
    """💵 Les quatre numéros des coins, et le montant du centre.

    ⚠️ Chaque coin a SA plage — elles ne se chevauchent pas, donc les
    quatre numéros sont forcément différents.
    """
    coins = [rng.randint(lo, hi) for lo, hi in COINS5000]
    montant = rng.choice(MONTANTS5000)
    return coins, montant

COLS_PAGE = 2
ROWS_PAGE = 4            # 8 billets par feuille (sceau Maeva 13/08)
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
    coins, montant = nums
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
    # ═══ 💵 LES QUATRE COINS ET LE MONTANT ═══
    # Le schéma de Maeva : deux numéros à gauche, deux à droite, et le
    # MONTANT au centre vers lequel quatre flèches ramènent l'œil.
    # ⭐ la condensée grasse étirée — la leçon du 500 F
    ETIRE = 1.55
    police_ch = _POLICE_GROS or police_ch
    place = zw * 0.24
    etage = zh / 2.4
    taille = 30.0
    while taille > 8 and (_lg5("88", police_ch, taille) > place * 0.80
                          or taille * 0.72 * ETIRE > etage * 0.90):
        taille -= 0.5

    # les quatre coins : haut-gauche, bas-gauche, haut-droit, bas-droit
    cx_g = zx + zw * 0.135
    cx_d = zx + zw * 0.865
    cy_h = zy + zh * 0.76
    cy_b = zy + zh * 0.24
    postes = ((cx_g, cy_h), (cx_g, cy_b), (cx_d, cy_h), (cx_d, cy_b))
    for (nx, ny), n in zip(postes, coins):
        c.saveState()
        try:
            c.translate(nx, ny - taille * 0.34)
            c.scale(1.0, ETIRE)
            if _sec:
                _sec.chiffre_micro(c, n, 0, 0, taille, gris_ch, police_ch)
            else:
                c.setFillColor(gris_ch)
                c.setFont(police_ch, taille)
                c.drawCentredString(0, 0, str(n))
        finally:
            c.restoreState()

    # ═══ 🌀 LES QUATRE COURBES ET LA ROSACE ═══
    # ⭐ 13/08 (sceau Maeva : « une idée originale pour rendre les flèches
    # et les montants waouh ») : au lieu de traits droits, des COURBES
    # DE BÉZIER qui s'incurvent vers le centre — le geste même du schéma
    # dessiné à la main par Maeva. Et au centre, une ROSACE GUILLOCHÉE,
    # comme les rosaces de sécurité des vrais billets.
    import math as _m
    mx, my = zx + zw / 2, zy + zh / 2
    r_ros = min(zw * 0.145, zh * 0.30)

    # ── les quatre courbes ────────────────────────────────────────────
    c.setStrokeColor(col)
    c.setLineWidth(0.85)
    for idx, (nx, ny) in enumerate(postes):
        dx, dy = mx - nx, my - ny
        lg = (dx * dx + dy * dy) ** 0.5
        if lg < 1:
            continue
        ux, uy = dx / lg, dy / lg
        # on part du bord du chiffre, on s'arrête au bord de la rosace
        x1 = nx + ux * (place * 0.42)
        y1 = ny + uy * (etage * 0.26)
        x2 = mx - ux * (r_ros + 1.2 * mm)
        y2 = my - uy * (r_ros + 1.2 * mm)
        # ⚠️ la courbe s'incurve PERPENDICULAIREMENT au trajet : c'est ce
        # qui donne le geste souple du dessin de Maeva. Le sens alterne
        # pour que les quatre courbes s'enroulent autour du centre.
        px_, py_ = -uy, ux
        sens = 1.0 if idx in (0, 3) else -1.0
        courbe = lg * 0.22 * sens
        c.bezier(x1, y1,
                 x1 + ux * lg * 0.35 + px_ * courbe,
                 y1 + uy * lg * 0.35 + py_ * courbe,
                 x2 - ux * lg * 0.28 + px_ * courbe,
                 y2 - uy * lg * 0.28 + py_ * courbe,
                 x2, y2)
        # ⚠️ 13/08 : LA POINTE. Elle doit s'ouvrir DERRIÈRE le point
        # d'arrivée, dans le sens d'où vient la courbe — sinon les deux
        # traits partent vers l'avant et la flèche semble retournée.
        # On prend la tangente : du DERNIER point de contrôle vers x2/y2.
        cx3 = x2 - ux * lg * 0.28 + px_ * courbe
        cy3 = y2 - uy * lg * 0.28 + py_ * courbe
        ang = _m.atan2(y2 - cy3, x2 - cx3)
        for d in (2.62, -2.62):     # ± 150° : la pointe s'ouvre en arrière
            c.line(x2, y2,
                   x2 + 2.4 * mm * _m.cos(ang + d),
                   y2 + 2.4 * mm * _m.sin(ang + d))

    # ── 🌀 LA ROSACE GUILLOCHÉE ───────────────────────────────────────
    # Deux cercles et une guirlande de pétales, dessinés au trait fin —
    # l'ornement des vrais billets, et il ne coûte presque rien en encre.
    c.setFillColor(colors.white)
    c.setStrokeColor(col)
    c.setLineWidth(1.2)
    c.circle(mx, my, r_ros, stroke=1, fill=1)
    c.setLineWidth(0.4)
    c.circle(mx, my, r_ros * 0.86, stroke=1, fill=0)
    # ⭐ LA GUIRLANDE : de petits ARCS ouverts vers l'extérieur — c'est le
    # guillochis des vrais billets. Des cercles pleins faisaient « chaîne » ;
    # des arcs donnent la dentelle. Un trait très fin suffit : la rosace
    # doit être délicate, pas lourde.
    c.setLineWidth(0.28)
    PETALES = 24
    for k in range(PETALES):
        a = 2 * _m.pi * k / PETALES
        cxp = mx + _m.cos(a) * r_ros * 0.955
        cyp = my + _m.sin(a) * r_ros * 0.955
        rp = r_ros * 0.115
        deg = _m.degrees(a)
        c.arc(cxp - rp, cyp - rp, cxp + rp, cyp + rp, deg - 118, 236)
    # deux fils concentriques au coeur : la profondeur du guillochis
    c.setLineWidth(0.22)
    c.circle(mx, my, r_ros * 0.74, stroke=1, fill=0)
    c.circle(mx, my, r_ros * 0.70, stroke=1, fill=0)

    # ── 💰 LE MONTANT, au cœur de la rosace ───────────────────────────
    t_m = taille * 0.70
    while t_m > 6 and _lg5("%d" % montant, police_ch, t_m) > r_ros * 1.42:
        t_m -= 0.5
    c.setFillColor(gris_ch)
    c.setFont(police_ch, t_m)
    c.drawCentredString(mx, my + r_ros * 0.02, "%d" % montant)
    c.setFillColor(col)
    c.setFont(POLICE, max(4.0, t_m * 0.28))
    c.drawCentredString(mx, my - r_ros * 0.52, "FRANCS")

    # 🎫 le numéro de série, au pied du billet
    # ⚠️ 13/08 : il était au CENTRE et écrasait le MONTANT — sur ce billet,
    # le centre appartient au montant, c'est tout le sens du jeu.
    c.setFillColor(col)
    c.setFont(POLICE, 5.0)
    c.drawString(px + iw * 0.215, py + ih * 0.045, "N\u00b0 %05d" % serie)

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
            _q = 9.0 * mm
            _sec.carton_qr(c, px + iw * 0.845, py + ih * 0.10, _q,
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
