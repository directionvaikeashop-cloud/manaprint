# -*- coding: utf-8 -*-
"""
MANAPRINT — Générateur BIN 6 BOULES (format A4)
12 cartes par feuille A4 (3 colonnes × 4 rangées).
Chaque carte : en-tête B · I · N avec la plage affichée sous chaque lettre
(1-12 / 13-24 / 25-36), grille 2 rangées × 3 colonnes, 6 numéros :
  B = 2 numéros 1-12 · I = 2 numéros 13-24 · N = 2 numéros 25-36
Ordre vertical LIBRE (non trié), fidèle au modèle.
Bande dédiée en bas : le QR de vérification y vit (coin droit), la grille au-dessus.
Pied « N° SERIE | 048001 » (fidèle au modèle).
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
LETTRES = ["B", "I", "N"]
PLAGES = [(1, 12), (13, 24), (25, 36)]

# 🥥 LE COCO DE MAEVA — chaque numéro se loge dans sa noix (12/08).
_RATIO_COCO = 1.125
VENTRE = (0.1388, 0.8603, 0.2043, 0.6567)   # x0, x1, y0, y1
# ⚠️ 12/08 : ventre ÉLARGI ×1,6 et blanchi dans le dessin (sceau Maeva :
# « 30 pt et blanchir leurs zones »). Le ventre d'origine ne portait que
# 20 pt ; ×1,3 donnait 25 pt ; ×1,6 donne 31 pt sans mordre la coque —
# vérifié à l'œil : les fibres et le relief du coco restent visibles.
import os as _os2
from reportlab.pdfbase.pdfmetrics import stringWidth as _lgc


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


_IMAGE_COCO = _choisir_image("bin6_coco", _RATIO_COCO)

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
    """6 numéros : 2 par colonne (B 1-12, I 13-24, N 25-36), ordre vertical libre."""
    return [rng.sample(range(pmin, pmax + 1), 2) for pmin, pmax in PLAGES]


def _dessiner_carte(c, x0, y0, cols_nums, couleur_hex, serie, titre_jeu="", telephone="", style="eco", evenement_id=""):
    police_ch, gris_ch = _style_chiffres(style)
    col = colors.HexColor(couleur_hex)
    ncols = 3
    cell_w = CARD_W / ncols

    # Bordure carte
    c.setStrokeColor(col); c.setLineWidth(0.8)
    c.roundRect(x0, y0, CARD_W, CARD_H, 1.5 * mm, stroke=1, fill=0)
    if _sec:  # cadre intérieur en microtexte (sécurité anti-photocopie)
        _sec.cadre_micro(c, x0, y0, CARD_W, CARD_H, serie, retrait=1.0 * mm)

    # En-tête B · I · N + plage sous chaque lettre (le nom du jeu, toujours visible)
    HDR_H = 8.0 * mm
    hdr_y = y0 + CARD_H - HDR_H
    c.setFillColor(col)
    for i, (lettre, (pmin, pmax)) in enumerate(zip(LETTRES, PLAGES)):
        cx = x0 + (i + 0.5) * cell_w
        c.setFont("Helvetica-Bold", 9)
        c.drawCentredString(cx, hdr_y + 4.0 * mm, lettre)
        c.setFont(POLICE, 3.8)
        c.drawCentredString(cx, hdr_y + 1.2 * mm, "%d - %d" % (pmin, pmax))
    c.setStrokeColor(col); c.setLineWidth(0.4)
    c.line(x0, hdr_y, x0 + CARD_W, hdr_y)

    # Grille 2 rangées × 3 colonnes — bande dédiée en bas pour le QR
    FOOT_H = 4.6 * mm
    grid_top = hdr_y
    grid_bot = y0 + 20 * mm      # 📏 la bande du bas : le QR y vit, la grille au-dessus
    row_h = (grid_top - grid_bot) / 2

    # ═══ 🥥 LES SIX COCOS ═══
    # Chaque numéro se loge dans le ventre de SA noix. Plus de grille :
    # les cocos séparent les numéros bien mieux qu'un trait.
    # ⚠️ 12/08 : la bande du bas était taillée pour l'ancienne grille et
    # volait 10 mm aux cocos. On la ramène à la place du QR, et les noix
    # grandissent d'autant — avec elles, les chiffres.
    grid_bot = y0 + 11.0 * mm
    ECART = 0.6 * mm
    cw2 = (CARD_W - 1.5 * mm - 2 * ECART) / 3.0
    ch2 = (grid_top - grid_bot - ECART) / 2.0
    kw = min(cw2, ch2 * _RATIO_COCO)
    kh = kw / _RATIO_COCO
    ox = x0 + (CARD_W - (3 * kw + 2 * ECART)) / 2
    oy = grid_bot + (grid_top - grid_bot - (2 * kh + ECART)) / 2

    # ⚠️ le chiffre se cale sur LE VENTRE de la noix, jamais en dur.
    vw = (VENTRE[1] - VENTRE[0]) * kw
    vh = (VENTRE[3] - VENTRE[2]) * kh
    taille = 40.0
    while taille > 10 and (_lgc("88", police_ch, taille) > vw * 0.99
                           or taille * 0.72 > vh * 0.99):
        taille -= 0.5

    for ci, nums in enumerate(cols_nums):
        for ri, val in enumerate(nums):
            px = ox + ci * (kw + ECART)
            py = oy + (1 - ri) * (kh + ECART)
            if _os2.path.exists(_IMAGE_COCO):
                try:
                    c.drawImage(_IMAGE_COCO, px, py, kw, kh, mask="auto",
                                preserveAspectRatio=True)
                except Exception:
                    pass
            nx = px + (VENTRE[0] + VENTRE[1]) / 2 * kw
            ny = py + (VENTRE[2] + VENTRE[3]) / 2 * kh - taille * 0.34
            if _sec:
                _sec.chiffre_micro(c, val, nx, ny, taille, gris_ch, police_ch)
            else:
                c.setFillColor(gris_ch)
                c.setFont(police_ch, taille)
                c.drawCentredString(nx, ny, str(val))

    # Bande du bas : signature à gauche + QR de vérification à droite
    signature = "BIN 6 boules"
    if telephone:
        signature += " " + telephone
    c.setFillColor(col); c.setFont(POLICE, 4.2)
    c.drawString(x0 + 2.0 * mm, y0 + FOOT_H + 5.5 * mm, signature[:44])
    if _sec and evenement_id:
        try:
            _q = 12.5 * mm
            _sec.carton_qr(c, x0 + CARD_W - _q - 2.0 * mm, y0 + FOOT_H + 1.4 * mm, _q, evenement_id, serie)
        except Exception:
            pass

    # Pied « N° SERIE | 048001 » — le titre client vit avec la série
    c.setStrokeColor(col); c.setLineWidth(0.4)
    c.line(x0, y0 + FOOT_H, x0 + CARD_W, y0 + FOOT_H)
    pied_g = "N\u00b0 SERIE"
    if titre_jeu and titre_jeu.strip() and titre_jeu.strip().upper() != "BIN 6":
        pied_g = titre_jeu.strip()[:24]
    c.setFillColor(GRIS_CLAIR if pied_g == "N\u00b0 SERIE" else col)
    c.setFont(POLICE, 4.2)
    c.drawString(x0 + 1.5 * mm, y0 + 1.5 * mm, pied_g[:34])
    c.setFillColor(col); c.setFont(POLICE, 6)
    c.drawRightString(x0 + CARD_W - 1.5 * mm, y0 + 1.4 * mm, "%06d" % serie)


def generer_pdf(nb_cartes=12, serie_start=1, theme="", couleur=True,
                nom_evenement="", titre_jeu="", couleur_perso="", date_lieu="", telephone="",
                style="eco", evenement_id="", page_start=1):
    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=A4, pageCompression=1)

    nb_cartes = max(1, min(int(nb_cartes), 10000))
    par_page = COLS_PAGE * ROWS_PAGE
    nb_pages = (nb_cartes + par_page - 1) // par_page

    rng = random.Random()   # graine fraîche : cartes uniques à chaque génération
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
                _dessiner_carte(c, x0, y0, cols_nums, coul, serie, titre_jeu, telephone, style=style, evenement_id=evenement_id)
                serie += 1
                faites += 1

        c.showPage()
        no_page += 1

    c.save()
    buf.seek(0)
    return buf


if __name__ == "__main__":
    pdf = generer_pdf(nb_cartes=12, couleur=True, serie_start=48001,
                      nom_evenement="", titre_jeu="", telephone="89 22 23 05")
    with open("test_bin6.pdf", "wb") as f:
        f.write(pdf.read())
    print("BIN 6 boules généré")
