"""
🌼 VANILLE DE DONA — LE 136e JEU (02/08, sur le dessin de vanille de Maeva)
5 numéros (30-75) triés puis posés fleur → O de DONA → tige → grappe → feuille,
et LE TRÉSOR au centre : un montant en francs (5/10/15/20/50/100).
Le montant se gagne selon les règles de la salle (l'organisateur seul décide).
6 cartons par feuille A4, dessin de vanille pâli en fond (économie de toner).
"""
import io
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

# ── fonte des chiffres (grasse, comme POW/QUINES/TUREIA ATOLL) ───────────
_POLICE_ECO = "Helvetica-Bold"
try:
    pdfmetrics.registerFont(TTFont("DJBOLDVA", "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"))
    _POLICE_ECO = "DJBOLDVA"
except Exception:
    pass
_GRIS_ECO = colors.Color(0.5, 0.5, 0.5)
_GRIS_P15 = colors.Color(0.25, 0.25, 0.25)


def _style_chiffres(style):
    if str(style).lower() in ("p15", "premium"):
        return _POLICE_ECO, _GRIS_P15
    return _POLICE_ECO, _GRIS_ECO


PAGE_W, PAGE_H = A4
COLS_PAGE, ROWS_PAGE = 2, 3          # 6 cartons / A4 (94 × 91,7 mm)
MARGIN_X, MARGIN_TOP, MARGIN_BOT = 9 * mm, 5 * mm, 9 * mm
GUTTER_X, GUTTER_Y = 4 * mm, 4 * mm
CARD_W = (PAGE_W - 2 * MARGIN_X - (COLS_PAGE - 1) * GUTTER_X) / COLS_PAGE
CARD_H = (PAGE_H - MARGIN_TOP - MARGIN_BOT - (ROWS_PAGE - 1) * GUTTER_Y) / ROWS_PAGE

GRAINE = 986000                       # graine propre (985000 = TUREIA ATOLL)
PLAGE = (30, 75)                      # les boules de la vanille
MONTANTS = [5, 10, 15, 20, 50, 100]   # références de la maison (pions de valeur)

RAINBOW = ["#6A994E", "#2A9D8F", "#BC6C25", "#457B9D", "#E76F51", "#7209B7",
           "#E63946", "#F4A261", "#8E7DBE", "#264653", "#D62828", "#F72585"]

# ── géométrie du carton (points PDF, mesurée sur le modèle certifié) ─────
T_NUM, DY_NUM = 25.5, 8.72           # chiffres des postes (gras, hachés)
T_O, DY_O, R_O = 19.0, 6.54, 14.75   # le numéro dans le O de DONA
R_POSTE = 17.55                       # rond blanc des 4 postes (6,2 mm)
R_TRESOR, R_ANNEAU = 32.0, 25.5       # bulle du trésor + anneau intérieur
T_MONTANT, DY_MONTANT = 29.0, 4.64    # 💰 montant à 25 points (sceau Maeva)
Y_TITRE, Y_CARTE = 232.87, 223.00     # lignes de base de l'en-tête
Y_O = 236.70                          # centre du O de DONA
IMG_X, IMG_Y, IMG_W = 31.7, 9.95, 203.0
Y_FOOTER = 7.43

# les 4 postes autour du trésor : (nom, cx, cy) en points depuis le coin
# bas-gauche du carton — ordre de pose = tirage TRIÉ (fleur, O, tige,
# grappe, feuille) : le carton se lit du plus petit au plus grand.
POSTES = [
    ("la fleur",   84.45, 137.70),
    ("la tige",   173.85, 178.90),
    ("la grappe", 116.95,  55.30),
    ("la feuille", 208.35, 113.00),
]


def _gen_carte(rng):
    """5 numéros DISTINCTS dans 30-75, TRIÉS — puis le montant du trésor."""
    nums = sorted(rng.sample(range(PLAGE[0], PLAGE[1] + 1), 5))
    montant = rng.choice(MONTANTS)
    return nums, montant


import os as _os
_DOSSIER = _os.path.dirname(_os.path.abspath(__file__))
_NOMS_IMAGE = ['vanille_dona.png']
_IMAGE_VANILLE = next((_os.path.join(_DOSSIER, n) for n in _NOMS_IMAGE
                       if _os.path.exists(_os.path.join(_DOSSIER, n))),
                      _os.path.join(_DOSSIER, _NOMS_IMAGE[0]))
_RATIO_VANILLE = 760.0 / 771.0        # proportions du dessin de la vanille


def _fond(c, x0, y0):
    """Le dessin de vanille de Maeva, déjà pâli pour l'encre."""
    if _os.path.exists(_IMAGE_VANILLE):
        try:
            iw = IMG_W
            ih = iw / _RATIO_VANILLE
            c.drawImage(_IMAGE_VANILLE, x0 + IMG_X, y0 + IMG_Y, iw, ih,
                        mask="auto", preserveAspectRatio=True)
        except Exception:
            pass


