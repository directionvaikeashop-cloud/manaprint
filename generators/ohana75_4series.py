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
from reportlab.pdfbase.pdfmetrics import stringWidth as _lg_o
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

# ══ ✒️ LA CALLIGRAPHIE DE LA CASE CENTRALE (sceau Maeva 11/09) ══════
# Même travail que sur P6 MARATHON et OHANA 75 · 2 séries : quand le client
# donne une personnalisation, son NOM remplace le « FREE / SPACE » et
# s'écrit en calligraphie. Le NUMÉRO DE SÉRIE reste au milieu, entre les
# deux lignes — il ne disparaît jamais.
import os as _os74
from reportlab.pdfbase import pdfmetrics as _pm74
from reportlab.pdfbase.ttfonts import TTFont as _TF74
from reportlab.pdfbase.pdfmetrics import stringWidth as _sw74
_POLICE_SCRIPT = "Times-Italic"
for _n74, _c74 in (
        ("CHORUS", _os74.path.join(_os74.path.dirname(_os74.path.abspath(__file__)), "Chorus.ttf")),
        ("FSERIT", "/usr/share/fonts/truetype/freefont/FreeSerifItalic.ttf")):
    try:
        _pm74.registerFont(_TF74(_n74, _c74)); _POLICE_SCRIPT = _n74; break
    except Exception:
        pass


def _lignes_centre74(texte):
    """✒️ 23/09 (sceau Maeva — échantillon KAIMIKILANIE) : LA CASE CENTRALE
    COUPE SUR « | » COMME LE 2 SÉRIES.

    ⚠️⚠️ NE PAS SUPPRIMER. Avant, le 4 séries faisait un bête
    « premier mot en haut, tout le reste en bas » : la barre « | » se
    retrouvait IMPRIMÉE sur la carte (« | KOHUHEILANIE | 11 NOVEMBRE
    2026 ») et la ligne était illisible. Le 2 séries, lui, coupait déjà
    proprement. Les deux jeux doivent se comporter PAREIL, sinon une
    même commande sort avec deux mises en page différentes.
    """
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
_GRIS_ECO = colors.Color(0.35, 0.35, 0.35)
_POLICE_P15 = "Helvetica-Bold"
_GRIS_P15 = colors.Color(0.35, 0.35, 0.35)
# ⭐⭐ 11/09 (sceau Maeva) : L'ÉCRITURE LATIN MODERN ROMAN dans les deux
#    gammes, et le gris de 0,50/0,55 à 0,35.
#    ⚠️ MESURÉ À TAILLE ÉGALE : cette écriture consomme 61 % de moins que
#    l'ancienne grasse. C'est ELLE la vraie économie de toner, pas la
#    nuance de gris. Ne jamais remettre une grasse « pour que ça se voie ».
#    ⚠️ LatinModern.ttf est rangé à côté de ce fichier (l'original est en
#    OTF, illisible par ReportLab). S'il manque, on garde l'ancienne.
import os as _osQ4
try:
    _pm.registerFont(_TF("LMROMAN", _osQ4.path.join(
        _osQ4.path.dirname(_osQ4.path.abspath(__file__)), "LatinModern.ttf")))
    _POLICE_ECO = "LMROMAN"
    _POLICE_P15 = "LMROMAN"
except Exception:
    pass

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
# ⭐⭐ 23/09 (sceau Maeva : « la personnalisation du haut de feuille à mettre
#    dans l'encadrement où il y a BINGO ») : LES MARGES HAUT ET BAS PASSENT
#    DE 8 À 5 mm. On récupère 3 mm par carton, et ces 3 mm vont TOUS dans le
#    bandeau (HDR_H : 9 → 12 mm) pour y loger le nom du client.
#    ⚠️⚠️ LA GRILLE NE BOUGE PAS D'UN POIL : le carton grandit de 3 mm ET le
#    bandeau grandit de 3 mm, donc grid_h = CARD_H − HDR_H est identique.
#    Les cases, les cercles et les chiffres font exactement la même taille
#    qu'avant. NE PAS « SIMPLIFIER » en ne changeant qu'un des deux.
#    ⚠️ 5 mm est le plancher : en dessous, certaines imprimantes laser
#    refusent d'imprimer la bordure du carton.
MARGIN_TOP = 5 * mm
MARGIN_BOT = 5 * mm
GUTTER = 6 * mm

