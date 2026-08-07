"""
🏝️ MOOREA — LA GRILLE DE L'ÎLE SŒUR (revisité 01/08 sur le croquis de Maeva)
Chaque commune du tour de l'île porte son numéro dans un rond blanc ;
la côte est tracée AU TRAIT (économie de toner : les montagnes crayonnées
du croquis ne sont PAS reprises). 12 grilles par feuille A4, comme POW.
"""
import io
import json
import random
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

try:
    from generators import securite as _sec
except ImportError:
    try:
        import securite as _sec
    except ImportError:
        _sec = None

# ── fonte des chiffres (grasse, comme POW/QUINES) ────────────────────────
_POLICE_ECO = "Helvetica-Bold"
try:
    pdfmetrics.registerFont(TTFont("DJBOLDM", "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"))
    _POLICE_ECO = "DJBOLDM"
except Exception:
    pass
_GRIS_ECO = colors.Color(0.5, 0.5, 0.5)
_GRIS_P15 = colors.Color(0.25, 0.25, 0.25)


def _style_chiffres(style):
    if str(style).lower() in ("p15", "premium"):
        return _POLICE_ECO, _GRIS_P15
    return _POLICE_ECO, _GRIS_ECO


PAGE_W, PAGE_H = A4
COLS_PAGE, ROWS_PAGE = 2, 3          # 6 grilles / A4 — l'île en grand, sans blanc perdu
MARGIN_X, MARGIN_TOP, MARGIN_BOT = 8 * mm, 10 * mm, 10 * mm
GUTTER_X, GUTTER_Y = 4 * mm, 4 * mm
CARD_W = (PAGE_W - 2 * MARGIN_X - (COLS_PAGE - 1) * GUTTER_X) / COLS_PAGE
CARD_H = (PAGE_H - MARGIN_TOP - MARGIN_BOT - (ROWS_PAGE - 1) * GUTTER_Y) / ROWS_PAGE

T_NUM = 30                            # 🔢 chiffres 30 points (sceau Maeva)
GRAINE = 983000                       # graine propre (982000 = QUINES 90)

RAINBOW = ["#E63946", "#F4A261", "#E9C46A", "#2A9D8F", "#264653",
           "#8E7DBE", "#D62828", "#457B9D", "#6A994E", "#BC6C25",
           "#7209B7", "#F72585"]

# ── la côte de MOOREA, relevée sur le croquis de Maeva (fractions) ───────
COTE = [
    (0.9472, 0.9862), (0.9074, 1.0000), (0.8778, 0.9585), (0.7352, 0.9194),
    (0.6389, 0.9228), (0.6148, 0.8975), (0.5944, 0.7846), (0.5481, 0.9055),
    (0.5407, 0.8675), (0.5287, 0.9055), (0.5417, 0.9101), (0.4907, 0.9124),
    (0.5231, 0.9412), (0.4556, 0.9562), (0.4546, 0.9274), (0.4648, 0.9389),
    (0.4898, 0.9171), (0.4000, 0.8963), (0.3824, 0.7753), (0.3657, 0.7638),
    (0.3917, 0.7742), (0.3778, 0.7477), (0.3435, 0.7684), (0.3380, 0.8065),
    (0.3639, 0.7650), (0.3380, 0.8479), (0.2991, 0.8940), (0.2093, 0.8975),
    (0.2037, 0.9147), (0.1889, 0.8963), (0.1278, 0.9171), (0.0972, 0.9055),
    (0.0843, 0.9516), (0.0389, 0.9505), (0.0000, 0.8825), (0.0176, 0.8283),
    (0.0074, 0.7684), (0.0333, 0.6959), (0.0296, 0.6325), (0.1407, 0.4493),
    (0.1750, 0.4205), (0.1843, 0.4309), (0.1907, 0.3548), (0.2361, 0.2788),
    (0.2361, 0.2512), (0.2602, 0.2454), (0.2620, 0.2235), (0.2481, 0.2270),
    (0.3019, 0.1751), (0.3194, 0.1198), (0.3639, 0.1152), (0.3796, 0.0438),
    (0.5315, 0.0000), (0.5787, 0.0046), (0.5907, 0.0518), (0.6509, 0.0876),
    (0.6833, 0.1382), (0.6972, 0.1371), (0.6963, 0.1152), (0.7694, 0.1221),
    (0.7046, 0.1302), (0.6880, 0.1509), (0.7870, 0.3341), (0.8204, 0.3641),
    (0.8463, 0.4493), (0.9139, 0.4747), (0.9880, 0.4643), (0.9361, 0.4758),
    (0.9241, 0.6060), (0.9315, 0.6647), (0.9583, 0.6993), (0.9583, 0.7454),
    (1.0000, 0.8018), (0.9907, 0.8848),
]

