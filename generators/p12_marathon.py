# -*- coding: utf-8 -*-
"""
MANAPRINT — Générateur P12 MARATHON (format A4 PAYSAGE)
12 grilles BINGO par feuille (4 colonnes × 3 rangées) — fidèle au modèle
de Maeva : en-tête B·I·N·G·O avec le N° de série encadré sous le N,
grille 5×5 du bingo américain, B 1-15 · I 16-30 · N 31-45 · G 46-60 ·
O 61-75 (ordre LIBRE), la case CENTRALE « MARATHON » — élargie en
SANCTUAIRE (croix centrale 16 mm) pour loger ENTIÈREMENT le QR de
vérification sans toucher aux chiffres (le mot MARATHON s'affiche
quand il n'y a pas d'événement).
Arc-en-ciel de 12 couleurs (ou couleur_perso) / gris (N&B). 2 gammes ÉCO/PREMIUM.
Caller : entrée « P6 / P12 / P15 MARATHON » (1-75) — boutons PAIRS/IMPAIRS inclus.
"""
import io
import os as _os
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

POLICE_NOIR = "Helvetica"
POLICE_GRAS = "Helvetica-Bold"
try:
    pdfmetrics.registerFont(TTFont("LMROMANB", _os.path.join(_os.path.dirname(_os.path.abspath(__file__)), "LatinModern-Bold.ttf")))
    POLICE_GRAS = "LMROMANB"
except Exception:
    pass
CHIFFRES_GRAS = False      # ⭐ 21/11 : modèle « chiffres bien gros et bien gras »
try:
    pdfmetrics.registerFont(TTFont("LMROMAN", _os.path.join(_os.path.dirname(_os.path.abspath(__file__)), "LatinModern.ttf")))
    POLICE_NOIR = "LMROMAN"
except Exception:
    pass
GRIS = colors.Color(0.42, 0.42, 0.42)
GRIS_CLAIR = colors.Color(0.80, 0.80, 0.80)

# L'arc-en-ciel du modèle : 12 cartes, 12 couleurs
RAINBOW = ["#E53935", "#FB8C00", "#FDD835", "#43A047",
           "#00ACC1", "#5E35B1", "#8E24AA", "#D81B60",
           "#00897B", "#7CB342", "#F4511E", "#1E88E5"]


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
COLONNES = [(1, 15), (16, 30), (31, 45), (46, 60), (61, 75)]

COLS_PAGE = 4
ROWS_PAGE = 3
MARGIN_X = 7 * mm
MARGIN_TOP = 11.5 * mm   # ⭐ 21/11 : place pour l'en-tête DANS la zone imprimable Konica (> 6 mm du bord)
MARGIN_BOT = 6 * mm
GUTTER_X = 4 * mm
GUTTER_Y = 4 * mm

CARD_W = (PAGE_W - 2 * MARGIN_X - (COLS_PAGE - 1) * GUTTER_X) / COLS_PAGE
CARD_H = (PAGE_H - MARGIN_TOP - MARGIN_BOT - (ROWS_PAGE - 1) * GUTTER_Y) / ROWS_PAGE
HDR_H = 7 * mm             # l'en-tête B·I·N·G·O + série encadrée sous le N
PIED_H = 1.6 * mm          # respiration : la dernière rangée ne touche pas le bord

SANCTUAIRE = 16.0 * mm     # la case royale MARATHON/QR : jamais un chiffre touché


def _gen_carte(rng):
    """Grille BINGO : 5 numéros distincts par colonne (4 au centre N),
    ordre LIBRE dans les colonnes — fidèle au modèle."""
    cols = []
    for ci, (pmin, pmax) in enumerate(COLONNES):
        n = 4 if ci == 2 else 5
        cols.append(rng.sample(range(pmin, pmax + 1), n))
    return cols


from reportlab.pdfbase.pdfmetrics import stringWidth as _lg_p12


def _decouper_sanctuaire(texte):
    """⭐ Coupe la personnalisation en lignes courtes pour la case centrale.

    Un mot par ligne tant que ça reste raisonnable ; au-delà de trois mots on
    regroupe pour ne pas empiler dix lignes minuscules.
    """
    mots = [m for m in str(texte).replace("\n", " ").split(" ") if m]
    if not mots:
        return ["MARA", "THON"]
    if len(mots) <= 3:
        return mots
    # plus de trois mots : on répartit en trois lignes équilibrées
    n = len(mots)
    c1, c2 = (n + 2) // 3, 2 * (n + 2) // 3
    return [" ".join(mots[:c1]), " ".join(mots[c1:c2]), " ".join(mots[c2:])]



