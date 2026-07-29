# -*- coding: utf-8 -*-
"""
MANAPRINT — Générateur QUINES 90 (format A4 PAYSAGE)
18 tickets par feuille = 3 COLONNES DE GRILLES (bandes) de 6 tickets empilés.
LA RÈGLE P6 MARATHON (enseignée par Maeva, 30/07) : chaque bande de 6 tickets
porte TOUT l'univers 1-90 — chaque numéro EXACTEMENT UNE FOIS dans la bande,
chaque colonne recevant sa dizaine (1-9, 10-19, …, 80-90) DISTRIBUÉE AU HASARD
le long de la bande. Chaque ticket : 15 numéros, 5 par ligne, 1 ou 2 par
colonne, triés croissants dans la colonne (règle P6).
N° de série discret sous chaque ticket ; sécurité maison (microtexte + QR en case vide).
Couleur arc-en-ciel (par ticket) ou gris (N&B).
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

RAINBOW = [
    "#E53935", "#FB8C00", "#F9A825", "#43A047", "#00ACC1",
    "#1E88E5", "#3949AB", "#8E24AA", "#D81B60", "#6D4C41",
]
GRIS = colors.Color(0.42, 0.42, 0.42)
GRIS_CLAIR = colors.Color(0.78, 0.78, 0.78)


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
# P15 : LA MÊME ÉCRITURE que l'ÉCO (DejaVu), simplement en GRAS
# (décision Maeva 30/07 : « pour les chiffres du P15 la même écriture et gras »)
try:
    # CONDENSÉ-Bold : la même écriture DejaVu en gras, chiffres plus étroits —
    # c'est elle qui permet le MAXIMUM dans le carré (décision Maeva 30/07 :
    # « grossis les chiffres au maximum qui peut rentrer dans chaque carré »)
    _pm.registerFont(_TF("DJBOLDC", "/usr/share/fonts/truetype/dejavu/DejaVuSansCondensed-Bold.ttf"))
    _POLICE_P15 = "DJBOLDC"
except Exception:
    _POLICE_P15 = "Helvetica-Bold"
_GRIS_P15 = colors.Color(0.55, 0.55, 0.55)

def _style_chiffres(style):
    """Les chiffres du QUINES 90 sont TOUJOURS GRAS, style P15
    (décision Maeva 30/07 : « les chiffres ne sont pas gras comme le P15 ») —
    quelle que soit la gamme, l'écriture DejaVu passe en Bold."""
    if str(style).lower() in ("p15", "premium"):
        return _POLICE_P15, _GRIS_P15
    return _POLICE_P15, _GRIS_ECO
# ═════════════════════════════════════════════════════════════════════

PAGE_W, PAGE_H = landscape(A4)   # 297 × 210 mm — fidèle au modèle
DECADES = [(1, 9), (10, 19), (20, 29), (30, 39), (40, 49),
           (50, 59), (60, 69), (70, 79), (80, 90)]

COLS_PAGE = 3
ROWS_PAGE = 6
MARGIN_X = 6 * mm
MARGIN_TOP = 8 * mm
MARGIN_BOT = 5 * mm
GUTTER_X = 4 * mm
GUTTER_Y = 3 * mm

TICKET_W = (PAGE_W - 2 * MARGIN_X - (COLS_PAGE - 1) * GUTTER_X) / COLS_PAGE
TICKET_H = (PAGE_H - MARGIN_TOP - MARGIN_BOT - (ROWS_PAGE - 1) * GUTTER_Y) / ROWS_PAGE
CELL_W = TICKET_W / 9
CELL_H = TICKET_H / 3


def _taille_max_chiffres():
    """Le plus gros chiffre qui RENTRE dans le carré (décision Maeva 30/07) :
    on pousse jusqu'à ce que « 88 » touche la marge de la case."""
    marge = 0.9 * mm
    t = 40.0
    while t > 6:
        if (pdfmetrics.stringWidth("88", _POLICE_P15, t) <= CELL_W - marge
                and 0.729 * t <= CELL_H - marge):
            return t
        t -= 0.1
    return CELL_H * 0.66


T_NUM = _taille_max_chiffres()


