# -*- coding: utf-8 -*-
"""Auto-tests des garde-fous : anti-doublon, exclusions, immuabilite.

S'execute dans un dossier temporaire : n'ecrit jamais dans les vrais journaux.
    python3 outils/test_journal.py
"""
import json, os, shutil, sys, tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import config as C

BAC = tempfile.mkdtemp(prefix="test_journal_")
C.RACINE = BAC
C.DOSSIER_COMMUN = os.path.join(BAC, "00_COMMUN")
os.makedirs(C.DOSSIER_COMMUN, exist_ok=True)

import journal as J
J.C = C
J.FICHIER_EXCLUSION = os.path.join(C.DOSSIER_COMMUN, "liste_exclusion.csv")

CAMP = "01_ENDOCRINOLOGUES"
ok_total = True

def verif(libelle, condition, detail=""):
    global ok_total
    ok_total = ok_total and condition
    print("  %s  %s%s" % ("OK    " if condition else "ECHEC ", libelle,
                          ("  -> " + detail) if detail and not condition else ""))

print("1. Statut non-EXACT : envoi refuse")
for statut in ("NON_VERIFIE", "A_CONFIRMER", "AMBIGU", "ABSENT", "DEJA_CONTACTE"):
    autorise, motif = J.peut_envoyer(CAMP, "10001111111", "ALPHA", "Jean", statut)
    verif("statut %-14s refuse" % statut, not autorise, motif)

print("2. Statut EXACT, professionnel vierge : envoi autorise")
autorise, motif = J.peut_envoyer(CAMP, "10001111111", "ALPHA", "Jean", "EXACT")
verif("autorisation accordee", autorise, motif)

print("3. Envoi sans confirmation d'interface : refuse")
try:
    J.consigner_envoi(CAMP, "10001111111", "ALPHA", "Jean", "p/1", "v1", "Bonjour", "")
    verif("exception levee", False)
except ValueError:
    verif("exception levee", True)

print("4. Verrou de version : texte non valide -> envoi impossible")
TEXTE = "Bonjour Docteur,\nLigne 2."
try:
    J.consigner_envoi(CAMP, "10001111111", "ALPHA", "Jean", "profil/1", "ENDO-v1",
                      TEXTE, "confirme")
    verif("envoi refuse sans modele valide", False)
except ValueError as exc:
    verif("envoi refuse sans modele valide", "non enregistree" in str(exc))

# Enregistrement d'une version validee dans le bac a sable
import json as _json
from datetime import datetime as _dt
os.makedirs(os.path.join(C.DOSSIER_COMMUN, "modeles"), exist_ok=True)
with open(os.path.join(C.DOSSIER_COMMUN, "modeles", "registre_modeles.jsonl"),
          "w", encoding="utf-8") as f:
    f.write(_json.dumps({"campagne": CAMP, "version": "ENDO-v1",
                         "empreinte_texte": J.empreinte_texte(TEXTE),
                         "horodatage": _dt.now().isoformat()}) + "\n")

try:
    J.consigner_envoi(CAMP, "10001111111", "ALPHA", "Jean", "profil/1", "ENDO-v1",
                      TEXTE + " texte modifie", "confirme")
    verif("envoi refuse si le texte differe de la version validee", False)
except ValueError as exc:
    verif("envoi refuse si le texte differe de la version validee",
          "mot pour mot" in str(exc))

print("5. Envoi consigne apres confirmation reelle")
e = J.consigner_envoi(CAMP, "10001111111", "ALPHA", "Jean", "profil/1", "ENDO-v1",
                      TEXTE, "Message affiche dans le fil, horodate 10:12")
verif("entree ecrite et chainee", e["rang"] == 1 and e["empreinte_precedente"] == J.GENESE)

print("6. Anti-doublon : meme RPPS")
autorise, motif = J.peut_envoyer(CAMP, "10001111111", "ALPHA", "Jean", "EXACT")
verif("second envoi refuse (RPPS)", not autorise, motif)

print("7. Anti-doublon : autre campagne, autre compte Connect, RPPS inconnu")
autorise, motif = J.peut_envoyer("03_RHUMATOLOGUES", "", "Alpha", "JEAN", "EXACT", "profil/2")
verif("refuse par rapprochement de nom", not autorise, motif)
autorise, motif = J.peut_envoyer("03_RHUMATOLOGUES", "99999999999", "Autre", "Nom",
                                 "EXACT", "profil/1")
verif("refuse par profil Connect identique", not autorise, motif)

print("8. Exclusion nominative durable")
J.ajouter_exclusion("10004444444", "DELTA", "Paul", "Demande expresse du Dr Benjoar")
autorise, motif = J.peut_envoyer("04_ORTHO_TRAUMATOLOGIE", "10004444444", "DELTA", "Paul", "EXACT")
verif("exclusion respectee", not autorise, motif)
autorise, _ = J.peut_envoyer("04_ORTHO_TRAUMATOLOGIE", "", "Delta", "PAUL", "EXACT")
verif("exclusion respectee sans RPPS", not autorise)

print("9. Immuabilite : detection d'une reecriture a posteriori")
ok, msg = J.verifier_integrite(CAMP, "envois")
verif("chaine intacte avant alteration", ok, msg)
chemin = J.chemin_journal(CAMP, "envois")
entrees = [json.loads(l) for l in open(chemin, encoding="utf-8") if l.strip()]
entrees[0]["version_message"] = "ENDO-v2"   # simulation d'une reecriture du modele
with open(chemin, "w", encoding="utf-8") as f:
    for x in entrees:
        f.write(json.dumps(x, ensure_ascii=False, sort_keys=True) + "\n")
ok, msg = J.verifier_integrite(CAMP, "envois")
verif("alteration detectee", not ok, msg)
print("     message d'alerte : %s" % msg)

shutil.rmtree(BAC, ignore_errors=True)
print("\n%s" % ("TOUS LES AUTO-TESTS PASSENT." if ok_total else "AU MOINS UN AUTO-TEST A ECHOUE."))
sys.exit(0 if ok_total else 1)
