"""
MANAPRINT — Générateur DIAMANT (format A4)

💍 REFAIT LE 10/08 (sceau Maeva) : DIX BAGUES, deux par lettre du mot
BINGO. Chaque bague porte SON NUMÉRO au cœur de sa pierre — « une boule
dans chaque bague » — et chaque rangée porte sa lettre.

RÈGLE (sceau Maeva 10/08) : 10 numéros, DEUX PAR LETTRE —
  B : 1-15 · I : 16-30 · N : 31-45 · G : 46-60 · O : 61-75
Le sac du crieur ne change pas : c'est toujours 1 à 75.

⚡ ÉCONOMIE D'ENCRE : la bague est réduite à SON CONTOUR (les facettes
fines des petits diamants ont été retirées à la découpe : 22 % d'encre
en moins), et le dessin est pâli une fois pour toutes.
"""
import io
from reportlab.pdfbase.pdfmetrics import stringWidth as _lgd
import random
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import mm

# SÉCURITÉ ANTI-PHOTOCOPIE (microtexte) — anti-panne : si le module securite
# est absent, les cartons sortent normalement, simplement sans microtexte.
try:
    from generators import securite as _sec
except Exception:
    try:
        import securite as _sec
    except Exception:
        _sec = None


# Couleurs DIAMANT : alternance jaune / orange (fidèle à la maquette)
DIAMANT_COULEURS = ["#F2C60A", "#F57C00"]
NOIR = colors.Color(0, 0, 0)
GRIS40 = colors.Color(0.60, 0.60, 0.60)
GREY = colors.Color(0.42, 0.42, 0.42)
GRIS_CROIX = colors.Color(0.72, 0.72, 0.72)
GRIS_GRILLE = colors.Color(0.55, 0.55, 0.55)

# ══ DEUX GAMMES COMMERCIALES (vision Maeva) ══════════════════════════
# ÉCO      : écriture fine DejaVu ExtraLight, gris 0,50 — économie de toner
# PREMIUM  : écriture grasse Helvetica-Bold, gris 0,55 — style P15
from reportlab.pdfbase import pdfmetrics as _pm
from reportlab.pdfbase.ttfonts import TTFont as _TF
try:
    # 💎 10/08 (sceau Maeva) : la GRASSE CONDENSÉE, celle de QUINES 90.
    # Elle est plus étroite qu'une grasse ordinaire, donc on peut la
    # monter plus haut à place égale — et elle se lit de loin.
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

# 💍 LA BAGUE DE MAEVA, et l'intérieur de sa pierre (mesuré au pixel).
_RATIO_BAGUE = 0.973
PIERRE = (0.233, 0.767, 0.208, 0.781)   # x0, x1, y0, y1 — l'intérieur du diamant
# ⚠️ 10/08 : ces fractions ont été RECALCULÉES sur l'image finale (le plus
# grand rectangle vide au cœur de la pierre). Les premières venaient du
# cadrage d'avant et disaient la pierre plus large que haute — l'inverse
# de la vérité — ce qui bridait les chiffres à 18 pt au lieu de 25.
import os as _os2


def _choisir_image(motif, ratio_attendu):
    """🛟 Retrouve le dessin, quel que soit son nom de fichier.

    Au téléversement, le nom peut garder un préfixe de livraison ou
    recevoir un « (1) ». On prend donc, parmi les fichiers dont le nom
    contient `motif`, celui dont les PROPORTIONS collent au dessin
    attendu — la seule marque qui ne mente pas.
    """
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


_IMAGE_BAGUE = _choisir_image("diamant_bague", _RATIO_BAGUE)

# 💍 12 cartes / A4 (sceau Maeva 10/08) : le carton d'avant laissait
# un large blanc a droite des bagues. En le serrant sur elles, on en
# tient QUATRE par rangee au lieu de deux — deux fois plus de cartons
# par feuille, et les chiffres gardent leurs 18 pt.
COLS_PAGE = 4
ROWS_PAGE = 3
MARGIN_X = 6 * mm
MARGIN_TOP = 11 * mm
MARGIN_BOT = 8 * mm
GUTTER_X = 4 * mm
GUTTER_Y = 3 * mm