def _repartir_lignes(rng, comptes):
    """Pour UN ticket : place les comptes (1 ou 2 par colonne) sur les 3 lignes,
    chaque ligne finissant à 5 cases. Retourne cases[ligne][colonne] = True/None."""
    while True:
        lignes_restantes = [5, 5, 5]
        cases = [[None] * 9 for _ in range(3)]
        ok = True
        ordre = sorted(range(9), key=lambda i: -comptes[i])
        for ci in ordre:
            cand = sorted(range(3), key=lambda r: (-lignes_restantes[r], rng.random()))
            choisies = cand[:comptes[ci]]
            if any(lignes_restantes[r] <= 0 for r in choisies):
                ok = False
                break
            for r in choisies:
                cases[r][ci] = True
                lignes_restantes[r] -= 1
        if ok and lignes_restantes == [0, 0, 0]:
            return cases


def _gen_bande(rng):
    """LA RÈGLE P6 MARATHON DU QUINES 90 (enseignée par Maeva, 30/07) :
    une COLONNE DE GRILLES = 6 tickets empilés qui portent, ENSEMBLE, TOUT
    l'univers 1-90 — chaque numéro exactement UNE fois dans la bande.
    Chaque colonne de la bande reçoit sa dizaine entière, distribuée AU HASARD
    entre les 6 tickets ; dans chaque grille la colonne reste triée (règle P6).
    Chaque ticket : 15 numéros, 5 par ligne, 1 ou 2 par colonne. Retourne 6 tickets."""
    tailles = [b - a + 1 for (a, b) in DECADES]      # 9, 10×7, 11 = 90
    while True:
        # matrice des comptes 6 tickets × 9 colonnes : 1 ou 2 —
        # lignes = 15 (6 doubles par ticket), colonnes = la taille de la dizaine
        deux_par_col = [t - 6 for t in tailles]      # 3, 4…4, 5 doubles à placer
        cap = [6] * 6                                 # chaque ticket veut 6 doubles
        comptes = [[1] * 9 for _ in range(6)]
        ok = True
        for ci in sorted(range(9), key=lambda i: -deux_par_col[i]):
            cand = sorted(range(6), key=lambda t: (-cap[t], rng.random()))
            pris = cand[:deux_par_col[ci]]
            if any(cap[t] <= 0 for t in pris):
                ok = False
                break
            for t in pris:
                comptes[t][ci] = 2
                cap[t] -= 1
        if not ok or any(cap):
            continue
        # les lignes de chaque ticket, puis la dizaine entière DISTRIBUÉE AU HASARD
        # dans sa colonne de grilles (décision Maeva 30/07 : « garde cette règle et
        # distribue aléatoirement les chiffres marathon de sa colonne ») —
        # la bande porte toujours TOUT 1-90 une seule fois ; dans chaque grille,
        # la colonne reste triée croissante (règle P6).
        tickets = [_repartir_lignes(rng, comptes[t]) for t in range(6)]
        for ci, (a, b) in enumerate(DECADES):
            sac = list(range(a, b + 1))
            rng.shuffle(sac)
            pos = 0
            for t in range(6):
                rangs = [r for r in range(3) if tickets[t][r][ci]]
                part = sorted(sac[pos:pos + len(rangs)])
                pos += len(rangs)
                for r, n in zip(rangs, part):
                    tickets[t][r][ci] = n
        return tickets


