# -*- coding: utf-8 -*-
"""
MANAPRINT — Générateur TAHITI (ex-FLÈCHE, format A4)

🌺 REFAIT LE 09/08 (sceau Maeva) : la BOUTEILLE de Maeva occupe tout le
carton, et les DIX NUMÉROS montent DANS LE VERRE — deux par lettre du
mot BINGO. Au pied, sa fleur d'hibiscus, et DANS LE CŒUR DE LA FLEUR,
NOS DÉS (ceux de motifs.py, la marque de la maison).

RÈGLE (sceau Maeva 09/08) : 10 numéros, DEUX PAR LETTRE —
  B : 1-15 · I : 16-30 · N : 31-45 · G : 46-60 · O : 61-75
Le sac du crieur ne change pas : c'est toujours 1 à 75.

⚡ ÉCONOMIE D'ENCRE : le dessin est pâli une fois pour toutes à la
découpe, et les dés sont tracés au trait.
"""
import io
from reportlab.pdfbase.pdfmetrics import stringWidth as _lgt
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
PLAGES = [(1, 15), (16, 30), (31, 45), (46, 60), (61, 75)]
# La FLÈCHE : rangées occupées par colonne (0 = rangée du haut)
# c1 : haut + plancher · c2 : 2e + plancher · c3 : 4e + plancher
# c4 : 3e, 4e + plancher · c5 : toutes (le bord droit complet)
RANGEES = [(0, 4), (1, 4), (3, 4), (2, 3, 4), (0, 1, 2, 3, 4)]
CASE_QR = (0, 2)   # (rangée, colonne) de la case barrée qui accueille le QR

# 🍾 LA BOUTEILLE DE MAEVA, et le cœur de sa fleur (mesuré au pixel).
_RATIO_TAHITI = 380.0 / 730.0
FLEUR = (0.005, 0.697, 0.000, 0.418)     # x0, x1, y0, y1 du bloc fleur
# 🍾 LE CORPS DE LA BOUTEILLE, mesuré ligne par ligne : c'est là que
# vivent les numéros (repère PDF, depuis le bas).
CORPS = (0.410, 0.865, 0.150, 0.585)     # x0, x1, y0, y1 du verre
# ⚠️ Le bas du verre est laisse a la FLEUR : les numeros s'arretent au-dessus.
LETTRES_BINGO = "BINGO"
# 💰 LE BONUS DE LA FLEUR : le montant est TIRE avec la carte.
MONTANTS = [5, 10, 20, 50, 100]
# ⚠️ le bas du corps est laisse a la FLEUR : les numeros s arretent au-dessus.
import os as _os2


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


_IMAGE_TAHITI = _choisir_image("tahiti_bouteille", _RATIO_TAHITI)


def _un_de(c, cx, cy, t, valeur, col, gris_ch):
    """🎲 LE DÉ DU CASINO — exactement le tracé de nos jeux SUN/POW/WIN
    CASINO : carré arrondi blanc bordé couleur, points bien francs
    disposés comme sur les dés du commerce.

    C'est le « principe casino » voulu par Maeva (09/08) : les mêmes
    proportions partout, pour que le joueur reconnaisse nos dés d'un
    seul coup d'œil.
    """
    r = t / 2.0
    c.setStrokeColor(col)
    c.setLineWidth(1.1)
    c.setFillColor(colors.white)
    c.roundRect(cx - r, cy - r, t, t, t * 0.18, stroke=1, fill=1)
    q = t * 0.26
    pos = {1: [(0, 0)], 2: [(-q, q), (q, -q)], 3: [(-q, q), (0, 0), (q, -q)],
           4: [(-q, q), (q, q), (-q, -q), (q, -q)],
           5: [(-q, q), (q, q), (0, 0), (-q, -q), (q, -q)],
           6: [(-q, q), (q, q), (-q, 0), (q, 0), (-q, -q), (q, -q)]}[valeur]
    c.setFillColor(gris_ch)
    for dx, dy in pos:
        c.circle(cx + dx, cy + dy, t * 0.085, stroke=0, fill=1)


# 🎲 la décomposition du casino : au-delà de 6, DEUX dés dont la somme
# donne le nombre — la règle de SUN CASINO, reprise telle quelle.
DECOMP_DES = {7: (4, 3), 8: (4, 4), 9: (5, 4), 10: (5, 5), 11: (6, 5), 12: (6, 6)}


