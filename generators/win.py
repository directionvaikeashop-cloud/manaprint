# -*- coding: utf-8 -*-
"""
MANAPRINT — Générateur WIN 9 BOULES (format A4)
12 cartes par feuille A4 (3 colonnes × 4 rangées).
Chaque carte : grille 3×3 PLEINE. 9 numéros (aucune case vide).
Numéro de série EN HAUT sous l'en-tête ("Carte N° 00001").
Colonnes : col1 = 1-15, col2 = 16-30, col3 = 31-45.
Couleur arc-en-ciel (par carte) ou gris (N&B). Chiffres en gris (2 gammes ÉCO/PREMIUM).
"""
import io
import random
from reportlab.pdfgen import canvas
from reportlab.pdfbase.pdfmetrics import stringWidth as _lg_h
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
GRIS40 = colors.Color(0.60, 0.60, 0.60)
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
# (min, max) par colonne — WIN 9 boules
PLAGES = [(1, 15), (16, 30), (31, 45)]

# ═══ 🧩 LE PUZZLE DE MAEVA (sceau 13/08) ═══
# Neuf pièces, une par numéro — et sur chacune, une liasse de billets.
# Le dessin remplace les traits de grille : il DIT le jeu sans un mot.
# ⚠️ Ses neuf pièces sont parfaitement régulières (tiers en largeur comme
# en hauteur, mesuré au pixel) : le numéro se pose donc au centre de sa
# case, exactement comme avant. Seule la liasse occupe le coin haut-gauche
# de chaque pièce, il faut donc décaler le chiffre vers le bas.
_RATIO_PUZZLE = 0.9962
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


_IMAGE_PUZZLE = _choisir_image("win_puzzle", _RATIO_PUZZLE)

COLS_PAGE = 3
ROWS_PAGE = 4
MARGIN_X = 8 * mm
MARGIN_TOP = 8 * mm
MARGIN_BOT = 8 * mm
GUTTER_X = 4 * mm
GUTTER_Y = 4 * mm

CARD_W = (PAGE_W - 2 * MARGIN_X - (COLS_PAGE - 1) * GUTTER_X) / COLS_PAGE
CARD_H = (PAGE_H - MARGIN_TOP - MARGIN_BOT - (ROWS_PAGE - 1) * GUTTER_Y) / ROWS_PAGE


def _gen_carte(rng):
    """9 numéros : col1 = 3 nums (1-9), col2 = 3 nums (10-18), col3 = 3 nums (19-27).
    Grille 3×3 entièrement remplie."""
    col1 = sorted(rng.sample(range(PLAGES[0][0], PLAGES[0][1] + 1), 3))
    col2 = sorted(rng.sample(range(PLAGES[1][0], PLAGES[1][1] + 1), 3))
    col3 = sorted(rng.sample(range(PLAGES[2][0], PLAGES[2][1] + 1), 3))
    grille = [
        [col1[0], col2[0], col3[0]],
        [col1[1], col2[1], col3[1]],
        [col1[2], col2[2], col3[2]],
    ]
    return grille


# 🎲 LES PETITS NUMÉROS EN VRAIS DÉS (sceau Maeva 30/07) : 1-6 = un dé à
# points ; 7, 8, 9 = DEUX dés dont les points s'additionnent (7=4+3, 8=4+4,
# 9=5+4) ; à partir de 10, le chiffre reste roi (un dé ne sait pas dire 47).
_DECOMP_DES = {7: (4, 3), 8: (4, 4), 9: (5, 4)}


def _un_de(c, cx, cy, t, valeur, col, gris_ch):
    """Un vrai dé : carré arrondi blanc bordé couleur, points gris disposés
    comme sur les dés du commerce."""
    r = t / 2.0
    c.setStrokeColor(col); c.setLineWidth(1.1)
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


def _dessine_des(c, valeur, cx, cy, col, gris_ch):
    if valeur <= 6:
        _un_de(c, cx, cy, 11.5 * mm, valeur, col, gris_ch)
    else:
        a, b = _DECOMP_DES[valeur]
        _un_de(c, cx - 4.4 * mm, cy, 7.8 * mm, a, col, gris_ch)
        _un_de(c, cx + 4.4 * mm, cy, 7.8 * mm, b, col, gris_ch)


