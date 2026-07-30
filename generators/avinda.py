# -*- coding: utf-8 -*-
"""
MANAPRINT — Générateur OHANA 75 · 2 SÉRIES (format A4)
2 cartes (séries) par feuille A4, séparées par un trait de découpe.
Chaque carte : grille 5×5 B·I·N·G·O, 2 numéros par case (un grand entouré + un petit),
case centrale FREE avec le N° de série. Règle MARATHON.\n🅰️ 3 LETTRES DIFFÉRENTES (A→L) vivent DANS les verres mystère, une par coupe — pilote LETTRE DE SALLE.
Plages : B 1-15, I 16-30, N 31-45, G 46-60, O 61-75.
Couleur arc-en-ciel (par carte) ou gris (économie d'encre). Personnalisation + responsable.
SÉCURITÉ ANTI-PHOTOCOPIE (module generators/securite.py) : cadre intérieur en
microtexte + chiffres remplis de microtexte (technique billet de banque).
Vérification à la loupe x10 : lettres nettes = original, trait flou = photocopie.
"""
import io
import random
import hmac as _hmac
import random as _random
import hashlib as _hashlib
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

# Police fine (look OHANA) avec repli Helvetica
try:
    pdfmetrics.registerFont(TTFont("DJL", "/usr/share/fonts/truetype/dejavu/DejaVuSans-ExtraLight.ttf"))
    POLICE = "DJL"
except Exception:
    POLICE = "Helvetica"

RAINBOW = [
    "#E53935", "#FB8C00", "#F9A825", "#43A047", "#00ACC1",
    "#1E88E5", "#3949AB", "#8E24AA", "#D81B60", "#6D4C41",
]
NOIR = colors.black
GRIS = colors.Color(0.42, 0.42, 0.42)
GRIS40 = colors.Color(0.50, 0.50, 0.50)   # gris 50% (un peu plus fort) — pour les chiffres
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

MYSTERE_COLONNES = ("B", "I", "O")   # 🔮 les colonnes du mystère (sceau Maeva 29/07 : « BIO »)
# Un « ? » par colonne, LE MÊME TRIO DE COLONNES sur tous les cartons — la
# révélation tire UNE boule-mystère PAR COLONNE, dans sa plage (règle Maeva :
# un mystère dans le I ne peut valoir qu'un numéro du I). Pour monter selon
# le retour des clients : ajouter une lettre ici (et au caller/app).


ALPHABET_LETTRES = "ABCDEFGHIJKL"   # 🅰️ LA LETTRE DU CARTON (décision Maeva 30/07)
# 12 lettres (pas 26) : 1 chance sur 12 par carton — presque chaque soirée a son
# porteur. Chaque carton PORTE SA LETTRE, visible dans un médaillon de la case
# vie ; en salle, le caller tire LA LETTRE (A→L) en public — le porteur gagne
# le bonus du comptoir. Rien de caché : la lettre est imprimée, le tirage est
# public et journalisé. Pilote : la famille A VINDA (les 2 jumeaux).


def _lettres_carte(serie):
    """LES 3 LETTRES du carton — une par coupe B·I·O, TOUTES DIFFÉRENTES
    (décision Maeva 30/07 : « différente lettre dans chaque coupe ») ;
    déterministes par HMAC : la refab redonne exactement les mêmes."""
    h = _hmac.new(b"LETTRE-2KEA", ("LETTRE:%d" % serie).encode(), _hashlib.sha256)
    rl = _random.Random(h.digest())
    return rl.sample(ALPHABET_LETTRES, len(MYSTERE_COLONNES))


def _positions_colonnes():
    """position (0-23, ordre du dessin) -> répartition par colonne B·I·N·G·O."""
    d = {lettre: [] for lettre, a, b in PLAGES}
    pos = 0
    for j in range(5):
        for i, (lettre, a, b) in enumerate(PLAGES):
            if i == 2 and j == 2:
                continue
            d[lettre].append(pos)
            pos += 1
    return d


PAGE_W, PAGE_H = A4
# position 0-23 -> lettre de colonne (⚠️ le saut de la case vie décale la
# numérotation : un modulo 5 mentirait dès la 3e rangée)
PLAGES = [("B", 1, 15), ("I", 16, 30), ("N", 31, 45), ("G", 46, 60), ("O", 61, 75)]
# position 0-23 -> lettre de colonne (⚠️ le saut de la case vie décale la
# numérotation : un modulo 5 mentirait dès la 3e rangée)
_COL_DE_CASE = {pos: lettre for lettre, ps in _positions_colonnes().items() for pos in ps}

