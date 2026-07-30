"""
MANAPRINT — Générateur P6 MARATHON (format A4)
6 cartes par feuille (2 colonnes × 3 rangées).
Chaque carte : 5 colonnes B·I·N·G·O, grille 5×5, case centrale "MARATHON" libre.
Plages : B 1-15, I 16-30, N 31-45, G 46-60, O 61-75.
N° série dans le header (colonne N). Responsable sur chaque grille.
Couleur arc-en-ciel (chiffres noirs) ou gris 40%.
"""
import io
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


RAINBOW = [
    "#E53935", "#FF7043", "#FB8C00", "#F9A825",
    "#43A047", "#00ACC1", "#1E88E5", "#3949AB",
    "#8E24AA", "#D81B60", "#6D4C41", "#546E7A",
]
NOIR = colors.Color(0, 0, 0)
GRIS40 = colors.Color(0.60, 0.60, 0.60)

GREY = colors.Color(0.42, 0.42, 0.42)


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
# 🃏 CHIFFRES BIEN GRAS COMME LE QUINES 90 (sceau Maeva 30/07) : les DEUX
# gammes écrivent en DejaVu GRAS (l'ÉCO garde son gris doux pour le toner).
try:
    _pm.registerFont(_TF("DJBOLD6", "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"))
    _POLICE_ECO = "DJBOLD6"
    _POLICE_P15_G = "DJBOLD6"
except Exception:
    _POLICE_ECO = "Helvetica-Bold"
    _POLICE_P15_G = "Helvetica-Bold"
_GRIS_ECO = colors.Color(0.50, 0.50, 0.50)
_POLICE_P15 = _POLICE_P15_G
_GRIS_P15 = colors.Color(0.55, 0.55, 0.55)

def _style_chiffres(style):
    """Retourne (police, gris) des chiffres selon la gamme choisie."""
    if str(style).lower() in ("p15", "premium"):
        return _POLICE_P15, _GRIS_P15
    return _POLICE_ECO, _GRIS_ECO
# ═════════════════════════════════════════════════════════════════════

PAGE_W, PAGE_H = A4

COLS_PAGE = 2
ROWS_PAGE = 3
MARGIN_X = 6 * mm
MARGIN_TOP = 11 * mm
MARGIN_BOT = 8 * mm
GUTTER_X = 4 * mm
GUTTER_Y = 3 * mm

CARD_W = (PAGE_W - 2 * MARGIN_X - (COLS_PAGE - 1) * GUTTER_X) / COLS_PAGE
CARD_H = (PAGE_H - MARGIN_TOP - MARGIN_BOT - (ROWS_PAGE - 1) * GUTTER_Y) / ROWS_PAGE

LETTERS = ["B", "I", "N", "G", "O"]
RANGES = [(1, 15), (16, 30), (31, 45), (46, 60), (61, 75)]
HDR_H = 4.5 * mm
FOOT_H = 3 * mm
GRID_N = 5  # 5x5


def _gen_carte():
    """5 colonnes × 5 numéros distincts triés. Case centrale (col N, ligne 2) = MARATHON."""
    cols = []
    for (lo, hi) in RANGES:
        cols.append(sorted(random.sample(range(lo, hi + 1), GRID_N)))
    return cols


# 🃏 LES CARTES À JOUER 1-13 (sceau Maeva 30/07, jumeau CASINO du P6) :
# 1 = As (A), 2-10 = leur valeur, 11 = V, 12 = D, 13 = R — chaque numéro vit
# dans une VRAIE carte (coin arrondi, valeur + enseigne dessinée à la main,
# jamais un glyphe Unicode = tofu Helvetica) ; dès 14, le chiffre reste roi.
_VALEURS_CARTES = {1: "A", 11: "V", 12: "D", 13: "R"}
_JOKER_ACTIF = False   # 🃏 EN RÉSERVE (Maeva 30/07 : lancement sans joker,
#     décision après les résultats du marché) — True réveille la règle au pied.