# ⭐ 22/11 (Maeva) : la nouvelle gamme COULEUR s'ouvre le 1er décembre 2026
#    (0 h, heure de Tahiti). Avant, la version couleur reste celle d'avant.
def _couleur_1er_dec():
    import datetime as _dtC
    m = _dtC.datetime.utcnow() - _dtC.timedelta(hours=10)
    return (m.year, m.month, m.day) >= (2026, 12, 1)

def _dessiner_carte(c, x0, y0, cols_nums, couleur_hex, serie, titre_jeu="", telephone="", style="eco", evenement_id="", nom_centre=""):
    police_ch, gris_ch = _style_chiffres(style)
    col = colors.HexColor(couleur_hex)
    # Colonnes en croix : la colonne N (centre) élargie pour le sanctuaire
    # ⭐ 21/11 (Maeva : « chaque colonne qui reçoit les chiffres doit être
    #    identique ») : 5 colonnes de MÊME largeur, 5 rangées de MÊME hauteur,
    #    comme sur son modèle p12_noir — plus de croix élargie au centre.
    _cw = CARD_W / 5.0
    LARGEURS = [_cw] * 5
    X_COL = [x0 + sum(LARGEURS[:i]) for i in range(6)]

    # Bordure carte arrondie et colorée (fidèle au modèle)
    # ⭐ 21/11 (Maeva, gamme COULEUR du 1er décembre) : en couleur, le contour
    #    et les traits de la grille prennent la couleur de la carte, toujours fins
    #    mais un peu plus épais que le gris pour que la couleur se voie bien.
    _en_couleur = couleur_hex.upper() != "#9A9A9A" and _couleur_1er_dec()
    _trait_grille = (col, 0.75) if _en_couleur else (GRIS_CLAIR, 0.3)
    c.setStrokeColor(col); c.setLineWidth(2.1 if _en_couleur else 1.6)
    c.roundRect(x0, y0, CARD_W, CARD_H, 2.2 * mm, stroke=1, fill=0)
    if _sec:  # cadre intérieur en microtexte (sécurité anti-photocopie)
        _sec.cadre_micro(c, x0, y0, CARD_W, CARD_H, serie, retrait=0.9 * mm)

    # En-tête : les lettres B I N G O dans la couleur de la carte,
    # et le N° de série ENCADRÉ sous le N (fidèle au modèle)
    hdr_bas = y0 + CARD_H - HDR_H
    c.setStrokeColor(_trait_grille[0]); c.setLineWidth(_trait_grille[1])
    c.line(x0, hdr_bas, x0 + CARD_W, hdr_bas)
    for i, lettre in enumerate(LETTRES):
        cx = (X_COL[i] + X_COL[i + 1]) / 2
        c.setFillColor(col)
        if i == 2:
            c.setFont("Helvetica-Bold", 5.5)
            c.drawCentredString(cx, y0 + CARD_H - 2.6 * mm, lettre)
            bw, bh = 11 * mm, 3.0 * mm
            c.setStrokeColor(col); c.setLineWidth(0.5)
            c.roundRect(cx - bw / 2, y0 + CARD_H - 6.4 * mm, bw, bh, 0.6 * mm, stroke=1, fill=0)
            c.setFillColor(GRIS); c.setFont("Helvetica", 4.4)
            c.drawCentredString(cx, y0 + CARD_H - 5.6 * mm, "%06d" % serie)
        else:
            c.setFont("Helvetica-Bold", 8)
            c.drawCentredString(cx, y0 + CARD_H - 4.6 * mm, lettre)

    # La grille 5×5 en croix : rangée centrale rehaussée pour le sanctuaire
    z_top = hdr_bas
    z_bot = y0 + PIED_H
    _rh = (z_top - z_bot) / 5.0
    HAUTEURS = [_rh] * 5
    Y_ROW = [z_top - sum(HAUTEURS[:i]) for i in range(6)]   # plafonds des rangées
    c.setStrokeColor(_trait_grille[0]); c.setLineWidth(_trait_grille[1])
    for i in range(1, 5):
        c.line(X_COL[i], z_bot, X_COL[i], z_top)
        c.line(x0, Y_ROW[i], x0 + CARD_W, Y_ROW[i])

    # Les 24 numéros — ordre libre (fidèle au modèle)
    # ⭐ 21/11 (modèle « p12_noir » de Maeva) : chiffres LATIN MODERN NOIRS,
    #    aussi grands que la case le permet (le « 88 » remplit la largeur).
    _pol = POLICE_GRAS if CHIFFRES_GRAS else POLICE_NOIR
    taille = 60.0
    while taille > 8 and (_lg_p12("88", _pol, taille) > _cw * (0.85 if CHIFFRES_GRAS else 0.90)
                          or taille * 0.66 > _rh * 0.70):
        taille -= 0.25
    _encre = colors.black if gris_ch in (_GRIS_ECO, _GRIS_P15) else gris_ch
    for ci, nums in enumerate(cols_nums):
        cx = (X_COL[ci] + X_COL[ci + 1]) / 2
        rangees = (0, 1, 3, 4) if ci == 2 else (0, 1, 2, 3, 4)
        for val, ri in zip(nums, rangees):
            cyc = (Y_ROW[ri] + Y_ROW[ri + 1]) / 2
            c.setFillColor(_encre)
            if CHIFFRES_GRAS:
                c.saveState()
                c.setStrokeColor(_encre); c.setLineWidth(taille * 0.018); c.setLineJoin(1)
                _o = c.beginText(); _o.setTextRenderMode(2); _o.setFont(_pol, taille)
                _o.setTextOrigin(cx - _lg_p12(str(val), _pol, taille) / 2.0, cyc - taille * 0.33)
                _o.textOut(str(val)); c.drawText(_o)
                c.restoreState()
            else:
                c.setFont(_pol, taille)
                c.drawCentredString(cx, cyc - taille * 0.322, str(val))

    # Le SANCTUAIRE central : le QR y loge ENTIER (sans code texte : le scan
    # dit tout) — ou le mot MARATHON du modèle quand il n'y a pas d'événement
    cx_c = (X_COL[2] + X_COL[3]) / 2
    cy_c = (Y_ROW[2] + Y_ROW[3]) / 2
    qr_ok = False
    if _sec and evenement_id:
        try:
            _q = 12.0 * mm
            qr_ok = _sec.carton_qr(c, cx_c - _q / 2, cy_c - _q / 2, _q, evenement_id, serie,
                                   avec_code=False)
        except Exception:
            qr_ok = False
    if not qr_ok:
        # ⭐ 10/09 (sceau Maeva) : QUAND LE CLIENT DONNE UNE PERSONNALISATION,
        #    c'est ELLE qui s'écrit dans la case centrale, à la place du mot
        #    « MARATHON » du modèle. Sans personnalisation, on garde MARATHON.
        #    Le texte est coupé en lignes et la taille descend jusqu'à ce que
        #    la plus longue tienne dans la case, sans jamais toucher un chiffre.
        _lignes = _decouper_sanctuaire(nom_centre) if nom_centre else ["MARA", "THON"]
        _larg_utile = (X_COL[3] - X_COL[2]) * 0.86
        _t = 7.5
        while _t > 3.0 and (max(_lg_p12(l, POLICE, _t) for l in _lignes) > _larg_utile
                            or len(_lignes) * _t * 1.25 > _rh * 0.80):
            _t -= 0.25
        c.setFillColor(GRIS); c.setFont(POLICE, _t)
        _inter = _t * 1.25
        _depart = cy_c + (len(_lignes) - 1) * _inter / 2 - _t * 0.36
        for _i, _l in enumerate(_lignes):
            c.drawCentredString(cx_c, _depart - _i * _inter, _l)

    # Signature discrète sous la carte (marque + titre client + téléphone)
    signature = "P12"
    if titre_jeu and "P12" not in titre_jeu.strip().upper():
        signature += " \u00b7 " + titre_jeu.strip()
    if telephone:
        signature += " \u00b7 " + telephone
    c.setFillColor(GRIS_CLAIR); c.setFont(POLICE, 4.0)
    c.drawCentredString(x0 + CARD_W / 2, y0 - 2.6 * mm, signature[:64])


