# -*- coding: utf-8 -*-
"""
MANAPRINT — Générateur LUNDI PAIR 74 (format A4)
12 cartons par feuille A4 (4 colonnes × 3 rangées), d'après le modèle dessiné
par Maeva : bandeau LUNE + « LUNDI / PAIR 74 », deux colonnes de 5 ronds,
bandeau du bas pour la personnalisation (2Kea&Associé par défaut).

LES NUMÉROS : 10 NOMBRES PAIRS de 2 à 74, tirés librement (sceau Maeva 18/09 :
« tirage libre »), jamais deux fois le même sur un carton. 37 pairs existent
(2, 4, 6 … 74) : on en pose 10, la lecture se fait colonne par colonne, de
haut en bas, en ordre croissant — comme sur le modèle PEA 74.

SÉCURITÉ ANTI-PHOTOCOPIE (module generators/securite.py) : cadre intérieur en
microtexte + chiffres remplis de microtexte (technique billet de banque).
Vérification à la loupe x10 : lettres nettes = original, trait flou = photocopie.
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

# SÉCURITÉ ANTI-PHOTOCOPIE (microtexte) — anti-panne : si le module securite
# est absent, les cartons sortent normalement, simplement sans microtexte.
try:
    from generators import securite as _sec
except Exception:
    try:
        import securite as _sec
    except Exception:
        _sec = None

# Police fine (look maison) avec repli Helvetica
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

# ══ L'ÉCRITURE DES CHIFFRES (sceau Maeva 18/09) ══════════════════════
# ⭐⭐ LATIN MODERN ROMAN dès la naissance de ce jeu — la serif fine et
#    contrastée de Maeva, déjà en poste sur les OHANA, les MARATHON et le
#    QUINES 90. Mesuré : 61 % de toner en moins que le gras condensé.
# ⭐ GRIS 0,35 : 20 % de toner en moins que le noir franc, et les chiffres
#    restent noirs à l'œil.
# ⚠️ LatinModern.ttf est rangé À CÔTÉ de ce générateur (l'original est en
#    OTF, que ReportLab ne sait pas lire). S'il manque, on retombe sur
#    l'ancienne écriture sans planter.
# ⚠️ LE MICROTEXTE RESTE EN POSTE : il CREUSE les chiffres, donc il
#    consomme MOINS d'encre qu'un chiffre plein.
import os as _osL
from reportlab.pdfbase import pdfmetrics as _pm
from reportlab.pdfbase.ttfonts import TTFont as _TF
_POLICE_ECO = "Helvetica"
try:
    _pm.registerFont(_TF("DJLECO", "/usr/share/fonts/truetype/dejavu/DejaVuSans-ExtraLight.ttf"))
    _POLICE_ECO = "DJLECO"
except Exception:
    pass
try:
    _pm.registerFont(_TF("LMROMAN", _osL.path.join(
        _osL.path.dirname(_osL.path.abspath(__file__)), "LatinModern.ttf")))
    _POLICE_ECO = "LMROMAN"
except Exception:
    pass
_GRIS_ECO = colors.Color(0.35, 0.35, 0.35)
_POLICE_P15 = _POLICE_ECO
_GRIS_P15 = colors.Color(0.14, 0.14, 0.14)   # objet distinct : sert à reconnaître la gamme


def _style_chiffres(style):
    """Retourne (police, gris) des chiffres selon la gamme choisie."""
    if str(style).lower() in ("p15", "premium"):
        return _POLICE_P15, _GRIS_P15
    return _POLICE_ECO, _GRIS_ECO
# ═════════════════════════════════════════════════════════════════════

PAGE_W, PAGE_H = A4

# ⭐ LES PAIRS : 2, 4, 6 … 74 — 37 nombres, on en pose 10 par carton.
PAIRS = list(range(2, 75, 2))
NB_NUMEROS = 10

COLS_PAGE = 4
ROWS_PAGE = 3
CARTES_PAGE = COLS_PAGE * ROWS_PAGE          # 12 cartons par feuille A4

MARGIN_X = 5 * mm
MARGIN_TOP = 7 * mm
MARGIN_BOT = 5 * mm
GUTTER_X = 3 * mm
GUTTER_Y = 4 * mm

CARD_W = (PAGE_W - 2 * MARGIN_X - (COLS_PAGE - 1) * GUTTER_X) / COLS_PAGE
CARD_H = (PAGE_H - MARGIN_TOP - MARGIN_BOT - (ROWS_PAGE - 1) * GUTTER_Y) / ROWS_PAGE

HDR_H = 20.5 * mm        # bandeau du haut : lune + LUNDI + PAIR 74
PIED_H = 6.2 * mm        # bandeau du bas : la personnalisation

# ⭐ LE ROND COMMANDE, LE CHIFFRE S'ADAPTE (même règle que sur les OHANA) :
#    le rayon est borné par la case, et la taille du chiffre descend jusqu'à
#    ce que sa DIAGONALE tienne dedans, quelle que soit l'écriture chargée.
R_ROND = 5.6 * mm
_T_NUM = 26.0
while _T_NUM > 10:
    _l = _pm.stringWidth("74", _POLICE_ECO, _T_NUM)
    _h = _T_NUM * 0.72
    if ((_l / 2) ** 2 + (_h / 2) ** 2) ** 0.5 <= R_ROND * 0.92:
        break
    _T_NUM -= 0.5


def _gen_carte(rng):
    """10 pairs distincts entre 2 et 74, rangés en 2 colonnes de 5 croissantes."""
    tirage = sorted(rng.sample(PAIRS, NB_NUMEROS))
    gauche = tirage[0::2]      # 1re, 3e, 5e… → colonne de gauche
    droite = tirage[1::2]      # 2e, 4e, 6e… → colonne de droite
    return gauche, droite


# ══ LE DESSIN DE LA LUNE (fidèle au croquis de Maeva) ════════════════
def _croissant(c, cx, cy, r, col):
    """Le croissant de lune : deux arcs de cercle, l'ouverture vers la droite.
    ⚠️ Dessiné point par point (et non avec les arcs de ReportLab) : c'est
    la seule façon d'obtenir un contour FERMÉ, propre à l'impression."""
    r2 = r * 0.92
    dx = r * 0.52           # décalage du cercle qui creuse le croissant
    d = dx
    a = (d * d + r * r - r2 * r2) / (2 * d)
    h2 = r * r - a * a
    if h2 <= 0:
        c.setStrokeColor(col); c.circle(cx, cy, r, stroke=1, fill=0); return
    h = math.sqrt(h2)
    # les deux points où les cercles se croisent
    p_haut = (cx + a, cy + h)
    p_bas = (cx + a, cy - h)
    ang1 = math.atan2(p_haut[1] - cy, p_haut[0] - cx)
    ang2 = math.atan2(p_bas[1] - cy, p_bas[0] - cx)
    b1 = math.atan2(p_haut[1] - cy, p_haut[0] - (cx + dx))
    b2 = math.atan2(p_bas[1] - cy, p_bas[0] - (cx + dx))

    p = c.beginPath()
    p.moveTo(*p_haut)
    n = 48
    # grand arc : on part du haut et on passe PAR LA GAUCHE
    for i in range(1, n + 1):
        t = ang1 + (2 * math.pi - (ang1 - ang2)) * i / n
        p.lineTo(cx + r * math.cos(t), cy + r * math.sin(t))
    # petit arc : on revient EN CREUSANT, donc en passant par la GAUCHE du
    # cercle qui creuse (⚠️ dans l'autre sens il bombe vers la droite et la
    # lune devient un gros nuage — erreur du premier essai).
    for i in range(1, n + 1):
        t = b2 + ((b1 - 2 * math.pi) - b2) * i / n
        p.lineTo(cx + dx + r2 * math.cos(t), cy + r2 * math.sin(t))
    p.close()
    c.setStrokeColor(col); c.setLineWidth(0.9)
    c.setFillColor(colors.white)
    c.drawPath(p, stroke=1, fill=1)

    # le petit visage endormi (œil + sourire), comme sur le croquis
    c.setStrokeColor(col); c.setLineWidth(0.7)
    c.circle(cx - r * 0.18, cy + r * 0.24, r * 0.075, stroke=1, fill=1)
    pv = c.beginPath()
    pv.moveTo(cx - r * 0.34, cy - r * 0.16)
    pv.curveTo(cx - r * 0.24, cy - r * 0.34,
               cx - r * 0.02, cy - r * 0.34,
               cx + r * 0.06, cy - r * 0.14)
    c.setFillColor(colors.white)
    c.drawPath(pv, stroke=1, fill=0)


def _etoile(c, cx, cy, r, col):
    """L'étincelle à 4 branches du croquis."""
    p = c.beginPath()
    pts = []
    for i in range(8):
        ang = math.pi / 2 - i * math.pi / 4
        rr = r if i % 2 == 0 else r * 0.30
        pts.append((cx + rr * math.cos(ang), cy + rr * math.sin(ang)))
    p.moveTo(*pts[0])
    for q in pts[1:]:
        p.lineTo(*q)
    p.close()
    c.setStrokeColor(col); c.setLineWidth(0.6); c.setFillColor(colors.white)
    c.drawPath(p, stroke=1, fill=1)


