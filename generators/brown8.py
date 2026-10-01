# ═════════════════════════════════════════════════════════════════════
# 🥂 30/09 — CHAMPAGNE : nouvelle planche, celle aux grosses bulles
#   (sceau Maeva : « voici la nouvelle maquette du jeu CHAMPAGNE »)
#   ⭐ LES PLAGES NE CHANGENT PAS : B 1-15 (1 numero), I 16-30 (3),
#     N 31-45 (4), G 46-60 (3), O 61-75 (1). Douze numeros par carton,
#     tries de gauche a droite. Le crieur reste sur 1-75.
#   ⚠️ LE DESSIN DU JEU CHANGE : les quinzaines se lisaient en COLONNES
#     (losange de bulles), elles se lisent maintenant en RANGEES, chacune
#     marquee par sa lettre B, I, N, G, O. Pour la joueuse et la crieuse,
#     la partie se joue exactement pareil.
#   ⭐ ELLE A SES 25 PT. Cette maquette met NEUF cartons par feuille au
#     lieu de seize : le trou des bulles passe de 6,28 a 10,69 mm et le
#     carton de 68x44 a 94x66 mm. Mesure sur les 108 bulles d'une
#     feuille : 0,21 mm de blanc avant son trait. A 27 pt ca toucherait.
#   ⚠️⚠️ 9 cartons par feuille A4 PAYSAGE au lieu de 6 en portrait. Sans
#     cette reinscription, 500 feuilles commandees n'en donneraient que
#     333.
#   ⚠️ Le jeu RESTE dans la liste « carton avec dessin » et RESTE au
#     tarif ordinaire (IMAGE_TARIF_NB_ORDINAIRE) : rien n'est touche de
#     ce cote, c'est son choix commercial.
#   ⭐ 63 582 553 125 cartons differents : le jeu ne s'epuise pas.
# ═════════════════════════════════════════════════════════════════════
GRIS_PARTICULIERS.update({"champagne": 0.40})
_GRIS_POSES = _imposer_gris_maison()
_enregistrer_paire("champagne", "CHAMPAGNE", "\U0001f942", 9, champagne.generer_pdf)
# ⭐ la regle du 28/09 : on rememorise la table de fabrication APRES
#    tout bloc qui touche au catalogue (le plafond des 375 feuilles).
CARTES_PAR_FEUILLE.update({_j: _v["cartes_par_feuille"] for _j, _v in REGISTRE_JEUX.items()})
print("[CHAMPAGNE] nouvelle planche · crieur %s · 9 cartons/feuille · %d jeux"
      % (_PLAGES_CALLER["champagne"], len(REGISTRE_JEUX)))
