# -*- coding: utf-8 -*-
"""
MANAPRINT — Générateur OHANA 75 · 4 SÉRIES (format A4 PAYSAGE)
4 cartes par feuille A4 paysage (2 × 2), traits de découpe pointillés entre elles.
Chaque carte : grille BINGO 5×5 — colonnes B(1-15) I(16-30) N(31-45) G(46-60) O(61-75),
« MARATHON » au-dessus du G. Chaque case contient DEUX numéros de la colonne :
le principal dans un CERCLE + un plus petit en bas à droite (fidèle au modèle).
Case centrale = FREE SPACE avec le numéro de carte… et le QR de vérification,
au cœur de la carte. 48 numéros par carte (10 par colonne, 8 pour le N).
4 séries = 4 couleurs par page (jaune, bleu, vert, mauve) en mode Couleur.
Chiffres en gris (2 gammes ÉCO/PREMIUM).
"""
import io
import random
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4, landscape
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

# Les 4 SÉRIES : une couleur par position de carte sur la page (vision historique)
SERIES_4 = ["#F9A825", "#1E88E5", "#43A047", "#8E24AA"]  # jaune, bleu, vert, mauve
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

PAGE_W, PAGE_H = landscape(A4)
LETTRES = "BINGO"
PLAGES = [(1, 15), (16, 30), (31, 45), (46, 60), (61, 75)]

COLS_PAGE = 2
ROWS_PAGE = 2
MARGIN_X = 8 * mm
MARGIN_TOP = 8 * mm
MARGIN_BOT = 8 * mm
GUTTER = 7 * mm

CARD_W = (PAGE_W - 2 * MARGIN_X - GUTTER) / COLS_PAGE
CARD_H = (PAGE_H - MARGIN_TOP - MARGIN_BOT - GUTTER) / ROWS_PAGE
HDR_H = 9 * mm


def _gen_carte(rng):
    """Par colonne : 10 numéros distincts (8 pour le N, la case centrale est FREE).
    Retourne cols[c] = liste de paires (cerclé, petit) par case, haut -> bas."""
    cols = []
    for ci, (pmin, pmax) in enumerate(PLAGES):
        n_cases = 4 if ci == 2 else 5
        tirage = rng.sample(range(pmin, pmax + 1), n_cases * 2)
        paires = [(tirage[2 * i], tirage[2 * i + 1]) for i in range(n_cases)]
        cols.append(paires)
    return cols


def _dessiner_carte(c, x0, y0, cols_paires, couleur_hex, serie, titre_jeu="", telephone="", style="eco", evenement_id=""):
    police_ch, gris_ch = _style_chiffres(style)
    col = colors.HexColor(couleur_hex)
    cell_w = CARD_W / 5

    # Ligne d'identité au-dessus de la carte — le nom du jeu apparaît TOUJOURS
    ident = "OHANA 75 \u00b7 4 s\u00e9ries  \u2014  Carte N\u00b0 %06d" % serie
    if titre_jeu and "OHANA" not in titre_jeu.strip().upper():
        ident += "  \u00b7  " + titre_jeu.strip()
    if telephone:
        ident += "  \u00b7  " + telephone
    c.setFillColor(col); c.setFont(POLICE, 5.5)
    c.drawCentredString(x0 + CARD_W / 2, y0 + CARD_H + 1.6 * mm, ident[:90])

    # Bordure carte
    c.setStrokeColor(col); c.setLineWidth(0.9)
    c.roundRect(x0, y0, CARD_W, CARD_H, 1.5 * mm, stroke=1, fill=0)
    if _sec:  # cadre intérieur en microtexte (sécurité anti-photocopie)
        _sec.cadre_micro(c, x0, y0, CARD_W, CARD_H, serie, retrait=1.0 * mm)

    # En-tête B I N G O + MARATHON au-dessus du G (fidèle au modèle)
    hdr_bas = y0 + CARD_H - HDR_H
    c.setStrokeColor(col); c.setLineWidth(0.6)
    c.line(x0, hdr_bas, x0 + CARD_W, hdr_bas)
    for i in range(1, 5):
        c.line(x0 + i * cell_w, hdr_bas, x0 + i * cell_w, y0 + CARD_H)
    c.setFillColor(col)
    for i, lettre in enumerate(LETTRES):
        cx = x0 + (i + 0.5) * cell_w
        if i == 3:  # G — MARATHON au-dessus
            c.setFont(POLICE, 4.5)
            c.drawCentredString(cx, y0 + CARD_H - 3.0 * mm, "MARATHON")
            c.setFont(POLICE, 10)
            c.drawCentredString(cx, hdr_bas + 1.6 * mm, lettre)
        else:
            c.setFont(POLICE, 13)
            c.drawCentredString(cx, hdr_bas + 2.2 * mm, lettre)

    # Grille 5×5 : séparateurs pointillés discrets (fidèle au modèle)
    grid_h = hdr_bas - y0
    cell_h = grid_h / 5
    c.setStrokeColor(GRIS_CLAIR); c.setLineWidth(0.3)
    c.setDash(1.5, 1.8)
    for i in range(1, 5):
        c.line(x0 + i * cell_w, y0, x0 + i * cell_w, hdr_bas)
        c.line(x0, y0 + i * cell_h, x0 + CARD_W, y0 + i * cell_h)
    c.setDash()

    # Les cases : cercle + petit numéro (colonne N : la case centrale = FREE SPACE)
    rayon = min(cell_w, cell_h) * 0.30
    t_cercle, t_petit = 15, 10.5
    for ci, paires in enumerate(cols_paires):
        idx = 0
        for ri in range(5):
            case_x = x0 + ci * cell_w
            case_y = hdr_bas - (ri + 1) * cell_h
            if ci == 2 and ri == 2:
                # ── FREE SPACE : le cœur de la carte, avec numéro… et QR 🛡️ ──
                fx = case_x + cell_w * 0.30
                c.setFillColor(col); c.setFont(POLICE, 5.5)
                c.drawCentredString(fx, case_y + cell_h * 0.70, "FREE")
                c.setFont(POLICE, 6.5)
                c.drawCentredString(fx, case_y + cell_h * 0.44, "%06d" % serie)
                c.setFont(POLICE, 5.5)
                c.drawCentredString(fx, case_y + cell_h * 0.16, "SPACE")
                if _sec and evenement_id:
                    try:
                        _q = min(cell_h - 2.0 * mm, 13.0 * mm)
                        _sec.carton_qr(c, case_x + cell_w - _q - 1.2 * mm,
                                       case_y + (cell_h - _q) / 2, _q, evenement_id, serie)
                    except Exception:
                        pass
                continue
            n_cercle, n_petit = paires[idx]; idx += 1
            ccx = case_x + cell_w * 0.32
            ccy = case_y + cell_h * 0.56
            c.setStrokeColor(col if False else GRIS); c.setLineWidth(0.7)
            c.setStrokeColor(col)
            c.circle(ccx, ccy, rayon, stroke=1, fill=0)
            if _sec:  # chiffres "billet de banque" remplis de microtexte
                _sec.chiffre_micro(c, n_cercle, ccx, ccy - t_cercle * 0.36, t_cercle, gris_ch, police_ch)
                _sec.chiffre_micro(c, n_petit, case_x + cell_w * 0.76,
                                   case_y + cell_h * 0.14, t_petit, gris_ch, police_ch)
            else:
                c.setFillColor(gris_ch); c.setFont(police_ch, t_cercle)
                c.drawCentredString(ccx, ccy - t_cercle * 0.36, str(n_cercle))
                c.setFont(police_ch, t_petit)
                c.drawCentredString(case_x + cell_w * 0.76, case_y + cell_h * 0.14, str(n_petit))


