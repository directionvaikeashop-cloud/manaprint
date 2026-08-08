"""
⭐ CORSICA — L'ÎLE DE LA BEAUTÉ (né le 07/08, sur la carte et l'idée de Maeva)

Sur chaque carton : la carte de la Corse à gauche, et à droite une grille
de NEUF cases. Les HUIT du pourtour portent les numéros, nommés par les
villes de l'île ; celle du MILIEU porte L'ÉTOILE et son montant — le
bonus.

RÈGLE : 8 numéros DISTINCTS tirés de 1 à 80, un par ville, du nord au
sud. Au centre, l'étoile annonce le bonus : 5, 10, 20, 50 ou 100 francs.
"""
import io
import os as _os
import random
import math
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase.pdfmetrics import stringWidth as _lg

try:
    from generators import securite as _sec
except ImportError:
    try:
        import securite as _sec
    except ImportError:
        _sec = None

POLICE = "Helvetica"
_POLICE_ECO = "Helvetica-Bold"
try:
    pdfmetrics.registerFont(TTFont("DJBOLDCORS", "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"))
    _POLICE_ECO = "DJBOLDCORS"
except Exception:
    pass
_POLICE_P15 = _POLICE_ECO
_GRIS_ECO = colors.Color(0.50, 0.50, 0.50)     # imposé au boot par app.py
_GRIS_P15 = colors.Color(0.25, 0.25, 0.25)


def _style_chiffres(style):
    if str(style).lower() in ("p15", "premium"):
        return _POLICE_P15, _GRIS_P15
    return _POLICE_ECO, _GRIS_ECO


PAGE_W, PAGE_H = A4
COLS_PAGE, ROWS_PAGE = 2, 4               # 8 cartes / A4
MARGIN_X, MARGIN_TOP, MARGIN_BOT = 9 * mm, 6 * mm, 9 * mm
GUTTER_X, GUTTER_Y = 4 * mm, 4 * mm
CARD_W = (PAGE_W - 2 * MARGIN_X - (COLS_PAGE - 1) * GUTTER_X) / COLS_PAGE
CARD_H = (PAGE_H - MARGIN_TOP - MARGIN_BOT - (ROWS_PAGE - 1) * GUTTER_Y) / ROWS_PAGE

GRAINE = 990000                            # 989000 = MAIA
PLAGE = (1, 80)
NB_NUMS = 8
MONTANTS = [5, 10, 20, 50, 100]            # le bonus de l'étoile

# 🗺️ les huit villes de la carte, du nord au sud
VILLES = ["Nonza", "BASTIA", "L'Île-Rousse", "Calvi",
          "Aléria", "AJACCIO", "P.-VECCHIO", "BONIFACIO"]

_RATIO_ILE = 700.0 / 1243.0                # la Corse est haute et étroite


def _choisir_image(motif, ratio_attendu):
    """🛟 Retrouve la carte, quel que soit son nom de fichier."""
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


_IMAGE_ILE = _choisir_image("corsica_ile", _RATIO_ILE)

RAINBOW = ["#E63946", "#2A9D8F", "#457B9D", "#BC6C25", "#6A994E", "#7209B7",
           "#E76F51", "#264653", "#D62828", "#F4A261", "#8E7DBE", "#F72585"]


def _gen_carte(rng):
    """8 numéros distincts de 1 à 80, triés, plus le montant du bonus."""
    nums = sorted(rng.sample(range(PLAGE[0], PLAGE[1] + 1), NB_NUMS))
    return nums, rng.choice(MONTANTS)


def _etoile(c, cx, cy, r, col):
    """L'étoile à cinq branches de la carte de Maeva, au trait."""
    pts = []
    for k in range(10):
        ang = math.radians(90 + k * 36)
        rayon = r if k % 2 == 0 else r * 0.42
        pts.append((cx + math.cos(ang) * rayon, cy + math.sin(ang) * rayon))
    p = c.beginPath()
    p.moveTo(*pts[0])
    for x, y in pts[1:]:
        p.lineTo(x, y)
    p.close()
    c.setFillColor(colors.white)
    c.setStrokeColor(col)
    c.setLineWidth(0.9)
    c.drawPath(p, stroke=1, fill=1)