def _nuage(c, x, y, w, col):
    """Le petit nuage posé sous la lune (trois bosses sur une ligne)."""
    h = w * 0.34
    p = c.beginPath()
    p.moveTo(x, y)
    p.curveTo(x + w * 0.02, y + h * 0.75, x + w * 0.26, y + h * 0.98, x + w * 0.36, y + h * 0.52)
    p.curveTo(x + w * 0.46, y + h * 1.25, x + w * 0.72, y + h * 1.10, x + w * 0.74, y + h * 0.42)
    p.curveTo(x + w * 0.86, y + h * 0.80, x + w * 1.02, y + h * 0.52, x + w, y)
    p.close()
    c.setStrokeColor(col); c.setLineWidth(0.6); c.setFillColor(colors.white)
    c.drawPath(p, stroke=1, fill=1)


def _texte_contour(c, x, y, texte, police, taille, col, epaisseur=0.55):
    """Le titre en LETTRES CREUSES du croquis (contour seul, intérieur blanc).
    ⭐ C'est aussi une économie : une lettre creuse consomme le tiers d'une
    lettre pleine."""
    t = c.beginText()
    t.setTextOrigin(x, y)
    t.setFont(police, taille)
    try:
        t.setTextRenderMode(1)          # 1 = contour seul
    except Exception:
        pass
    c.setStrokeColor(col); c.setLineWidth(epaisseur)
    t.textLine(texte)
    c.drawText(t)
    try:
        t2 = c.beginText(); t2.setTextRenderMode(0)   # on remet le mode normal
        c.drawText(t2)
    except Exception:
        pass


