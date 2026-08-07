# -*- coding: utf-8 -*-
"""
MANAPRINT — Générateur HUAHINE (format A4)

⛵ REFAIT LE 07/08 (sceau Maeva, disposition n°3) : la CARTE DE L'ÎLE à
gauche — avec ses baies, ses passes et ses villages — et les SIX NUMÉROS
en colonne à droite, chacun sous le nom de son village.

C'est la disposition qui donne les plus gros chiffres : sur la carte,
Haapu et Parea sont si proches que deux ronds se toucheraient.

RÈGLE INCHANGÉE : 6 numéros, deux par famille — 1-15, 46-60, 76-90.
Chaque village porte sa famille, du nord au sud :
    FARE (1-15) · Avea (76-90) · Haapu (1-15)
    Parea (46-60) · Maeva (76-90) · Faie (46-60)
Le sac du crieur ne change donc pas d'un chiffre.
"""
import io
import os as _os
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
# Les 3 familles de HUAHINE : gauche 1-15, centre 46-60, droite 76-90 (2 numéros chacune)
PLAGE_G = (1, 15)
PLAGE_C = (46, 60)
PLAGE_D = (76, 90)

COLS_PAGE = 2
ROWS_PAGE = 4
MARGIN_X = 8 * mm
MARGIN_TOP = 10 * mm
MARGIN_BOT = 8 * mm
GUTTER_X = 5 * mm
GUTTER_Y = 4 * mm

CARD_W = (PAGE_W - 2 * MARGIN_X - (COLS_PAGE - 1) * GUTTER_X) / COLS_PAGE
CARD_H = (PAGE_H - MARGIN_TOP - MARGIN_BOT - (ROWS_PAGE - 1) * GUTTER_Y) / ROWS_PAGE

# 🗺️ LA CARTE DE MAEVA et ses six villages, du nord au sud.
# Chaque village porte SA famille de numéros — la règle du jeu est
# inchangée, seul l'habillage a changé.
_RATIO_ILE = 900.0 / 1041.0        # la carte est plus HAUTE que large
VILLAGES = ["FARE", "Avea", "Haapu", "Parea", "Maeva", "Faie"]


def _choisir_image(motif, ratio_attendu):
    """🛟 Retrouve la carte, quel que soit son nom de fichier.

    Au téléversement le nom peut garder un préfixe ou recevoir un
    « (1) », et une ancienne version peut rester dans le dossier : on
    prend celui dont les PROPORTIONS collent au dessin attendu.
    """
    dossier = _os.path.dirname(_os.path.abspath(__file__))
    exact = _os.path.join(dossier, motif + ".png")
    candidats = []
    try:
        for f in _os.listdir(dossier):
            if motif in f and f.lower().endswith(".png"):
                candidats.append(_os.path.join(dossier, f))
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


_IMAGE_ILE = _choisir_image("huahine_ile", _RATIO_ILE)


def _gen_carte(rng):
    """6 numéros : 2 à gauche (1-15), 2 au centre (46-60), 2 à droite (76-90)."""
    g = rng.sample(range(PLAGE_G[0], PLAGE_G[1] + 1), 2)
    cmid = sorted(rng.sample(range(PLAGE_C[0], PLAGE_C[1] + 1), 2))
    d = rng.sample(range(PLAGE_D[0], PLAGE_D[1] + 1), 2)
    # (haut-gauche, haut-droit, centre-1, centre-2, bas-gauche, bas-droit)
    return (g[0], d[0], cmid[0], cmid[1], g[1], d[1])


