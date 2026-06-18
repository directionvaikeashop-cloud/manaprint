"""
MANAPRINT — Couche base de données
SQLite par défaut (développement). Pour la production sur Railway,
remplacer DATABASE_URL par une base PostgreSQL : le schéma reste identique.
"""
import sqlite3
import os
import json
from datetime import datetime
from contextlib import contextmanager

DB_PATH = os.environ.get("MANAPRINT_DB", os.path.join(os.path.dirname(__file__), "manaprint.db"))


@contextmanager
def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def init_db():
    """Crée les tables si elles n'existent pas."""
    with get_db() as conn:
        c = conn.cursor()

        # Clients Pacific Ink confirmés (numéro de client vérifié)
        c.execute("""
            CREATE TABLE IF NOT EXISTS clients_pacific_ink (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                numero      TEXT UNIQUE NOT NULL,
                nom         TEXT,
                ile         TEXT,
                machine_id  TEXT,
                actif       INTEGER DEFAULT 1,
                cree_le     TEXT NOT NULL
            )
        """)

        # Clients internationaux (génèrent un PDF, impriment où ils veulent)
        c.execute("""
            CREATE TABLE IF NOT EXISTS clients_international (
                id        INTEGER PRIMARY KEY AUTOINCREMENT,
                nom       TEXT NOT NULL,
                email     TEXT NOT NULL,
                pays      TEXT,
                cree_le   TEXT NOT NULL
            )
        """)

        # Les 4 machines reliées à la plateforme (gérées par 2KEA & Associé)
        c.execute("""
            CREATE TABLE IF NOT EXISTS machines (
                id          TEXT PRIMARY KEY,
                statut      TEXT NOT NULL DEFAULT 'disponible',
                client_nom  TEXT,
                client_num  TEXT,
                ile         TEXT,
                installee_le TEXT,
                cree_le     TEXT NOT NULL
            )
        """)

        # Historique des générations (facturation par feuille : 10 XPF couleur / 5 XPF N&B)
        c.execute("""
            CREATE TABLE IF NOT EXISTS impressions (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                origine     TEXT NOT NULL,
                identifiant TEXT,
                programme   TEXT NOT NULL,
                theme       TEXT,
                couleur     INTEGER DEFAULT 1,
                nb_feuilles INTEGER DEFAULT 1,
                prix_feuille INTEGER DEFAULT 10,
                montant_total INTEGER DEFAULT 0,
                machine_id  TEXT,
                cree_le     TEXT NOT NULL
            )
        """)

        # Suivi des essais gratuits par client (3 essais max, 1 feuille chacun)
        c.execute("""
            CREATE TABLE IF NOT EXISTS essais (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                identifiant TEXT NOT NULL,
                nb_essais   INTEGER DEFAULT 0,
                cree_le     TEXT NOT NULL
            )
        """)

        # Commandes payées (en ligne ou validées manuellement)
        c.execute("""
            CREATE TABLE IF NOT EXISTS commandes (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                identifiant TEXT NOT NULL,
                origine     TEXT,
                programme   TEXT,
                couleur     INTEGER DEFAULT 1,
                nb_feuilles INTEGER NOT NULL,
                montant     INTEGER NOT NULL,
                mode_paiement TEXT,                 -- 'stripe' | 'manuel'
                statut      TEXT DEFAULT 'en_attente', -- 'en_attente' | 'payee' | 'generee'
                params_perso TEXT,                  -- personnalisation en JSON
                cree_le     TEXT NOT NULL
            )
        """)

        conn.commit()


# ── CLIENTS PACIFIC INK ───────────────────────────────────────────────────────
def normalize_num(n):
    n = (n or "").replace(" ", "").replace(".", "").replace("-", "")
    if n.startswith("+689"):
        n = n[4:]
    elif n.startswith("689") and len(n) > 8:
        n = n[3:]
    return n


def ajouter_client_pi(numero, nom=None, ile=None, machine_id=None):
    num = normalize_num(numero)
    if not num:
        return False, "Numéro vide"
    with get_db() as conn:
        try:
            conn.execute(
                "INSERT INTO clients_pacific_ink (numero, nom, ile, machine_id, cree_le) VALUES (?,?,?,?,?)",
                (num, nom, ile, machine_id, datetime.utcnow().isoformat())
            )
            return True, num
        except sqlite3.IntegrityError:
            return False, "Ce numéro est déjà confirmé"


def verifier_client_pi(numero):
    """Retourne True si le numéro figure parmi les clients actifs."""
    num = normalize_num(numero)
    with get_db() as conn:
        row = conn.execute(
            "SELECT id FROM clients_pacific_ink WHERE numero = ? AND actif = 1", (num,)
        ).fetchone()
        return row is not None


def lister_clients_pi():
    with get_db() as conn:
        rows = conn.execute(
            "SELECT * FROM clients_pacific_ink ORDER BY cree_le DESC"
        ).fetchall()
        return [dict(r) for r in rows]


def retirer_client_pi(numero):
    num = normalize_num(numero)
    with get_db() as conn:
        conn.execute("DELETE FROM clients_pacific_ink WHERE numero = ?", (num,))
        return True


# ── CLIENTS INTERNATIONAUX ────────────────────────────────────────────────────
def enregistrer_client_intl(nom, email, pays=None):
    with get_db() as conn:
        conn.execute(
            "INSERT INTO clients_international (nom, email, pays, cree_le) VALUES (?,?,?,?)",
            (nom, email, pays, datetime.utcnow().isoformat())
        )
        return True