def _dessiner_carte(c, x0, y0, nums, montant, couleur_hex, serie,
                    titre_jeu="", telephone="", style="eco", evenement_id=""):
    police_ch, gris_ch = _style_chiffres(style)
    col = colors.HexColor(couleur_hex)

    c.setStrokeColor(col)
    c.setLineWidth(0.9)
    c.roundRect(x0, y0, CARD_W, CARD_H, 1.5 * mm, stroke=1, fill=0)
    if _sec:
        _sec.cadre_micro(c, x0, y0, CARD_W, CARD_H, serie, retrait=1.0 * mm)

    # ── l'en-tête : le nom du jeu s'écrit TOUJOURS ───────────────────────
    ligne = "CORSICA \u00b7 l'\u00eele de la beaut\u00e9"
    if titre_jeu and "CORSICA" not in titre_jeu.strip().upper():
        ligne += "  \u00b7  " + titre_jeu.strip()[:22]
    if telephone:
        ligne += "  \u00b7  " + str(telephone)[:16]
    t = 7.0
    while t > 4.4 and _lg(ligne, "Helvetica-Bold", t) > CARD_W - 8 * mm:
        t -= 0.2
    c.setFillColor(col)
    c.setFont("Helvetica-Bold", t)
    c.drawCentredString(x0 + CARD_W / 2, y0 + CARD_H - 5.4 * mm, ligne)

    PIED_H = 4.2 * mm
    z_bot = y0 + PIED_H + 1.4 * mm
    z_top = y0 + CARD_H - 7.6 * mm
    z_h = z_top - z_bot

    # ═══ LA CARTE AU CENTRE, LES NUMÉROS AUTOUR (idée n°2, choix Maeva) ═══
    # Chaque numéro vit sur le bord et rejoint SA ville par un fil
    # pointillé. Et l'ÉTOILE du bonus se pose AU CŒUR DE L'ÎLE — c'est
    # bien « au milieu », comme Maeva l'a demandé.
    LARG_COL = 26.0 * mm
    ilw = CARD_W - 2 * LARG_COL - 5.0 * mm
    ilh = ilw / _RATIO_ILE
    if ilh > z_h:
        ilh = z_h
        ilw = ilh * _RATIO_ILE
    ilx = x0 + (CARD_W - ilw) / 2
    ily = z_bot + (z_h - ilh) / 2
    if _os.path.exists(_IMAGE_ILE):
        try:
            c.drawImage(_IMAGE_ILE, ilx, ily, ilw, ilh, mask="auto",
                        preserveAspectRatio=True)
        except Exception:
            pass

    # les huit villes, à leur vraie place sur la carte (fractions mesurées)
    PLACES = [("Nonza", 0.8390, 0.8390), ("BASTIA", 0.8175, 0.7490),
              ("L'Île-Rousse", 0.3703, 0.7560), ("Calvi", 0.1288, 0.6560),
              ("Aléria", 0.8587, 0.4680), ("AJACCIO", 0.1878, 0.3490),
              ("P.-VECCHIO", 0.7156, 0.2250), ("BONIFACIO", 0.5617, 0.0340)]
    # quatre numéros à gauche, quatre à droite — du nord au sud
    COTES = [(1, 0), (1, 1), (-1, 0), (-1, 1), (1, 2), (-1, 2), (1, 3), (-1, 3)]
    lh = z_h / 4.0
    taille = min(30.0, (lh * 0.82 - 3.2 * mm) / 0.72 * 72 / 25.4,
                 LARG_COL * 0.58 / 0.60 * 72 / 25.4)
    for (ville, fx, fy), val, (cote, rang) in zip(PLACES, nums, COTES):
        vx = ilx + fx * ilw
        vy = ily + fy * ilh
        bx = (x0 + 1.8 * mm) if cote < 0 else (x0 + CARD_W - LARG_COL - 1.8 * mm)
        by = z_top - (rang + 1) * lh
        c.setStrokeColor(col)
        c.setLineWidth(0.4)
        c.setDash(1, 2)
        depart = bx + (LARG_COL if cote < 0 else 0)
        c.line(depart, by + lh * 0.5, vx, vy)
        c.setDash()
        c.setFillColor(colors.white)
        c.setStrokeColor(col)
        c.setLineWidth(0.6)
        c.roundRect(bx, by + lh * 0.09, LARG_COL, lh * 0.82, 1.3 * mm, stroke=1, fill=1)
        nx = bx + LARG_COL / 2
        ny = by + lh * 0.5 - taille * 0.28 + 0.7 * mm
        if _sec:
            _sec.chiffre_micro(c, val, nx, ny, taille, gris_ch, police_ch)
        else:
            c.setFillColor(gris_ch)
            c.setFont(police_ch, taille)
            c.drawCentredString(nx, ny, str(val))
        tv = 5.2
        while tv > 3.4 and _lg(ville, POLICE, tv) > LARG_COL - 2.0 * mm:
            tv -= 0.2
        c.setFillColor(col)
        c.setFont(POLICE, tv)
        c.drawCentredString(nx, by + lh * 0.16, ville)

    # ── ⭐ L'ÉTOILE DU BONUS, AU CŒUR DE L'ÎLE ───────────────────────────
    ex = ilx + ilw * 0.50
    ey = ily + ilh * 0.50
    r_et = min(ilw * 0.46, ilh * 0.14)
    _etoile(c, ex, ey, r_et, col)
    tm = min(12.0, r_et * 0.90)
    c.setFillColor(gris_ch)
    c.setFont(police_ch, tm)
    c.drawCentredString(ex, ey - tm * 0.34, str(montant))
    c.setFillColor(col)
    c.setFont(POLICE, 4.6)
    c.drawCentredString(ex, ey - r_et - 3.0, "FRANCS")

    # ── le pied : n° de carte, et le QR sous la colonne de gauche ────────
    c.setFillColor(col)
    c.setFont(POLICE, 5.0)
    c.drawString(x0 + 3.0 * mm, y0 + 1.6 * mm, "Carte N\u00b0 %05d" % serie)
    if _sec and evenement_id:
        try:
            # le QR se glisse sous la pointe de l'île, au centre : c'est
            # le seul coin vraiment libre du carton.
            _q = 8.0 * mm
            _sec.carton_qr(c, ilx + ilw / 2 - _q / 2, z_bot + 0.4 * mm,
                           _q, evenement_id, serie, avec_code=False)
        except Exception:
            pass