# ── les 9 communes du tour de l'île (fractions de la zone, écartées pour
#    qu'un nombre de 30 pts tienne dans chaque rond sans toucher son voisin)
COMMUNES = [
    ("Haapiti", 0.1725, 0.8766),
    ("Paopao", 0.4857, 0.9084),
    ("Maharepa", 0.6852, 0.9040),
    ("Temae", 0.9799, 0.8218),
    ("Afareaitu", 0.0588, 0.5779),
    ("Vaiare", 0.9033, 0.4855),
    ("Papetoai", 0.2409, 0.2547),
    ("Teavaro", 0.6817, 0.1522),
    ("Pihaena", 0.4822, 0.0368),
]

# chaque commune tire dans SA plage : le carton fait le tour de 1 à 75
PLAGES_COMMUNES = [(1, 15), (1, 15), (16, 30), (16, 30), (31, 45),
                   (31, 45), (46, 60), (46, 60), (61, 75)]


def _gen_carte(rng):
    """9 numéros — un par commune, chacun dans sa plage, jamais deux fois le même."""
    pris, nums = set(), []
    for a, b in PLAGES_COMMUNES:
        while True:
            n = rng.randint(a, b)
            if n not in pris:
                pris.add(n)
                nums.append(n)
                break
    return nums


import os as _os
_RATIO_ILE = 1000.0 / 752.0     # proportions du CONTOUR de Maeva (06/08)
# \u26a0\ufe0f Ce ratio doit TOUJOURS suivre celui de moorea_ile.png : c'est lui
# qui calcule la zone ou l'ile est dessinee, et donc ou se posent les ronds
# des communes. Un ratio perime = des numeros a cote de leur cote.

def _choisir_image(motif, ratio_attendu):
    """🛟 Retrouve la bonne image, quel que soit son nom de fichier.

    Parmi tous les fichiers du dossier dont le nom contient `motif`,
    on garde celui dont les PROPORTIONS collent au dessin attendu.
    Ainsi, ni un prefixe de livraison, ni un « (1) », ni une ancienne
    version restee la ne peuvent tromper le jeu.
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


_IMAGE_ILE = _choisir_image("moorea_ile", _RATIO_ILE)


def _ile(c, x0, y0, zx, zy, zw, zh, col):
    """Le croquis de Maeva, pâli pour l'encre — repli : la côte au trait."""
    if _os.path.exists(_IMAGE_ILE):
        try:
            iw = zw
            ih = iw / _RATIO_ILE
            if ih > zh:
                ih = zh; iw = ih * _RATIO_ILE
            c.drawImage(_IMAGE_ILE, x0 + zx + (zw - iw) / 2, y0 + zy + (zh - ih) / 2,
                        iw, ih, mask="auto", preserveAspectRatio=True)
            return (zx + (zw - iw) / 2, zy + (zh - ih) / 2, iw, ih)
        except Exception:
            pass
    c.setStrokeColor(col)
    c.setLineWidth(0.7)
    p = c.beginPath()
    px, py = COTE[0]
    p.moveTo(x0 + zx + px * zw, y0 + zy + py * zh)
    for px, py in COTE[1:]:
        p.lineTo(x0 + zx + px * zw, y0 + zy + py * zh)
    p.close()
    c.drawPath(p, stroke=1, fill=0)
    return (zx, zy, zw, zh)