MARGIN_X = 8 * mm
MARGIN_TOP = 9 * mm
MARGIN_BOT = 8 * mm
GUTTER_Y = 7 * mm   # espace de découpe entre les 2 cartes

CARD_W = PAGE_W - 2 * MARGIN_X
CARD_H = (PAGE_H - MARGIN_TOP - MARGIN_BOT - GUTTER_Y) / 2


def _verre(c, cx, cy, col):
    """COUPE DE VIN VIDE au trait (vision Maeva) : buvant, flancs, jambe
    fine et pied — tout en vecteurs maison, rien ne traverse le chiffre
    qui loge dans la coupe."""
    c.saveState()
    c.setStrokeColor(col); c.setLineWidth(1.7)   # contours FRANCS (décision Maeva : lisibilité)
    y_t, y_b, y_f = cy + 8.2 * mm, cy - 5.8 * mm, cy - 9.6 * mm
    r_rim, r_pied = 14.0 * mm, 6.5 * mm   # calice LARGE : les flancs passent HORS du chiffre
    # la coupe (deux flancs en courbe de Bézier) + le buvant
    p = c.beginPath()
    p.moveTo(cx - r_rim, y_t)
    p.curveTo(cx - 14.3 * mm, y_t - 9.5 * mm, cx - 7.5 * mm, y_b + 0.8 * mm, cx, y_b)
    c.drawPath(p, stroke=1, fill=0)
    p = c.beginPath()
    p.moveTo(cx + r_rim, y_t)
    p.curveTo(cx + 14.3 * mm, y_t - 9.5 * mm, cx + 7.5 * mm, y_b + 0.8 * mm, cx, y_b)
    c.drawPath(p, stroke=1, fill=0)
    c.ellipse(cx - r_rim, y_t - 1.1 * mm, cx + r_rim, y_t + 1.1 * mm, stroke=1, fill=0)
    # coupe VIDE (décision Maeva : rien ne doit gêner la lecture du chiffre)
    # la jambe et le pied
    c.line(cx, y_b, cx, y_f)
    c.ellipse(cx - r_pied, y_f - 0.9 * mm, cx + r_pied, y_f + 0.9 * mm, stroke=1, fill=0)
    c.restoreState()


def _gen_carte(rng, forcer=()):
    """Vision Maeva : 13 cases tirées au sort portent UN numéro dans un VERRE ;
    les 11 autres suivent la règle du OHANA 75 · 2 boules (paire de 2 numéros
    distincts, triée). Chaque colonne tire TOUS ses numéros d'un seul coup
    → aucun doublon possible sur la carte."""
    verres = set(rng.sample(range(24), 13))
    for p in forcer:
        # 🔮 les cases mystère DOIVENT être des verres : on force, à 13 constants
        if p not in verres:
            candidats = sorted(verres - set(forcer))
            verres.remove(rng.choice(candidats))
            verres.add(p)
    # position -> (colonne, rang de case) dans l'ordre du dessin (lignes puis colonnes, FREE sauté)
    pos = 0
    besoins = {lettre: [] for lettre, a, b in PLAGES}
    for j in range(5):
        for i, (lettre, a, b) in enumerate(PLAGES):
            if i == 2 and j == 2:
                continue                       # case centrale FREE
            besoins[lettre].append(1 if pos in verres else 2)
            pos += 1
    carte = {}
    for lettre, a, b in PLAGES:
        total = sum(besoins[lettre])
        nums = rng.sample(range(a, b + 1), total)
        cases, k = [], 0
        for n in besoins[lettre]:
            cases.append(sorted(nums[k:k + n])); k += n
        carte[lettre] = cases
    return carte, verres