CARD_W = (PAGE_W - 2 * MARGIN_X - GUTTER) / COLS_PAGE
CARD_H = (PAGE_H - MARGIN_TOP - MARGIN_BOT - GUTTER) / ROWS_PAGE
HDR_H = 12.5 * mm
# ⚠️ HAUTEUR D'ORIGINE DU BANDEAU BINGO. Les cases B I N G O gardent
#    EXACTEMENT cette hauteur ; les 3,5 mm gagnés font une bande à part
#    AU-DESSUS, réservée au nom du client. NE PAS FUSIONNER LES DEUX.
HDR_BINGO = 9 * mm


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


def _dessiner_carte(c, x0, y0, cols_paires, couleur_hex, serie, titre_jeu="", telephone="", style="eco", evenement_id="", nom_centre=""):
    police_ch, gris_ch = _style_chiffres(style)
    col = colors.HexColor(couleur_hex)
    cell_w = CARD_W / 5

    # Ligne d'identité — le nom du jeu apparaît TOUJOURS.
    # ⭐⭐ 23/09 (sceau Maeva) : ELLE EST DESCENDUE DANS LE CARTON. Elle
    #    était imprimée AU-DESSUS de la bordure : à la découpe elle partait
    #    à la poubelle. Elle tient maintenant la gauche de la bande du nom.
    ident = "OHANA 75 \u00b7 4 s\u00e9ries \u2014 N\u00b0 %06d" % serie
    if titre_jeu and "OHANA" not in titre_jeu.strip().upper():
        ident += "  \u00b7  " + titre_jeu.strip()
    if telephone:
        ident += "  \u00b7  " + telephone
    ident = ident[:90]

    # Bordure carte
    c.setStrokeColor(col); c.setLineWidth(0.9)
    c.roundRect(x0, y0, CARD_W, CARD_H, 1.5 * mm, stroke=1, fill=0)
    if _sec:  # cadre intérieur en microtexte (sécurité anti-photocopie)
        _sec.cadre_micro(c, x0, y0, CARD_W, CARD_H, serie, retrait=1.0 * mm)

    # En-tête B I N G O + MARATHON au-dessus du G (fidèle au modèle)
    hdr_bas = y0 + CARD_H - HDR_H
    hdr_haut = hdr_bas + HDR_BINGO     # ⚠️ le haut des CASES B I N G O
    c.setStrokeColor(col); c.setLineWidth(0.6)
    c.line(x0, hdr_bas, x0 + CARD_W, hdr_bas)
    # ⭐ 23/09 : les cases B I N G O sont refermées par un trait à leur
    #    sommet. Avant, c'était la bordure du carton qui les fermait ; la
    #    bordure est maintenant 3,5 mm plus haut (bande du nom du client),
    #    donc sans ce trait les cases resteraient ouvertes. Dessin identique.
    c.line(x0, hdr_haut, x0 + CARD_W, hdr_haut)
    for i in range(1, 5):
        c.line(x0 + i * cell_w, hdr_bas, x0 + i * cell_w, hdr_haut)
    c.setFillColor(col)
    for i, lettre in enumerate(LETTRES):
        cx = x0 + (i + 0.5) * cell_w
        if i == 3:  # G — MARATHON au-dessus
            c.setFont(POLICE, 4.5)
            # ⚠️ calé sur le HAUT DES CASES (hdr_haut), plus sur le bord du
            #    carton : il reste exactement où il était dans la maquette.
            c.drawCentredString(cx, hdr_haut - 3.0 * mm, "MARATHON")
            c.setFont(POLICE, 10)
            c.drawCentredString(cx, hdr_bas + 1.6 * mm, lettre)
        else:
            c.setFont(POLICE, 13)
            c.drawCentredString(cx, hdr_bas + 2.2 * mm, lettre)

    # ⭐⭐ 23/09 (sceau Maeva : « la personnalisation du haut de feuille à
    #    mettre dans l'encadrement où il y a BINGO ») : LA BANDE DU NOM.
    #    Elle occupe les 3,5 mm gagnés sur les marges, entre le haut des
    #    cases B I N G O et la bordure du carton :
    #       à gauche  → OHANA 75 · 4 séries · N° du carton
    #       au centre → LE NOM DU CLIENT ET SA DATE, en noir
    #    ⚠️⚠️ AVANT, le nom était en haut de la FEUILLE : on le découpait et
    #    on le jetait. Maintenant il reste sur le carton. NE PAS LE REMONTER.
    #    ⚠️ Le texte se rétrécit tout seul ; plafonné à 7,5 pt sinon il monte
    #    dans le cadre de microtexte (1 mm à l'intérieur de la bordure).
    _bande_y = hdr_haut + 1.05 * mm
    c.setFillColor(col); c.setFont(POLICE, 5.0)
    c.drawString(x0 + 2.2 * mm, _bande_y, ident)
    _evt4 = (nom_centre or "").replace("|", "  ·  ").replace("\n", "  ·  ")
    _evt4 = " ".join(_evt4.split())
    if _evt4:
        _libre4 = CARD_W - 2 * (2.2 * mm + _sw74(ident, POLICE, 5.0) + 3 * mm)
        _te4 = 7.5
        while _te4 > 3.6 and _sw74(_evt4, POLICE, _te4) > _libre4:
            _te4 -= 0.25
        c.setFillColor(colors.black); c.setFont(POLICE, _te4)
        c.drawCentredString(x0 + CARD_W / 2, _bande_y, _evt4)

    # Grille 5×5 : séparateurs pointillés discrets (fidèle au modèle)
    grid_h = hdr_bas - (y0 + 2.2 * mm)   # petit pied : la dernière rangée ne touche JAMAIS le trait de fond
    cell_h = grid_h / 5
    c.setStrokeColor(GRIS_CLAIR); c.setLineWidth(0.3)
    c.setDash(1.5, 1.8)
    for i in range(1, 5):
        c.line(x0 + i * cell_w, y0, x0 + i * cell_w, hdr_bas)
        yp = hdr_bas - i * cell_h - 1.2   # pointillé descendu au CENTRE exact du couloir d'encre
        c.line(x0, yp, x0 + CARD_W, yp)
    c.setDash()

    # Les cases : cercle + petit numéro (colonne N : la case centrale = FREE SPACE)
    # ⚠️⚠️ 13/08 : LA BULLE DOIT ENVELOPPER SON CHIFFRE. À 24 pt elle était
    # trop petite et le chiffre débordait. On la calcule DEPUIS le chiffre :
    # « 88 » à 24 pt fait 10,8 mm, il lui faut donc au moins 6,5 mm de rayon.
    # Elle reste bornée par la case pour ne jamais mordre la voisine.
    _t_prevu = 24
    # ⚠️⚠️ 11/09 : LE RAYON SE CALCULE SUR LA DIAGONALE DU CHIFFRE, pas sur
    #    sa seule largeur. L'ancien calcul (largeur × 0,64) marchait avec
    #    DejaVu, dont le « 88 » est large ; avec Latin Modern, bien plus
    #    étroit, le cercle rétrécissait alors que la HAUTEUR du chiffre ne
    #    changeait pas — et les chiffres débordaient par le haut.
    #    On prend donc la demi-diagonale du rectangle du chiffre, plus une
    #    marge : le cercle s'adapte à n'importe quelle écriture.
    _lg88 = _lg_o("88", police_ch, _t_prevu)
    _ht88 = _t_prevu * 0.72                      # hauteur réelle des chiffres
    rayon = min(cell_w * 0.42, cell_h * 0.34,
                max(((_lg88 / 2) ** 2 + (_ht88 / 2) ** 2) ** 0.5 * 1.16, 3.0 * mm))
    # ⭐ 13/08 (sceau Maeva) : LES DEUX CHIFFRES À 24 PT, à la taille du
    # modèle que ses clientes aiment. C'est la BULLE qui borne le cerclé.
    t_cercle, t_petit = 24, 24
    for ci, paires in enumerate(cols_paires):
        idx = 0
        for ri in range(5):
            case_x = x0 + ci * cell_w
            case_y = hdr_bas - (ri + 1) * cell_h
            if ci == 2 and ri == 2:
                # ── FREE SPACE : le cœur de la carte, avec numéro… et QR 🛡️ ──
                # ⚠️⚠️ 11/09 (sceau Maeva : « la personnalisation à la place
                #    de SPACE à bien centrer ») : le texte était calé à 0,30
                #    de la case — une position héritée du temps où le QR
                #    occupait la droite. SANS QR, ON CENTRE VRAIMENT.
                fx = case_x + (cell_w * 0.30 if evenement_id else cell_w / 2)
                c.setFillColor(col)
                # ✒️ 11/09 : avec une personnalisation, le NOM est calligraphié
                #    au-dessus du numéro et le reste (téléphone) en dessous ;
                #    sans personnalisation on garde « FREE / SPACE ».
                _perso = (nom_centre or "").strip()
                if _perso:
                    # ✒️ 23/09 : MÊME RENDU QUE LE 2 SÉRIES — le nom
                    #    calligraphié en haut, les lignes suivantes en
                    #    petites capitales, le numéro de carte tout en bas.
                    #    Le bloc est CENTRÉ dans la case : on mesure sa
                    #    hauteur totale avant de poser la première ligne,
                    #    sinon avec trois lignes le texte sort de la case.
                    _lg4 = _lignes_centre74(_perso)
                    _larg = cell_w * (0.56 if evenement_id else 0.90)
                    _th = 8.0
                    while _th > 3.4 and _sw74(_lg4[0], _POLICE_SCRIPT, _th) > _larg:
                        _th -= 0.25
                    _tp4 = max(3.0, _th * 0.52)
                    while _tp4 > 2.6 and len(_lg4) > 1 and max(
                            _sw74(_l, POLICE, _tp4) for _l in _lg4[1:]) > _larg:
                        _tp4 -= 0.15
                    _ts4 = 5.5
                    _htot = _th * 0.72 + (len(_lg4) - 1) * _tp4 * 1.30 + _ts4 * 1.45
                    _yc4 = case_y + cell_h / 2 + _htot / 2 - _th * 0.62
                    c.setFont(_POLICE_SCRIPT, _th)
                    c.drawCentredString(fx, _yc4, _lg4[0])
                    c.setFont(POLICE, _tp4)
                    for _k4, _l4 in enumerate(_lg4[1:], 1):
                        c.drawCentredString(fx, _yc4 - _th * 0.24 - _k4 * _tp4 * 1.30, _l4)
                    _ys4 = _yc4 - _th * 0.24 - (len(_lg4) - 1) * _tp4 * 1.30 - _ts4 * 1.45
                    c.setFont(POLICE, _ts4)
                    c.drawCentredString(fx, _ys4, "%06d" % serie)
                else:
                    c.setFont(POLICE, 5.5)
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
            # ⚠️⚠️ 13/08 (sceau Maeva : « pousse vers la gauche pour ne pas
            # déranger les chiffres hors bulles ») : LA BULLE SE COLLE À
            # GAUCHE. Elle était à 0,36 de la case en dur ; à 24 pt elle
            # empiétait sur la place du petit chiffre. On la pose depuis le
            # BORD GAUCHE de la case — juste son rayon plus un cheveu.
            # ⭐⭐ 11/09 (sceau Maeva : « centre-les bien dans chaque
            #    carré ») : L'ENSEMBLE BULLE + PETIT CHIFFRE EST CENTRÉ.
            #    Mesuré avant correction : la bulle laissait 0,60 mm à
            #    gauche et 15,31 mm à droite — tout était tassé dans le
            #    coin. On calcule maintenant la largeur totale occupée
            #    (bulle + petit numéro) et on la centre dans la case.
            _lp0 = _lg_o("88", police_ch, t_petit)
            _larg_bloc = 2 * rayon + _lp0 * 1.02
            ccx = case_x + max(rayon + 0.4 * mm, (cell_w - _larg_bloc) / 2 + rayon)
            # ⚠️⚠️ 13/08 (sceau Maeva : « que les chiffres dans les bulles
            # ne dépassent pas les grilles ») : LA BULLE SE PLACE TOUTE
            # SEULE. Elle était posée à 0,72 de la case en dur ; à 24 pt
            # son rayon la faisait chevaucher le trait de la rangée du
            # dessus. On la remonte le plus haut possible, MAIS jamais
            # au-delà de ce que la case permet — son sommet reste toujours
            # sous le trait, avec un cheveu de marge.
            # ⭐ et VERTICALEMENT de même : la bulle occupe le haut, le
            #    petit numéro le bas ; on centre les deux ensemble au lieu
            #    de coller la bulle sous le trait du dessus.
            _hors = rayon + 0.4 * mm
            _haut_bloc = 2 * rayon + t_petit * 0.82
            _marge_v = max(0.4 * mm, (cell_h - _haut_bloc) / 2)
            ccy = case_y + min(cell_h - _hors, cell_h - _marge_v - rayon)
            # ⭐ 11/09 : le cercle passe de 0,7 à 0,5 — il y en a beaucoup
            #    par feuille, c'est le 2e poste de toner après les chiffres.
            c.setStrokeColor(col if False else GRIS); c.setLineWidth(0.5)
            c.setStrokeColor(col)
            c.circle(ccx, ccy, rayon, stroke=1, fill=0)
            # ⚠️ LE PETIT CHIFFRE se pose SOUS ET À DROITE de la bulle,
            # sans jamais la toucher : on part du BORD DE LA BULLE, pas
            # d'une fraction de case en dur. Il reste dans sa case.
            _lp = _lg_o("88", police_ch, t_petit)
            _px_petit = min(ccx + rayon + _lp * 0.52, case_x + cell_w - _lp * 0.58)
            _py_petit = max(case_y + cell_h * 0.075, ccy - rayon - t_petit * 0.62)
            # ⚠️⚠️ LE MICROTEXTE EST GARDÉ (sceau Maeva 11/09, après essai
            #    dans les deux sens).
            #    ⚠️ CONTRE-INTUITIF MAIS MESURÉ : le microtexte NE RAJOUTE
            #    PAS d'encre, il CREUSE le chiffre — l'intérieur devient
            #    des lettres minuscules séparées de blanc, au lieu d'une
            #    surface pleine. Avec microtexte 2,88 % · sans 3,51 %,
            #    soit 22 % DE TONER EN PLUS SANS LUI.
            #    On le garde donc : moins de toner, ET la protection
            #    anti-photocopie sur chaque chiffre.
            if _sec:  # chiffres "billet de banque" remplis de microtexte
                _sec.chiffre_micro(c, n_cercle, ccx, ccy - t_cercle * 0.36, t_cercle, gris_ch, police_ch)
                _sec.chiffre_micro(c, n_petit, _px_petit, _py_petit, t_petit, gris_ch, police_ch)
            else:
                c.setFillColor(gris_ch); c.setFont(police_ch, t_cercle)
                c.drawCentredString(ccx, ccy - t_cercle * 0.36, str(n_cercle))
                c.setFont(police_ch, t_petit)
                c.drawCentredString(_px_petit, _py_petit, str(n_petit))