def _dessiner_carte(c, x0, y0, nums, couleur_hex, serie, titre_jeu="", telephone="",
                    style="eco", evenement_id=""):
    police_ch, gris_ch = _style_chiffres(style)
    col = colors.HexColor(couleur_hex)

    c.setStrokeColor(col); c.setLineWidth(0.8)
    c.roundRect(x0, y0, CARD_W, CARD_H, 1.5 * mm, stroke=1, fill=0)
    if _sec:
        _sec.cadre_micro(c, x0, y0, CARD_W, CARD_H, serie, retrait=1.0 * mm)

    # en-tête : le nom du jeu s'écrit TOUJOURS, le titre client s'ajoute
    c.setFillColor(col); c.setFont("Helvetica-Bold", 9.0)
    tete = "MOOREA \u00b7 le tour de l'\u00eele"
    if titre_jeu:
        tete += "  \u2014  " + str(titre_jeu)[:26]
    if telephone:
        tete += "  " + str(telephone)[:16]
    c.drawCentredString(x0 + CARD_W / 2, y0 + CARD_H - 6.4 * mm, tete[:70])
    c.setFont("Helvetica", 7.0)
    c.drawCentredString(x0 + CARD_W / 2, y0 + CARD_H - 10.4 * mm, "Carte N\u00b0 %05d" % serie)

    zx, zy, zw, zh = 4.0 * mm, 5.0 * mm, CARD_W - 8.0 * mm, CARD_H - 18.0 * mm
    zx, zy, zw, zh = _ile(c, x0, y0, zx, zy, zw, zh, col)

    # les 9 communes : rond blanc + numéro 30 pts + nom minuscule
    r = 7.6 * mm
    # 🛟 aucune boule ne sort de la grille (sceau Maeva 01/08) : chaque rond
    # se range à l'intérieur du cadre, avec le nom qui tient dessous.
    BORD = 1.6 * mm
    for (nom, fx, fy), n in zip(COMMUNES, nums):
        cx = x0 + zx + fx * zw
        cy = y0 + zy + fy * zh
        cx = min(max(cx, x0 + r + BORD), x0 + CARD_W - r - BORD)
        cy = min(max(cy, y0 + r + 4.4 * mm), y0 + CARD_H - r - 12.0 * mm)
        c.setFillColor(colors.white); c.setStrokeColor(col); c.setLineWidth(0.6)
        c.circle(cx, cy, r, stroke=1, fill=1)
        if _sec:
            _sec.chiffre_micro(c, n, cx, cy - T_NUM * 0.34, T_NUM, gris_ch, police_ch)
        else:
            c.setFillColor(gris_ch); c.setFont(police_ch, T_NUM)
            c.drawCentredString(cx, cy - T_NUM * 0.34, str(n))
        c.setFillColor(col); c.setFont("Helvetica", 5.6)
        c.drawCentredString(cx, cy - r - 3.0 * mm, nom)

    # QR de contrôle — au cœur de l'île, là où sont les monts
    if _sec and evenement_id:
        try:
            q = 14.0 * mm
            _sec.carton_qr(c, x0 + CARD_W / 2 - q / 2, y0 + zy + zh * 0.44 - q / 2,
                           q, evenement_id, serie)
        except Exception:
            pass


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
                nums = _gen_carte(rng)
                coul = (couleur_perso if (couleur and couleur_perso)
                        else RAINBOW[(serie - 1) % len(RAINBOW)] if couleur else "#9A9A9A")
                _dessiner_carte(c, x0, y0, nums, coul, serie, titre_jeu, telephone,
                                style=style, evenement_id=evenement_id)
                serie += 1
                faites += 1
        c.setFillColor(colors.Color(0.72, 0.72, 0.72)); c.setFont("Helvetica", 5.4)
        c.drawCentredString(PAGE_W / 2, PAGE_H - 6 * mm, "%03d" % no_page)
        c.showPage()
        no_page += 1

    c.save()
    buf.seek(0)
    return buf


if __name__ == "__main__":
    pdf = generer_pdf(nb_cartes=6, couleur=True, titre_jeu="MOOREA", telephone="89 22 23 05")
    with open("test_moorea.pdf", "wb") as f:
        f.write(pdf.read())
    print("MOOREA généré")
