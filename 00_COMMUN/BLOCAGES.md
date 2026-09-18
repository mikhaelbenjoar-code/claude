# Blocages — à lire en premier

Constaté le 2026-09-18. Deux blocages empêchent aujourd'hui de produire les
listes et de faire les vérifications. Ils sont **externes** au projet : tout le
reste est en place et attend uniquement la levée de ces blocages.

---

## Blocage 1 — Accès réseau aux données RPPS refusé

La politique d'egress de cet environnement refuse la connexion (403 sur le
tunnel CONNECT) vers **tous** les hôtes portant les données publiques :

| Hôte | Rôle | Résultat |
|---|---|---|
| `annuaire.sante.fr` | Annuaire Santé (ANS) | 403 — bloqué |
| `service.annuaire.sante.fr` | Webservice d'extraction PS_LibreAcces | 403 — bloqué |
| `www.data.gouv.fr` | Miroir open data de l'extraction | 403 — bloqué |
| `industriels.esante.gouv.fr` | Spécification des fichiers (DSFT) | 403 — bloqué |

Vérifié par `curl` **et** par l'outil de récupération web, avec le même refus.
La recherche web fonctionne (elle s'exécute côté serveur) mais ne permet pas de
télécharger un fichier : elle renvoie des descriptions, pas les données.

**Conséquence : aucune base RPPS n'a pu être constituée.** Les quatre classeurs
Excel n'existent donc pas encore, et tous les compteurs du bilan sont à zéro.

**Ce chiffre « 0 » signifie « rien n'a été collecté », et non « aucun
professionnel ne correspond ».**

### Deux façons de lever ce blocage

**A. Autoriser les hôtes** (à faire par un administrateur de l'environnement) :
`annuaire.sante.fr`, `service.annuaire.sante.fr`, `www.data.gouv.fr`.

**B. Fournir le fichier manuellement** — sans rien changer à l'environnement.
Télécharger l'extraction publique « Annuaire Santé — Extraction des PS autorisés
à exercer » depuis `annuaire.sante.fr` (rubrique *Extractions publiques*, accès
libre, mise à jour quotidienne), puis déposer le ZIP ou le fichier
`PS_LibreAcces_Personne_activite_*.txt` dans `donnees_source/`.

La chaîne de traitement est prête et testée. Une seule commande suffit ensuite :

```bash
python3 outils/01_extraction_rpps.py --source donnees_source/<fichier> --date-source AAAA-MM-JJ
```

---

## Blocage 2 — Aucun accès à Doctolib Connect

Aucun accès au compte professionnel n'est disponible dans cette session :

- `www.doctolib.fr` est **bloqué par la même politique d'egress** (403) ;
- aucune session authentifiée, aucun jeton, aucun accès navigateur au compte
  professionnel n'a été fourni ;
- un navigateur est bien installé localement, mais il resterait soumis au même
  blocage réseau.

**Conséquence : aucune vérification Connect n'a été réalisée.** Aucun
professionnel n'a été recherché, aucun statut n'a été attribué. Aucun « cas
patient » n'a été créé — aucune action n'a eu lieu sur Doctolib.

**Aucun message n'a été envoyé. Aucun envoi n'est possible en l'état**, et ce
indépendamment du blocage : les textes ne sont pas encore validés.

### Point de méthode à trancher avant de lever ce blocage

La vérification sur Connect suppose que l'assistant opère le compte
professionnel du centre. Merci d'indiquer la modalité retenue :

1. **Vérification manuelle par le centre** — les procédures et les fichiers de
   suivi sont prêts à être remplis à la main ; c'est la voie la plus simple et
   la plus sûre, et elle ne dépend d'aucun déblocage réseau.
2. **Vérification assistée** — nécessite un accès explicitement autorisé au
   compte, et la levée du blocage réseau.

Cette question relève de vous, pas de l'outil : opérer un compte professionnel
de santé engage votre responsabilité.

---

## Ce que ces blocages n'empêchent pas

L'outillage, les référentiels, les garde-fous et les quatre projets de message
sont en place, testés, et n'attendent que les données. Voir
`00_COMMUN/ETAT_AVANCEMENT.md`.