def _dessiner_carte(c, x0, y0, nums, couleur_hex, serie, titre_jeu="", telephone="", style="eco", evenement_id=""):
    police_ch, gris_ch = _style_chiffres(style)
    col = colors.HexColor(couleur_hex)
    hg, hd, c1, c2, bg, bd = nums

    # Bordure carte
    c.setStrokeColor(col); c.setLineWidth(0.8)
    c.roundRect(x0, y0, CARD_W, CARD_H, 1.5 * mm, stroke=1, fill=0)
    if _sec:  # cadre intérieur en microtexte (sécurité anti-photocopie)
        _sec.cadre_micro(c, x0, y0, CARD_W, CARD_H, serie, retrait=1.0 * mm)

    # En-tête — le nom du jeu apparaît TOUJOURS (fidèle au modèle)
    hdr_y = y0 + CARD_H - 3.6 * mm
    titre = "Le jeu HUAHINE · pour 6 boules"
    if titre_jeu and "HUAHINE" not in titre_jeu.strip().upper():
        titre += " · " + titre_jeu.strip()
    titre += "" + ((" Tél : " + telephone) if telephone else "")
    c.setFillColor(col); c.setFont(POLICE, 4.8)
    c.drawCentredString(x0 + CARD_W / 2, hdr_y, titre[:78])

    # Pied de carte : « N° SERIE | 036001 »
    PIED_H = 4.6 * mm
    c.setStrokeColor(col); c.setLineWidth(0.4)
    c.line(x0 + 1.5 * mm, y0 + PIED_H, x0 + CARD_W - 1.5 * mm, y0 + PIED_H)
    c.line(x0 + CARD_W * 0.42, y0 + 0.8 * mm, x0 + CARD_W * 0.42, y0 + PIED_H - 0.6 * mm)
    c.setFillColor(GRIS_CLAIR); c.setFont(POLICE, 4.2)
    c.drawString(x0 + 3 * mm, y0 + 1.6 * mm, "N\u00b0 SERIE")
    c.setFillColor(col); c.setFont(POLICE, 6)
    c.drawRightString(x0 + CARD_W - 3 * mm, y0 + 1.5 * mm, "%06d" % serie)

    # ═══ LA CARTE À GAUCHE, LES SIX VILLAGES À DROITE (07/08) ═══
    z_bot = y0 + PIED_H + 1.6 * mm
    z_top = hdr_y - 2.6 * mm
    z_h = z_top - z_bot

    # ── la carte de l'île, à gauche, aussi grande que la place le permet ──
    part_carte = 0.42                      # elle prend 42 % de la largeur
    PLACE_QR = 12.5 * mm               # la bande du bas, reservee au QR
    ilw = CARD_W * part_carte - 4.0 * mm
    ilh = ilw / _RATIO_ILE
    if ilh > z_h - PLACE_QR:
        ilh = z_h - PLACE_QR
        ilw = ilh * _RATIO_ILE
    ilx = x0 + 2.5 * mm
    ily = z_bot + PLACE_QR + (z_h - PLACE_QR - ilh) / 2
    if _os.path.exists(_IMAGE_ILE):
        try:
            c.drawImage(_IMAGE_ILE, ilx, ily, ilw, ilh, mask="auto",
                        preserveAspectRatio=True)
        except Exception:
            pass

    # ── les six villages, en colonne à droite ────────────────────────────
    # L'ordre suit la règle : FARE et Haapu (1-15), Parea et Faie (46-60),
    # Avea et Maeva (76-90) — la même que depuis toujours.
    # FARE (1-15) · Avea (76-90) · Haapu (1-15) · Parea (46-60)
    # Maeva (76-90) · Faie (46-60)  — conforme a l'en-tete du fichier
    valeurs = [hg, hd, bg, c1, bd, c2]
    # 🔢 LES VILLAGES EN DEUX COLONNES DE TROIS (07/08) : en une seule
    # colonne de six, la hauteur limitait les chiffres a 22 pt — moins
    # qu'avant. Sur deux colonnes, chaque case est deux fois plus haute
    # et les chiffres retrouvent leur calibre de maison.
    gx = x0 + CARD_W * part_carte + 1.0 * mm
    gw = CARD_W - (gx - x0) - 2.5 * mm
    ECART = 1.4 * mm
    cw = (gw - ECART) / 2.0
    lh = z_h / 3.0
    taille = min(34.0, (lh * 0.90 - 4.2 * mm) / 0.72 * 72 / 25.4,
                 cw * 0.62 / 0.60 * 72 / 25.4)
    for i, (nom, val) in enumerate(zip(VILLAGES, valeurs)):
        colonne, rangee = i % 2, i // 2
        bx = gx + colonne * (cw + ECART)
        by = z_top - (rangee + 1) * lh
        c.setFillColor(colors.white)
        c.setStrokeColor(col)
        c.setLineWidth(0.55)
        c.roundRect(bx, by + lh * 0.06, cw, lh * 0.88, 1.4 * mm, stroke=1, fill=1)
        # le numéro, au centre de sa case
        nx = bx + cw / 2
        ny = by + lh * 0.5 - taille * 0.30 + 1.2 * mm
        if _sec:
            _sec.chiffre_micro(c, val, nx, ny, taille, gris_ch, police_ch)
        else:
            c.setFillColor(gris_ch)
            c.setFont(police_ch, taille)
            c.drawCentredString(nx, ny, str(val))
        # le nom du village, sous son numéro
        c.setFillColor(col)
        c.setFont(POLICE, 5.8)
        c.drawCentredString(nx, by + lh * 0.14, nom)

    # ── le QR, sous la carte, là où il ne gêne personne ──────────────────
    if _sec and evenement_id:
        try:
            _q = min(10.5 * mm, ilw * 0.62)
            _sec.carton_qr(c, ilx + (ilw - _q) / 2, z_bot + (PLACE_QR - _q) / 2,
                           _q, evenement_id, serie, avec_code=False)
        except Exception:
            pass


def generer_pdf(nb_cartes=8, serie_start=1, theme="", couleur=True,
                nom_evenement="", titre_jeu="", couleur_perso="", date_lieu="", telephone="",
                style="eco", evenement_id=""):
    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=A4, pageCompression=1)

    nb_cartes = max(1, min(int(nb_cartes), 10000))
    par_page = COLS_PAGE * ROWS_PAGE
    nb_pages = (nb_cartes + par_page - 1) // par_page

    rng = random.Random(975000 + int(serie_start))
    serie = int(serie_start)
    no_page = 1
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
    pdf = generer_pdf(nb_cartes=8, couleur=True,
                      nom_evenement="ASSOCIATION TE MANU", titre_jeu="Grand Loto",
                      telephone="87 77 34 26")
    with open("test_huahine.pdf", "wb") as f:
        f.write(pdf.read())
    print("HUAHINE généré")