def generer_pdf(nb_cartes=12, serie_start=1, theme="", couleur=True,
                nom_evenement="", titre_jeu="", couleur_perso="", date_lieu="", telephone="",
                style="eco", evenement_id="", page_start=1, nom_centre=None,
                nom_gauche="", nom_droite="", series_par_cote=False, demi_total=0, graine=0, gras=False, **_ig):
    """⭐ 21/11 : `nom_gauche` / `nom_droite` = une personnalisation par MOITIÉ de
    feuille (les 6 grilles de gauche, les 6 de droite) — en tête de chaque moitié
    et dans la case centrale de ses grilles (commande HEIPOE samedi / dimanche).
⭐ `nom_centre` remplit la CASE CENTRALE. Laissé à None, elle reprend
    `nom_evenement` — c'est le cas courant. On peut donc écrire un texte en
    tête de feuille et un autre au cœur du carton, si le client le demande.
    """
    global CHIFFRES_GRAS
    CHIFFRES_GRAS = bool(gras)
    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=landscape(A4), pageCompression=1)

    nb_cartes = max(1, min(int(nb_cartes), 10000))
    par_page = COLS_PAGE * ROWS_PAGE
    nb_pages = (nb_cartes + par_page - 1) // par_page

    rng = random.Random(120300 + int(serie_start) + int(graine) * 7919)  # ⭐ graine : 2e tirage avec les mêmes numéros
    serie = int(serie_start)
    # ⭐ 21/11 (HEIPOE) : series_par_cote=True -> DEUX séries indépendantes,
    #    les 6 grilles de gauche et les 6 de droite partent chacune de serie_start
    #    (une page = 6 numéros à gauche + les 6 MÊMES numéros à droite).
    serie_cote = int(serie_start)
    # 📄 la page continue d'une rame à l'autre (sceau Maeva 12/08)
    no_page = max(1, int(page_start))
    faites = 0

    for _ in range(nb_pages):
        # en-tête de page
        if nom_gauche or nom_droite:
            c.setFillColor(colors.black); c.setFont("Helvetica-Bold", 10)
            for _k, _txt in ((0, nom_gauche), (2, nom_droite)):
                if _txt:
                    _xc = MARGIN_X + _k * (CARD_W + GUTTER_X) + CARD_W + GUTTER_X / 2.0
                    c.drawCentredString(_xc, PAGE_H - 9.6 * mm, _txt)
        elif nom_evenement:
            c.setFillColor(colors.black); c.setFont("Helvetica-Bold", 10)
            c.drawCentredString(PAGE_W / 2, PAGE_H - 9.6 * mm, nom_evenement)
        # ⭐ 21/11 : n° de page en haut à droite, lui aussi dans la zone imprimable
        if not demi_total:
            c.setFillColor(GRIS); c.setFont("Helvetica", 7)
            c.drawRightString(PAGE_W - MARGIN_X, PAGE_H - 9.6 * mm, "%03d" % no_page)

        for row in range(ROWS_PAGE):
            for col_i in range(COLS_PAGE):
                if faites >= nb_cartes:
                    break
                x0 = MARGIN_X + col_i * (CARD_W + GUTTER_X)
                y0 = MARGIN_BOT + (ROWS_PAGE - 1 - row) * (CARD_H + GUTTER_Y)
                cols_nums = _gen_carte(rng)
                idx = (serie - 1) % len(RAINBOW)
                coul = (couleur_perso if (couleur and couleur_perso)
                        else RAINBOW[idx] if couleur else "#9A9A9A")
                if series_par_cote:
                    _demi = COLS_PAGE // 2
                    serie = serie_cote + row * _demi + (col_i % _demi)
                if demi_total:
                    # ⭐ 21/11 (HEIPOE, 9 rames, série 1→9000) : chaque DEMI-FEUILLE
                    #    a son numéro — la GAUCHE (samedi) de 1 à demi_total, puis la DROITE
                    #    continue de demi_total+1 à 2×demi_total ; les grilles suivent.
                    _demi = COLS_PAGE // 2
                    _k = row * _demi + (col_i % _demi)
                    _base = (no_page - 1) * ROWS_PAGE * _demi
                    serie = _base + _k + 1 + (0 if col_i < _demi else demi_total * ROWS_PAGE * _demi)
                _dessiner_carte(c, x0, y0, cols_nums, coul, serie, titre_jeu, telephone,
                                style=style, evenement_id=evenement_id,
                                nom_centre=((nom_gauche if col_i < COLS_PAGE // 2 else nom_droite)
                                            if (nom_gauche or nom_droite)
                                            else nom_centre if nom_centre is not None
                                            else nom_evenement))
                serie += 1
                faites += 1

        if demi_total:
            c.setFillColor(colors.black); c.setFont("Helvetica-Bold", 10)
            # ⭐ 21/11 (Maeva : « le 1 va sur le samedi ») : GAUCHE 1→demi_total, DROITE la suite
            c.drawString(MARGIN_X, PAGE_H - 9.6 * mm, "N° %04d" % no_page)
            c.drawRightString(PAGE_W - MARGIN_X, PAGE_H - 9.6 * mm, "N° %04d" % (demi_total + no_page))
        if series_par_cote:
            serie_cote += ROWS_PAGE * (COLS_PAGE // 2)
            # n° de page aussi au-dessus de la moitié GAUCHE (chaque demi-feuille garde le sien)
            c.setFillColor(GRIS); c.setFont("Helvetica", 7)
            c.drawString(MARGIN_X, PAGE_H - 9.6 * mm, "%03d" % no_page)
        c.showPage()
        no_page += 1

    c.save()
    buf.seek(0)
    return buf


if __name__ == "__main__":
    pdf = generer_pdf(nb_cartes=12, couleur=True,
                      nom_evenement="ASSOCIATION TE MANU", titre_jeu="Grand Loto",
                      telephone="89 22 23 05")
    with open("test_p12.pdf", "wb") as f:
        f.write(pdf.read())
    print("P12 Marathon généré")
