# MANAPRINT — Générateur de cartes de jeux polynésiens

Plateforme de génération de cartes de bingo/loto polynésiens (moteur 2KEA).
En partenariat avec Pacific Ink pour l'impression en Polynésie française.

## Deux accès
- **Client Pacific Ink** (Polynésie) : accès par numéro de client confirmé, impression sur machine Pacific Ink.
- **Client international** : inscription email, génération et téléchargement du PDF à imprimer librement.

## Espace gestion (2KEA & Associé)
Gestion des numéros clients confirmés et des 4 machines reliées à la plateforme.

## Stack
Flask + ReportLab + SQLite (→ PostgreSQL en production sur Railway)

## Lancer en local
```
pip install -r requirements.txt
python app.py
```

## Variables d'environnement (production)
- `MANAPRINT_SECRET` : clé secrète Flask
- `MANAPRINT_ADMIN_CODE` : code de l'espace gestion
- `PORT` : port (fourni par Railway)
- `MANAPRINT_DB` : chemin base (ou URL PostgreSQL en prod)