CARD_W = (PAGE_W - 2 * MARGIN_X - (COLS_PAGE - 1) * GUTTER_X) / COLS_PAGE
CARD_H = (PAGE_H - MARGIN_TOP - MARGIN_BOT - (ROWS_PAGE - 1) * GUTTER_Y) / ROWS_PAGE

RANGES = [(1, 15), (16, 30), (31, 45), (46, 60), (61, 75)]
FOOT_H = 3 * mm
BANDEAU_H = 2.8 * mm
GRID_N = 5  # 5x5

# Le motif DIAMANT : cases pleines (ligne, colonne), lignes numérotées du HAUT
POSITIONS = {
    (0, 0), (0, 2), (0, 4),
    (1, 1), (1, 2), (1, 3),
    (3, 1), (3, 2), (3, 3),
    (4, 0), (4, 2), (4, 4),
}
# Nombre de numéros nécessaires par colonne
_NB_PAR_COL = [2, 2, 4, 2, 2]


LETTRES_BINGO = "BINGO"


def _gen_carte():
    """🎰 DIX numéros : DEUX par lettre du mot BINGO, triés.

    B : 1-15 · I : 16-30 · N : 31-45 · G : 46-60 · O : 61-75
    (sceau Maeva 10/08 — avant, la grille en portait 12.)
    """
    return [sorted(random.sample(range(lo, hi + 1), 2)) for (lo, hi) in RANGES]

