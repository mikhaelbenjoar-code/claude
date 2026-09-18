# Automatiser la connexion à Doctolib et les envois ?

Question posée le 2026-09-18. Réponse : **non**, pour trois raisons d'ordres
différents, qu'il faut distinguer parce qu'elles ne se lèvent pas de la même façon.

---

## 1. Impossible techniquement dans cet environnement

Vérifié le 2026-09-18 :

| Hôte | Résultat |
|---|---|
| `www.doctolib.fr` | injoignable — refus au niveau du tunnel réseau |
| `pro.doctolib.fr` | injoignable — idem |
| `partners.doctolib.fr` | injoignable — idem |

Un navigateur est bien installé localement, mais il emprunterait le même réseau
et se heurterait au même refus. Aucun identifiant Doctolib n'est présent dans
l'environnement.

Ce point est **contingent** : un administrateur peut lever le blocage réseau,
et des identifiants peuvent être fournis. Les deux points suivants, eux, ne se
lèvent pas par un réglage technique.

## 2. Nécessiterait de me confier vos identifiants professionnels

Automatiser des envois suppose d'opérer votre compte professionnel de santé en
votre nom. Cela transfère à un outil des actions qui engagent votre
responsabilité de praticien, sur un compte qui donne accès à des données de
santé. Confier des identifiants de compte professionnel à un tiers est en outre
très généralement contraire aux conditions d'utilisation des plateformes de
santé.

Si vous souhaitez malgré tout aller dans cette direction, c'est une décision qui
vous appartient — mais elle doit être prise en connaissance de cause, pas comme
un simple réglage technique, et je vous le signalerais à nouveau.

## 3. Le sujet dépasse la technique — et la recherche l'a confirmé

Une recherche vérifiée (quatre angles, réfutation adversariale) a été menée le
2026-09-18. Conclusions détaillées et réserves dans **`00_COMMUN/CONFORMITE.md`**.
En résumé :

- **Aucune voie officielle d'automatisation n'existe** *(fiabilité : solide)*.
  L'API Doctolib est fermée et ne couvre pas la messagerie entre praticiens ; la
  seule API Connect identifiée est du provisionnement d'utilisateurs. Les
  prestataires qui vendent de l'« automatisation Doctolib » reconnaissent
  eux-mêmes passer par du scraping. Automatiser signifierait donc contourner,
  pas intégrer.
- **Doctolib documente une détection de l'« utilisation robotisée non
  autorisée »**, avec suspension ou résiliation possible du compte. Le risque
  n'est pas théorique : c'est votre compte professionnel.
- **Deux questions peuvent remettre en cause la campagne entière**, bien avant
  celle de l'automatisation — la forme juridique du centre, et la licéité du
  démarchage confraternel lui-même. Voir `CONFORMITE.md`.

Autrement dit : « non, on ne peut pas automatiser » est exact, mais insuffisant.
La licéité de la démarche doit être établie **même pour un envoi entièrement
manuel**.

## Ce qui est automatisé à la place

La chaîne automatise tout ce qui peut l'être sans opérer votre compte :

| Étape | Qui |
|---|---|
| Constituer et dédoublonner la base RPPS | **automatisé** |
| Sélectionner les destinataires autorisés | **automatisé** |
| Écarter exclusions, statuts non `EXACT`, déjà contactés | **automatisé** |
| Verrouiller le texte sur la version exactement validée | **automatisé** |
| Produire un fichier texte brut par destinataire, prêt au collage | **automatisé** |
| Ouvrir la conversation et **lire l'historique** | humain |
| Coller et envoyer | humain |
| **Lire ce que l'interface affiche réellement** | humain |
| Reverser les confirmations dans le journal immuable | **automatisé** |

Les trois gestes laissés à l'humain ne sont pas des oublis. Ce sont précisément
ceux où une machine se tromperait sans s'en apercevoir : envoyer à un homonyme,
écraser un échange existant, ou déclarer « envoyé » un message qui ne l'a pas été.

En pratique, l'opérateur n'a jamais à retaper un texte — donc jamais le risque
d'une saisie caractère par caractère qui enverrait chaque retour à la ligne en
message séparé. Il copie, il colle, il vérifie.

**Ordre de grandeur** : le facteur limitant n'est pas la frappe, c'est la
vérification d'identité sur Connect, qui doit de toute façon être faite par un
humain pour chaque praticien.
