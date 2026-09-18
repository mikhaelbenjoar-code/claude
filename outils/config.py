# -*- coding: utf-8 -*-
"""Configuration partagee des quatre campagnes Doctolib Connect.

Source de verite unique : specialites, departements, statuts, colonnes.
Toute modification ici se propage aux scripts d'extraction, de journalisation
et de bilan.
"""

from __future__ import annotations

import os

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOSSIER_SOURCE = os.path.join(RACINE, "donnees_source")
DOSSIER_COMMUN = os.path.join(RACINE, "00_COMMUN")

# --- Perimetre geographique : Ile-de-France -------------------------------
DEPARTEMENTS_IDF = {
    "75": "Paris",
    "77": "Seine-et-Marne",
    "78": "Yvelines",
    "91": "Essonne",
    "92": "Hauts-de-Seine",
    "93": "Seine-Saint-Denis",
    "94": "Val-de-Marne",
    "95": "Val-d'Oise",
}

# --- Les quatre campagnes -------------------------------------------------
# `motifs` : expressions regulieres appliquees au "Libelle savoir-faire" du
# referentiel RPPS, en minuscules et sans accents (voir normaliser()).
# Le filet est volontairement large ; le script produit un audit des libelles
# reellement rencontres, a valider par un humain avant exploitation.
CAMPAGNES = {
    "01_ENDOCRINOLOGUES": {
        "libelle": "Endocrinologues",
        "libelle_long": "Endocrinologie - diabetologie - nutrition",
        "motifs": [
            r"endocrinolog",
            r"diabetolog",
            r"\bnutrition\b",
            r"maladies metaboliques",
        ],
        "motifs_exclusion": [
            r"pediatr",  # endocrinologie pediatrique : hors cible par defaut
        ],
    },
    "02_ORL_CHIR_CERVICO_FACIALE": {
        "libelle": "ORL et chirurgiens cervico-faciaux",
        "libelle_long": "Oto-rhino-laryngologie et chirurgie cervico-faciale",
        "motifs": [
            r"oto.?rhino.?laryngolog",
            r"\borl\b",
            r"cervico.?facial",
        ],
        "motifs_exclusion": [],
    },
    "03_RHUMATOLOGUES": {
        "libelle": "Rhumatologues",
        "libelle_long": "Rhumatologie",
        "motifs": [
            r"rhumatolog",
        ],
        "motifs_exclusion": [],
    },
    "04_ORTHO_TRAUMATOLOGIE": {
        "libelle": "Chirurgiens orthopedistes et traumatologues",
        "libelle_long": "Chirurgie orthopedique et traumatologie",
        "motifs": [
            r"orthoped",
            r"traumatolog",
        ],
        "motifs_exclusion": [
            r"pediatr",
        ],
    },
}

# --- Statuts Doctolib Connect (vocabulaire ferme) -------------------------
# Toute valeur hors de cette liste est refusee par les scripts.
STATUTS = [
    "NON_VERIFIE",          # pas encore recherche sur Connect
    "EXACT",                # correspondance exacte, prete pour un futur envoi
    "A_CONFIRMER",          # profil trouve, specialite ou identite a confirmer
    "AMBIGU",               # resultat ambigu / homonyme : aucun envoi
    "ABSENT",               # apparemment absent ou n'utilisant pas Connect
    "DEJA_CONTACTE",        # ne pas solliciter a nouveau
    "EXCLU",                # exclusion nominative demandee
]

STATUTS_ENVOI_AUTORISE = {"EXACT"}  # seul statut ouvrant droit a un envoi

