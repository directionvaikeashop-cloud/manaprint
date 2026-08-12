# -*- coding: utf-8 -*-
"""
MANAPRINT — Générateur 4 COIN (jeu des 4 coins, format A4 portrait)

🖨️ REFAIT LE 12/08 (sceau Maeva) : la grille 5×5 laisse place à QUATRE
IMPRIMANTES — une par coin. Chaque imprimante porte SES QUATRE NUMÉROS
dans son bac à papier : « il y a 4 grilles donc 4 imprimantes ».

RÈGLE INCHANGÉE : 16 numéros, quatre par bloc, tirés dans les colonnes
du BINGO 75 — col0 1-15 · col1 16-30 · col3 46-60 · col4 61-75
(la colonne centrale 31-45 reste vide, c'est la croix du jeu).
6 cartes par feuille A4.
"""
import io
from reportlab.pdfbase.pdfmetrics import stringWidth as _lg4
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
try:
    pdfmetrics.registerFont(TTFont("DJB", "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"))
    POLICE_NUM = "DJB"
except Exception:
    POLICE_NUM = "Helvetica-Bold"

RAINBOW = [
    "#E53935", "#FB8C00", "#F9A825", "#43A047", "#00ACC1",
    "#1E88E5", "#3949AB", "#8E24AA", "#D81B60", "#6D4C41",
]
GRIS = colors.Color(0.60, 0.60, 0.60)
GRIS40 = colors.Color(0.60, 0.60, 0.60)
GRIS_CLAIR = colors.Color(0.80, 0.80, 0.80)



# ══ DEUX GAMMES COMMERCIALES (vision Maeva) ══════════════════════════
# ÉCO      : écriture fine DejaVu ExtraLight, gris 0,50 — économie de toner
# PREMIUM  : écriture grasse Helvetica-Bold, gris 0,55 — style P15
from reportlab.pdfbase import pdfmetrics as _pm
from reportlab.pdfbase.ttfonts import TTFont as _TF
try:
    # 🖨️ 12/08 (sceau Maeva) : la GRASSE CONDENSÉE, celle de QUINES 90.
    # Plus étroite qu'une grasse ordinaire, donc on peut la monter plus
    # haut à place égale — et elle se lit de loin. La feuille de sortie
    # de l'imprimante n'offre que 5,3 mm de haut : le gras y compense.
    _pm.registerFont(_TF("DJBOLDC", "/usr/share/fonts/truetype/dejavu/DejaVuSansCondensed-Bold.ttf"))
    _POLICE_ECO = "DJBOLDC"
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

LETTRES = ["4", "C", "O", "I", "N"]
# plages BINGO 75 par colonne (col2 = vide)
PLAGES = [(1, 15), (16, 30), (31, 45), (46, 60), (61, 75)]
# colonnes actives (avec chiffres) = toutes sauf celle du milieu
COLS_ACTIVES = [0, 1, 3, 4]
# rangées remplies (toutes sauf celle du milieu)
ROWS_ACTIVES = [0, 1, 3, 4]

# 🖨️ L'IMPRIMANTE DE MAEVA — les numéros se rangent dans son bac.
_RATIO_IMP = 1.3333
BAC = (0.2902, 0.7098, 0.677, 0.97)   # x0, x1, y0, y1
SORTIE = (0.3023, 0.6977, 0.037, 0.2)   # la feuille qui sort
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


_IMAGE_IMP = _choisir_image("quatre_imprimante", _RATIO_IMP)

COLS_PAGE = 2
ROWS_PAGE = 3
MARGIN_X = 8 * mm
MARGIN_TOP = 8 * mm
MARGIN_BOT = 8 * mm
GUTTER_X = 6 * mm
GUTTER_Y = 6 * mm

CARD_W = (PAGE_W - 2 * MARGIN_X - (COLS_PAGE - 1) * GUTTER_X) / COLS_PAGE
CARD_H = (PAGE_H - MARGIN_TOP - MARGIN_BOT - (ROWS_PAGE - 1) * GUTTER_Y) / ROWS_PAGE


def _gen_carte(rng):
    """Grille 5×5 : 4 chiffres par colonne active (rangées 0,1,3,4), sans doublon."""
    carte = [[None] * 5 for _ in range(5)]
    for c in COLS_ACTIVES:
        a, b = PLAGES[c]
        nums = rng.sample(range(a, b + 1), 4)   # 4 distincts, ordre aléatoire
        for k, r in enumerate(ROWS_ACTIVES):
            carte[r][c] = nums[k]
    return carte


