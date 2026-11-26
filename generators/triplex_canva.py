# -*- coding: utf-8 -*-
"""MANAPRINT — TRIPLE X 75 (création 2KEA) · maquette CANVA de Maeva (25/11/2026, « triple_x_canva_10_A4 »).
Reprise TELLE QUELLE : 10 billets / feuille A4 PORTRAIT (5 colonnes x 2 rangées),
traits de coupe en pointillés. Chaque billet : cadre arrondi, « N° ___ », TRIPLE X et ses
étoiles, et ses bulles (lettre + plage sur le bandeau). Le dessin est rejoué TRAIT POUR TRAIT
depuis la maquette et enregistré une seule fois par document (fichier léger).
RÈGLE (inchangée) — TROIS numéros par bulle, triés (deux en haut, un dessous) :
   places 1 et 5 : bulle B 1-15  + bulle O 61-75
   places 2 et 4 : bulle I 16-30 + bulle G 46-60
   place 3       : bulle N 31-45 seule              -> crieur 1 à 75.
Chiffres gras comme la maquette, 30 pt (le maximum), toujours DANS la bulle (25/11).
Le tout est réduit pour garder 6 mm de marge d'impression (Konica / Sharp)."""
import io, random
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors

PAGE_W, PAGE_H = A4
COLS, RANGS = 5, 2
CARTES_PAGE = COLS * RANGS                # 10
CELL_W, CELL_H = 119.0551, 420.9449
NOIR = colors.black
RAINBOW = ["#E53935", "#FB8C00", "#F9A825", "#43A047", "#00ACC1",
           "#1E88E5", "#3949AB", "#8E24AA", "#D81B60", "#6D4C41"]
POLICE_NUM, T_NUM = "Helvetica-Bold", 30
PLAGES = {"B": (1, 15), "I": (16, 30), "N": (31, 45), "G": (46, 60), "O": (61, 75)}
# modèle de billet par place (1 à 5) et ses bulles : (lettre, ligne de base du haut, ligne du bas)
MODELES = {"BO": [("B", 234.5, 209.5), ("O", 78.6, 53.6)],
           "IG": [("I", 234.5, 209.5), ("G", 78.6, 53.6)],
           "N": [("N", 166.47, 141.47)]}
PLACES = ["BO", "IG", "N", "IG", "BO"]
_XG, _XD, _XM = 40.0, 79.06, 59.53      # centres : gauche, droite (ligne du haut), milieu (dessous)

MARGE_SURE = 6 * 72 / 25.4
ECHELLE = min((PAGE_W - 2 * MARGE_SURE) / PAGE_W, (PAGE_H - 2 * MARGE_SURE) / PAGE_H)
DECAL_X = (PAGE_W - PAGE_W * ECHELLE) / 2.0
DECAL_Y = (PAGE_H - PAGE_H * ECHELLE) / 2.0
_DEJA = set()


def _numeros(rng, modele):
    for _ in range(500):
        t = tuple(tuple(sorted(rng.sample(range(PLAGES[L][0], PLAGES[L][1] + 1), 3)))
                  for L, _h, _b in MODELES[modele])
        if (modele, t) not in _DEJA:
            break
    _DEJA.add((modele, t))
    return t


def _txt(c, s, x, y, police, taille, col, centre=False):
    w = c.stringWidth(s, police, taille)
    t = c.beginText(x - w / 2.0 if centre else x, y); t.setFont(police, taille)
    t.setFillColor(col); t.textOut(s)
    c.drawText(t)


def _modele(c, nom):
    cle = "_tx_modele_" + nom
    if getattr(c, cle, False):
        return
    d = _DESSINS[nom]
    for k, v in (("{HB}", "Helvetica-Bold"), ("{H}", "Helvetica")):
        d = d.replace(k, c._doc.getInternalFontName(v))
    c.beginForm("TRIPLEX_" + nom, 0, 0, CELL_W, CELL_H)
    c._code.append("q\n" + d + "\nQ")
    c.endForm()
    setattr(c, cle, True)


def _billet(c, ox, oy, serie, place, rng, col):
    nom = PLACES[place]
    _modele(c, nom)
    c.saveState()
    c.translate(ox, oy)
    c.doForm("TRIPLEX_" + nom)
    _txt(c, "%06d" % serie, 70.09543, 398.2677, "Helvetica-Bold", 10, NOIR)
    for (L, yh, yb), (a, b, d) in zip(MODELES[nom], _numeros(rng, nom)):
        _txt(c, str(a), _XG, yh, POLICE_NUM, T_NUM, col, centre=True)
        _txt(c, str(b), _XD, yh, POLICE_NUM, T_NUM, col, centre=True)
        _txt(c, str(d), _XM, yb, POLICE_NUM, T_NUM, col, centre=True)
    c.restoreState()