def _dessiner_carte(c, x0, y0, nums, montant, couleur_hex, serie,
                    titre_jeu="", telephone="", style="eco", evenement_id=""):
    police_ch, gris_ch = _style_chiffres(style)
    col = colors.HexColor(couleur_hex)

    c.setStrokeColor(col); c.setLineWidth(0.9)
    c.roundRect(x0, y0, CARD_W, CARD_H, 1.5 * mm, stroke=1, fill=0)
    if _sec:
        _sec.cadre_micro(c, x0, y0, CARD_W, CARD_H, serie, retrait=1.0 * mm)

    # le dessin d'abord : les boules blanches se posent dessus
    _fond(c, x0, y0)

    # ── en-tête : « Vanille de D◯NA », le O est une boule qui joue ───────
    n_fleur, n_o, n_tige, n_grappe, n_feuille = nums
    gauche, droite = "Vanille de D", "NA"
    wl = _lg(gauche, "Helvetica-Bold", 11)
    wr = _lg(droite, "Helvetica-Bold", 11)
    sx = x0 + CARD_W / 2 - (wl + 2 * R_O + wr) / 2
    o_cx, o_cy = sx + wl + R_O, y0 + Y_O
    c.setFillColor(colors.white); c.setStrokeColor(col); c.setLineWidth(0.9)
    c.circle(o_cx, o_cy, R_O, stroke=1, fill=1)
    c.setFillColor(col); c.setFont("Helvetica-Bold", 11)
    c.drawString(sx, y0 + Y_TITRE, gauche)
    c.drawString(sx + wl + 2 * R_O, y0 + Y_TITRE, droite)
    if _sec:
        _sec.chiffre_micro(c, n_o, o_cx, o_cy - DY_O, T_O, gris_ch, police_ch)
    else:
        c.setFillColor(gris_ch); c.setFont(police_ch, T_O)
        c.drawCentredString(o_cx, o_cy - DY_O, str(n_o))

    # la ligne d'identité : N° de série, titre du client, téléphone
    ligne = "Carte N\u00b0 %05d" % serie
    if titre_jeu and titre_jeu.strip().upper() not in ("VANILLE", "VANILLE DE DONA"):
        ligne += "  \u00b7  " + titre_jeu.strip()[:26]
    if telephone:
        ligne += "  \u00b7  " + str(telephone)[:16]
    t = 6.4
    while t > 4.6 and _lg(ligne, "Helvetica", t) > CARD_W - 10 * mm:
        t -= 0.2
    c.setFillColor(col); c.setFont("Helvetica", t)
    c.drawCentredString(x0 + CARD_W / 2, y0 + Y_CARTE, ligne)

    # ── les 4 postes de la vanille (tirage trié, boules blanches) ────────
    for (nom, cx, cy), n in zip(POSTES, (n_fleur, n_tige, n_grappe, n_feuille)):
        px, py = x0 + cx, y0 + cy
        c.setFillColor(colors.white); c.setStrokeColor(col); c.setLineWidth(0.9)
        c.circle(px, py, R_POSTE, stroke=1, fill=1)
        if _sec:
            _sec.chiffre_micro(c, n, px, py - DY_NUM, T_NUM, gris_ch, police_ch)
        else:
            c.setFillColor(gris_ch); c.setFont(police_ch, T_NUM)
            c.drawCentredString(px, py - DY_NUM, str(n))
        c.setFillColor(col); c.setFont("Helvetica", 4.6)
        c.drawCentredString(px, py - R_POSTE - 7.48, nom)

    # ── 💰 LE TRÉSOR — la bulle du montant, AU CENTRE (sceau Maeva) ──────
    tx, ty = x0 + CARD_W / 2, y0 + CARD_H / 2 - 17.0
    c.setFillColor(colors.white); c.setStrokeColor(col); c.setLineWidth(1.3)
    c.circle(tx, ty, R_TRESOR, stroke=1, fill=1)
    c.setLineWidth(0.6)
    c.circle(tx, ty, R_ANNEAU, stroke=1, fill=0)
    # le montant au plus grand calibre qui tient dans le disque (« 100 » se serre)
    t_m = T_MONTANT
    while _lg(str(montant), _POLICE_ECO, t_m) > 2 * R_TRESOR - 7 and t_m > 20:
        t_m -= 0.5
    c.setFillColor(col); c.setFont(_POLICE_ECO, t_m)
    c.drawCentredString(tx, ty - 0.16 * t_m, str(montant))
    c.setFont("Helvetica-Bold", 8.8)
    c.drawCentredString(tx, ty - 20.5, "FRANCS")
    c.setFillColor(col); c.setFont("Helvetica", 4.6)
    c.drawCentredString(tx, ty - R_TRESOR - 7.48, "le tr\u00e9sor")

    # la règle de prudence : le montant n'est PAS une promesse de la maison
    c.setFillColor(colors.Color(0.55, 0.55, 0.55)); c.setFont("Helvetica", 4.2)
    c.drawCentredString(x0 + CARD_W / 2, y0 + Y_FOOTER,
                        "COCHEZ \u00b7 le montant se gagne selon les r\u00e8gles de la salle")

    # QR de contrôle — dans sa poche blanche, bas-droit
    if _sec and evenement_id:
        try:
            q = 12.0 * mm
            _sec.carton_qr(c, x0 + 238.1 - q / 2, y0 + 26.96 - q / 2,
                           q, evenement_id, serie, avec_code=False)
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
                nums, montant = _gen_carte(rng)
                coul = (couleur_perso if (couleur and couleur_perso)
                        else RAINBOW[(serie - 1) % len(RAINBOW)] if couleur else "#9A9A9A")
                _dessiner_carte(c, x0, y0, nums, montant, coul, serie,
                                titre_jeu, telephone, style=style,
                                evenement_id=evenement_id)
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
    pdf = generer_pdf(nb_cartes=6, couleur=True, telephone="89 22 23 05")
    with open("test_vanille.pdf", "wb") as f:
        f.write(pdf.read())
    print("VANILLE DE DONA g\u00e9n\u00e9r\u00e9e")