def _dessiner_carte(c, x0, y0, carte, verres, couleur_hex, serie, encre,
                    telephone="", titre_jeu="", no_page=1, style="eco", evenement_id="",
                    pos_mysteres=frozenset()):
    police_ch, gris_ch = _style_chiffres(style)
    col = colors.HexColor(couleur_hex)
    ncols = 5
    cell_w = CARD_W / ncols

    # Bordure carte
    c.setStrokeColor(col)
    c.setLineWidth(1.0)
    c.roundRect(x0, y0, CARD_W, CARD_H, 2 * mm, stroke=1, fill=0)
    if _sec:  # cadre intérieur en microtexte (sécurité anti-photocopie)
        _sec.cadre_micro(c, x0, y0, CARD_W, CARD_H, serie, retrait=1.5 * mm)

    # Bandeau haut (sécurité : nom du jeu + tournoi + n° carte, sur chaque grille)
    bandeau = "A VINDA"
    if titre_jeu:
        bandeau += "  —  " + titre_jeu
    c.setFillColor(GRIS); c.setFont(POLICE, 6)
    c.drawString(x0 + 4 * mm, y0 + CARD_H - 5 * mm, bandeau[:60])
    c.drawRightString(x0 + CARD_W - 4 * mm, y0 + CARD_H - 5 * mm,
                      "Page %d  ·  Carte N° %05d" % (no_page, serie))

    # En-tête des colonnes B I N G O
    hdr_base = y0 + CARD_H - 14 * mm
    for i, (lettre, a, b) in enumerate(PLAGES):
        cx = x0 + (i + 0.5) * cell_w
        if lettre == "G":
            c.setFillColor(col); c.setFont(POLICE, 5.5)
            c.drawCentredString(cx, hdr_base + 6.5 * mm, "MARATHON")
        c.setFillColor(col); c.setFont(POLICE, 16)
        c.drawCentredString(cx, hdr_base + 0.5 * mm, lettre)
    # ligne sous l'en-tête
    c.setStrokeColor(col); c.setLineWidth(0.5)
    c.line(x0 + 2 * mm, hdr_base - 2 * mm, x0 + CARD_W - 2 * mm, hdr_base - 2 * mm)

    # Grille des numéros
    grid_top = hdr_base - 2 * mm
    grid_bot = y0 + 6 * mm
    grid_h = grid_top - grid_bot
    row_h = grid_h / 5
    r_cercle = min(cell_w, row_h) * 0.42

    no_case = 0                 # compteur des 24 cases (pour les 13 verres)
    for j in range(5):          # rangées (0 = haut)
        cy = grid_top - (j + 0.5) * row_h
        for i, (lettre, a, b) in enumerate(PLAGES):
            cell_x = x0 + i * cell_w

            # séparateurs de colonnes
            if i > 0:
                c.setStrokeColor(GRIS_CLAIR); c.setLineWidth(0.3)
                c.line(cell_x, grid_bot, cell_x, grid_top)

            # Case centrale (colonne N) = LE NOM DU JEU + série
            if i == 2 and j == 2:
                # 🍷 Case vie du N (décision Maeva 29/07 : « c'est à cet endroit que
                # tu mettras le jeu A VINDA ») : le nom trône au cœur du carton,
                # et la case accueille toujours le QR de sécurité.
                c.setFillColor(col); c.setFont("Helvetica-Bold", 8.5)
                c.drawCentredString(cell_x + cell_w / 2, cy + row_h / 2 - 3.6 * mm, "A VINDA")
                if _sec and evenement_id:
                    try:
                        _q = 13.0 * mm
                        _sec.carton_qr(c, cell_x + (cell_w - _q) / 2,
                                       cy - row_h / 2 + 5.2 * mm, _q, evenement_id, serie)
                    except Exception:
                        pass
                continue

            # La case : VERRE à numéro unique (13 élues) ou PAIRE du OHANA 2 boules (les 11 autres)
            idx = j if i != 2 else (j if j < 2 else j - 1)  # N saute la case centrale
            nums_case = carte[lettre][idx]
            if no_case in verres:
                # 🍷 un seul numéro, servi au centre dans son verre
                cxc = cell_x + cell_w * 0.50
                _verre(c, cxc, cy, col)
                # médaillon blanc (recette 100 FRANCS) : la coupe s'efface sous le chiffre
                c.setFillColor(colors.white)
                c.roundRect(cxc - 7.7 * mm, cy - 3.6 * mm, 15.4 * mm, 9.8 * mm, 1.8 * mm, stroke=0, fill=1)
                if no_case in pos_mysteres:
                    # 🔮 LES VERRES MYSTÈRE (décision Maeva 29/07 : « on va commencer
                    # par 3 mystères, ensuite on attendra le retour de nos clients ») :
                    # TROIS des 13 coupes attendent d'être remplies — un grand « ? »,
                    # AUCUN numéro n'existe derrière (la boule-mystère naîtra du
                    # tirage public au caller et remplira les coupes « ? » de toute
                    # la salle au même instant). Un « ? » par colonne B·I·O — la boule de
                    # chaque colonne respecte sa plage (règle Maeva).
                    # 🅰️ LES LETTRES SONT DANS LE VERRE (idée Maeva 30/07) : la coupe
                    # mystère porte LA LETTRE DU CARTON avec son « ? » — la salle
                    # tire sa lettre au caller, le porteur se reconnaît dans ses verres.
                    k = MYSTERE_COLONNES.index(_COL_DE_CASE[no_case])
                    c.setFillColor(gris_ch); c.setFont("Helvetica-Bold", 30)
                    c.drawCentredString(cxc - 3.2 * mm, cy - 8, _lettres_carte(serie)[k])
                    c.setFont("Helvetica-Bold", 17)
                    c.drawCentredString(cxc + 5.6 * mm, cy + 1.5 * mm, "?")
                    c.setFillColor(col); c.setFont(POLICE, 4.6)
                    c.drawCentredString(cxc, cy - 12.8 * mm, "LETTRE DE SALLE")
                elif _sec:
                    _sec.chiffre_micro(c, nums_case[0], cxc, cy - 8, 32, gris_ch, police_ch)
                else:
                    c.setFillColor(gris_ch); c.setFont(police_ch, 32)
                    c.drawCentredString(cxc, cy - 8, str(nums_case[0]))
            else:
                # règle du OHANA 75 · 2 boules : gros cerclé + petit à côté
                cxc = cell_x + cell_w * 0.30
                cx2 = cell_x + cell_w * 0.79
                n1, n2 = nums_case[0], nums_case[1]
                c.setStrokeColor(col); c.setLineWidth(1.0)
                c.circle(cxc, cy, r_cercle, stroke=1, fill=0)
                if _sec:
                    _sec.chiffre_micro(c, n1, cxc, cy - 14, 42, gris_ch, police_ch)
                    _sec.chiffre_micro(c, n2, cx2, cy - 12, 36, gris_ch, police_ch)
                else:
                    c.setFillColor(gris_ch); c.setFont(police_ch, 42)
                    c.drawCentredString(cxc, cy - 14, str(n1))
                    c.setFillColor(gris_ch); c.setFont(police_ch, 36)
                    c.drawCentredString(cx2, cy - 12, str(n2))
            no_case += 1

        # séparateur de rangée
        if j > 0:
            yy = grid_top - j * row_h
            c.setStrokeColor(GRIS_CLAIR); c.setLineWidth(0.3)
            c.line(x0 + 2 * mm, yy, x0 + CARD_W - 2 * mm, yy)

    # Pied : série + responsable
    c.setStrokeColor(col); c.setLineWidth(0.5)
    c.line(x0 + 2 * mm, grid_bot, x0 + CARD_W - 2 * mm, grid_bot)
    c.setFillColor(GRIS); c.setFont(POLICE, 5.5)
    c.drawString(x0 + 4 * mm, y0 + 2 * mm, "N° %06d" % serie)
    if pos_mysteres:
        # 🔮 LA RÈGLE GRAVÉE SUR LE CARTON (demande Maeva 29/07 : « comment le client
        # peut savoir que le chiffre mystère sorti est son chiffre mystère ») :
        # il n'y a qu'UN chiffre mystère pour toute la salle — le carton le dit.
        c.setFillColor(col); c.setFont(POLICE, 4.8)
        c.drawCentredString(x0 + CARD_W / 2, y0 + 2 * mm,
                            "LES 3 LETTRES des verres (B\u00b7I\u00b7O) = VOS lettres de salle (A\u2192L) \u2014 tir\u00e9es du sac avec les boules, cochez quand la v\u00f4tre sort !")
    if telephone:
        c.drawRightString(x0 + CARD_W - 4 * mm, y0 + 2 * mm, "Resp. " + telephone)

    # QR de vérification (anti-duplication) — coin bas-droit, discret
    if _sec and evenement_id:
        try:
            pass  # le QR vit désormais dans la case centrale FREE
        except Exception:
            pass