def _dessiner_carte(c, x0, y0, gauche, droite, couleur_hex, serie,
                    style="eco", nom_pied="", titre_jeu="", telephone="",
                    evenement_id=""):
    police_ch, gris_ch = _style_chiffres(style)
    col = colors.HexColor(couleur_hex)

    # ---- Le double cadre du modèle ----
    c.setStrokeColor(col); c.setLineWidth(1.1)
    c.roundRect(x0, y0, CARD_W, CARD_H, 1.6 * mm, stroke=1, fill=0)
    c.setLineWidth(0.4)
    c.roundRect(x0 + 1.1 * mm, y0 + 1.1 * mm, CARD_W - 2.2 * mm, CARD_H - 2.2 * mm,
                1.1 * mm, stroke=1, fill=0)
    if _sec:   # cadre intérieur en microtexte (sécurité anti-photocopie)
        _sec.cadre_micro(c, x0, y0, CARD_W, CARD_H, serie, retrait=2.1 * mm)

    # ---- Le bandeau du haut : lune, LUNDI, PAIR 74 ----
    hdr_bas = y0 + CARD_H - HDR_H
    lune_cx = x0 + 8.2 * mm
    lune_cy = y0 + CARD_H - 8.0 * mm
    _croissant(c, lune_cx, lune_cy, 4.9 * mm, col)
    _etoile(c, x0 + 15.0 * mm, y0 + CARD_H - 4.4 * mm, 1.15 * mm, col)
    _etoile(c, x0 + 13.2 * mm, y0 + CARD_H - 10.4 * mm, 0.85 * mm, col)

    # LUNDI — grandes lettres creuses, calées à droite de la lune
    zone_g = x0 + 15.6 * mm
    larg_dispo = x0 + CARD_W - 2.6 * mm - zone_g
    t_lundi = 19.0
    while t_lundi > 8 and pdfmetrics.stringWidth("LUNDI", "Helvetica-Bold", t_lundi) > larg_dispo:
        t_lundi -= 0.25
    _texte_contour(c, x0 + CARD_W - 2.6 * mm - pdfmetrics.stringWidth("LUNDI", "Helvetica-Bold", t_lundi),
                   y0 + CARD_H - 8.2 * mm, "LUNDI", "Helvetica-Bold", t_lundi, col, 0.6)

    # PAIR 74 — dans son cartouche, sous LUNDI
    t_pair = 9.5
    sous = "PAIR 74"
    lb = pdfmetrics.stringWidth(sous, "Helvetica-Bold", t_pair) + 3.4 * mm
    xb = x0 + CARD_W - 2.6 * mm - lb
    yb = y0 + CARD_H - 13.9 * mm
    c.setStrokeColor(col); c.setLineWidth(0.5)
    c.roundRect(xb, yb, lb, 4.6 * mm, 0.9 * mm, stroke=1, fill=0)
    _texte_contour(c, xb + 1.7 * mm, yb + 1.25 * mm, sous, "Helvetica-Bold", t_pair, col, 0.45)

    # les nuages qui ferment le bandeau
    _nuage(c, x0 + 3.0 * mm, hdr_bas + 0.4 * mm, 8.4 * mm, col)
    _nuage(c, x0 + CARD_W - 13.0 * mm, hdr_bas + 0.4 * mm, 9.2 * mm, col)
    c.setStrokeColor(col); c.setLineWidth(0.5)
    c.line(x0 + 2.2 * mm, hdr_bas, x0 + CARD_W - 2.2 * mm, hdr_bas)

    # ---- Les 10 ronds : 2 colonnes de 5 ----
    pied_haut = y0 + PIED_H + 1.6 * mm
    zone_h = hdr_bas - pied_haut
    pas_y = zone_h / 5.0
    cx_g = x0 + CARD_W * 0.29
    cx_d = x0 + CARD_W * 0.71

    # le trait vertical de séparation, comme sur le modèle
    c.setStrokeColor(col); c.setLineWidth(0.5)
    c.line(x0 + CARD_W / 2, hdr_bas - 1.4 * mm, x0 + CARD_W / 2, pied_haut + 1.4 * mm)

    for i in range(5):
        cy = hdr_bas - (i + 0.5) * pas_y
        for cx, val in ((cx_g, gauche[i]), (cx_d, droite[i])):
            c.setStrokeColor(col); c.setLineWidth(0.9)
            c.circle(cx, cy, R_ROND, stroke=1, fill=0)
            if _sec:   # chiffres « billet de banque » remplis de microtexte
                _sec.chiffre_micro(c, val, cx, cy - _T_NUM * 0.36, _T_NUM, gris_ch, police_ch)
            else:
                c.setFillColor(gris_ch); c.setFont(police_ch, _T_NUM)
                c.drawCentredString(cx, cy - _T_NUM * 0.36, str(val))

    # ---- Le bandeau du bas : la personnalisation ----
    pied_y = y0 + 2.2 * mm
    c.setStrokeColor(col); c.setLineWidth(0.5)
    c.rect(x0 + 2.2 * mm, pied_y, CARD_W - 4.4 * mm, PIED_H - 1.2 * mm, stroke=1, fill=0)
    nom = (str(nom_pied).replace("|", " ").strip() or "2Kea&Associé")
    if telephone:
        nom += "  " + str(telephone).strip()
    t_nom = 7.0
    libre = CARD_W - 16.0 * mm
    while t_nom > 3.6 and pdfmetrics.stringWidth(nom, "Helvetica", t_nom) > libre:
        t_nom -= 0.2
    c.setFillColor(colors.black); c.setFont("Helvetica", t_nom)
    c.drawCentredString(x0 + CARD_W / 2, pied_y + 1.7 * mm, nom)
    # les doubles traits qui encadrent le nom, comme sur le modèle
    ln = pdfmetrics.stringWidth(nom, "Helvetica", t_nom)
    for sens in (-1, 1):
        xa = x0 + CARD_W / 2 + sens * (ln / 2 + 1.5 * mm)
        xb2 = x0 + CARD_W / 2 + sens * (CARD_W / 2 - 3.6 * mm)
        if sens * (xb2 - xa) > 0.6 * mm:
            c.setStrokeColor(col); c.setLineWidth(0.5)
            c.line(xa, pied_y + 2.9 * mm, xb2, pied_y + 2.9 * mm)
            c.line(xa, pied_y + 1.8 * mm, xb2, pied_y + 1.8 * mm)

    # ---- N° de série, discret, sous le bandeau ----
    c.setFillColor(GRIS); c.setFont(POLICE, 3.6)
    c.drawRightString(x0 + CARD_W - 2.4 * mm, y0 + 0.7 * mm, "N° %06d" % serie)

    # QR de vérification (anti-duplication) — seulement si un événement est fourni
    if _sec and evenement_id:
        try:
            _q = 6.2 * mm
            _sec.carton_qr(c, x0 + 2.6 * mm, y0 + PIED_H + 1.0 * mm, _q, evenement_id, serie)
        except Exception:
            pass


