# -*- coding: utf-8 -*-
"""Enregistrement des oppositions (« STOP ») et des exclusions nominatives.

Le droit d opposition annonce en pied de message doit etre effectif et
persistant. Cet outil inscrit le professionnel dans la liste d exclusion
durable et partagee par les quatre campagnes : il ne sera plus jamais retenu
par 04_preparer_envois.py, quelle que soit la campagne.

    python3 outils/06_opposition.py --rpps 10001234567 --nom DUPONT --prenom Jean \
        --motif "opposition exprimee le 2026-09-20 par reponse STOP"
    python3 outils/06_opposition.py --lister
"""
from __future__ import annotations

import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import config as C
import journal as J


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--rpps", default="")
    p.add_argument("--nom", default="")
    p.add_argument("--prenom", default="")
    p.add_argument("--motif", default="")
    p.add_argument("--demande-par", default="le professionnel lui-meme")
    p.add_argument("--lister", action="store_true")
    a = p.parse_args()

    if a.lister:
        exclusions = J.charger_exclusions()
        if not exclusions:
            print("Aucune exclusion enregistree.")
            return 0
        print("%d cle(s) d exclusion enregistree(s) :" % len(exclusions))
        for cle, motif in sorted(exclusions.items()):
            print("  %-28s %s" % (cle, motif))
        return 0

    if not a.rpps and not (a.nom and a.prenom):
        print("ERREUR : fournir --rpps, ou --nom et --prenom.", file=sys.stderr)
        return 2
    if not a.motif.strip():
        print("ERREUR : --motif est obligatoire (trace de la demande).", file=sys.stderr)
        return 2

    J.ajouter_exclusion(a.rpps, a.nom, a.prenom, a.motif, a.demande_par)
    print("Exclusion enregistree : %s %s (RPPS %s)"
          % (a.nom or "?", a.prenom or "", a.rpps or "non renseigne"))
    print("Ce professionnel est desormais ecarte de TOUTES les campagnes.")

    autorise, motif = J.peut_envoyer("01_ENDOCRINOLOGUES", a.rpps, a.nom, a.prenom, "EXACT")
    print("\nVerification immediate : envoi %s" % ("AUTORISE — ANOMALIE !" if autorise else "refuse."))
    if not autorise:
        print("  motif : %s" % motif)
    return 0 if not autorise else 1


if __name__ == "__main__":
    sys.exit(main())
