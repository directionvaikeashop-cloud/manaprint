# -*- coding: utf-8 -*-
"""
MANAPRINT — Générateur OHANA 75 · 10 BOULES (format A4)
9 cartes (bandes allongées) par feuille A4, empilées.
Chaque carte : 10 numéros en ligne, alternant GROS chiffre (sans rond) et
petit chiffre dans un ROND POINTILLÉ. N° de série en boîte à gauche.
5 plages (2 numéros chacune) : 1-15, 16-30, 46-60, 61-75.
Dans chaque plage : le plus petit = gros chiffre, le plus grand = petit chiffre rond.
Couleur arc-en-ciel (par carte) ou gris (N&B). Chiffres en gris 40%.
"""
import io
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
GRIS40 = colors.Color(0.60, 0.60, 0.60)
GRIS_CLAIR = colors.Color(0.78, 0.78, 0.78)



# ══ L'ÉCRITURE DES CHIFFRES (sceau Maeva 18/09) ══════════════════════
# ⭐⭐ MÊME TRAVAIL QUE SUR LE OHANA 75 · 2 SÉRIES ET SES FRÈRES :
#    LATIN MODERN ROMAN, la serif fine et contrastée choisie par Maeva —
#    déliés minces, terminaisons rondes. Elle remplace DejaVu ExtraLight
#    (éco) ET Helvetica-Bold (premium) : mesuré à taille égale, Latin
#    Modern consomme 61 % de toner en moins que le gras DejaVu condensé.
# ⭐ GRIS 0,35 : mesuré, c'est 20 % de toner en moins que le noir franc,
#    et les chiffres restent noirs à l'œil. Au-delà (0,45 · 0,55) ça
#    commence à se voir sur le papier ordinaire.
# ⚠️ Le fichier LatinModern.ttf est rangé À CÔTÉ de ce générateur (la
#    version d'origine est en OTF, que ReportLab ne sait pas lire). S'il
#    manque, on retombe sur l'ancienne écriture sans planter.
# ⚠️ LE MICROTEXTE RESTE EN POSTE : il CREUSE les chiffres, donc il
#    consomme MOINS d'encre qu'un chiffre plein (2,87 % contre 3,49 %).
import os as _osL
from reportlab.pdfbase import pdfmetrics as _pm
from reportlab.pdfbase.ttfonts import TTFont as _TF
_POLICE_ECO = "Helvetica"
try:
    _pm.registerFont(_TF("DJLECO", "/usr/share/fonts/truetype/dejavu/DejaVuSans-ExtraLight.ttf"))
    _POLICE_ECO = "DJLECO"
except Exception:
    pass
try:
    _pm.registerFont(_TF("LMROMAN", _osL.path.join(
        _osL.path.dirname(_osL.path.abspath(__file__)), "LatinModern.ttf")))
    _POLICE_ECO = "LMROMAN"
except Exception:
    pass
_GRIS_ECO = colors.Color(0.26, 0.26, 0.26)
# ⭐⭐ 23/09 (sceau Maeva : « renforce le gras, on ne change pas
#    l'écriture ») : LE TRAIT DU CHIFFRE S'ÉPAISSIT, LA POLICE NE BOUGE PAS.
#    Latin Modern reste Latin Modern ; c'est le CONTOUR du chiffre qui
#    passe de 0,010 à 0,026 de sa taille. Le gris passe de 0,35 à 0,26 en
#    même temps, sinon le trait plus large reste pâle.
#       0,010 + gris 0,35 = l'ancien   ·  0,018 + 0,30 = un cran
#       0,026 + gris 0,26 = ACTUEL     ·  0,034 + 0,22 = très gras
_GRAS_TRAIT = 0.026
# ⭐⭐ 19/09 (sceau Maeva : « quand je lance l'impression c'est long ») :
#    LE MICROTEXTE DES CHIFFRES EST ÉCRIT EN 0,9 pt, PAS EN 0,5.
#    Deux fois moins de travail pour l'imprimante, exactement le même
#    toner, la sécurité intacte. ⚠️ Ne pas monter au-dessus de 1 pt.
#    Ce réglage vient de la maquette du 19/09 : il est gardé ici.
MICRO_PT = 0.9
# ⭐⭐ 26/09 (sceau Maeva : « revenir à l'ancienne maquette tout en gardant
#    la police et le gras ») : CE FICHIER REPREND LA MAQUETTE D'AVANT le
#    18/09 — le carton simple à coins arrondis, sans bordure festonnée,
#    sans les fleurs de lys ni le bandeau OHANA 75. L'écriture Latin
#    Modern, le gras 0,026, le gris 0,26 et le microtexte 0,9 pt sont
#    CONSERVÉS. Rien d'autre n'a bougé.
_POLICE_P15 = _POLICE_ECO
_GRIS_P15 = colors.Color(0.14, 0.14, 0.14)   # objet distinct : sert à reconnaître la gamme