def _boule(c, cx, cy, r, telephone):
    """Boule-logo BLANCHE (économie de toner) : contour léger + TK création + téléphone."""
    # cercle blanc, simple contour fin
    c.setFillColor(colors.white)
    c.setStrokeColor(GRIS_CLAIR); c.setLineWidth(0.6)
    c.circle(cx, cy, r, stroke=1, fill=1)
    # textes en gris 40% (écriture fine DJL)
    c.setFillColor(GRIS40)
    c.setFont(POLICE, 5.4)
    c.drawCentredString(cx, cy + r * 0.30, "TK création")
    c.setFont(POLICE, 5.8)
    tel = (telephone or "89 22 23 05").replace(" ", "")
    c.drawCentredString(cx, cy - r * 0.50, tel)


def _dessiner_carte(c, x0, y0, carte, couleur_hex, serie, telephone="", style="eco", evenement_id=""):
    police_ch, gris_ch = _style_chiffres(style)
    col = colors.HexColor(couleur_hex)

    # bordure carte
    c.setStrokeColor(col); c.setLineWidth(1.0)
    c.roundRect(x0, y0, CARD_W, CARD_H, 1.5 * mm, stroke=1, fill=0)
    if _sec:  # cadre intérieur en microtexte (sécurité anti-photocopie)
        _sec.cadre_micro(c, x0, y0, CARD_W, CARD_H, serie, retrait=1.0 * mm)

    # en-tête 4 C O I N
    head_h = 9 * mm
    grid_top = y0 + CARD_H - head_h
    grid_bot = y0 + 3 * mm
    gx0 = x0 + 2.5 * mm
    grid_w = CARD_W - 5 * mm
    cell_w = grid_w / 5
    grid_h = grid_top - grid_bot
    cell_h = grid_h / 5

    # lettres d'en-tête (écriture fine DJL)
    for i, L in enumerate(LETTRES):
        cx = gx0 + (i + 0.5) * cell_w
        c.setFillColor(col); c.setFont(POLICE, 19)
        c.drawCentredString(cx, grid_top + 2.2 * mm, L)

    # ═══ 🖨️ LES QUATRE IMPRIMANTES ═══
    # Une par coin, chacune portant SES QUATRE NUMÉROS dans son bac à
    # papier — deux par rangée. Plus de grille : les imprimantes
    # dessinent elles-mêmes les quatre blocs du jeu.
    ECART = 2.0 * mm
    iw = (grid_w - ECART) / 2.0
    ih = iw / _RATIO_IMP
    if ih * 2 + ECART > grid_h:
        ih = (grid_h - ECART) / 2.0
        iw = ih * _RATIO_IMP
    ox = gx0 + (grid_w - (2 * iw + ECART)) / 2
    oy = grid_bot + (grid_h - (2 * ih + ECART)) / 2

    # la place d'un numéro dans le bac : deux colonnes, deux rangées
    # 🖨️ DEUX numéros dans le BAC, DEUX sur la FEUILLE QUI SORT : la
    # machine range vraiment ses chiffres, et chacun a deux fois plus de
    # hauteur qu'entassé à quatre dans le seul bac (18 × 10 mm).
    bw = (BAC[1] - BAC[0]) * iw / 2.0
    bh = (BAC[3] - BAC[2]) * ih
    sw = (SORTIE[1] - SORTIE[0]) * iw / 2.0
    sh = (SORTIE[3] - SORTIE[2]) * ih
    taille = 34.0
    # ⚠️ on mesure avec la VRAIE police : la condensée est plus étroite,
    # elle permet donc une taille plus haute à place égale.
    while taille > 8 and (_lg4("88", police_ch, taille) > min(bw, sw) * 0.88
                          or taille * 0.72 > min(bh, sh) * 0.82):
        taille -= 0.5

    # les quatre blocs du jeu : haut-gauche, haut-droit, bas-gauche, bas-droit
    BLOCS = (((0, 0), (0, 1), (1, 0), (1, 1)),      # coin haut-gauche
             ((0, 3), (0, 4), (1, 3), (1, 4)),      # coin haut-droit
             ((3, 0), (3, 1), (4, 0), (4, 1)),      # coin bas-gauche
             ((3, 3), (3, 4), (4, 3), (4, 4)))      # coin bas-droit
    for k, cases in enumerate(BLOCS):
        px = ox + (k % 2) * (iw + ECART)
        py = oy + (1 - k // 2) * (ih + ECART)
        if _os2.path.exists(_IMAGE_IMP):
            try:
                c.drawImage(_IMAGE_IMP, px, py, iw, ih, mask="auto",
                            preserveAspectRatio=True)
            except Exception:
                pass
        for n, (r, cc) in enumerate(cases):
            v = carte[r][cc]
            if v is None:
                continue
            # les deux premiers dans le BAC, les deux autres sur la FEUILLE
            Z = BAC if n < 2 else SORTIE
            nx = px + (Z[0] + (n % 2 + 0.5) * (Z[1] - Z[0]) / 2) * iw
            ny = py + (Z[2] + (Z[3] - Z[2]) / 2) * ih
            if _sec:
                _sec.chiffre_micro(c, v, nx, ny - taille * 0.36, taille, gris_ch, police_ch)
            else:
                c.setFillColor(gris_ch)
                c.setFont(police_ch, taille)
                c.drawCentredString(nx, ny - taille * 0.36, str(v))

    # série en bas
    c.setFillColor(col); c.setFont(POLICE, 5)
    c.drawRightString(x0 + CARD_W - 2.5 * mm, y0 + 0.8 * mm, "%06d" % serie)

    # QR de vérification par grille (anti-duplication) — coin bas-droit
    if _sec and evenement_id:
        try:
            # 🎯 LE QR au centre, dans la croix entre les quatre imprimantes.
            # ⚠️ 12/08 : il faisait 13 mm avec son code écrit à droite et
            # débordait sur les bacs voisins, mangeant deux numéros. Réduit
            # et posé nu, il tient dans l'écart des machines.
            _q = min(9.0 * mm, ECART + iw * 0.20)
            _xq = ox + iw + (ECART - _q) / 2 + iw * 0.0
            _sec.carton_qr(c, ox + iw + ECART / 2 - _q / 2,
                           oy + ih + ECART / 2 - _q / 2,
                           _q, evenement_id, serie, avec_code=False)
        except Exception:
            pass


def generer_pdf(nb_cartes=6, serie_start=1, theme="", couleur=True,
                nom_evenement="", titre_jeu="", couleur_perso="", date_lieu="", telephone="",
                style="eco", evenement_id="", page_start=1):
    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=A4, pageCompression=1)

    nb_cartes = max(1, min(int(nb_cartes), 20000))
    par_page = COLS_PAGE * ROWS_PAGE
    nb_pages = (nb_cartes + par_page - 1) // par_page

    rng = random.Random()   # graine fraîche : cartes uniques à chaque génération
    serie = int(serie_start)
    # 📄 la page continue d'une rame à l'autre (sceau Maeva 12/08)
    no_page = max(1, int(page_start))
    faites = 0

    for _ in range(nb_pages):
        if nom_evenement:
            c.setFillColor(colors.black); c.setFont(POLICE, 9)
            c.drawCentredString(PAGE_W / 2, PAGE_H - 5 * mm, nom_evenement)
        # numéro de page (Maeva, juil. 2026)
        c.setFillColor(GRIS_CLAIR); c.setFont(POLICE, 6)
        c.drawCentredString(PAGE_W / 2, PAGE_H - 7.2 * mm, "%03d" % no_page)

        for row in range(ROWS_PAGE):
            for col_i in range(COLS_PAGE):
                if faites >= nb_cartes:
                    break
                x0 = MARGIN_X + col_i * (CARD_W + GUTTER_X)
                y0 = MARGIN_BOT + (ROWS_PAGE - 1 - row) * (CARD_H + GUTTER_Y)
                carte = _gen_carte(rng)
                coul = (couleur_perso if (couleur and couleur_perso)
                        else RAINBOW[(serie - 1) % len(RAINBOW)] if couleur else "#9A9A9A")
                _dessiner_carte(c, x0, y0, carte, coul, serie, telephone, style=style, evenement_id=evenement_id)
                serie += 1
                faites += 1

        c.showPage()
        no_page += 1

    c.save()
    buf.seek(0)
    return buf


if __name__ == "__main__":
    pdf = generer_pdf(nb_cartes=6, couleur=True, nom_evenement="ASSOCIATION TE MANU",
                      titre_jeu="4 COIN", telephone="89 22 23 05")
    with open("test_4coin.pdf", "wb") as f:
        f.write(pdf.read())
    print("4 COIN généré")