def _dessiner_ticket(c, x0, y0, cases, couleur_hex, serie, style="eco", evenement_id=""):
    police_ch, gris_ch = _style_chiffres(style)
    col = colors.HexColor(couleur_hex)

    # Bordure du ticket (un peu plus affirmée, fidèle au modèle)
    c.setStrokeColor(col); c.setLineWidth(0.9)
    c.rect(x0, y0, TICKET_W, TICKET_H, stroke=1, fill=0)
    if _sec:  # cadre intérieur en microtexte (sécurité anti-photocopie)
        _sec.cadre_micro(c, x0, y0, TICKET_W, TICKET_H, serie, retrait=0.8 * mm)

    # Quadrillage intérieur fin
    c.setStrokeColor(col); c.setLineWidth(0.35)
    for i in range(1, 9):
        c.line(x0 + i * CELL_W, y0, x0 + i * CELL_W, y0 + TICKET_H)
    for j in range(1, 3):
        c.line(x0, y0 + j * CELL_H, x0 + TICKET_W, y0 + j * CELL_H)

    # Les numéros — gros, au cœur de leur case (taille au calibre des cases)
    t_num = T_NUM   # le maximum mesuré qui rentre dans le carré
    for r in range(3):          # r = 0 en HAUT
        cy = y0 + TICKET_H - (r + 1) * CELL_H
        for ci in range(9):
            n = cases[r][ci]
            cx = x0 + ci * CELL_W + CELL_W / 2
            if n is None:
                continue
            if _sec:  # chiffres "billet de banque" remplis de microtexte
                _sec.chiffre_micro(c, n, cx, cy + CELL_H / 2 - t_num * 0.36, t_num, gris_ch, police_ch)
            else:
                c.setFillColor(gris_ch); c.setFont(police_ch, t_num)
                c.drawCentredString(cx, cy + CELL_H / 2 - t_num * 0.36, str(n))

    # N° de série discret, sous le ticket (dans le couloir)
    c.setFillColor(GRIS); c.setFont(POLICE, 4)
    c.drawRightString(x0 + TICKET_W - 0.5 * mm, y0 - 2.1 * mm, "N\u00b0 %06d" % serie)

    # 🚫 PAS DE QR sur ce jeu (décision Maeva 30/07 : le QUINES 90 est le seul
    # jeu de la maison SANS QR CODE — le microtexte de sécurité reste en poste).


def generer_pdf(nb_cartes=18, serie_start=1, theme="", couleur=True,
                nom_evenement="", titre_jeu="", couleur_perso="", date_lieu="", telephone="",
                style="eco", evenement_id=""):
    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=landscape(A4), pageCompression=1)

    nb_cartes = max(1, min(int(nb_cartes), 10000))
    par_page = COLS_PAGE * ROWS_PAGE
    nb_pages = (nb_cartes + par_page - 1) // par_page

    rng = random.Random(982000 + int(serie_start))
    serie = int(serie_start)
    no_page = 1
    faites = 0

    for _ in range(nb_pages):
        # En-tête de page : identité à gauche, numéro de page au centre (fidèle au modèle)
        ident = "QUINES 90"
        if titre_jeu and titre_jeu.strip().upper() != "QUINES 90":
            ident += "  \u2014  " + titre_jeu.strip()
        if nom_evenement and nom_evenement.strip().upper() not in ident.upper():
            ident += "  \u00b7  " + nom_evenement.strip()
        if telephone:
            ident += "  \u00b7  " + telephone
        c.setFillColor(GRIS); c.setFont(POLICE, 6.5)
        c.drawString(MARGIN_X, PAGE_H - 5.2 * mm, ident[:110])
        c.setFillColor(GRIS_CLAIR); c.setFont(POLICE, 6)
        c.drawCentredString(PAGE_W / 2, PAGE_H - 5.2 * mm, "%03d" % no_page)

        for col_i in range(COLS_PAGE):
            if faites >= nb_cartes:
                break
            bande = _gen_bande(rng)
            for row in range(ROWS_PAGE):
                if faites >= nb_cartes:
                    break
                x0 = MARGIN_X + col_i * (TICKET_W + GUTTER_X)
                y0 = MARGIN_BOT + (ROWS_PAGE - 1 - row) * (TICKET_H + GUTTER_Y)
                cases = bande[row]
                coul = (couleur_perso if (couleur and couleur_perso)
                        else RAINBOW[(serie - 1) % len(RAINBOW)] if couleur else "#9A9A9A")
                _dessiner_ticket(c, x0, y0, cases, coul, serie, style=style, evenement_id=evenement_id)
                serie += 1
                faites += 1

        c.showPage()
        no_page += 1

    c.save()
    buf.seek(0)
    return buf


if __name__ == "__main__":
    pdf = generer_pdf(nb_cartes=18, couleur=True, titre_jeu="QUINES 90", telephone="89 22 23 05")
    with open("test_quines90.pdf", "wb") as f:
        f.write(pdf.read())
    print("QUINES 90 généré")