def generer_pdf(nb_cartes=None, nb_tickets=None, serie_start=1, theme="", couleur=True,
                nom_evenement="", titre_jeu="", couleur_perso="", date_lieu="",
                telephone="", page_start=1, evenement_id="", style="", motif="", **_ig):
    n_ = nb_cartes if nb_cartes is not None else nb_tickets
    n_ = max(1, int(n_ if n_ else CARTES_PAGE))
    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=(PAGE_W, PAGE_H), pageCompression=1)
    rng = random.Random(int(serie_start) * 100003 + 3075)
    _DEJA.clear()
    serie = int(serie_start)
    faits = 0
    try:
        no_page = max(1, int(page_start))
    except Exception:
        no_page = 1
    col_imposee = None
    if couleur and couleur_perso:
        try:
            col_imposee = colors.HexColor(couleur_perso)
        except Exception:
            col_imposee = None

    while faits < n_:
        entete = "  \u00b7  ".join(t for t in ((nom_evenement or "").strip(), (date_lieu or "").strip()) if t)
        if entete:
            c.setFillColor(NOIR); c.setFont("Helvetica-Bold", 7)
            c.drawCentredString(PAGE_W / 2.0, PAGE_H - DECAL_Y / 2.0 - 2.5, entete)
        c.setFillColor(colors.Color(0.5, 0.5, 0.5)); c.setFont("Helvetica", 6)
        c.drawRightString(PAGE_W - DECAL_X, DECAL_Y / 2.0 - 2, "page %d" % no_page)

        c.saveState()
        c.translate(DECAL_X, DECAL_Y); c.scale(ECHELLE, ECHELLE)
        for idx in range(CARTES_PAGE):
            if faits >= n_:
                break
            ox = (idx % COLS) * CELL_W
            oy = (RANGS - 1 - idx // COLS) * CELL_H
            col = (col_imposee or colors.HexColor(RAINBOW[serie % len(RAINBOW)])) if couleur else NOIR
            _billet(c, ox, oy, serie, idx % COLS, rng, col)
            serie += 1
            faits += 1
        c.setStrokeColor(colors.Color(0.5, 0.5, 0.5)); c.setLineWidth(0.3); c.setDash(2, 2)
        for i in range(1, COLS):
            c.line(i * CELL_W, 0, i * CELL_W, RANGS * CELL_H)
        for j in range(1, RANGS):
            c.line(0, j * CELL_H, COLS * CELL_W, j * CELL_H)
        c.restoreState()
        c.showPage()
        no_page += 1
    c.save()
    buf.seek(0)
    return buf


_DESSINS = {
    'BO': '0 0 0 RG\n1 1 1 rg\n1.5 w\nn\n13.6063 2.834646 m\n105.4488 2.834646 l\n111.4034 2.834646 116.2205 7.651729 116.2205 13.6063 c\n116.2205 407.3386 l\n116.2205 413.2932 111.4034 418.1102 105.4488 418.1102 c\n13.6063 418.1102 l\n7.651729 418.1102 2.834646 413.2932 2.834646 407.3386 c\n2.834646 13.6063 l\n2.834646 7.651729 7.651729 2.834646 13.6063 2.834646 c\nh\nB*\nBT 1 0 0 1 0 0 Tm 0 Tc 1 0 0 1 14.17323 398.2677 Tm 0 0 0 rg {HB} 10 Tf 12 TL (N\\260) Tj 0 Tc ET\n.5 w\nn 41.10236 394.5827 m 104.8819 394.5827 l S\n1 1 1 rg\n0 0 0 RG\n.5 w\nn 17.00787 387.4961 m 15.73326 384.4315 l 12.42483 384.1663 l 14.9455 382.0071 l 14.1754 378.7786 l 17.00787 380.5087 l 19.84035 378.7786 l 19.07024 382.0071 l 21.59092 384.1663 l 18.28249 384.4315 l h\nB*\n1 1 1 rg\n0 0 0 RG\n.5 w\nn 10.77165 374.4567 m 9.946903 372.4738 l 7.806154 372.3021 l 9.437179 370.905 l 8.938874 368.816 l 10.77165 369.9354 l 12.60443 368.816 l 12.10613 370.905 l 13.73715 372.3021 l 11.5964 372.4738 l h\nB*\nBT 1 0 0 1 0 0 Tm .3 Tc 1 0 0 1 16.26335 353.4803 Tm 0 0 0 rg {H} 17 Tf 20.4 TL (TRIPLE) Tj 0 Tc ET\nBT 1 0 0 1 0 0 Tm 0 Tc 1 0 0 1 89.20772 350.0787 Tm 0 0 0 rg {H} 30 Tf 36 TL (X) Tj 0 Tc ET\n0 0 0 RG\n1 1 1 rg\n1.4 w\nn\n111.685 262.2047 m\n111.685 295.8637 88.33334 323.1496 59.52756 323.1496 c\n30.72178 323.1496 7.370079 295.8637 7.370079 262.2047 c\n7.370079 228.5458 30.72178 201.2598 59.52756 201.2598 c\n88.33334 201.2598 111.685 228.5458 111.685 262.2047 c\nB*\n.8 w\nn 7.643855 268.4409 m 111.4113 268.4409 l S\nBT 1 0 0 1 0 0 Tm 0 Tc 1 0 0 1 52.30588 288.8504 Tm 0 0 0 rg {HB} 20 Tf 24 TL (B) Tj 0 Tc ET\nBT 1 0 0 1 0 0 Tm 0 Tc 1 0 0 1 45.46335 273.2598 Tm 0 0 0 rg {HB} 11 Tf 13.2 TL (1 - 15) Tj 0 Tc ET\n0 0 0 rg\n0 0 0 RG\n1 1 1 rg\n1.4 w\nn\n111.685 106.2992 m\n111.685 139.9581 88.33334 167.2441 59.52756 167.2441 c\n30.72178 167.2441 7.370079 139.9581 7.370079 106.2992 c\n7.370079 72.64028 30.72178 45.35433 59.52756 45.35433 c\n88.33334 45.35433 111.685 72.64028 111.685 106.2992 c\nB*\n.8 w\nn 7.643855 112.5354 m 111.4113 112.5354 l S\nBT 1 0 0 1 0 0 Tm 0 Tc 1 0 0 1 51.74924 132.9449 Tm 0 0 0 rg {HB} 20 Tf 24 TL (O) Tj 0 Tc ET\nBT 1 0 0 1 0 0 Tm 0 Tc 1 0 0 1 42.40451 117.3543 Tm 0 0 0 rg {HB} 11 Tf 13.2 TL (61 - 75) Tj 0 Tc ET\n0 0 0 rg',
    'IG': '0 0 0 RG\n1 1 1 rg\n1.5 w\nn\n13.6063 2.834646 m\n105.4488 2.834646 l\n111.4034 2.834646 116.2205 7.651729 116.2205 13.6063 c\n116.2205 407.3386 l\n116.2205 413.2932 111.4034 418.1102 105.4488 418.1102 c\n13.6063 418.1102 l\n7.651729 418.1102 2.834646 413.2932 2.834646 407.3386 c\n2.834646 13.6063 l\n2.834646 7.651729 7.651729 2.834646 13.6063 2.834646 c\nh\nB*\nBT 1 0 0 1 0 0 Tm 0 Tc 1 0 0 1 14.17323 398.2677 Tm 0 0 0 rg {HB} 10 Tf 12 TL (N\\260) Tj 0 Tc ET\n.5 w\nn 41.10236 394.5827 m 104.8819 394.5827 l S\n1 1 1 rg\n0 0 0 RG\n.5 w\nn 17.00787 387.4961 m 15.73326 384.4315 l 12.42483 384.1663 l 14.9455 382.0071 l 14.1754 378.7786 l 17.00787 380.5087 l 19.84035 378.7786 l 19.07024 382.0071 l 21.59092 384.1663 l 18.28249 384.4315 l h\nB*\n1 1 1 rg\n0 0 0 RG\n.5 w\nn 10.77165 374.4567 m 9.946903 372.4738 l 7.806154 372.3021 l 9.437179 370.905 l 8.938874 368.816 l 10.77165 369.9354 l 12.60443 368.816 l 12.10613 370.905 l 13.73715 372.3021 l 11.5964 372.4738 l h\nB*\nBT 1 0 0 1 0 0 Tm .3 Tc 1 0 0 1 16.26335 353.4803 Tm 0 0 0 rg {H} 17 Tf 20.4 TL (TRIPLE) Tj 0 Tc ET\nBT 1 0 0 1 0 0 Tm 0 Tc 1 0 0 1 89.20772 350.0787 Tm 0 0 0 rg {H} 30 Tf 36 TL (X) Tj 0 Tc ET\n0 0 0 RG\n1 1 1 rg\n1.4 w\nn\n111.685 262.2047 m\n111.685 295.8637 88.33334 323.1496 59.52756 323.1496 c\n30.72178 323.1496 7.370079 295.8637 7.370079 262.2047 c\n7.370079 228.5458 30.72178 201.2598 59.52756 201.2598 c\n88.33334 201.2598 111.685 228.5458 111.685 262.2047 c\nB*\n.8 w\nn 7.643855 268.4409 m 111.4113 268.4409 l S\nBT 1 0 0 1 0 0 Tm 0 Tc 1 0 0 1 56.74924 288.8504 Tm 0 0 0 rg {HB} 20 Tf 24 TL (I) Tj 0 Tc ET\nBT 1 0 0 1 0 0 Tm 0 Tc 1 0 0 1 42.40451 273.2598 Tm 0 0 0 rg {HB} 11 Tf 13.2 TL (16 - 30) Tj 0 Tc ET\n0 0 0 rg\n0 0 0 RG\n1 1 1 rg\n1.4 w\nn\n111.685 106.2992 m\n111.685 139.9581 88.33334 167.2441 59.52756 167.2441 c\n30.72178 167.2441 7.370079 139.9581 7.370079 106.2992 c\n7.370079 72.64028 30.72178 45.35433 59.52756 45.35433 c\n88.33334 45.35433 111.685 72.64028 111.685 106.2992 c\nB*\n.8 w\nn 7.643855 112.5354 m 111.4113 112.5354 l S\nBT 1 0 0 1 0 0 Tm 0 Tc 1 0 0 1 51.74924 132.9449 Tm 0 0 0 rg {HB} 20 Tf 24 TL (G) Tj 0 Tc ET\nBT 1 0 0 1 0 0 Tm 0 Tc 1 0 0 1 42.40451 117.3543 Tm 0 0 0 rg {HB} 11 Tf 13.2 TL (46 - 60) Tj 0 Tc ET\n0 0 0 rg',
    'N': '0 0 0 RG\n1 1 1 rg\n1.5 w\nn\n13.6063 2.834646 m\n105.4488 2.834646 l\n111.4034 2.834646 116.2205 7.651729 116.2205 13.6063 c\n116.2205 407.3386 l\n116.2205 413.2932 111.4034 418.1102 105.4488 418.1102 c\n13.6063 418.1102 l\n7.651729 418.1102 2.834646 413.2932 2.834646 407.3386 c\n2.834646 13.6063 l\n2.834646 7.651729 7.651729 2.834646 13.6063 2.834646 c\nh\nB*\nBT 1 0 0 1 0 0 Tm 0 Tc 1 0 0 1 14.17323 398.2677 Tm 0 0 0 rg {HB} 10 Tf 12 TL (N\\260) Tj 0 Tc ET\n.5 w\nn 41.10236 394.5827 m 104.8819 394.5827 l S\n1 1 1 rg\n0 0 0 RG\n.5 w\nn 17.00787 387.4961 m 15.73326 384.4315 l 12.42483 384.1663 l 14.9455 382.0071 l 14.1754 378.7786 l 17.00787 380.5087 l 19.84035 378.7786 l 19.07024 382.0071 l 21.59092 384.1663 l 18.28249 384.4315 l h\nB*\n1 1 1 rg\n0 0 0 RG\n.5 w\nn 10.77165 374.4567 m 9.946903 372.4738 l 7.806154 372.3021 l 9.437179 370.905 l 8.938874 368.816 l 10.77165 369.9354 l 12.60443 368.816 l 12.10613 370.905 l 13.73715 372.3021 l 11.5964 372.4738 l h\nB*\nBT 1 0 0 1 0 0 Tm .3 Tc 1 0 0 1 16.26335 353.4803 Tm 0 0 0 rg {H} 17 Tf 20.4 TL (TRIPLE) Tj 0 Tc ET\nBT 1 0 0 1 0 0 Tm 0 Tc 1 0 0 1 89.20772 350.0787 Tm 0 0 0 rg {H} 30 Tf 36 TL (X) Tj 0 Tc ET\n0 0 0 RG\n1 1 1 rg\n1.4 w\nn\n111.685 194.1732 m\n111.685 227.8322 88.33334 255.1181 59.52756 255.1181 c\n30.72178 255.1181 7.370079 227.8322 7.370079 194.1732 c\n7.370079 160.5143 30.72178 133.2283 59.52756 133.2283 c\n88.33334 133.2283 111.685 160.5143 111.685 194.1732 c\nB*\n.8 w\nn 7.643855 200.4094 m 111.4113 200.4094 l S\nBT 1 0 0 1 0 0 Tm 0 Tc 1 0 0 1 52.30588 220.8189 Tm 0 0 0 rg {HB} 20 Tf 24 TL (N) Tj 0 Tc ET\nBT 1 0 0 1 0 0 Tm 0 Tc 1 0 0 1 42.40451 205.2283 Tm 0 0 0 rg {HB} 11 Tf 13.2 TL (31 - 45) Tj 0 Tc ET\n0 0 0 rg',
}


if __name__ == "__main__":
    open("test_triplex.pdf", "wb").write(generer_pdf(nb_cartes=10, couleur=False).read())
    print("TRIPLE X genere")