def _dessiner_carte(c, x0, y0, grille, couleur_hex, serie, titre_jeu="", telephone="", style="eco", evenement_id="", des=False):
    police_ch, gris_ch = _style_chiffres(style)
    col = colors.HexColor(couleur_hex)
    ncols = 3

    # ⚠️⚠️ 13/08 (sceau Maeva : « retire la grille qui enveloppe la grille
    # des puzzles ») : PLUS DE CADRE AUTOUR DU CARTON. Le puzzle se suffit
    # à lui-même — ses bords dessinés font la bordure. Le microtexte
    # anti-photocopie reste, lui : il est invisible mais il protège.
    # ═══ 🧩 LE PUZZLE N'EST QUE POUR WIN NORMAL (sceau Maeva 13/08) ═══
    # ⚠️⚠️ « c'est seulement sur le WIN NORMALE que je veux faire avec le
    # modèle puzzle ». WIN CASINO (des=True) garde son ANCIEN visage :
    # son cadre, sa grille à traits, son QR et son microtexte.
    _puzzle = not des

    # ⚠️ WIN CASINO garde sa bordure et son microtexte
    if not _puzzle:
        c.setStrokeColor(col); c.setLineWidth(0.8)
        c.roundRect(x0, y0, CARD_W, CARD_H, 1.5 * mm, stroke=1, fill=0)
        if _sec:
            _sec.cadre_micro(c, x0, y0, CARD_W, CARD_H, serie, retrait=1.0 * mm)

    # ⚠️⚠️ 13/08 : sur WIN NORMAL seulement, plus de cadre microtexte.
    # ⚠️⚠️ CE QUE CELA VEUT DIRE : WIN n'a PLUS AUCUNE PROTECTION
    # anti-copie — ni QR (retiré plus tôt), ni cadre de microtexte.
    # Maeva a été prévenue et l'a voulu ainsi : elle veut le carton net.
    # ⚠️ LE MICROTEXTE DANS LES CHIFFRES RESTE, lui : chaque numéro est
    # dessiné par `chiffre_micro`, qui le trace en minuscules caractères.
    # C'est discret, invisible à l'œil, et cela survit au retrait du cadre.

    # ═══ UNE SEULE LIGNE : le nom du jeu et le numéro de série ═══
    # Elle était sur deux lignes ; une seule suffit et rend de la place
    # au puzzle.
    hdr_y = y0 + CARD_H - 3.6 * mm
    titre = "WIN 9 boules"
    if titre_jeu and titre_jeu.strip().upper() != titre.upper():
        titre = titre_jeu.strip()
    _ligne = titre + "  ·  N\u00b0 %05d" % serie
    if telephone:
        _ligne += "  ·  " + telephone
    # ⭐ 13/08 (sceau Maeva : « que les côtés soient arrondis pour un rendu
    # magnifique et pro ») : LE BANDEAU. Une pastille aux bouts ronds — les
    # coins sont arrondis À MOITIÉ DE SA HAUTEUR, ce qui donne la forme de
    # gélule des billets et des cartes de jeu. Le texte s'y pose en creux.
    _t_l = 6.0
    while _t_l > 3.4 and _lg_h(_ligne, POLICE, _t_l) > CARD_W - 9.0 * mm:
        _t_l -= 0.25
    _bh = _t_l * 1.72                       # la hauteur du bandeau
    _bw = min(_lg_h(_ligne, POLICE, _t_l) + _bh * 1.30, CARD_W - 2.0 * mm)
    _bx = x0 + (CARD_W - _bw) / 2
    _by = hdr_y - _bh * 0.34
    # ⚠️⚠️ EN COULEUR le bandeau est PLEIN et le texte blanc dessus ;
    # EN NOIR & BLANC il devient CREUX, texte gris à l'intérieur — un
    # bandeau gris plein aurait bu du toner sur chaque carton, pour rien.
    _plein = couleur_hex not in ("#9A9A9A", "#999999")
    if not _puzzle:
        # WIN CASINO garde son en-tête d'origine, sans bandeau
        _bh = 0.0
    c.setStrokeColor(col)
    c.setLineWidth(0.6)
    # ⚠️ le rayon vaut la MOITIÉ de la hauteur : c'est ce qui fait les
    # bouts parfaitement ronds. Plus petit, on aurait de simples coins
    # adoucis ; plus grand, ReportLab refuserait de dessiner.
    if not _puzzle:
        c.setFillColor(col)                 # casino : texte simple
    elif _plein:
        c.setFillColor(col)
        c.roundRect(_bx, _by, _bw, _bh, _bh / 2.0, stroke=1, fill=1)
        c.setFillColor(colors.white)
    else:
        c.roundRect(_bx, _by, _bw, _bh, _bh / 2.0, stroke=1, fill=0)
        c.setFillColor(col)
    c.setFont(POLICE, _t_l)
    c.drawCentredString(x0 + CARD_W / 2, (_by + _bh * 0.32) if _puzzle else hdr_y, _ligne)

    # Zone grille 3×3 — le puzzle gagne la ligne qu'on vient d'économiser
    grid_top = hdr_y - 2.2 * mm
    # ⚠️ 13/08 : la bande du bas était de 21 mm, taillée pour l'ancienne
    # grille rectangulaire. Le puzzle étant CARRÉ, il est bridé par la
    # LARGEUR — cette bande ne servait plus qu'à perdre de la place.
    # ⚠️ 13/08 : sans le cadre, la bande du bas peut encore se réduire —
    # le QR y tient à l'aise. Le puzzle descend d'autant et ses chiffres
    # grandissent.
    # ⚠️ 13/08 : PLUS DE BANDE EN BAS — le QR y vivait, il n'est plus là.
    # Le puzzle descend au ras du carton et ses chiffres grandissent.
    grid_bot = y0 + (1.0 if _puzzle else 21.0) * mm
    cell_w = CARD_W / ncols
    grid_h = grid_top - grid_bot
    row_h = grid_h / 3

    # séparateurs de grille
    c.setStrokeColor(GRIS_CLAIR); c.setLineWidth(0.3)
    # ═══ 🧩 LE PUZZLE À LA PLACE DES TRAITS ═══
    # ⚠️ le puzzle est CARRÉ (ratio ~1) : on le pose au plus grand qui
    # tienne dans la grille, et la grille se recale dessus — sinon les
    # neuf pièces ne coïncideraient pas avec les neuf cases.
    # ⚠️⚠️ 13/08 (sceau Maeva : « LA GRILLE DEVIENT LA GRILLE DU PUZZLE ») :
    # le puzzle N'EST PLUS un carré posé au milieu — IL EST LA GRILLE. Il
    # prend TOUTE la carte, en largeur comme en hauteur. Le dessin s'étire
    # donc un peu (il était carré, la carte ne l'est pas) : ses pièces
    # restent régulières, seule leur forme s'allonge — et les chiffres
    # gagnent dix points au passage (24,5 → 34).
    _pw = CARD_W - 0.8 * mm
    _ph = grid_h
    _px = x0 + (CARD_W - _pw) / 2
    _py = grid_bot
    if _puzzle and _os2.path.exists(_IMAGE_PUZZLE):
        try:
            # ⚠️⚠️ PAS de preserveAspectRatio ICI : il refuserait d'étirer
            # le puzzle et le recentrerait en laissant du vide sur les
            # côtés. Ici on VEUT l'étirer — le puzzle EST la grille, il
            # doit épouser la carte exactement.
            c.drawImage(_IMAGE_PUZZLE, _px, _py, _pw, _ph, mask="auto")
        except Exception:
            pass
    # la grille suit le puzzle, pièce par pièce
    cell_w = _pw / 3.0
    row_h = _ph / 3.0
    # ⚠️ WIN CASINO garde sa GRILLE À TRAITS, comme avant le puzzle
    if not _puzzle:
        c.setStrokeColor(col); c.setLineWidth(0.5)
        for _i in range(1, 3):
            c.line(_px + _i * cell_w, _py, _px + _i * cell_w, _py + _ph)
            c.line(_px, _py + _i * row_h, _px + _pw, _py + _i * row_h)
    # ⚠️⚠️ 13/08 : LA TAILLE SE CALCULE DEPUIS LA PIÈCE, plus jamais en dur.
    # Elle était figée à 32 pt : les chiffres débordaient sur les pièces
    # voisines. La LIASSE occupe le coin haut-gauche, il reste donc environ
    # les trois quarts de la pièce pour le chiffre.
    from reportlab.pdfbase.pdfmetrics import stringWidth as _lg_w
    _t_num = 42.0
    # ⚠️ 13/08 : la marge de LARGEUR était trop lâche et les chiffres
    # touchaient le bord de leur pièce. On resserre à 0,62 — la pièce
    # étant plus large que haute, c'est elle qui commande maintenant.
    # ⚠️ 13/08 : c'est la LARGEUR qui borne (la pièce fait 20,4 mm et
    # « 88 » n'en prenait que 12,6). On desserre à 0,70 : le chiffre passe
    # à 32 pt et garde 3 mm de chaque côté — il ne touche jamais le bord.
    # ⚠️ 13/08 : sans le QR ni la bande du bas, la pièce est devenue
    # presque carrée (20,4 × 20,2 mm). On desserre à 0,78 : le chiffre
    # passe à 35 pt et garde 2,3 mm de chaque côté — il respire encore.
    while _t_num > 8 and (_lg_w("88", police_ch, _t_num) > cell_w * 0.78
                          or _t_num * 0.72 > row_h * 0.78):
        _t_num -= 0.5
    x0_g = _px
    grid_top = _py + _ph

    # contenu des cellules (toutes pleines)
    for r in range(3):
        for cc in range(3):
            # ⚠️ la LIASSE occupe le coin haut-gauche de chaque pièce :
            # le chiffre descend un peu et se décale à droite pour ne pas
            # la couvrir — il reste bien au cœur de sa pièce.
            cx = x0_g + (cc + 0.54) * cell_w
            cyc = grid_top - (r + 0.62) * row_h
            val = grille[r][cc]
            if des and val <= 9:   # 🎲 jumeau CASINO : le petit numéro vit en dés
                _dessine_des(c, val, cx, cyc, col, gris_ch)
            elif _sec:  # chiffres "billet de banque" remplis de microtexte
                _sec.chiffre_micro(c, val, cx, cyc - _t_num * 0.34, _t_num, gris_ch, police_ch)
            else:
                c.setFillColor(gris_ch); c.setFont(police_ch, _t_num)
                c.drawCentredString(cx, cyc - 11, str(val))

    # ⚠️⚠️ 13/08 : PLUS DE QR SUR WIN NORMAL (Maeva le veut net).
    # ⚠️ MAIS WIN CASINO LE GARDE : sa bande du bas existe toujours.
    if not _puzzle and _sec and evenement_id:
        try:
            _q = 9.5 * mm
            _sec.carton_qr(c, x0 + CARD_W - _q - 2.0 * mm, y0 + 6.0 * mm, _q,
                           evenement_id, serie)
        except Exception:
            pass