def _style_chiffres(style):
    """Retourne (police, gris) des chiffres selon la gamme choisie."""
    if str(style).lower() in ("p15", "premium"):
        return _POLICE_P15, _GRIS_P15
    return _POLICE_ECO, _GRIS_ECO
# ═════════════════════════════════════════════════════════════════════
# ⭐⭐ 18/09 : LA TAILLE DU CHIFFRE CERCLÉ S'ADAPTE AU ROND, jamais l'inverse.
#    ⚠️ Avec l'ancienne écriture le « 30 » en dur faisait déjà sortir les
#    deux-chiffres du rond pointillé ; Latin Modern est plus étroit, mais
#    à 30 pt le « 88 » touchait encore le pointillé. On descend donc
#    jusqu'à ce que la DIAGONALE du chiffre tienne dans le rond, quelle que
#    soit l'écriture réellement chargée (le repli DejaVu compris).
#    ⚠️ LE ROND NE GRANDIT PAS : c'est lui qui commande.
# ⭐⭐ 26/09 (sceau Maeva : « on va bien grossir les chiffres ») ═══════
#    LA PLACE DU QR N'EST RÉSERVÉE QUE S'IL Y A UN QR.
#    ⚠️ CE QUI BLOQUAIT : 24 mm étaient gardés à droite du carton pour le
#    QR, et 10 mm à gauche — soit 34 des 198 mm, réservés sur TOUS les
#    cartons alors que le QR n'est dessiné que si la commande porte un
#    évènement. Les cinq paires se partageaient donc 32,8 mm chacune, et
#    à 35 pt le gros chiffre touchait déjà presque le rond pointillé.
#    ⭐ Désormais : sans QR, la ligne prend 187 mm au lieu de 164, et les
#    chiffres grossissent d'autant. AVEC un QR, tout reste exactement
#    comme avant — mêmes places, mêmes tailles, le QR garde sa maison.
#    ⚠️ Les tailles ci-dessous sont MESURÉES, pas choisies : chaque valeur
#    de chaque plage a été imprimée à 600 dpi dans sa case, et on a compté
#    les pixels où le chiffre touche un trait du carton.
#       gros 46 · rond 7,8 mm  ->  0 contact
#       gros 48 · rond 7,9 mm  ->  0 contact      ← INSTALLÉ
#       gros 50 · rond 8,0 mm  ->  136 pixels
#       gros 52 · rond 8,0 mm  ->  1 057 pixels
#    Le gros chiffre passe donc de 35 à 48 pt (+37 %) et le chiffre
#    cerclé de 27,25 à 32,75 pt (+20 %).
#            marge gauche · réserve droite · gros · rayon du rond · petit
_SANS_QR = (5.0, 6.0, 48.0, 7.9, None)     # None = la taille se calcule sur le rond
_AVEC_QR = (10.0, 24.0, 35.0, 6.6, None)   # l'ancien calibre, inchangé


def _taille_rond(r_mm):
    """La taille du chiffre cerclé s'adapte au rond, jamais l'inverse
    (sceau 18/09) : on descend jusqu'à ce que la DIAGONALE du « 88 »,
    trait de gras compris, tienne dans le rond."""
    R = r_mm * mm
    t = 44.0
    while t > 10:
        l = _pm.stringWidth("88", _POLICE_ECO, t) + t * _GRAS_TRAIT
        if ((l / 2) ** 2 + ((t * 0.72) / 2) ** 2) ** 0.5 <= R * 0.92:
            break
        t -= 0.25
    return t


_R_ROND_MM = 6.6
_R_ROND = _R_ROND_MM * mm
_T_GROS = 35.0
_GAUCHE = 10.0
_ZONE_QR = 24.0
_T_ROND = 30.0
while _T_ROND > 12:
    _l = _pm.stringWidth("88", _POLICE_ECO, _T_ROND); _h = _T_ROND * 0.72
    if ((_l / 2) ** 2 + (_h / 2) ** 2) ** 0.5 <= _R_ROND * 0.92:
        break
    _T_ROND -= 0.5

PAGE_W, PAGE_H = A4
RANGES = [(1, 15), (16, 30), (31, 45), (46, 60), (61, 75)]

CARTES_PAGE = 9
MARGIN_X = 6 * mm
MARGIN_TOP = 8 * mm
MARGIN_BOT = 6 * mm
GUTTER_Y = 2 * mm

CARD_W = PAGE_W - 2 * MARGIN_X
CARD_H = (PAGE_H - MARGIN_TOP - MARGIN_BOT - (CARTES_PAGE - 1) * GUTTER_Y) / CARTES_PAGE


