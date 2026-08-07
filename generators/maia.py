"""
🍌 MAIA — LA BANANE MAÏÀ (né le 06/08, sur l'image et l'idée de Maeva)

Le jeu WOW 6 BOULES devient MAIA. Sur chaque carton, la banane Maïà
apparaît TROIS FOIS, et chaque fois elle tend sa pancarte : dedans, DEUX
numéros séparés par une DIAGONALE — six numéros par carton.

RÈGLE (celle de WOW 6, conservée) : 6 numéros DISTINCTS tirés de 30 à 59.
ENCRE : le dessin est pâli une fois pour toutes à la découpe ; les
chiffres suivent la teinte de la maison (app.py).
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
from reportlab.pdfbase.pdfmetrics import stringWidth as _lg

try:
    from generators import securite as _sec
except ImportError:
    try:
        import securite as _sec
    except ImportError:
        _sec = None

_POLICE_ECO = "Helvetica-Bold"
try:
    pdfmetrics.registerFont(TTFont("DJBOLDMAIA", "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"))
    _POLICE_ECO = "DJBOLDMAIA"
except Exception:
    pass
_POLICE_P15 = _POLICE_ECO
_GRIS_ECO = colors.Color(0.50, 0.50, 0.50)     # imposé au boot par app.py
_GRIS_P15 = colors.Color(0.25, 0.25, 0.25)


def _style_chiffres(style):
    """Retourne (police, gris) des chiffres selon la gamme choisie."""
    if str(style).lower() in ("p15", "premium"):
        return _POLICE_P15, _GRIS_P15
    return _POLICE_ECO, _GRIS_ECO


PAGE_W, PAGE_H = A4
COLS_PAGE, ROWS_PAGE = 2, 6               # 12 cartes / A4 — le carton est
                                          # resserre juste ce qu'il faut :
                                          # SANS QR, il n'y a plus un blanc
                                          # perdu (sceau Maeva 06/08).
MARGIN_X, MARGIN_TOP, MARGIN_BOT = 9 * mm, 6 * mm, 9 * mm
GUTTER_X, GUTTER_Y = 4 * mm, 4 * mm
CARD_W = (PAGE_W - 2 * MARGIN_X - (COLS_PAGE - 1) * GUTTER_X) / COLS_PAGE
CARD_H = (PAGE_H - MARGIN_TOP - MARGIN_BOT - (ROWS_PAGE - 1) * GUTTER_Y) / ROWS_PAGE

GRAINE = 989000                            # 988000 = BNG
PLAGE = (30, 59)                           # la règle de WOW 6, conservée
NB_NUMS = 6
TAILLE_CHIFFRE = 21

# 🍌 le dessin de Maïà et SA PANCARTE.
_RATIO_MAIA = 1.028                        # proportions du dessin
# la case libre de la pancarte, en fractions du dessin (mesurée au pixel) :
CASE = (0.009, 0.610, 0.038, 0.671)        # x0, x1, y0, y1


def _choisir_image(motif, ratio_attendu):
    """🛟 Retrouve le dessin, quel que soit son nom de fichier.

    Au téléversement, le nom peut garder un préfixe de livraison ou
    recevoir un « (1) », et une ancienne version peut rester dans le
    dossier. On prend donc, parmi les fichiers dont le nom contient
    `motif`, celui dont les PROPORTIONS collent au dessin attendu.
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
    meilleur, ecart_min = candidats[0], 9e9
    for chemin in candidats:
        try:
            from PIL import Image as _Im
            with _Im.open(chemin) as im:
                ecart = abs(im.width / float(im.height) - ratio_attendu)
        except Exception:
            continue
        if ecart < ecart_min:
            meilleur, ecart_min = chemin, ecart
    return meilleur


_IMAGE_MAIA = _choisir_image("maia", _RATIO_MAIA)

RAINBOW = ["#6A994E", "#2A9D8F", "#BC6C25", "#457B9D", "#E76F51", "#7209B7",
           "#E63946", "#F4A261", "#8E7DBE", "#264653", "#D62828", "#F72585"]


def _gen_carte(rng):
    """6 numéros distincts de 30 à 59, triés."""
    return sorted(rng.sample(range(PLAGE[0], PLAGE[1] + 1), NB_NUMS))


def _maia(c, x, y, larg, deux, col, gris_ch, police_ch):
    """UNE Maïà avec sa pancarte : le dessin, puis les DEUX numéros
    séparés par une diagonale — l'un en haut à gauche, l'autre en bas
    à droite, comme deux triangles qui se répondent."""
    haut = larg / _RATIO_MAIA
    if _os.path.exists(_IMAGE_MAIA):
        try:
            c.drawImage(_IMAGE_MAIA, x, y, larg, haut, mask="auto",
                        preserveAspectRatio=True)
        except Exception:
            pass
    # la case libre de la pancarte
    cx0 = x + CASE[0] * larg
    cx1 = x + CASE[1] * larg
    cy0 = y + CASE[2] * haut
    cy1 = y + CASE[3] * haut
    cw, ch = cx1 - cx0, cy1 - cy0
    # LA DIAGONALE : du coin bas-gauche au coin haut-droit
    c.setStrokeColor(col)
    c.setLineWidth(1.1)
    c.line(cx0 + cw * 0.08, cy0 + ch * 0.14, cx1 - cw * 0.18, cy1 - ch * 0.12)
    # le premier numéro en HAUT À GAUCHE, le second en BAS À DROITE
    # ⚠️ la pancarte est PENCHÉE : son bord droit fuit vers la gauche en
    # descendant. Le numéro du bas se range donc plus au centre, sinon il
    # déborde du carton de Maïà.
    for n, (fx, fy) in zip(deux, ((0.28, 0.70), (0.62, 0.28))):
        nx = cx0 + cw * fx
        ny = cy0 + ch * fy - TAILLE_CHIFFRE * 0.36
        if _sec:
            _sec.chiffre_micro(c, n, nx, ny, TAILLE_CHIFFRE, gris_ch, police_ch)
        else:
            c.setFillColor(gris_ch)
            c.setFont(police_ch, TAILLE_CHIFFRE)
            c.drawCentredString(nx, ny, str(n))


