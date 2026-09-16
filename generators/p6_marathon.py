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

# ══ ✒️ LA CALLIGRAPHIE DE LA CASE CENTRALE (sceau Maeva 11/09) ══════
# La case du milieu est libre par nature : quand le client donne une
# personnalisation, son NOM s'y écrit EN CALLIGRAPHIE. TeX Gyre Chorus est
# la seule vraie anglaise installée ; à défaut on retombe sur l'italique.
import os as _os6
from reportlab.pdfbase import pdfmetrics as _pm6
from reportlab.pdfbase.ttfonts import TTFont as _TF6
from reportlab.pdfbase.pdfmetrics import stringWidth as _sw6
# ⚠️ TeX Gyre Chorus est livré en OTF, que ReportLab ne sait pas lire : une
#    copie convertie en TTF est rangée à côté de ce fichier (Chorus.ttf).
#    Si elle manque, on retombe sur l'italique serif, puis sur Times-Italic.
_POLICE_SCRIPT = "Times-Italic"
for _nom6, _ch6 in (
        ("CHORUS", _os6.path.join(_os6.path.dirname(_os6.path.abspath(__file__)), "Chorus.ttf")),
        ("FSERIT", "/usr/share/fonts/truetype/freefont/FreeSerifItalic.ttf")):
    try:
        _pm6.registerFont(_TF6(_nom6, _ch6)); _POLICE_SCRIPT = _nom6; break
    except Exception:
        pass


def _lignes_centre(texte):
    """✒️ Le NOM sur la 1re ligne (calligraphié, en gros), le reste dessous."""
    # ⭐ 11/09 : ON PEUT IMPOSER LA COUPURE avec « | » ou un retour à la
    #    ligne — « SAINT ANNE | HIVA OA » donne deux lignes propres au lieu
    #    d'un découpage automatique qui séparerait SAINT de ANNE.
    brut = str(texte).replace("\n", "|")
    if "|" in brut:
        return [l.strip() for l in brut.split("|") if l.strip()][:3]
    mots = [m for m in brut.split(" ") if m]
    if not mots:
        return []
    if len(mots) == 1:
        return [mots[0]]
    if len(mots) >= 3:
        return [mots[0], " ".join(mots[1:-1]), mots[-1]]
    return [mots[0], " ".join(mots[1:])]


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
    """5 colonnes × 5 numéros distincts triés. Case centrale (col N, ligne 2) = MARATHON.
    ⚠️ Tirage libre, gardé pour compatibilité : la COLONNE DE GRILLES se
    fabrique désormais par _gen_bande (règle MARATHON, voir ci-dessous)."""
    cols = []
    for (lo, hi) in RANGES:
        cols.append(sorted(random.sample(range(lo, hi + 1), GRID_N)))
    return cols


# ══ 🏃 LA RÈGLE MARATHON (enseignée par Maeva 04/08, celle du QUINES 90) ═══
# « dans une colonne, sur les 3 grilles, les nombres de 1 à 15 suivent une
#   chronologie aléatoire, avec un seul nombre 1 qui doit sortir »
# → l'unité du marathon est la COLONNE DE GRILLES : 3 grilles empilées.
#   Chaque quinzaine y est distribuée AU HASARD et EN ENTIER :
#     colonnes B · I · G · O : 3 grilles × 5 cases = 15 → 1-15 EXACTEMENT
#                              UNE FOIS chacun, aucun doublon dans la colonne ;
#     colonne  N (centre libre) : 3 × 4 = 12 cases seulement → 12 des 15,
#                              les 3 restants tirés au sort à chaque bande.
#   Dans chaque grille, la colonne reste TRIÉE croissante (règle P6).

def _gen_bande(n_grilles=3):
    """Fabrique une COLONNE DE GRILLES : n_grilles cartes qui portent,
    ensemble, chaque quinzaine une seule fois. Renvoie la liste des cartes."""
    cartes = [[None] * len(RANGES) for _ in range(n_grilles)]
    for ci, (lo, hi) in enumerate(RANGES):
        centre_libre = (ci == 2)               # colonne N : case du milieu libre
        par_grille = GRID_N - (1 if centre_libre else 0)
        sac = list(range(lo, hi + 1))
        random.shuffle(sac)                    # la chronologie aléatoire de Maeva
        besoin = n_grilles * par_grille
        while len(sac) < besoin:               # (bandes plus hautes que 3 grilles)
            rab = list(range(lo, hi + 1))
            random.shuffle(rab)
            sac += rab
        pos = 0
        for gi in range(n_grilles):
            part = sorted(sac[pos:pos + par_grille])   # triée dans la grille
            pos += par_grille
            if centre_libre:                   # on réserve la place du centre
                part = part[:2] + [None] + part[2:]
            cartes[gi][ci] = part
    return cartes


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


