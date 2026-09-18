# Conformité : ce qu'il faut vérifier avant tout envoi

Recherche du 2026-09-18, menée sur quatre angles indépendants, chacun soumis à
un agent de réfutation adversariale.

> ## Réserve méthodologique, à lire avant tout le reste
>
> **Aucune source primaire n'a pu être lue directement.** La politique réseau de
> cet environnement a bloqué la lecture de doctolib.fr, Légifrance, data.gouv.fr,
> esante.gouv.fr — et même Wikipédia. Tout ce qui suit provient d'extraits de
> moteur de recherche, donc de seconde main.
>
> Trois des quatre angles sont cotés **fiabilité partielle**. Rien ici ne doit
> être opposé à l'Ordre, à la CNIL ou à Doctolib sans revérification à la source.
> Ce document sert à **savoir quoi vérifier**, pas à trancher.

---

## 1. Aucune voie officielle d'automatisation *(fiabilité : solide)*

Il n'existe aucune trace publique d'un accès programmatique officiel à la
messagerie Doctolib Connect.

- L'API Doctolib est fermée, réservée à des partenaires accrédités au cas par cas.
  Son périmètre public documenté : prise de rendez-vous, agenda, synchronisation
  avec les logiciels métier / DPI. **Jamais la messagerie entre praticiens.**
- La seule API mentionnée côté Connect est une API **SCIM** — du provisionnement
  d'utilisateurs, pas de l'envoi de messages.
- Les **« groupes de diffusion »** existent nativement, mais sont réservés à
  l'administrateur d'un réseau « Connect pour les organisations » et ne touchent
  que les **membres de ce réseau**. Inutilisable pour des correspondants externes.

Indice le plus parlant : les prestataires qui vendent de l'« automatisation
Doctolib » reconnaissent eux-mêmes passer par du scraping et de la RPA.

*Nuance apportée par la réfutation :* l'argument « le chiffrement de bout en bout
rend l'automatisation impossible » est trop fort — il la déplace côté client, il
ne l'interdit pas. La conclusion tient par l'absence de point d'entrée publié,
pas par la cryptographie.

## 2. Conditions d'utilisation Doctolib *(fiabilité : partielle — CGU non lues)*

Le texte des CGU n'a **pas** pu être lu. Sous cette réserve, trois éléments
convergent :

- les conditions de Connect imposeraient de ne pas communiquer ses identifiants
  à un tiers, le titulaire restant seul responsable de tout usage du compte ;
- Doctolib documente publiquement une détection des « comportements anormaux »
  et de l'« utilisation robotisée non autorisée », avec suspension ou résiliation ;
- il n'existe pas d'API ouverte permettant un envoi programmatique légitime.

**Question non tranchée, et distincte de l'automatisation :** les CGU
autorisent-elles l'usage de l'annuaire Connect à des fins de prospection
confraternelle, **même manuelle** ? Personne n'a pu le vérifier. À demander par
écrit à Doctolib.

## 3. Déontologie médicale *(fiabilité : partielle)*

### Le code a été refondu le 27 juillet 2026

**Décret n° 2026-691 du 27 juillet 2026** (JO du 29, en vigueur le 30) : une
soixantaine d'articles modifiés ou réécrits, « clientèle » remplacé par
« patientèle », renumérotations (R.4127-81 deviendrait R.4127-92), et création
d'un article nouveau — annoncé R.4127-13-1 — sur les **outils numériques et
l'intelligence artificielle**, dont le contenu n'a pas pu être lu.

**Conséquence : aucun numéro d'article ne doit être cité sans revérification sur
Légifrance en version « en vigueur ».**

### Deux points de fond

- Le seul fondement textuel d'une communication du médecin **vers des
  professionnels de santé** serait le **II de l'article R.4127-19-1**, limité aux
  informations *scientifiquement étayées, à finalité éducative ou sanitaire* — ce
  qui **ne couvre pas** un message de présentation d'un plateau technique.
  (L'article R.4127-19-2, parfois cité, ne concerne pas ce sujet : il vise les
  praticiens européens en accès partiel.)
- Le CNOM a considéré, dans un rapport de **2016**, que le **caractère répétitif**
  d'envois — papier ou électroniques — leur donne un caractère de démarchage
  répréhensible. Ce rapport est antérieur à la réforme de 2020 et son statut
  actuel est incertain, mais le critère mérite d'être connu avant d'écrire à des
  centaines de confrères.

### Point structurant à trancher en premier

**Le centre est-il juridiquement un « centre de santé » au sens de L.6323-1 CSP ?**

