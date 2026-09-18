# Campagnes Doctolib Connect — Centre d'Imagerie Médicale Manin-Crimée

Quatre campagnes professionnelles distinctes, Île-de-France (75, 77, 78, 91,
92, 93, 94, 95) : endocrinologues ; ORL et chirurgiens cervico-faciaux ;
rhumatologues ; chirurgiens orthopédistes et traumatologues.

> ## État au 2026-09-18
>
> **0 professionnel recensé, 0 vérifié, 0 message envoyé.**
>
> L'accès réseau aux données RPPS et l'accès à Doctolib Connect sont tous deux
> refusés dans cet environnement : **voir `00_COMMUN/BLOCAGES.md`**, qui décrit
> précisément le blocage et les deux façons de le lever.
>
> L'outillage, les référentiels, les garde-fous et les quatre projets de message
> sont en place et testés. Ils n'attendent que les données et votre validation.

---

## Organisation

```
00_COMMUN/           référentiels partagés par les quatre campagnes
  BLOCAGES.md                        ← à lire en premier
  ETAT_AVANCEMENT.md                 mémoire du projet, reprise sans perte
  socle_factuel_centre.md            ce qu'on a le droit d'écrire sur le centre
  referentiel_statuts.md             vocabulaire fermé des statuts Connect
  procedure_verification_connect.md  mode opératoire de la vérification
  liste_exclusion.csv                exclusions nominatives, durables
  bilan_global.md                    chiffres consolidés (recalculés)
  modeles/                           registre des textes validés

01_ENDOCRINOLOGUES/  02_ORL_CHIR_CERVICO_FACIALE/
03_RHUMATOLOGUES/    04_ORTHO_TRAUMATOLOGIE/
  base_rpps_*.xlsx                   base consolidée + statut Connect
  suivi_connect_*.csv                suivi des recherches
  ambiguites_a_verifier.csv          cas à trancher par un humain
  bilan_chiffre.md                   bilan de la campagne
  projet_message.md                  texte à valider avant tout envoi
  journaux/journal_recherches.jsonl  journal des recherches (append-only)
  journaux/journal_envois.jsonl      journal des envois (append-only, chaîné)

donnees_source/      y déposer l'extraction RPPS (vide aujourd'hui)
outils/              chaîne de traitement
```

## Chaîne de traitement

```bash
# 1. Constituer et dédoublonner les bases (après dépôt du fichier ANS)
python3 outils/01_extraction_rpps.py --source donnees_source/<fichier> --date-source AAAA-MM-JJ

#    Contrôle préalable recommandé : quels libellés de spécialité seront captés ?
python3 outils/01_extraction_rpps.py --source donnees_source/<fichier> --audit-libelles

# 2. Recalculer tous les chiffres depuis le disque
python3 outils/02_bilan.py

# 3. Enregistrer un texte validé par le Dr Benjoar (préalable à tout envoi)
python3 outils/03_valider_modele.py --enregistrer --campagne 03_RHUMATOLOGUES \
    --version RHUM-v1 --fichier 00_COMMUN/modeles/RHUM-v1.txt \
    --preuve "validation écrite du ..."

# 4. Vérifier les garde-fous et l'intégrité des journaux
python3 outils/test_journal.py
python3 outils/journal.py
```

## Garde-fous (tous vérifiés par `outils/test_journal.py`)

Un envoi est refusé **programmatiquement** si l'une de ces conditions n'est pas
remplie :

1. le statut n'est pas `EXACT` ;
2. le professionnel figure sur la liste d'exclusion — par RPPS **ou** par nom ;
3. il a déjà été contacté — y compris dans **une autre campagne**, via **un autre
   compte Connect** ou **un autre lieu d'exercice** ;
4. la version du message n'a pas été enregistrée comme validée ;
5. le texte ne correspond pas **mot pour mot** à la version validée ;
6. l'interface Doctolib n'a pas confirmé l'envoi.

Le journal des envois est chaîné par empreinte : toute réécriture a posteriori
est détectée. Modifier un modèle plus tard ne réécrit jamais l'historique des
textes déjà envoyés.

## Règles permanentes

- **Doctolib Connect uniquement.** Aucune campagne LinkedIn.
- **Aucun « cas patient ».** Messagerie professionnelle et recherche de
  professionnels exclusivement.
- **Aucun envoi avant validation écrite** du texte par le Dr Benjoar.
- **En cas d'ambiguïté, on n'envoie rien** : on documente les candidats trouvés
  et la raison du doute pour vérification humaine.
- **Aucune activité médicale inventée** : seul `00_COMMUN/socle_factuel_centre.md`
  fait foi, et il distingue le vérifié du non vérifié.
- **Ne jamais déclarer** qu'un message a été lu, accepté, ou qu'une mise en
  relation a réussi, sans confirmation explicite de l'interface.
- **Messages multilignes : collage en texte brut, en une seule opération.**