# ── MACHINES ──────────────────────────────────────────────────────────────────
def init_machines(n=4):
    """Crée les machines reliées à la plateforme si elles n'existent pas."""
    with get_db() as conn:
        for i in range(1, n + 1):
            mid = f"MP-MACHINE-{i:02d}"
            existe = conn.execute("SELECT id FROM machines WHERE id = ?", (mid,)).fetchone()
            if not existe:
                conn.execute(
                    "INSERT INTO machines (id, statut, cree_le) VALUES (?, 'disponible', ?)",
                    (mid, datetime.utcnow().isoformat())
                )
        conn.commit()


def lister_machines():
    with get_db() as conn:
        rows = conn.execute("SELECT * FROM machines ORDER BY id").fetchall()
        return [dict(r) for r in rows]


def installer_machine(machine_id, client_nom, client_num, ile):
    with get_db() as conn:
        conn.execute(
            "UPDATE machines SET statut='installee', client_nom=?, client_num=?, ile=?, installee_le=? WHERE id=?",
            (client_nom, client_num, ile, datetime.utcnow().isoformat(), machine_id)
        )
        return True


# ── IMPRESSIONS / FACTURATION ─────────────────────────────────────────────────
PRIX_COULEUR = 10  # XPF par feuille couleur
PRIX_NB = 5        # XPF par feuille noir & blanc


def enregistrer_impression(origine, identifiant, programme, theme, nb_feuilles=1, couleur=True, machine_id=None):
    prix_feuille = PRIX_COULEUR if couleur else PRIX_NB
    montant_total = prix_feuille * nb_feuilles
    with get_db() as conn:
        conn.execute(
            """INSERT INTO impressions
               (origine, identifiant, programme, theme, couleur, nb_feuilles, prix_feuille, montant_total, machine_id, cree_le)
               VALUES (?,?,?,?,?,?,?,?,?,?)""",
            (origine, identifiant, programme, theme, 1 if couleur else 0,
             nb_feuilles, prix_feuille, montant_total, machine_id, datetime.utcnow().isoformat())
        )
        return montant_total


# ── ESSAIS GRATUITS (3 max, 1 feuille chacun) ─────────────────────────────────
NB_ESSAIS_MAX = 3


def get_essais(identifiant):
    """Retourne le nombre d'essais déjà utilisés par ce client."""
    with get_db() as conn:
        row = conn.execute("SELECT nb_essais FROM essais WHERE identifiant = ?", (identifiant,)).fetchone()
        return row["nb_essais"] if row else 0


def incrementer_essai(identifiant):
    """Ajoute un essai. Retourne (ok, essais_restants)."""
    with get_db() as conn:
        row = conn.execute("SELECT nb_essais FROM essais WHERE identifiant = ?", (identifiant,)).fetchone()
        if row is None:
            conn.execute("INSERT INTO essais (identifiant, nb_essais, cree_le) VALUES (?,1,?)",
                         (identifiant, datetime.utcnow().isoformat()))
            return True, NB_ESSAIS_MAX - 1
        if row["nb_essais"] >= NB_ESSAIS_MAX:
            return False, 0
        nouveau = row["nb_essais"] + 1
        conn.execute("UPDATE essais SET nb_essais = ? WHERE identifiant = ?", (nouveau, identifiant))
        return True, NB_ESSAIS_MAX - nouveau


# ── COMMANDES ─────────────────────────────────────────────────────────────────
def creer_commande(identifiant, origine, programme, couleur, nb_feuilles, mode_paiement, params_perso=""):
    prix_feuille = PRIX_COULEUR if couleur else PRIX_NB
    montant = prix_feuille * nb_feuilles
    statut = "en_attente"
    with get_db() as conn:
        cur = conn.execute(
            """INSERT INTO commandes
               (identifiant, origine, programme, couleur, nb_feuilles, montant, mode_paiement, statut, params_perso, cree_le)
               VALUES (?,?,?,?,?,?,?,?,?,?)""",
            (identifiant, origine, programme, 1 if couleur else 0, nb_feuilles, montant,
             mode_paiement, statut, params_perso, datetime.utcnow().isoformat())
        )
        return cur.lastrowid, montant


def get_commande(commande_id):
    with get_db() as conn:
        row = conn.execute("SELECT * FROM commandes WHERE id = ?", (commande_id,)).fetchone()
        return dict(row) if row else None


def marquer_commande_payee(commande_id):
    with get_db() as conn:
        conn.execute("UPDATE commandes SET statut = 'payee' WHERE id = ?", (commande_id,))
        return True


def marquer_commande_generee(commande_id):
    with get_db() as conn:
        conn.execute("UPDATE commandes SET statut = 'generee' WHERE id = ?", (commande_id,))
        return True


def lister_commandes(statut=None):
    with get_db() as conn:
        if statut:
            rows = conn.execute("SELECT * FROM commandes WHERE statut = ? ORDER BY cree_le DESC", (statut,)).fetchall()
        else:
            rows = conn.execute("SELECT * FROM commandes ORDER BY cree_le DESC").fetchall()
        return [dict(r) for r in rows]


if __name__ == "__main__":
    init_db()
    init_machines(4)
    print("Base de données initialisée :", DB_PATH)
    print("Machines :", len(lister_machines()))