def _dessiner_carte(c, x0, y0, nums, couleur_hex, serie,
                    titre_jeu="", telephone="", style="eco", evenement_id=""):
    police_ch, gris_ch = _style_chiffres(style)
    col = colors.HexColor(couleur_hex)

    c.setStrokeColor(col)
    c.setLineWidth(0.9)
    c.roundRect(x0, y0, CARD_W, CARD_H, 1.5 * mm, stroke=1, fill=0)
    if _sec:
        _sec.cadre_micro(c, x0, y0, CARD_W, CARD_H, serie, retrait=1.0 * mm)

    # ── la ligne d'identité (le nom du jeu s'écrit TOUJOURS) ─────────────
    ligne = "MAIA"
    if titre_jeu and titre_jeu.strip().upper() != "MAIA":
        ligne += "  \u2014  " + titre_jeu.strip()[:26]
    if telephone:
        ligne += "  \u00b7  " + str(telephone)[:16]
    t = 7.4
    while t > 4.6 and _lg(ligne, "Helvetica-Bold", t) > CARD_W - 8 * mm:
        t -= 0.2
    c.setFillColor(col)
    c.setFont("Helvetica-Bold", t)
    c.drawCentredString(x0 + CARD_W / 2, y0 + CARD_H - 5.8 * mm, ligne)

    # ── les TROIS Maïà : deux en haut, une en bas au milieu ─────────────
    # 🍌 LES TROIS MAÏÀ EN LIGNE (choix du 06/08) : le carton est large et
    # bas ; alignees, elles sont PLUS GRANDES qu'en triangle (28 mm au lieu
    # de 26) et le carton respire mieux.
    # ⚠️ 06/08 : Maeva n'aimait pas le grand vide sous le titre. Les Maïà
    # remontent donc JUSTE SOUS l'en-tete et prennent toute la largeur
    # disponible ; ce qui reste de blanc se range en bas, ou vivent le
    # numero de carte et le QR — la, il est a sa place.
    ecart = 1.2 * mm
    larg = (CARD_W - 5.0 * mm - 2 * ecart) / 3
    haut = larg / _RATIO_MAIA
    ligne_y = y0 + CARD_H - 8.2 * mm - haut          # collee sous le titre
    places = [(x0 + 2.5 * mm + k * (larg + ecart), ligne_y) for k in range(3)]
    for (px, py), duo in zip(places, (nums[0:2], nums[2:4], nums[4:6])):
        _maia(c, px, py, larg, duo, col, gris_ch, police_ch)

    # ── le pied : n° de carte + QR, dans le coin libre ──────────────────
    # le pied : une seule ligne discrete, le carton n'a plus de place a perdre
    c.setFillColor(col)
    c.setFont("Helvetica", 5.4)
    c.drawString(x0 + 4.0 * mm, y0 + 3.0 * mm, "Carte N\u00b0 %05d" % serie)
    # 🚫 PAS DE QR sur MAIA (choix Maeva 06/08) : le carton est trop
    # resserre pour lui, et c'est cette place gagnee qui permet
    # 12 grilles par feuille au lieu de 8.



def generer_pdf(nb_cartes=6, serie_start=1, theme="", couleur=True,
                nom_evenement="", titre_jeu="", telephone="", date_lieu="",
                couleur_perso=None, style="eco", evenement_id="", motif=""):
    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=A4)
    rng = random.Random(GRAINE + serie_start)
    serie, faites, no_page = serie_start, 0, 1

    while faites < nb_cartes:
        for row in range(ROWS_PAGE):
            for coln in range(COLS_PAGE):
                if faites >= nb_cartes:
                    break
                x0 = MARGIN_X + coln * (CARD_W + GUTTER_X)
                y0 = MARGIN_BOT + (ROWS_PAGE - 1 - row) * (CARD_H + GUTTER_Y)
                coul = (couleur_perso if (couleur and couleur_perso)
                        else RAINBOW[(serie - 1) % len(RAINBOW)] if couleur else "#9A9A9A")
                _dessiner_carte(c, x0, y0, _gen_carte(rng), coul, serie,
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
    with open("test_maia.pdf", "wb") as f:
        f.write(generer_pdf(nb_cartes=6, couleur=True, telephone="89 22 23 05").read())
    print("MAIA g\u00e9n\u00e9r\u00e9")