def _enseigne(c, cx, cy, t, quelle, coul):
    """♠♥♦♣ DESSINÉES : 0=pique 1=coeur 2=carreau 3=trèfle."""
    c.setFillColor(coul)
    if quelle == 2:   # carreau
        p = c.beginPath()
        p.moveTo(cx, cy + t); p.lineTo(cx + t * 0.72, cy)
        p.lineTo(cx, cy - t); p.lineTo(cx - t * 0.72, cy); p.close()
        c.drawPath(p, stroke=0, fill=1)
        return
    if quelle == 1:   # coeur
        c.circle(cx - t * 0.42, cy + t * 0.28, t * 0.46, stroke=0, fill=1)
        c.circle(cx + t * 0.42, cy + t * 0.28, t * 0.46, stroke=0, fill=1)
        p = c.beginPath()
        p.moveTo(cx - t * 0.85, cy + t * 0.16); p.lineTo(cx, cy - t)
        p.lineTo(cx + t * 0.85, cy + t * 0.16); p.close()
        c.drawPath(p, stroke=0, fill=1)
        return
    if quelle == 0:   # pique = coeur inversé + pied
        c.circle(cx - t * 0.40, cy - t * 0.18, t * 0.42, stroke=0, fill=1)
        c.circle(cx + t * 0.40, cy - t * 0.18, t * 0.42, stroke=0, fill=1)
        p = c.beginPath()
        p.moveTo(cx - t * 0.80, cy - t * 0.08); p.lineTo(cx, cy + t)
        p.lineTo(cx + t * 0.80, cy - t * 0.08); p.close()
        c.drawPath(p, stroke=0, fill=1)
    else:             # trèfle = trois feuilles
        c.circle(cx, cy + t * 0.42, t * 0.42, stroke=0, fill=1)
        c.circle(cx - t * 0.42, cy - t * 0.10, t * 0.42, stroke=0, fill=1)
        c.circle(cx + t * 0.42, cy - t * 0.10, t * 0.42, stroke=0, fill=1)
    c.rect(cx - t * 0.12, cy - t, t * 0.24, t * 0.85, stroke=0, fill=1)


def _carte_jeu(c, cx, cy, val, col, gris_ch):
    """La carte à jouer du numéro : cadre blanc arrondi bordé couleur,
    valeur Bold au centre, l'enseigne (n %% 4) au-dessus et en-dessous."""
    w, h = 11.6 * mm, 14.8 * mm
    c.setStrokeColor(col); c.setLineWidth(1.2)
    c.setFillColor(colors.white)
    c.roundRect(cx - w / 2, cy - h / 2, w, h, 1.5 * mm, stroke=1, fill=1)
    vtxt = _VALEURS_CARTES.get(val, str(val))
    c.setFillColor(gris_ch); c.setFont(_POLICE_ECO, 17 if len(vtxt) < 2 else 14)
    c.drawCentredString(cx, cy - 2.1 * mm, vtxt)
    _enseigne(c, cx, cy + 4.4 * mm, 1.35 * mm, val % 4, gris_ch)
    _enseigne(c, cx, cy - 4.6 * mm, 1.35 * mm, val % 4, gris_ch)


def _dessiner_carte(c, x0, y0, carte, couleur_hex, serie, encre, telephone="", titre_jeu="", style="eco", evenement_id="", cartes=False):
    police_ch, gris_ch = _style_chiffres(style)
    col = colors.HexColor(couleur_hex)
    cell_w = CARD_W / GRID_N

    # Bordure
    c.setStrokeColor(col)
    c.setLineWidth(0.9)
    c.roundRect(x0, y0, CARD_W, CARD_H, 1.8 * mm, stroke=1, fill=0)
    if _sec:  # cadre intérieur en microtexte (sécurité anti-photocopie)
        _sec.cadre_micro(c, x0, y0, CARD_W, CARD_H, serie, retrait=1.0 * mm)

    # Mini-bandeau : nom du jeu + nom du tournoi (sécurité)
    bandeau = "PJOKER" if cartes else "P6 MARATHON"
    if titre_jeu:
        bandeau += "  —  " + titre_jeu
    c.setFillColor(GREY); c.setFont("Helvetica", 4)
    c.drawCentredString(x0 + CARD_W / 2, y0 + CARD_H - 2.3 * mm, bandeau[:60])

    # Header : lettres B I N G O centrées dans chaque colonne
    hdr_y = y0 + CARD_H - HDR_H - 2.3 * mm
    c.setFillColor(col)
    c.setFont("Helvetica-Bold", 10)
    for i, lettre in enumerate(LETTERS):
        cx = x0 + (i + 0.5) * cell_w
        c.drawCentredString(cx, hdr_y + 1.4 * mm, lettre)

    c.setStrokeColor(col); c.setLineWidth(0.4)
    c.line(x0, hdr_y, x0 + CARD_W, hdr_y)

    # Grille 5×5
    zone_h = CARD_H - HDR_H - FOOT_H - 2.3 * mm
    cell_h = zone_h / GRID_N
    for ci, nums in enumerate(carte):
        cx = x0 + (ci + 0.5) * cell_w
        for ri in range(GRID_N):
            cy = y0 + FOOT_H + (GRID_N - 1 - ri) * cell_h + cell_h * 0.30
            # case centrale (colonne N=2, ligne du milieu ri=2) = MARATHON
            if ci == 2 and ri == 2:
                pass  # case libre : elle accueille le QR de sécurité (dessiné plus bas)
            elif cartes and nums[ri] <= 13:
                # 🃏 jumeau CASINO : le numéro 1-13 vit dans sa carte à jouer
                _carte_jeu(c, cx, cy + 5, nums[ri], col, gris_ch)
            elif _sec and gris_ch is not _GRIS_ECO:
                # PREMIUM : chiffres "billet de banque" gras remplis de microtexte
                _sec.chiffre_micro(c, nums[ri], cx, cy, 30, gris_ch, police_ch)
            else:
                c.setFillColor(gris_ch); c.setFont(police_ch, 30)
                c.drawCentredString(cx, cy, str(nums[ri]))
        if ci > 0:
            c.setStrokeColor(colors.Color(0.85, 0.85, 0.85)); c.setLineWidth(0.3)
            c.line(x0 + ci * cell_w, y0 + FOOT_H, x0 + ci * cell_w, hdr_y)

    # Pied : N° série + responsable sur chaque grille
    c.setStrokeColor(col); c.setLineWidth(0.4)
    c.line(x0, y0 + FOOT_H, x0 + CARD_W, y0 + FOOT_H)
    c.setFillColor(GREY); c.setFont("Helvetica", 4.5)
    c.drawString(x0 + 1.5 * mm, y0 + 1.3 * mm, f"N° {serie:06d}")
    if cartes and _JOKER_ACTIF:
        # 🃏 la règle du JOKER, imprimée sur le carton (rien n'est payé : c'est le jeu)
        c.setFont("Helvetica", 4.2)
        c.drawRightString(x0 + CARD_W - 1.5 * mm, y0 + 1.3 * mm,
                          "JOKER : quand la boule JOKER sort, cochez UNE carte de votre choix")
    if telephone:
        c.drawRightString(x0 + CARD_W - 1.5 * mm, y0 + 1.3 * mm, f"Resp. {telephone}")

    # QR de vérification par grille (anti-duplication) — coin bas-droit
    if _sec and evenement_id:
        try:
            # 🎯 QR intégré : dans la case centrale MARATHON (libre par nature)
            _q = 11.5 * mm
            _xq = x0 + 2 * cell_w + (cell_w - _q) / 2
            _yq = y0 + FOOT_H + 2 * cell_h + (cell_h - _q - 3.4 * mm) / 2 + 3.4 * mm
            _sec.carton_qr(c, _xq, _yq, _q, evenement_id, serie)
        except Exception:
            pass