def _des_casino(c, valeur, cx, cy, ech, col, gris_ch):
    """Pose la valeur EN DÉS, à la manière du casino : un seul dé
    jusqu'à 6, deux dés au-delà."""
    if valeur <= 6:
        _un_de(c, cx, cy, 11.5 * mm * ech, valeur, col, gris_ch)
    else:
        a, b = DECOMP_DES.get(valeur, (5, 4))
        _un_de(c, cx - 4.4 * mm * ech, cy, 7.8 * mm * ech, a, col, gris_ch)
        _un_de(c, cx + 4.4 * mm * ech, cy, 7.8 * mm * ech, b, col, gris_ch)



# 🍾 6 cartes / A4 (sceau Maeva 09/08) : le carton d'avant laissait
# 28 mm de blanc de chaque cote de la bouteille. En le serrant sur
# elle, on en tient TROIS par rangee au lieu de deux — +50 % de
# cartons par feuille, et les chiffres ne perdent que 2 pt.
COLS_PAGE = 3
ROWS_PAGE = 2   # 4 cartes / A4 : les numéros vivent DANS la bouteille
MARGIN_X = 8 * mm
MARGIN_TOP = 10 * mm
MARGIN_BOT = 7 * mm
GUTTER_X = 3.5 * mm
GUTTER_Y = 4 * mm

CARD_W = (PAGE_W - 2 * MARGIN_X - (COLS_PAGE - 1) * GUTTER_X) / COLS_PAGE
CARD_H = (PAGE_H - MARGIN_TOP - MARGIN_BOT - (ROWS_PAGE - 1) * GUTTER_Y) / ROWS_PAGE
HDR_H = 6 * mm


def _gen_carte(rng):
    """🎰 DIX numéros : DEUX par lettre du mot BINGO, triés.

    B : 1-15 · I : 16-30 · N : 31-45 · G : 46-60 · O : 61-75
    (sceau Maeva 09/08 — avant, la flèche en portait 14.)
    """
    return ([sorted(rng.sample(range(lo, hi + 1), 2)) for (lo, hi) in PLAGES],
            rng.choice(MONTANTS))