# 💰 MYSTÈRE-MONTANTS (sceau Maeva 30/07) : 2 positions CONDAMNÉES par carton
# deviennent des coupes portant un MONTANT — imprimé, il ne promet RIEN : c'est
# une boule tirée en public ; règle de salle + juriste gouvernent le bonus.
import hmac as _hmac
import hashlib as _hashlib
MONTANTS = [100, 400, 600, 700, 800, 900, 2000, 3000, 4000, 5000, 6000, 7000,
            8000, 9000, 100000, 500000, 1000000, 2000000, 3000000]


def _mystere_carte(serie, nb_cols):
    """(les DEUX colonnes condamnées, leurs DEUX montants) — chaque paire
    (chiffre nu + cerclé) s'efface pour SON rectangle (sceau Maeva 30/07)."""
    h = _hmac.new(b"MONTANT-2KEA", ("OHMONT:%d" % serie).encode(), _hashlib.sha256)
    rm = random.Random(h.digest())
    return sorted(rm.sample(range(nb_cols), 2)), rm.sample(MONTANTS, 2)


def _texte_montant(n):
    return "{:,}".format(n).replace(",", " ")   # espace simple : Helvetica la connaît (l'espace fine dessinait un carré)


def _montant_rectangle(c, cx, cy, w, h, montant, col, gris_ch):
    """Le RECTANGLE élégant qui accueille le montant de la colonne condamnée."""
    c.setStrokeColor(col); c.setLineWidth(1.2)
    c.roundRect(cx - w / 2, cy - h / 2, w, h, 1.6 * mm, stroke=1, fill=0)
    mtxt = _texte_montant(montant)
    t = 15.0
    while t > 6 and pdfmetrics.stringWidth(mtxt, "Helvetica-Bold", t) > w - 3.2 * mm:
        t -= 0.5
    c.setFillColor(gris_ch); c.setFont("Helvetica-Bold", t)
    c.drawCentredString(cx, cy + 0.8 * mm, mtxt)
    c.setFont("Helvetica-Bold", 4.6)
    c.drawCentredString(cx, cy - 3.4 * mm, "FRANCS")
    c.setFillColor(col); c.setFont(POLICE, 3.8)
    c.drawCentredString(cx, cy - h / 2 + 1.2 * mm, "MONTANT DE SALLE")


def _gen_carte(rng):
    """8 entrées (valeur, rond_pointille) : par plage, petit=gros chiffre, grand=rond."""
    out = []
    for (a, b) in RANGES:
        pair = sorted(rng.sample(range(a, b + 1), 2))
        out.append((pair[0], False))   # gros chiffre
        out.append((pair[1], True))    # petit chiffre, rond pointillé
    return out


