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

        # Suivi des essais gratuits : un enregistrement par essai, avec horodatage
        # (3 essais autorisés par fenêtre de 5 minutes, puis renouvellement auto)
        c.execute("""
            CREATE TABLE IF NOT EXISTS essais (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                identifiant TEXT NOT NULL,
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

        # Suivi des visiteurs de la plateforme (1 ligne par visite de la page d'accueil)
        c.execute("""
            CREATE TABLE IF NOT EXISTS visites (
                id        INTEGER PRIMARY KEY AUTOINCREMENT,
                ip_hash   TEXT,
                page      TEXT,
                ua        TEXT,
                source    TEXT,
                cree_le   TEXT NOT NULL
            )
        """)
        # Migration : ajoute la colonne source si la table existait déjà sans elle
        try:
            c.execute("ALTER TABLE visites ADD COLUMN source TEXT")
        except Exception:
            pass

        conn.commit()
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
# Tarifs par profil (XPF par feuille A4) — VISION 2 GAMMES (Maeva, juil. 2026) :
#   eco : écriture fine, économie de toner (la 1re proposition, préservée)
#   p15 : écriture grasse PREMIUM style P15
TARIFS = {
    #                       ── gamme ÉCO ──          ── gamme PREMIUM P15 ──
    "produit_imprime": {"eco": {"couleur": 7,  "nb": 3},   "p15": {"couleur": 10, "nb": 8}},   # produit fini imprimé (encre/toner + papier) — Accès ECO LASER
    "polynesien":      {"eco": {"couleur": 3,  "nb": 1.5}, "p15": {"couleur": 3,  "nb": 2}},   # génération du fichier PDF
    "international":   {"eco": {"couleur": 6,  "nb": 3},   "p15": {"couleur": 6,  "nb": 3}},   # fichier PDF uniquement (sans impression) — tarif unique, gammes confondues
}
# Compatibilité : les anciennes commandes/sessions utilisent encore l'ancien identifiant interne.
TARIFS["pacific_ink"] = TARIFS["produit_imprime"]
PRIX_COULEUR = 10  # défaut (compatibilité)
PRIX_NB = 5


def _gamme_du_programme(programme):
    """Détecte la gamme depuis l'identifiant du jeu : ..._p15_... = PREMIUM, sinon ÉCO."""
    return "p15" if "_p15" in str(programme or "") else "eco"


def prix_feuille_profil(origine, couleur, gamme="eco"):
    """Retourne le prix d'une feuille selon le profil, le mode couleur/N&B et la gamme."""
    t = TARIFS.get(origine, TARIFS["produit_imprime"])
    g = t.get(gamme, t["eco"])
    return g["couleur"] if couleur else g["nb"]


def enregistrer_impression(origine, identifiant, programme, theme, nb_feuilles=1, couleur=True, machine_id=None):
    prix_feuille = prix_feuille_profil(origine, couleur, _gamme_du_programme(programme))
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


# ── ESSAIS GRATUITS (3 par fenêtre de 5 minutes, renouvellement auto) ─────────
NB_ESSAIS_MAX = 3
FENETRE_ESSAIS_MINUTES = 5


def _essais_recents(conn, identifiant):
    """Nombre d'essais utilisés dans les 5 dernières minutes."""
    from datetime import timedelta
    limite = (datetime.utcnow() - timedelta(minutes=FENETRE_ESSAIS_MINUTES)).isoformat()
    row = conn.execute(
        "SELECT COUNT(*) AS n FROM essais WHERE identifiant = ? AND cree_le >= ?",
        (identifiant, limite)
    ).fetchone()
    return row["n"] if row else 0


def get_essais(identifiant):
    """Retourne le nombre d'essais utilisés dans la fenêtre de 5 minutes."""
    with get_db() as conn:
        return _essais_recents(conn, identifiant)


def incrementer_essai(identifiant):
    """Ajoute un essai si moins de 3 dans les 5 dernières minutes.
    Retourne (ok, essais_restants)."""
    with get_db() as conn:
        utilises = _essais_recents(conn, identifiant)
        if utilises >= NB_ESSAIS_MAX:
            return False, 0
        conn.execute(
            "INSERT INTO essais (identifiant, cree_le) VALUES (?,?)",
            (identifiant, datetime.utcnow().isoformat())
        )
        return True, NB_ESSAIS_MAX - (utilises + 1)


# ── COMMANDES ─────────────────────────────────────────────────────────────────
def creer_commande(identifiant, origine, programme, couleur, nb_feuilles, mode_paiement, params_perso=""):
    prix_feuille = prix_feuille_profil(origine, couleur, _gamme_du_programme(programme))
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


# ── VISITEURS ─────────────────────────────────────────────────────────────────
def enregistrer_visite(ip_hash, page, ua, source=None):
    """Enregistre une visite (ip_hash anonymisé, page, navigateur, source)."""
    with get_db() as conn:
        conn.execute(
            "INSERT INTO visites (ip_hash, page, ua, source, cree_le) VALUES (?, ?, ?, ?, ?)",
            (ip_hash, page, (ua or "")[:300], (source or "direct")[:40], datetime.now().isoformat())
        )


def stats_visites():
    """Renvoie un résumé de fréquentation de la plateforme."""
    auj = datetime.now().strftime("%Y-%m-%d")
    with get_db() as conn:
        c = conn.cursor()
        def un(q, args=()):
            r = c.execute(q, args).fetchone()
            return r[0] if r else 0
        total       = un("SELECT COUNT(*) FROM visites")
        uniques     = un("SELECT COUNT(DISTINCT ip_hash) FROM visites")
        visites_auj = un("SELECT COUNT(*) FROM visites WHERE substr(cree_le,1,10)=?", (auj,))
        uniques_auj = un("SELECT COUNT(DISTINCT ip_hash) FROM visites WHERE substr(cree_le,1,10)=?", (auj,))
        essais      = un("SELECT COUNT(*) FROM essais")
        impressions = un("SELECT COUNT(*) FROM impressions")
        feuilles    = un("SELECT COALESCE(SUM(nb_feuilles),0) FROM impressions")
        commandes   = un("SELECT COUNT(*) FROM commandes")
        rows = c.execute(
            "SELECT substr(cree_le,1,10) AS j, COUNT(*) AS n, COUNT(DISTINCT ip_hash) AS u "
            "FROM visites GROUP BY j ORDER BY j DESC LIMIT 14"
        ).fetchall()
        par_jour = [dict(r) for r in rows]
        rows2 = c.execute(
            "SELECT COALESCE(NULLIF(source,''),'direct') AS s, COUNT(*) AS n, "
            "COUNT(DISTINCT ip_hash) AS u FROM visites GROUP BY s ORDER BY n DESC"
        ).fetchall()
        par_source = [dict(r) for r in rows2]
    return {
        "total": total, "uniques": uniques,
        "visites_auj": visites_auj, "uniques_auj": uniques_auj,
        "essais": essais, "impressions": impressions,
        "feuilles": feuilles, "commandes": commandes,
        "par_jour": par_jour, "par_source": par_source
    }


if __name__ == "__main__":
    init_db()
    init_machines(4)
    print("Base de données initialisée :", DB_PATH)
    print("Machines :", len(lister_machines()))