def _dessiner_carte(c, x0, y0, carte, couleur_hex, serie, encre,
                    telephone="", titre_jeu="", style="eco", evenement_id=""):
    police_ch, gris_ch = _style_chiffres(style)
    col = colors.HexColor(couleur_hex)
    cell_w = CARD_W / GRID_N

    # Bordure ÉPAISSE (signature DIAMANT)
    c.setStrokeColor(col)
    c.setLineWidth(2.4)
    c.roundRect(x0, y0, CARD_W, CARD_H, 1.8 * mm, stroke=1, fill=0)
    if _sec:  # cadre intérieur en microtexte (sécurité anti-photocopie)
        _sec.cadre_micro(c, x0, y0, CARD_W, CARD_H, serie, retrait=1.4 * mm)

    # Mini-bandeau : nom du jeu + nom du tournoi (sécurité)
    bandeau = "LE JEU \u00ab DIAMANT \u00bb"
    if titre_jeu:
        bandeau += "  \u2014  " + titre_jeu
    c.setFillColor(GREY); c.setFont("Helvetica", 4)
    c.drawCentredString(x0 + CARD_W / 2, y0 + CARD_H - 2.3 * mm, bandeau[:60])

    # ═══ 💍 LES DIX BAGUES — DEUX PAR LETTRE DU MOT BINGO ═══
    # Cinq rangées, chacune avec sa lettre à gauche et ses deux bagues.
    grid_top = y0 + CARD_H - BANDEAU_H - 0.8 * mm
    # ⚠️ le bas du carton est RÉSERVÉ au pied et au QR.
    grid_bot = y0 + FOOT_H + 10.0 * mm
    zone_h = grid_top - grid_bot
    NR = 5
    case_h = zone_h / NR
    LET_W = CARD_W * 0.11               # la colonne des lettres
    case_w = (CARD_W - LET_W - 3.0 * mm) / 2
    bw = min(case_w * 0.96, case_h * 0.99 * _RATIO_BAGUE)
    bh = bw / _RATIO_BAGUE
    pl = (PIERRE[1] - PIERRE[0]) * bw
    ph = (PIERRE[3] - PIERRE[2]) * bh
    taille = 30.0
    # ⚠️ la pierre est un OVALE : à mi-hauteur, là où se pose le chiffre,
    # elle est plus large que le rectangle qu'on peut y inscrire. On
    # mesure donc avec la VRAIE police et on s'autorise un quart de plus
    # en largeur — sinon les chiffres restaient à 16 pt dans une pierre
    # qui pouvait en porter 25.
    while taille > 10 and (_lgd("88", police_ch, taille) > pl * 1.06
                           or taille * 0.72 > ph * 0.92):
        taille -= 0.5
    for ri in range(NR):
        cyc = grid_top - (ri + 0.5) * case_h
        # la lettre B·I·N·G·O
        c.setFillColor(col)
        c.setFont("Helvetica-Bold", max(9.0, taille * 0.62))
        c.drawCentredString(x0 + 1.5 * mm + LET_W / 2,
                            cyc - taille * 0.62 * 0.34, LETTRES_BINGO[ri])
        for ci in range(2):
            n = carte[ri][ci]
            bx = x0 + 1.5 * mm + LET_W + ci * case_w + (case_w - bw) / 2
            by = cyc - bh / 2
            if _os2.path.exists(_IMAGE_BAGUE):
                try:
                    c.drawImage(_IMAGE_BAGUE, bx, by, bw, bh, mask="auto",
                                preserveAspectRatio=True)
                except Exception:
                    pass
            nx = bx + (PIERRE[0] + PIERRE[1]) / 2 * bw
            ny = by + (PIERRE[2] + PIERRE[3]) / 2 * bh - taille * 0.34
            if _sec:
                _sec.chiffre_micro(c, n, nx, ny, taille, gris_ch, police_ch)
            else:
                c.setFillColor(gris_ch)
                c.setFont(police_ch, taille)
                c.drawCentredString(nx, ny, str(n))

    # ── LE PIED : n° de série, téléphone, et le QR ───────────────────────
    # ⚠️ Ce bloc vivait sous l'ancienne grille 5×5 ; en la remplaçant par
    # les bagues, j'avais emporté le pied ET le QR avec elle (attrapé le
    # 10/08 : le carton sortait sans numéro de série ni QR).
    c.setFillColor(GREY)
    c.setFont("Helvetica", 4.4)
    c.drawString(x0 + 1.5 * mm, y0 + 1.3 * mm, "Carte N\u00b0 %05d" % serie)
    if telephone:
        c.drawRightString(x0 + CARD_W - 14.5 * mm, y0 + 1.3 * mm,
                          "Resp. %s" % telephone)
    if _sec and evenement_id:
        try:
            _q = 8.0 * mm
            _sec.carton_qr(c, x0 + CARD_W - _q - 2.0 * mm, y0 + 0.9 * mm,
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

    serie = serie_start
    # 📄 la page continue d'une rame à l'autre (sceau Maeva 12/08)
    no_page = max(1, int(page_start))
    encre = NOIR if couleur else GRIS40

    for _ in range(nb_pages):
        if nom_evenement:
            c.setFillColor(NOIR); c.setFont("Helvetica-Bold", 11)
            c.drawCentredString(PAGE_W / 2, PAGE_H - 5 * mm, nom_evenement)
        titre_aff = titre_jeu if titre_jeu else "DIAMANT"
        ligne2 = titre_aff
        if date_lieu: ligne2 += "  \u00b7  " + date_lieu
        ligne2 += f"  \u00b7  Page {no_page}"
        c.setFillColor(GREY); c.setFont("Helvetica", 7)
        y2 = (PAGE_H - 8.5 * mm) if nom_evenement else (PAGE_H - 6 * mm)
        c.drawCentredString(PAGE_W / 2, y2, ligne2)

        idx = 0
        for row in range(ROWS_PAGE):
            for col_i in range(COLS_PAGE):
                x0 = MARGIN_X + col_i * (CARD_W + GUTTER_X)
                y0 = MARGIN_BOT + (ROWS_PAGE - 1 - row) * (CARD_H + GUTTER_Y)
                carte = _gen_carte()
                if couleur and couleur_perso:
                    coul = couleur_perso
                elif couleur:
                    coul = DIAMANT_COULEURS[idx % len(DIAMANT_COULEURS)]  # jaune / orange
                else:
                    coul = "#999999"
                _dessiner_carte(c, x0, y0, carte, coul, serie, encre,
                                telephone, titre_jeu, style=style, evenement_id=evenement_id)
                serie += 1
                idx += 1

        c.showPage()
        no_page += 1

    c.save()
    buf.seek(0)
    return buf


if __name__ == "__main__":
    pdf = generer_pdf(nb_cartes=6, couleur=True, titre_jeu="")
    with open("test_diamant.pdf", "wb") as f:
        f.write(pdf.read())
    print("DIAMANT g\u00e9n\u00e9r\u00e9")