def generer_pdf(nb_cartes=2, serie_start=1, theme="", couleur=True,
                nom_evenement="", titre_jeu="", couleur_perso="", date_lieu="", telephone="",
                style="eco", evenement_id="", mystere=False):
    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=A4, pageCompression=1)

    nb_cartes = max(1, min(int(nb_cartes), 10000))
    par_page = 2
    nb_pages = (nb_cartes + par_page - 1) // par_page

    rng = random.Random(978000 + int(serie_start))
    serie = int(serie_start)
    no_page = 1
    encre = NOIR if couleur else GRIS
    faites = 0

    for _ in range(nb_pages):
        # En-tête de page (événement)
        if nom_evenement:
            c.setFillColor(NOIR); c.setFont(POLICE, 11)
            c.drawCentredString(PAGE_W / 2, PAGE_H - 6 * mm, nom_evenement)
        ligne2 = (titre_jeu or "A VINDA — 2 séries")
        if date_lieu:
            ligne2 += "  ·  " + date_lieu
        c.setFillColor(GRIS); c.setFont(POLICE, 6.5)
        if nom_evenement:
            c.drawCentredString(PAGE_W / 2, PAGE_H - 9 * mm, ligne2)

        for slot in range(par_page):
            if faites >= nb_cartes:
                break
            # carte du haut (slot 0) puis du bas (slot 1)
            y0 = MARGIN_BOT + (1 - slot) * (CARD_H + GUTTER_Y)
            x0 = MARGIN_X
            forcer = ()
            if mystere:
                # 🔮 un verre mystère PAR COLONNE B·I·O, déterministe (refab comprise)
                h = _hmac.new(b"MYSTERE-2KEA", ("MYSTERE:%d" % serie).encode(), _hashlib.sha256)
                rng_m = random.Random(int.from_bytes(h.digest()[:8], "big"))
                cols = _positions_colonnes()
                forcer = tuple(rng_m.choice(cols[lettre]) for lettre in MYSTERE_COLONNES)
            carte, verres = _gen_carte(rng, forcer)
            pos_mysteres = frozenset(forcer)
            coul = (couleur_perso if (couleur and couleur_perso)
                    else RAINBOW[(serie - 1) % len(RAINBOW)] if couleur else "#9A9A9A")
            _dessiner_carte(c, x0, y0, carte, verres, coul, serie, encre, telephone, titre_jeu, no_page,
                            style=style, evenement_id=evenement_id, pos_mysteres=pos_mysteres)
            serie += 1
            faites += 1

        # trait de découpe pointillé entre les 2 cartes
        c.setStrokeColor(GRIS_CLAIR); c.setLineWidth(0.5); c.setDash(3, 3)
        yc = MARGIN_BOT + CARD_H + GUTTER_Y / 2
        c.line(MARGIN_X, yc, PAGE_W - MARGIN_X, yc)
        c.setDash()

        c.showPage()
        no_page += 1

    c.save()
    buf.seek(0)
    return buf


# ── Deux variantes pour le registre : Couleur (arc-en-ciel) et Noir & Blanc ──
def generer_couleur(**kwargs):
    """A VINDA — version COULEUR (verres et lettres arc-en-ciel)."""
    kwargs["couleur"] = True
    return generer_pdf(**kwargs)


def generer_nb(**kwargs):
    """A VINDA — version NOIR & BLANC (tout en gris, économie d'encre)."""
    kwargs["couleur"] = False
    return generer_pdf(**kwargs)


if __name__ == "__main__":
    pdf = generer_pdf(nb_cartes=2, couleur=True,
                      nom_evenement="ASSOCIATION TE MANU", titre_jeu="GRAND LOTO OHANA",
                      date_lieu="20 déc 2026", telephone="87 12 34 56")
    with open("test_avinda.pdf", "wb") as f:
        f.write(pdf.read())
    print("A VINDA généré")


def generer_pdf_mystere(**kw):
    """A VINDA MYSTÈRE 🔮 — le jumeau : un verre mystère par colonne B·I·O (MYSTERE_COLONNES)."""
    kw["mystere"] = True
    return generer_pdf(**kw)