def generer_pdf(nb_cartes=8, serie_start=1, theme="", couleur=True,
                nom_evenement="", titre_jeu="", telephone="", date_lieu="",
                couleur_perso=None, style="eco", evenement_id="", motif=""):
    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=A4, pageCompression=1)
    rng = random.Random(GRAINE + int(serie_start))
    serie, faites, no_page = int(serie_start), 0, 1

    while faites < nb_cartes:
        for row in range(ROWS_PAGE):
            for coln in range(COLS_PAGE):
                if faites >= nb_cartes:
                    break
                x0 = MARGIN_X + coln * (CARD_W + GUTTER_X)
                y0 = MARGIN_BOT + (ROWS_PAGE - 1 - row) * (CARD_H + GUTTER_Y)
                coul = (couleur_perso if (couleur and couleur_perso)
                        else RAINBOW[(serie - 1) % len(RAINBOW)] if couleur else "#9A9A9A")
                nums, montant = _gen_carte(rng)
                _dessiner_carte(c, x0, y0, nums, montant, coul, serie,
                                titre_jeu, telephone, style=style,
                                evenement_id=evenement_id)
                serie += 1
                faites += 1
        c.setFillColor(colors.Color(0.72, 0.72, 0.72))
        c.setFont("Helvetica", 5.4)
        c.drawCentredString(PAGE_W / 2, PAGE_H - 5 * mm, "%03d" % no_page)
        c.showPage()
        no_page += 1

    c.save()
    buf.seek(0)
    return buf


if __name__ == "__main__":
    with open("test_corsica.pdf", "wb") as f:
        f.write(generer_pdf(nb_cartes=8, couleur=True, telephone="89 22 23 05").read())
    print("CORSICA g\u00e9n\u00e9r\u00e9")