def _dessiner_carte(c, x0, y0, cols_nums, bonus_des, couleur_hex, serie, titre_jeu="", telephone="", style="eco", evenement_id=""):
    police_ch, gris_ch = _style_chiffres(style)
    col = colors.HexColor(couleur_hex)
    cell_w = CARD_W / 5

    # Bordure carte
    c.setStrokeColor(col); c.setLineWidth(0.8)
    c.roundRect(x0, y0, CARD_W, CARD_H, 1.5 * mm, stroke=1, fill=0)
    if _sec:  # cadre intérieur en microtexte (sécurité anti-photocopie)
        _sec.cadre_micro(c, x0, y0, CARD_W, CARD_H, serie, retrait=0.9 * mm)

    # En-tête : nom du jeu (TOUJOURS visible) + série (fidèle au modèle)
    hdr_bas = y0 + CARD_H - HDR_H
    c.setStrokeColor(col); c.setLineWidth(0.4)
    c.line(x0, hdr_bas, x0 + CARD_W, hdr_bas)
    l1 = "TAHITI"
    if titre_jeu and "TAHITI" not in titre_jeu.strip().upper():
        l1 = "TAHITI \u00b7 " + titre_jeu.strip() + ""
    if telephone:
        l1 += " " + telephone
    c.setFillColor(col); c.setFont(POLICE, 5)
    c.drawString(x0 + 2.5 * mm, hdr_bas + 1.8 * mm, l1[:54])
    c.setFont(POLICE, 6.5)
    c.drawRightString(x0 + CARD_W - 2.5 * mm, hdr_bas + 1.7 * mm, "%06d" % serie)

    # ═══ 🍾 LES QUATORZE NUMÉROS DANS LA BOUTEILLE ═══
    z_top = hdr_bas - 1.0 * mm
    z_bot = y0 + 1.5 * mm
    z_h = z_top - z_bot

    ilw = CARD_W - 3.5 * mm      # le carton est taille sur la bouteille
    ilh = ilw / _RATIO_TAHITI
    if ilh > z_h:
        ilh = z_h
        ilw = ilh * _RATIO_TAHITI
    ilx = x0 + (CARD_W - ilw) / 2
    ily = z_bot + (z_h - ilh) / 2
    if _os2.path.exists(_IMAGE_TAHITI):
        try:
            c.drawImage(_IMAGE_TAHITI, ilx, ily, ilw, ilh, mask="auto",
                        preserveAspectRatio=True)
        except Exception:
            pass

    # ── 🎲 NOS DÉS, AU CŒUR DE LA FLEUR ─────────────────────────────────
    # 💰 LE BONUS, AU CŒUR DE LA FLEUR (sceau Maeva 09/08) : un montant
    # en francs, tiré avec la carte — 5, 10, 20, 50 ou 100.
    fcx = ilx + 0.268 * ilw
    fcy = ily + 0.143 * ilh
    tm = min(ilw * 0.125, ilh * 0.065) * 72 / 25.4 * 0.72
    tm = min(tm, 24.0)
    # ⚠️ le bloc « montant + FRANCS » est CENTRÉ sur le cœur : le chiffre
    # remonte d'un quart pour que l'ensemble tombe juste dans le calice.
    y_chiffre = fcy - tm * 0.34 + tm * 0.22
    if _sec:
        _sec.chiffre_micro(c, bonus_des, fcx, y_chiffre, tm, gris_ch, police_ch)
    else:
        c.setFillColor(gris_ch)
        c.setFont(police_ch, tm)
        c.drawCentredString(fcx, y_chiffre, str(bonus_des))
    c.setFillColor(col)
    c.setFont("Helvetica-Bold", tm * 0.32)
    c.drawCentredString(fcx, y_chiffre - tm * 0.40, "FRANCS")

    # ── les DIX numéros, DANS le verre : une rangée par lettre ──────────
    # Chaque rangée porte sa lettre du mot BINGO et ses DEUX numéros.
    gx = ilx + CORPS[0] * ilw
    gw = (CORPS[1] - CORPS[0]) * ilw
    gy = ily + CORPS[2] * ilh
    gh = (CORPS[3] - CORPS[2]) * ilh
    NR = 5
    chh = gh / NR
    LET_W = gw * 0.15                      # la colonne des lettres, à gauche
    cw2 = (gw - LET_W) / 2.0
    taille = 34.0
    # ⚠️ 0,74 et non 0,80 : deux nombres par rangée, il leur faut de l'air
    while taille > 12 and (_lgt("88", "Helvetica-Bold", taille) > cw2 * 0.74
                           or taille * 0.72 > chh * 0.74):
        taille -= 0.5
    for ri in range(NR):
        cyc = gy + gh - (ri + 0.5) * chh
        # la lettre B·I·N·G·O
        c.setFillColor(col)
        c.setFont("Helvetica-Bold", taille * 0.46)
        c.drawCentredString(gx + LET_W / 2, cyc - taille * 0.46 * 0.34,
                            LETTRES_BINGO[ri])
        # ses deux numéros
        for ci in range(2):
            val = cols_nums[ri][ci]
            nx = gx + LET_W + (ci + 0.5) * cw2
            ny = cyc - taille * 0.34
            if _sec:
                _sec.chiffre_micro(c, val, nx, ny, taille, gris_ch, police_ch)
            else:
                c.setFillColor(gris_ch)
                c.setFont(police_ch, taille)
                c.drawCentredString(nx, ny, str(val))

    # QR de vérification — dans sa case barrée du haut
    if _sec and evenement_id:
        try:
            _q = 11.0 * mm
            _sec.carton_qr(c, x0 + CARD_W - _q - 3.0 * mm, y0 + 2.5 * mm,
                           _q, evenement_id, serie, avec_code=False)
        except Exception:
            pass


def generer_pdf(nb_cartes=6, serie_start=1, theme="", couleur=True,
                nom_evenement="", titre_jeu="", couleur_perso="", date_lieu="", telephone="",
                style="eco", evenement_id="", page_start=1):
    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=A4, pageCompression=1)

    nb_cartes = max(1, min(int(nb_cartes), 10000))
    par_page = COLS_PAGE * ROWS_PAGE
    nb_pages = (nb_cartes + par_page - 1) // par_page

    rng = random.Random(935500 + int(serie_start))
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
                cols_nums, bonus_des = _gen_carte(rng)
                coul = (couleur_perso if (couleur and couleur_perso)
                        else RAINBOW[(serie - 1) % len(RAINBOW)] if couleur else "#9A9A9A")
                _dessiner_carte(c, x0, y0, cols_nums, bonus_des, coul, serie, titre_jeu, telephone,
                                style=style, evenement_id=evenement_id)
                serie += 1
                faites += 1

        c.showPage()
        no_page += 1

    c.save()
    buf.seek(0)
    return buf


if __name__ == "__main__":
    pdf = generer_pdf(nb_cartes=6, couleur=True,
                      nom_evenement="ASSOCIATION TE MANU", titre_jeu="Grand Loto",
                      telephone="689 89 22 23 05")
    with open("test_fleche.pdf", "wb") as f:
        f.write(pdf.read())
    print("FLÈCHE généré")