- **Si oui** : l'article **L.6323-1-9**, dans sa rédaction issue de la **loi
  n° 2023-378 du 19 mai 2023**, interdit « toute forme de publicité en faveur des
  centres de santé, **ou incitant à recourir à des actes ou à des prestations
  délivrés par ces derniers** ». Cette rédaction est plus large que celle validée
  par le Conseil constitutionnel en 2022 (décision n° 2022-998 QPC). La marge
  serait alors très réduite.
- **Si non** (SELARL, SCM, exercice libéral) : c'est la déontologie des médecins
  associés qui s'applique, et une marge existe.

**Cette question conditionne tout le reste et doit être tranchée avant d'écrire
la moindre ligne.** Vous seul pouvez y répondre.

## 4. RGPD et réutilisation du RPPS *(fiabilité : partielle)*

### Le constat qui change tout : pas de coordonnées dans l'open data

L'extraction en libre accès **ne contient aucune coordonnée de contact
personnelle**. Elle fournit le numéro RPPS, l'identité, la profession, les
qualifications et les **coordonnées de la structure** d'exercice.

Les « coordonnées de correspondance » relèvent des données à **accès restreint**,
réservées par l'arrêté RPPS à des catégories limitativement définies — agences
sanitaires, GRADeS, services de l'État. **Un centre d'imagerie privé n'y figure
pas.**

Le fichier open data permet donc d'**identifier** les correspondants, pas de les
**joindre**. C'est précisément pourquoi le canal de contact — Connect — devient
la question centrale, et non un détail d'exécution.

### MSSanté n'est pas une solution de repli

Les adresses MSSanté font l'objet d'une extraction distincte, mais cet espace de
confiance a pour finalité l'échange de données de santé **dans le cadre de la
prise en charge d'un patient**. Un message de présentation y est hors finalité :
dans un espace défini par sa finalité, l'absence d'interdiction expresse ne vaut
pas autorisation.

### Ce qui est licite, et à quelles conditions

Constituer le fichier est **en principe licite** : les extractions sont diffusées
en open data et le CRPA autorise la réutilisation, y compris commerciale. Mais
l'ouverture de la donnée n'est **jamais** une autorisation de traitement.

Si la démarche est engagée, sont requis :

| Obligation | Détail |
|---|---|
| Base légale | Intérêt légitime, avec **test de mise en balance écrit** |
| Information (art. 14 RGPD) | Dès le **premier message** : collecte indirecte, **source RPPS nommée** |
| Droit d'opposition | Moyen **simple et gratuit** dans **chaque** message, + liste de suppression persistante |
| Identification | Émetteur clairement identifiable |
| Conservation | 3 ans à compter du dernier contact émanant de la personne |
| Registre | Article 30 RGPD — la dispense « moins de 250 personnes » ne joue pas pour un traitement non occasionnel |
| Source (licence) | Mention du concédant (ANS / Annuaire Santé) et de la date de mise à jour |
| Fraîcheur | Rafraîchissement régulier ; les extractions sont publiées quotidiennement |

La CNIL admet que la prospection visant des professionnels repose sur l'intérêt
légitime sans consentement exprès, à condition que l'objet soit en rapport avec
leur profession et qu'ils aient été informés et mis en mesure de s'opposer.
*Faille assumée du raisonnement :* la formulation CNIL conditionne cette dispense
à une information délivrée « au moment de la collecte de l'adresse ». Ici
l'adresse ne vient pas du médecin. Le raccordement à l'article 14 est raisonnable
mais constitue une **inférence**, pas une position CNIL vérifiée telle quelle.

### Charte RPPS : non lue

La **Charte de réutilisation des données contenues dans le RPPS** existe
(référencée `Charte_utilisation_RPPS_V5_du_02072020`). Elle n'a **pas** pu être
ouverte. Aucune clause interdisant la prospection n'a été trouvée — mais
l'absence de preuve d'interdiction n'est pas une preuve d'absence d'interdiction.

Aucune sanction CNIL portant spécifiquement sur un fichier de prospection issu du
RPPS n'a été trouvée.

---

## Les quatre vérifications à obtenir par écrit, avant tout envoi

1. **Forme juridique du centre** — « centre de santé » au sens de L.6323-1 CSP ?
   Détermine si L.6323-1-9 s'applique. *À trancher en premier.*
2. **Charte de réutilisation RPPS** — auprès du support ANS : la prospection
   confraternelle est-elle un usage admis ?
3. **CGU Doctolib Connect** — auprès de Doctolib : l'annuaire peut-il servir à une
   prise de contact confraternelle non sollicitée, même manuelle ?
4. **Position ordinale** — auprès du conseil départemental de l'Ordre : un
   courrier de présentation de plateau technique à des correspondants est-il admis,
   et sous quelles conditions de forme et de répétition ?

Ces quatre points ne relèvent pas de l'outillage. Ils relèvent de vous, et
idéalement de votre conseil.