def generer_pdf(nb_cartes=12, serie_start=1, theme="", couleur=True,
                nom_evenement="", titre_jeu="", couleur_perso="", date_lieu="", telephone="",
                style="eco", evenement_id="", page_start=1):
    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=A4, pageCompression=1)

    nb_cartes = max(1, min(int(nb_cartes), 10000))
    nb_pages = (nb_cartes + CARTES_PAGE - 1) // CARTES_PAGE

    # ⚠️ GRAINE : deux lots lancés avec le même serie_start sortent identiques.
    #    Pour un second tirage, décaler serie_start (c'est la règle maison).
    rng = random.Random(174000 + int(serie_start))
    serie = int(serie_start)
    faites = 0
    no_page = max(1, int(page_start))

    for _ in range(nb_pages):
        c.setFillColor(GRIS_CLAIR); c.setFont(POLICE, 6)
        c.drawCentredString(PAGE_W / 2, PAGE_H - 4.2 * mm, "%d" % no_page)

        for slot in range(CARTES_PAGE):
            if faites >= nb_cartes:
                break
            ci = slot % COLS_PAGE
            ri = slot // COLS_PAGE
            x0 = MARGIN_X + ci * (CARD_W + GUTTER_X)
            y0 = PAGE_H - MARGIN_TOP - (ri + 1) * CARD_H - ri * GUTTER_Y

            if couleur:
                coul = couleur_perso.strip() if couleur_perso.strip() else RAINBOW[faites % len(RAINBOW)]
            else:
                coul = "#3A3A3A"

            gauche, droite = _gen_carte(rng)
            _dessiner_carte(c, x0, y0, gauche, droite, coul, serie, style=style,
                            nom_pied=nom_evenement, titre_jeu=titre_jeu,
                            telephone=telephone, evenement_id=evenement_id)
            serie += 1
            faites += 1

        c.showPage()
        no_page += 1

    c.save()
    buf.seek(0)
    return buf.read()