def _dessiner_carte(c, x0, y0, carte, couleur_hex, serie, encre, telephone="", titre_jeu="", style="eco", evenement_id="", cartes=False, nom_centre=""):
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
                # ✒️ case libre : le NOM DU CLIENT s'y écrit EN CALLIGRAPHIE.
                #    Sans personnalisation elle reste vide (et reçoit le QR).
                if nom_centre:
                    _lg = _lignes_centre(nom_centre)
                    _larg = cell_w * 0.88
                    _t = 16.0
                    while _t > 4.0 and _sw6(_lg[0], _POLICE_SCRIPT, _t) > _larg:
                        _t -= 0.25
                    _tp = max(3.2, _t * 0.40)
                    while _tp > 3.0 and len(_lg) > 1 and max(
                            _sw6(_l, "Helvetica-Bold", _tp) for _l in _lg[1:]) > _larg:
                        _tp -= 0.25
                    _haut = _t * 0.72 + (len(_lg) - 1) * _tp * 1.40
                    _y0c = cy + _haut / 2 - _t * 0.60
                    c.setFillColor(gris_ch)
                    c.setFont(_POLICE_SCRIPT, _t)
                    c.drawCentredString(cx, _y0c, _lg[0])
                    c.setFont("Helvetica-Bold", _tp)
                    for _k, _l in enumerate(_lg[1:], 1):
                        c.drawCentredString(cx, _y0c - _t * 0.26 - _k * _tp * 1.40, _l)
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
                nom_centre=None,
                style="eco", evenement_id="", cartes=False, page_start=1):
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
            # ⭐⭐ 11/09 (sceau Maeva : « que ça se voie à l'impression ») :
            #    le nom de la cliente passe de 11 à 17 pt. La marge du haut
            #    fait 11 mm et la 1re carte commence à 31 pt : mesuré, il y
            #    a la place. La taille redescend toute seule si le nom est
            #    trop long pour la largeur de la feuille.
            #    ⚠️ MESURÉ : la 1re carte commence à 31 pt du haut et une
            #    imprimante ne tire pas dans les 4 premiers millimètres. Le
            #    nom tient donc entre 11 et 24 pt du bord — d'où 14 pt et
            #    une ligne de base à 7,5 mm.
            _nomh = nom_evenement.replace("|", " ").replace("  ", " ").strip()
            _tnom = 14.0
            while _tnom > 8.0 and _sw6(_nomh, "Helvetica-Bold", _tnom) > PAGE_W - 40 * mm:
                _tnom -= 0.5
            c.setFillColor(NOIR); c.setFont("Helvetica-Bold", _tnom)
            c.drawCentredString(PAGE_W / 2, PAGE_H - 7.5 * mm, _nomh)
        # ⭐ 11/09 (sceau Maeva) : QUAND LE CLIENT DONNE SON NOM, C'EST LUI
        #    QUI OCCUPE LE HAUT DE LA FEUILLE — « P6 MARATHON » s'efface au
        #    lieu de se répéter sous la personnalisation. La 2e ligne ne
        #    garde alors que la date et le numéro de page.
        #    Sans personnalisation, le titre du jeu revient comme avant.
        titre_aff = titre_jeu if titre_jeu else (
            "" if nom_evenement else ("PJOKER" if cartes else "P6 MARATHON"))
        ligne2 = titre_aff
        if date_lieu:
            ligne2 = (ligne2 + "  ·  " + date_lieu) if ligne2 else date_lieu
        ligne2 = (ligne2 + f"  ·  Page {no_page}") if ligne2 else f"Page {no_page}"
        c.setFillColor(GREY); c.setFont("Helvetica", 7)
        if nom_evenement:
            # ⭐ avec une personnalisation, la page et la date filent à
            #    DROITE sur la même ligne : le nom garde tout le centre.
            c.drawRightString(PAGE_W - 6 * mm, PAGE_H - 7.5 * mm, ligne2)
        else:
            c.drawCentredString(PAGE_W / 2, PAGE_H - 6 * mm, ligne2)

        # 🏃 une bande par COLONNE de la feuille : 3 grilles empilées qui
        # portent ensemble toute la quinzaine de chaque colonne B·I·N·G·O
        bandes = [_gen_bande(ROWS_PAGE) for _ in range(COLS_PAGE)]
        for row in range(ROWS_PAGE):
            for col_i in range(COLS_PAGE):
                x0 = MARGIN_X + col_i * (CARD_W + GUTTER_X)
                y0 = MARGIN_BOT + (ROWS_PAGE - 1 - row) * (CARD_H + GUTTER_Y)
                carte = bandes[col_i][row]
                coul = (couleur_perso if (couleur and couleur_perso)
                        else RAINBOW[(serie - 1) % len(RAINBOW)] if couleur else "#999999")
                _dessiner_carte(c, x0, y0, carte, coul, serie, encre, telephone, titre_jeu, style=style, evenement_id=evenement_id, cartes=cartes,
                                nom_centre=(nom_centre if nom_centre is not None else nom_evenement))
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