DESCRIPTION_STATUTS = {
    "NON_VERIFIE": "Pas encore recherche dans l'annuaire Doctolib Connect.",
    "EXACT": "Identite, specialite et lieu concordants. Pret pour un futur envoi apres validation du texte.",
    "A_CONFIRMER": "Profil trouve mais specialite ou identite insuffisamment certaine. Aucun envoi.",
    "AMBIGU": "Plusieurs candidats / homonyme non departageable. Aucun envoi, verification humaine requise.",
    "ABSENT": "Aucun profil trouve dans l'annuaire Connect, ou professionnel n'utilisant pas Connect.",
    "DEJA_CONTACTE": "A deja recu une presentation du centre. Ne pas solliciter a nouveau.",
    "EXCLU": "Exclusion nominative demandee. Ne jamais contacter.",
}

# --- Schema de la base RPPS consolidee ------------------------------------
# (libelle de colonne, largeur Excel, commentaire)
COLONNES_BASE = [
    ("RPPS",                     14, "Identifiant national du professionnel (cle de deduplication primaire)"),
    ("Nom",                      20, "Nom d'exercice"),
    ("Prenom",                   18, "Prenom d'exercice"),
    ("Nom_usage_variantes",      26, "Noms d'usage / variantes rapprochees lors de la deduplication"),
    ("Civilite",                  9, "Civilite d'exercice"),
    ("Profession",               22, "Libelle profession (RPPS)"),
    ("Specialite_exacte",        34, "Libelle savoir-faire RPPS retenu"),
    ("Surspecialite",            28, "Savoir-faire complementaires declares"),
    ("Mode_exercice",            16, "Liberal / salarie / mixte, si disponible"),
    ("Departement",              12, "Code departement du lieu principal"),
    ("Departement_libelle",      18, ""),
    ("Ville",                    20, "Commune du lieu principal"),
    ("Code_postal",              12, ""),
    ("Adresse",                  42, "Adresse du lieu principal"),
    ("Etablissement_cabinet",    34, "Raison sociale / enseigne du lieu principal"),
    ("Telephone_structure",      18, "Telephone public de la structure"),
    ("Email_professionnel",      30, "Adresse e-mail professionnelle publique (RPPS)"),
    ("Nb_lieux_exercice",        10, "Nombre de lieux d'exercice regroupes sur cette ligne"),
    ("Liste_lieux_exercice",     70, "Tous les lieux, separes par ' | '"),
    ("Source",                   28, "Fichier source precis"),
    ("Date_source",              14, "Date de l'extraction source (AAAA-MM-JJ)"),
    ("Statut_Connect",           18, "Voir 00_COMMUN/referentiel_statuts.md"),
    ("Connect_profil_url",       34, "URL / identifiant du profil Connect retenu"),
    ("Connect_date_verification",16, "Date de la verification (AAAA-MM-JJ)"),
    ("Connect_candidats",        40, "Candidats trouves si ambiguite"),
    ("Motif_doute",              40, "Raison de l'ambiguite ou du non-envoi"),
    ("Message_envoye",           14, "OUI / NON - renseigne uniquement par le journal d'envois"),
    ("Date_envoi",               14, "AAAA-MM-JJ, depuis le journal d'envois"),
    ("Version_message_envoye",   20, "Identifiant de version du texte reellement envoye"),
    ("Commentaire",              40, ""),
]

# --- Colonnes du fichier de suivi des recherches Connect ------------------
COLONNES_SUIVI = [
    "horodatage", "rpps", "nom", "prenom", "specialite_cible",
    "requete_effectuee", "nb_resultats", "candidats", "statut_retenu",
    "profil_retenu", "motif", "operateur",
]

# --- Colonnes du journal d'envois (immuable) ------------------------------
COLONNES_ENVOI = [
    "horodatage", "rpps", "nom", "prenom", "profil_connect",
    "version_message", "empreinte_texte", "confirmation_interface", "operateur",
]


def normaliser(texte: str) -> str:
    """Minuscules, sans accents, espaces normalises. Pour comparer des libelles."""
    import unicodedata
    if texte is None:
        return ""
    t = unicodedata.normalize("NFD", str(texte))
    t = "".join(c for c in t if unicodedata.category(c) != "Mn")
    return " ".join(t.lower().split())