def generer_pdf(nb_cartes=6, serie_start=1, theme="", couleur=True,
                nom_evenement="", titre_jeu="", couleur_perso="", date_lieu="", telephone="",
                style="eco", evenement_id="", cartes=False):
    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=A4, pageCompression=1)

    nb_cartes = max(1, min(int(nb_cartes), 10000))
    par_page = COLS_PAGE * ROWS_PAGE
    nb_pages = (nb_cartes + par_page - 1) // par_page

    serie = serie_start
    no_page = 1
    encre = NOIR if couleur else GRIS40

    for _ in range(nb_pages):
        if nom_evenement:
            c.setFillColor(NOIR); c.setFont("Helvetica-Bold", 11)
            c.drawCentredString(PAGE_W / 2, PAGE_H - 5 * mm, nom_evenement)
        titre_aff = titre_jeu if titre_jeu else ("PJOKER" if cartes else "P6 MARATHON")
        ligne2 = titre_aff
        if date_lieu: ligne2 += "  ·  " + date_lieu
        ligne2 += f"  ·  Page {no_page}"
        c.setFillColor(GREY); c.setFont("Helvetica", 7)
        y2 = (PAGE_H - 8.5 * mm) if nom_evenement else (PAGE_H - 6 * mm)
        c.drawCentredString(PAGE_W / 2, y2, ligne2)

        for row in range(ROWS_PAGE):
            for col_i in range(COLS_PAGE):
                x0 = MARGIN_X + col_i * (CARD_W + GUTTER_X)
                y0 = MARGIN_BOT + (ROWS_PAGE - 1 - row) * (CARD_H + GUTTER_Y)
                carte = _gen_carte()
                coul = (couleur_perso if (couleur and couleur_perso)
                        else RAINBOW[(serie - 1) % len(RAINBOW)] if couleur else "#999999")
                _dessiner_carte(c, x0, y0, carte, coul, serie, encre, telephone, titre_jeu, style=style, evenement_id=evenement_id, cartes=cartes)
                serie += 1

        c.showPage()
        no_page += 1

    c.save()
    buf.seek(0)
    return buf


def generer_pdf_casino(**kw):
    """🃏 PJOKER (nom définitif, Maeva 30/07) — les numéros 1-13 vivent en cartes."""
    kw["cartes"] = True
    return generer_pdf(**kw)


if __name__ == "__main__":
    pdf = generer_pdf(nb_cartes=6, couleur=True,
                      nom_evenement="ASSOCIATION TE MANU", titre_jeu="GRAND LOTO",
                      date_lieu="20 déc 2026", telephone="87 12 34 56")
    with open("test_p6.pdf", "wb") as f:
        f.write(pdf.read())
    print("P6 MARATHON généré")