def _dessiner_carte(c, x0, y0, nums, couleur_hex, serie, titre_jeu="", telephone="", style="eco", evenement_id="", myst_pos=None, myst_mnt=None):
    police_ch, gris_ch = _style_chiffres(style)
    col = colors.HexColor(couleur_hex)

    # Bordure
    c.setStrokeColor(col); c.setLineWidth(0.8)
    c.roundRect(x0, y0, CARD_W, CARD_H, 1.2 * mm, stroke=1, fill=0)
    if _sec:  # cadre intérieur en microtexte (sécurité anti-photocopie)
        _sec.cadre_micro(c, x0, y0, CARD_W, CARD_H, serie, retrait=0.9 * mm)

    # ---- En-tête ----
    htxt_y = y0 + CARD_H - 4.3 * mm
    # boîte série (gauche)
    sb_w, sb_h = 16 * mm, 4.4 * mm
    c.setStrokeColor(col); c.setLineWidth(0.5)
    c.roundRect(x0 + 2 * mm, htxt_y - 1.7 * mm, sb_w, sb_h, 0.8 * mm, stroke=1, fill=0)
    c.setFillColor(col); c.setFont(POLICE, 7)
    c.drawCentredString(x0 + 2 * mm + sb_w / 2, htxt_y, "%05d" % serie)
    # titre centré
    titre = "Le jeu OHANA 75 pour 10 boules"
    if titre_jeu and "OHANA" not in titre_jeu.strip().upper():
        titre = "OHANA 75 \u00b7 10 boules \u00b7 " + titre_jeu.strip()   # le nom du jeu TOUJOURS affiché (décision Maeva)
    elif titre_jeu:
        titre = titre_jeu.strip()
    if telephone:
        titre += "  " + telephone
    c.setFillColor(col); c.setFont(POLICE, 6)
    c.drawCentredString(x0 + CARD_W / 2 + 9 * mm, htxt_y, titre[:64])

    # ---- Ligne des 10 numéros ----
    zone_top = htxt_y - 3 * mm
    zone_bot = y0 + 2 * mm
    cy = (zone_top + zone_bot) / 2

    _g, _z, _tg, _rr, _tr = _AVEC_QR if (_sec and evenement_id) else _SANS_QR
    if _tr is None:
        _tr = _taille_rond(_rr)
    gauche = x0 + _g * mm
    droite = x0 + CARD_W - _z * mm
    usable = droite - gauche
    pair_w = usable / 5.0

    for p in range(5):
        pleft = gauche + p * pair_w
        big_val = nums[2 * p][0]
        small_val = nums[2 * p + 1][0]
        # gros chiffre
        bx = pleft + pair_w * 0.30
        if myst_pos is not None and p in myst_pos:   # 💰 colonne condamnée : le rectangle
            _montant_rectangle(c, pleft + pair_w * 0.52, cy, 24 * mm, 16.5 * mm,
                               myst_mnt[myst_pos.index(p)], col, gris_ch)
            continue
        if _sec:  # chiffres "billet de banque" remplis de microtexte
            _sec.chiffre_micro(c, big_val, bx, cy - _tg*0.357, _tg, gris_ch, police_ch,
                               taille_micro=MICRO_PT, epaisseur=_GRAS_TRAIT)
        else:
            c.setFillColor(gris_ch); c.setFont(police_ch, _tg)
            c.drawCentredString(bx, cy - _tg*0.357, str(big_val))
        # petit chiffre dans rond pointillé — ou la coupe 💰
        sx = pleft + pair_w * 0.74
        c.setStrokeColor(col); c.setLineWidth(0.7)
        c.setDash([1.4, 1.4])
        c.circle(sx, cy, _rr * mm, stroke=1, fill=0)
        c.setDash([])
        if _sec:
            _sec.chiffre_micro(c, small_val, sx, cy - _tr * 0.36, _tr, gris_ch, police_ch,
                               taille_micro=MICRO_PT, epaisseur=_GRAS_TRAIT)
        else:
            c.setFillColor(gris_ch); c.setFont(police_ch, _tr)
            c.drawCentredString(sx, cy - _T_ROND * 0.36, str(small_val))

    # QR de vérification par grille (anti-duplication) — coin bas-droit
    if _sec and evenement_id:
        try:
            # 🎯 QR dans la zone droite réservée (aucun chiffre dérangé)
            _q = 12.0 * mm
            _xq = x0 + CARD_W - _q - 4.5 * mm
            _yq = y0 + (CARD_H - _q - 3.4 * mm) / 2 + 3.4 * mm
            _sec.carton_qr(c, _xq, _yq, _q, evenement_id, serie)
        except Exception:
            pass


def generer_pdf(nb_cartes=9, serie_start=1, theme="", couleur=True,
                nom_evenement="", titre_jeu="", couleur_perso="", date_lieu="", telephone="",
                style="eco", evenement_id="", mystere=False, page_start=1):
    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=A4, pageCompression=1)

    nb_cartes = max(1, min(int(nb_cartes), 10000))
    nb_pages = (nb_cartes + CARTES_PAGE - 1) // CARTES_PAGE

    rng = random.Random(751000 + int(serie_start))
    serie = int(serie_start)
    faites = 0
    # 📄 la page continue d'une rame à l'autre (sceau Maeva 12/08)
    no_page = max(1, int(page_start))

    for _ in range(nb_pages):
        c.setFillColor(GRIS_CLAIR); c.setFont(POLICE, 6)
        c.drawCentredString(PAGE_W / 2, PAGE_H - 4.5 * mm, "%d" % no_page)
        for row in range(CARTES_PAGE):
            if faites >= nb_cartes:
                break
            y0 = MARGIN_BOT + (CARTES_PAGE - 1 - row) * (CARD_H + GUTTER_Y)
            x0 = MARGIN_X
            nums = _gen_carte(rng)
            mp, mv = (None, None)
            if mystere:   # 💰 LA colonne condamnée et SON montant
                mp, mv = _mystere_carte(serie, 5)
            coul = (couleur_perso if (couleur and couleur_perso)
                    else RAINBOW[(serie - 1) % len(RAINBOW)] if couleur else "#9A9A9A")
            _dessiner_carte(c, x0, y0, nums, coul, serie, titre_jeu, telephone, style=style, evenement_id=evenement_id, myst_pos=mp, myst_mnt=mv)
            serie += 1
            faites += 1
        c.showPage()
        no_page += 1

    c.save()
    buf.seek(0)
    return buf


def generer_pdf_mystere(**kw):
    """💰 OHANA 75 \u00b7 10 boules MYSTÈRE — 2 coupes à MONTANTS remplacent 2 numéros."""
    kw["mystere"] = True
    return generer_pdf(**kw)


if __name__ == "__main__":
    pdf = generer_pdf(nb_cartes=9, couleur=True,
                      titre_jeu="Le jeu OHANA 75 pour 10 boules", telephone="89 22 23 05")
    with open("test_ohana8.pdf", "wb") as f:
        f.write(pdf.read())
    print("OHANA 75 8 boules généré")