def generer_pdf(nb_cartes=4, serie_start=1, theme="", couleur=True,
                nom_evenement="", titre_jeu="", couleur_perso="", date_lieu="", telephone="",
                style="eco", evenement_id="", page_start=1):
    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=landscape(A4), pageCompression=1)

    nb_cartes = max(1, min(int(nb_cartes), 10000))
    par_page = COLS_PAGE * ROWS_PAGE
    nb_pages = (nb_cartes + par_page - 1) // par_page

    rng = random.Random(998000 + int(serie_start))
    serie = int(serie_start)
    # 📄 la page continue d'une rame à l'autre (sceau Maeva 12/08)
    no_page = max(1, int(page_start))
    faites = 0

    for _ in range(nb_pages):
        # en-tête de page + traits de découpe pointillés (fidèle au modèle)
        # ⭐⭐ 23/09 (sceau Maeva : « la personnalisation du haut de feuille à
        #    mettre dans l'encadrement où il y a BINGO ») : PLUS DE NOM ICI.
        #    Il est imprimé dans la bande du nom de CHAQUE carton, à
        #    l'intérieur de la bordure (voir _dessiner_carte).
        #    ⚠️⚠️ IL N'Y A PLUS LA PLACE DE TOUTE FAÇON : la marge du haut est
        #    passée de 8 à 5 mm pour agrandir le bandeau des cartons. Écrire
        #    à 6,6 mm mordrait maintenant sur le premier carton.
        #    ⚠️ NE PAS RÉTABLIR : on aurait le nom deux fois.
        c.setFillColor(GRIS_CLAIR); c.setFont(POLICE, 5.5)
        c.drawRightString(PAGE_W - 6 * mm, PAGE_H - 3.4 * mm, "%03d" % no_page)
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
                                nom_centre=nom_evenement,
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