def generer_pdf(nb_cartes=4, serie_start=1, theme="", couleur=True,
                nom_evenement="", titre_jeu="", couleur_perso="", date_lieu="", telephone="",
                style="eco", evenement_id=""):
    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=landscape(A4), pageCompression=1)

    nb_cartes = max(1, min(int(nb_cartes), 10000))
    par_page = COLS_PAGE * ROWS_PAGE
    nb_pages = (nb_cartes + par_page - 1) // par_page

    rng = random.Random(998000 + int(serie_start))
    serie = int(serie_start)
    no_page = 1
    faites = 0

    for _ in range(nb_pages):
        # en-tête de page + traits de découpe pointillés (fidèle au modèle)
        if nom_evenement:
            c.setFillColor(colors.black); c.setFont(POLICE, 8)
            c.drawCentredString(PAGE_W / 2, PAGE_H - 4 * mm, nom_evenement)
        c.setFillColor(GRIS_CLAIR); c.setFont(POLICE, 6)
        c.drawCentredString(PAGE_W / 2, PAGE_H - 6.4 * mm, "%03d" % no_page)
        c.setStrokeColor(GRIS_CLAIR); c.setLineWidth(0.4)
        c.setDash(3, 3)
        c.line(PAGE_W / 2, 3 * mm, PAGE_W / 2, PAGE_H - 3 * mm)
        c.line(3 * mm, PAGE_H / 2, PAGE_W - 3 * mm, PAGE_H / 2)
        c.setDash()

        for row in range(ROWS_PAGE):
            for col_i in range(COLS_PAGE):
                if faites >= nb_cartes:
                    break
                pos = row * COLS_PAGE + col_i
                x0 = MARGIN_X + col_i * (CARD_W + GUTTER)
                y0 = MARGIN_BOT + (ROWS_PAGE - 1 - row) * (CARD_H + GUTTER)
                cols_paires = _gen_carte(rng)
                coul = (couleur_perso if (couleur and couleur_perso)
                        else SERIES_4[pos] if couleur else "#9A9A9A")
                _dessiner_carte(c, x0, y0, cols_paires, coul, serie, titre_jeu, telephone,
                                style=style, evenement_id=evenement_id)
                serie += 1
                faites += 1

        c.showPage()
        no_page += 1

    c.save()
    buf.seek(0)
    return buf


if __name__ == "__main__":
    pdf = generer_pdf(nb_cartes=4, couleur=True,
                      nom_evenement="ASSOCIATION TE MANU", titre_jeu="Grand Loto",
                      telephone="89.22.23.05")
    with open("test_ohana75_4series.pdf", "wb") as f:
        f.write(pdf.read())
    print("OHANA 75 4 séries généré")
