# -*- coding: utf-8 -*-
"""
MANAPRINT — Générateur TRIO 90 (format A4)

📏 NÉ LE 12/08 (sceau Maeva) : L'ÉCHELLE GRADUÉE. Six rangées sont
rangées dans la règle — une par plage — comme TRIO 75 range ses cinq
grilles dans sa carte d'embarquement. Deux cartes par feuille A4.

Bâti sur le modèle de TRIPLE ACTION 90, pour le sac de 90 :
  • 6 plages : 1-15 · 16-30 · 31-45 · 46-60 · 61-75 · 76-90
  • 3 numéros par trio, 5 trios par rangée
  • 6 rangées ⇒ 90 numéros sur la carte

⭐ LA CARTE EST DONC **PLEINE** — 5 trios × 3 = les quinze numéros d'une
plage, ni plus ni moins. Chaque numéro du sac figure sur la carte, UNE
SEULE FOIS.

⚠️⚠️ RÈGLE MARATHON (la même qu'OHANA 75 · 2 séries et TRIO 75) : un
numéro ne sort qu'une fois. Ici elle est parfaite par construction —
sinon un même tirage cocherait deux cases et le jeu serait faussé.

Le trio se lit comme sur le modèle : DEUX numéros en haut, LE TROISIÈME
dessous, centré entre les deux.
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
# (min, max) des 6 groupes — TRIPLE ACTION 90
# 🎫 les cinq plages du sac de 75
PLAGES = [(1, 15), (16, 30), (31, 45), (46, 60), (61, 75), (76, 90)]
NB_GRILLES = 5                 # cinq trios par rangée
NB_PAR_PLAGE = 3               # trois numéros par plage et par grille

# 🎫 LA CARTE D'EMBARQUEMENT DE MAEVA — les grilles se rangent dedans.
_RATIO_CARTE = 1.4041
CADRE = (0.0094, 0.9906, 0.0936, 0.9075)   # x0, x1, y0, y1
# ⚠️⚠️ 12/08 : L'IMAGE NE PORTE PLUS QUE LES DEUX RÈGLES. Le titre
# « TRIO 90 » de l'image d'origine était en portrait ; le coucher puis
# l'aplatir le rendait laid et illisible. Il est désormais ÉCRIT PAR LE
# PDF, en vraie typographie — net à toutes les tailles, et il ne coûte
# presque rien en encre. L'image y gagne aussi : la carte passe de 155
# à 190 mm de large, et les chiffres respirent.
# ⚠️⚠️ 12/08 : L'ÉCHELLE A ÉTÉ COUCHÉE d'un quart de tour. En portrait
# (ratio 0,63) elle ne remplissait qu'un tiers du carton et les chiffres
# tombaient à 10 pt. Couchée (1,593), elle prend toute la largeur — les
# deux règles graduées courent en haut et en bas, et les deux cartes se
# rangent l'une SOUS l'autre, comme les cartes de TRIO 75.
# ⚠️ 12/08 : NOUVELLE IMAGE de Maeva — le titre passe en lettres creuses
# et les 12 petites cases du bas ont disparu. Le grand cadre gagne donc
# en hauteur (0,0383 → 0,8520 contre 0,0972 → 0,8503 avant).
import os as _os2
from reportlab.pdfbase.pdfmetrics import stringWidth as _lgt


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


_IMAGE_CARTE = _choisir_image("trio90_echelle", _RATIO_CARTE)

COLS_PAGE = 1
ROWS_PAGE = 2            # 2 cartes pleine largeur, l'une sous l'autre
MARGIN_X = 6 * mm
MARGIN_TOP = 10 * mm
MARGIN_BOT = 8 * mm
GUTTER_X = 4 * mm        # l'écart entre les deux cartes côte à côte
GUTTER_Y = 2.4 * mm

CARD_W = (PAGE_W - 2 * MARGIN_X - (COLS_PAGE - 1) * GUTTER_X) / COLS_PAGE
CARD_H = (PAGE_H - MARGIN_TOP - MARGIN_BOT - (ROWS_PAGE - 1) * GUTTER_Y) / ROWS_PAGE
ZONE_QR = 16 * mm        # bande de droite réservée au QR de vérification


def _gen_carte(rng):
    """🎫 Les QUATRE grilles de la carte, sans un seul doublon.

    ⚠️⚠️ RÈGLE MARATHON : on tire d'abord, pour CHAQUE plage, les 12
    numéros de la carte entière (4 grilles × 3) — d'un seul coup, avec
    `sample`, qui ne rend jamais deux fois le même. On les distribue
    ensuite entre les grilles. Tirer grille par grille aurait laissé
    passer des doublons d'une grille à l'autre.
    """
    grilles = [[] for _ in range(NB_GRILLES)]
    for pmin, pmax in PLAGES:
        besoin = NB_GRILLES * NB_PAR_PLAGE
        tous = rng.sample(range(pmin, pmax + 1), besoin)
        for g in range(NB_GRILLES):
            grilles[g].append(sorted(tous[g * NB_PAR_PLAGE:(g + 1) * NB_PAR_PLAGE]))
    return grilles

def _dessiner_carte(c, x0, y0, grilles, couleur_hex, serie, titre_jeu="", telephone="", style="eco", evenement_id=""):
    police_ch, gris_ch = _style_chiffres(style)
    col = colors.HexColor(couleur_hex)

    # Bordure du bandeau
    c.setStrokeColor(col); c.setLineWidth(0.8)
    c.roundRect(x0, y0, CARD_W, CARD_H, 1.5 * mm, stroke=1, fill=0)
    if _sec:  # cadre intérieur en microtexte (sécurité anti-photocopie)
        _sec.cadre_micro(c, x0, y0, CARD_W, CARD_H, serie, retrait=0.9 * mm)

    # ═══ 🎫 LA CARTE D'EMBARQUEMENT, ET SES QUATRE GRILLES ═══
    # Le dessin de Maeva occupe toute la carte ; les quatre grilles se
    # rangent dans son grand cadre, l'une sous l'autre.
    # ⚠️ 12/08 : une BANDE est réservée en haut pour le titre — l'image
    # (les deux règles) descend d'autant, sinon le titre chevauche la
    # graduation du haut.
    BANDE_TITRE = 8.0 * mm
    iw = CARD_W - 2.0 * mm
    ih = iw / _RATIO_CARTE
    if ih > CARD_H - 2.0 * mm - BANDE_TITRE:
        ih = CARD_H - 2.0 * mm - BANDE_TITRE
        iw = ih * _RATIO_CARTE
    px = x0 + (CARD_W - iw) / 2
    py = y0 + (CARD_H - BANDE_TITRE - ih) / 2
    if _os2.path.exists(_IMAGE_CARTE):
        try:
            c.drawImage(_IMAGE_CARTE, px, py, iw, ih, mask="auto",
                        preserveAspectRatio=True)
        except Exception:
            pass

    # le grand cadre : c'est là que vivent les quatre grilles
    gx0 = px + CADRE[0] * iw
    gw = (CADRE[1] - CADRE[0]) * iw
    gy0 = py + CADRE[2] * ih
    gh = (CADRE[3] - CADRE[2]) * ih

    # ⚠️ 12/08 : une bande est RÉSERVÉE au QR à droite, sinon il mange le
    # dernier numéro de la dernière rangée.
    # ⚠️ 12/08 : le QR passe SOUS le cadre, dans la bande du pied — sur
    # TRIO 90 les SIX colonnes ont besoin de toute la largeur, et les
    # 12,5 mm qu'il volait bridaient les chiffres à 26 pt au lieu de 30.
    PLACE_QR = 0.0 * mm
    gw_num = gw - PLACE_QR
    n_pl = len(PLAGES)
    cell_w = gw_num / n_pl
    rang_h = gh / NB_GRILLES
    # ⚡ 12/08 (sceau Maeva) : LE TRIO SE LIT COMME SUR SON MODÈLE —
    # DEUX numéros en haut, LE TROISIÈME dessous, centré entre les deux.
    # Ils étaient alignés côte à côte ; en deux étages, chacun gagne la
    # moitié de la largeur de la case et devient bien plus grand.
    place = cell_w / 2.0                 # deux numéros par étage du haut
    demi_h = rang_h / 2.0                # deux étages dans la rangée
    taille = 30.0
    # ⚠️⚠️ 12/08 : LES DEUX ÉTAGES SE RAPPROCHENT pour tenir les 30 pt
    # demandés par Maeva. Le chiffre peut monter à 0,90 de la demi-hauteur :
    # les deux étages se frôlent, mais un chiffre n'occupe en vrai que les
    # deux tiers de sa hauteur nominale — vérifié à l'œil, ils ne se
    # touchent pas. C'est la HAUTEUR qui bridait, jamais la largeur
    # (16,5 mm disponibles pour 15,7 nécessaires).
    while taille > 8 and (_lgt("88", police_ch, taille) > place * 0.94
                          or taille * 0.72 > demi_h * 0.90):
        taille -= 0.5
    # 🔻 la troisième boule : cinq points de moins, et jamais plus large
    # que sa case (elle a toute la largeur, elle est seule sur son étage).
    taille_3 = max(10.0, taille - 5.0)
    while taille_3 > 8 and _lgt("88", police_ch, taille_3) > cell_w * 0.80:
        taille_3 -= 0.5

    for gi, grille in enumerate(grilles):
        cy = gy0 + gh - (gi + 0.5) * rang_h
        # un trait fin sépare les grilles (sauf au-dessus de la première)
        if gi > 0:
            c.setStrokeColor(colors.Color(0.85, 0.85, 0.85))
            c.setLineWidth(0.3)
            c.line(gx0 + 1.5 * mm, gy0 + gh - gi * rang_h,
                   gx0 + gw_num - 1.5 * mm, gy0 + gh - gi * rang_h)
        for pi, nums in enumerate(grille):
            gx = gx0 + pi * cell_w
            # ⚡ 12/08 (sceau Maeva) : un trait fin sépare les colonnes —
            # il court sur toute la hauteur du cadre, pas seulement dans
            # la rangée, pour que l'œil suive la plage de haut en bas.
            if pi > 0 and gi == 0:
                c.setStrokeColor(colors.Color(0.85, 0.85, 0.85))
                c.setLineWidth(0.3)
                c.line(gx, gy0 + 1.0 * mm, gx, gy0 + gh - 1.0 * mm)
            haut_y = cy + demi_h * 0.44 - taille * 0.34    # l'étage du haut
            bas_y3 = cy - demi_h * 0.46 - taille_3 * 0.34  # celui du bas
            for ni, n in enumerate(nums):
                # ⚡ 12/08 (sceau Maeva) : LA TROISIÈME BOULE EST PLUS PETITE
                # — 25 pt contre 30 pour les deux du haut, comme sur le
                # modèle TRIPLE ACTION 75 où le numéro du bas est discret.
                t_ch = taille if ni < 2 else taille_3
                if ni < 2:
                    nx = gx + (ni + 0.5) * place           # les deux du haut
                    ny = haut_y
                else:
                    nx = gx + cell_w / 2                   # le troisième,
                    ny = bas_y3                            # centré dessous
                if _sec:
                    _sec.chiffre_micro(c, n, nx, ny, t_ch, gris_ch, police_ch)
                else:
                    c.setFillColor(gris_ch)
                    c.setFont(police_ch, t_ch)
                    c.drawCentredString(nx, ny, str(n))

    # ═══ 📏 LE TITRE, ÉCRIT PROPREMENT PAR LE PDF ═══
    # En capitales espacées, centré au-dessus des règles. Il prend la
    # couleur de la carte, comme le reste du décor.
    t_titre = min(BANDE_TITRE * 0.82, iw * 0.050)
    c.setFillColor(col)
    c.setFont("Helvetica-Bold", t_titre)
    # ⚠️ cette version de ReportLab n'a pas setCharSpace : on espace les
    # lettres à la main, une par une, pour un titre qui respire.
    _mot = "TRIO 90"
    _esp = t_titre * 0.16
    _larg = sum(_lgt(ch, "Helvetica-Bold", t_titre) for ch in _mot) + _esp * (len(_mot) - 1)
    _x = px + iw / 2 - _larg / 2
    _y = y0 + CARD_H - BANDE_TITRE * 0.80
    for ch in _mot:
        c.drawString(_x, _y, ch)
        _x += _lgt(ch, "Helvetica-Bold", t_titre) + _esp

    # le nom du jeu et la série, dans la bande du haut de la carte
    c.setFillColor(col)
    c.setFont(POLICE, 5.4)
    bas = ""
    if titre_jeu and "TRIO 75" not in titre_jeu.strip().upper():
        bas = titre_jeu.strip()
    if telephone:
        bas = (bas + "  \u00b7  " if bas else "") + telephone
    # ⚠️ au-dessus des petites cases du bas, sinon le texte tombe dedans
    if bas:
        c.drawString(gx0 + 1.0 * mm, gy0 + 1.4 * mm, bas[:60])
    c.setFont(POLICE, 5.4)
    c.drawRightString(gx0 + gw_num - 1.0 * mm, gy0 + 1.4 * mm, "N\u00b0 %06d" % serie)

    # QR de vérification par carte (anti-duplication) — bande de droite
    if _sec and evenement_id:
        try:
            # ⚠️ 12/08 : le QR vivait dans une bande de droite héritée de
            # TRIPLE ACTION 90 — il débordait de la carte. Il se pose
            # désormais DANS la carte, au coin bas-droit du grand cadre.
            _q = 9.5 * mm
            _sec.carton_qr(c, gx0 + gw - _q - 1.0 * mm, py + ih * 0.012,
                           _q, evenement_id, serie, avec_code=False)
        except Exception:
            pass


def generer_pdf(nb_cartes=10, serie_start=1, theme="", couleur=True,
                nom_evenement="", titre_jeu="", couleur_perso="", date_lieu="", telephone="",
                style="eco", evenement_id="", page_start=1):
    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=A4, pageCompression=1)

    nb_cartes = max(1, min(int(nb_cartes), 10000))
    nb_pages = (nb_cartes + COLS_PAGE * ROWS_PAGE - 1) // (COLS_PAGE * ROWS_PAGE)

    rng = random.Random(945000 + int(serie_start))
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
            if faites >= nb_cartes:
                break
            x0 = MARGIN_X
            y0 = MARGIN_BOT + (ROWS_PAGE - 1 - row) * (CARD_H + GUTTER_Y)
            grilles = _gen_carte(rng)
            coul = (couleur_perso if (couleur and couleur_perso)
                    else RAINBOW[(serie - 1) % len(RAINBOW)] if couleur else "#9A9A9A")
            _dessiner_carte(c, x0, y0, grilles, coul, serie, titre_jeu, telephone,
                            style=style, evenement_id=evenement_id)
            serie += 1
            faites += 1

        c.showPage()
        no_page += 1

    c.save()
    buf.seek(0)
    return buf


if __name__ == "__main__":
    pdf = generer_pdf(nb_cartes=10, couleur=True,
                      nom_evenement="ASSOCIATION TE MANU", titre_jeu="Grand Loto",
                      telephone="89.22.23.05")
    with open("test_triple_action_90.pdf", "wb") as f:
        f.write(pdf.read())
    print("TRIPLE ACTION 90 généré")