def generer_pdf(nb_cartes=12, serie_start=1, theme="", couleur=True,
                nom_evenement="", titre_jeu="", couleur_perso="", date_lieu="", telephone="",
                style="eco", evenement_id="", des=False, page_start=1):
    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=A4, pageCompression=1)

    nb_cartes = max(1, min(int(nb_cartes), 10000))
    par_page = COLS_PAGE * ROWS_PAGE
    nb_pages = (nb_cartes + par_page - 1) // par_page

    rng = random.Random(910000 + int(serie_start))
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
                grille = _gen_carte(rng)
                coul = (couleur_perso if (couleur and couleur_perso)
                        else RAINBOW[(serie - 1) % len(RAINBOW)] if couleur else "#9A9A9A")
                _dessiner_carte(c, x0, y0, grille, coul, serie, titre_jeu, telephone, style=style, evenement_id=evenement_id, des=des)
                serie += 1
                faites += 1

        c.showPage()
        no_page += 1

    c.save()
    buf.seek(0)
    return buf


def generer_pdf_casino(**kw):
    """🎲 WIN CASINO — le jumeau où les numéros 1-9 vivent en vrais dés."""
    kw["des"] = True
    return generer_pdf(**kw)


if __name__ == "__main__":
    pdf = generer_pdf(nb_cartes=12, couleur=True,
                      nom_evenement="ASSOCIATION TE MANU", titre_jeu="WIN 9 boules",
                      telephone="89.22.23.05")
    with open("test_pow.pdf", "wb") as f:
        f.write(pdf.read())
    print("WIN 9 boules généré")
