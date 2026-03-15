# Wiseflow

**[中文](README.md) | [English](README_EN.md) | [日本語](README_JP.md) | [한국어](README_KR.md) | [Deutsch](README_DE.md) | [العربية](README_AR.md)**

🚀 **STEP INTO 5.x**

> 📌 **Vous cherchez la version 4.x ?** Le code original de la v4.30 et des versions antérieures est disponible sur la [branche `4.x`](https://github.com/TeamWiseFlow/wiseflow/tree/4.x).

```
« Ma vie a des limites, mais la connaissance n'en a point. Poursuivre l'illimité avec le limité — voilà qui est périlleux ! » — Zhuangzi, Chapitres intérieurs, Nourrir le principe vital
```

Wiseflow 4.x (y compris les versions précédentes) a permis d'atteindre de puissantes capacités d'acquisition de données dans des scénarios spécifiques grâce à une série de workflows précis, mais présentait encore des limitations significatives :

- 1. Incapacité à acquérir du contenu interactif (contenu qui n'apparaît qu'après un clic, en particulier dans les cas de chargement dynamique)
- 2. Limité au filtrage et à l'extraction d'informations, avec pratiquement aucune capacité de traitement en aval
- ……

Bien que nous nous soyons constamment efforcés d'améliorer ses fonctionnalités et d'étendre ses limites, le monde réel est complexe, tout comme l'internet. Les règles ne peuvent jamais être exhaustives, c'est pourquoi un workflow fixe ne peut jamais s'adapter à tous les scénarios. Ce n'est pas un problème de wiseflow — c'est un problème des logiciels traditionnels !

Cependant, les progrès fulgurants des Agents au cours de l'année écoulée nous ont montré la possibilité technique de simuler entièrement le comportement humain sur Internet grâce aux grands modèles de langage. L'apparition d'[openclaw](https://github.com/openclaw/openclaw) a renforcé davantage cette conviction.

Plus remarquable encore, grâce à nos expériences et explorations préliminaires, nous avons découvert que l'intégration des capacités d'acquisition de wiseflow dans openclaw sous forme de « plugins » résout parfaitement les deux limitations mentionnées ci-dessus.

https://github.com/user-attachments/assets/8d097b3b-f9ab-42eb-98bb-88af5d28b089

Il convient de noter que le système de plugins d'openclaw diffère considérablement de ce que nous comprenons traditionnellement par « plugins » (similaires aux plugins de Claude Code). Nous avons donc dû introduire le concept d'« add-on ». Pour être précis, wiseflow 5.x apparaîtra sous la forme d'un add-on openclaw. L'openclaw original ne dispose pas d'une architecture « add-on », mais en pratique, vous n'avez besoin que de quelques commandes shell simples pour effectuer cette « transformation ». Nous avons également préparé une version améliorée d'openclaw prête à l'emploi avec des configurations prédéfinies pour des scénarios commerciaux réels : [openclaw_for_business](https://github.com/TeamWiseFlow/openclaw_for_business). Vous pouvez simplement le cloner et extraire la release wiseflow dans le dossier add-on d'openclaw_for_business.

## ✨ Que gagnez-vous en installant wiseflow (supérieur à l'openclaw original) ?

### 1. Navigateur anti-détection, sans extensions de navigateur

Le patch-001 de wiseflow remplace le Playwright intégré d'openclaw par [Patchright](https://github.com/Kaliiiiiiiiii-Vinyzu/patchright) (un fork non détectable de Playwright), réduisant considérablement le risque que les navigateurs automatisés soient identifiés et bloqués par les sites cibles. Cela permet d'atteindre des capacités d'acquisition et d'opération web équivalentes, voire supérieures à celles d'une configuration relay, en utilisant uniquement un navigateur géré sans installer d'extension Chrome relay.

📥 *Nous avons évalué tous les principaux frameworks d'automatisation de navigateur disponibles, notamment nodriver, browser-use et agent-browser de Vercel. Nous pouvons confirmer que bien qu'ils fonctionnent tous via CDP et fournissent des profils persistants dédiés à openclaw, seul Patchright assure la suppression complète des empreintes CDP. En d'autres termes, même l'approche de connexion CDP la plus directe laisse des signatures détectables. Les autres frameworks sont conçus pour les tests automatisés, non pour l'acquisition de données, tandis que Patchright a été spécifiquement conçu pour l'acquisition. Étant essentiellement un patch de Playwright, il hérite de presque toutes ses API de haut niveau — le rendant nativement compatible avec openclaw sans nécessiter d'extensions ou de MCP supplémentaires.*

### 2. Mécanisme de récupération automatique des onglets

Lorsqu'un onglet cible est fermé ou perdu de manière inattendue lors d'une opération Agent, le système effectue automatiquement une récupération d'onglet basée sur des snapshots, garantissant que les tâches ne soient pas interrompues par une perte d'onglet.

### 3. Smart Search Skill

Remplace le `web_search` intégré d'openclaw par des capacités de recherche plus puissantes. Comparé à l'outil web search intégré d'origine, Smart Search présente trois avantages clés :

- **Entièrement gratuit, sans clé API** : Ne dépend d'aucune API de recherche tierce — coût zéro
- **Recherche en temps réel pour une actualité maximale** : Pilote directement le navigateur vers les pages cibles ou les grandes plateformes de médias sociaux (Weibo, Twitter/X, Facebook, etc.) pour récupérer immédiatement les contenus publiés récemment
- **Sources de recherche personnalisables** : Les utilisateurs peuvent librement spécifier leurs sources de recherche pour une récupération d'informations précise et ciblée

### 4. New Media Editor Crew (Agent IA préconfiguré)

Un agent IA de création de contenu pour les réseaux sociaux chinois prêt à l'emploi, spécialisé dans les principales plateformes chinoises comme Weibo, Xiaohongshu, Zhihu, Bilibili et Douyin.

**Capacités principales :**

- Recherche de sujets + analyse des tendances (Mode A)
- Expansion du brouillon + justification en ligne (Mode B)
- Après finalisation de l'article, appel automatique de [Wenyan](https://github.com/caol64/wenyan) pour le rendre en HTML style compte officiel WeChat, avec 7 thèmes intégrés
- Envoi direct vers la boîte de brouillons du compte officiel WeChat (Mode C, nécessite `WECHAT_APP_ID`/`WECHAT_APP_SECRET`)
- Support de génération d'images/vidéos IA ([SiliconFlow](https://www.siliconflow.com/) génération d'images/vidéos, nécessite `SILICONFLOW_API_KEY`)

## 🌟 Démarrage rapide

> **💡 Note sur les coûts API**
>
> wiseflow 5.x repose sur le workflow Agent d'openclaw, qui nécessite un accès à l'API LLM. Nous recommandons de préparer vos identifiants API à l'avance :
>
> - **Utilisateurs internationaux (recommandé)** : [SiliconFlow](https://www.siliconflow.com/) — des crédits gratuits sont disponibles après inscription, couvrant les coûts initiaux
> - **OpenAI / Anthropic et autres fournisseurs** : Toute API compatible fonctionne

Téléchargez le package intégré (qui inclut openclaw_for_business et le wiseflow addon) directement depuis les [Releases](https://github.com/TeamWiseFlow/wiseflow/releases) de ce dépôt.

1. Télécharger et extraire l'archive
2. Accéder au dossier extrait
3. Choisir le mode de démarrage :

   **Mode débogage** (démarrage unique, pour les tests et le développement) :
   ```bash
   ./scripts/dev.sh gateway
   ```

   **Mode production** (installation en tant que service système, pour un fonctionnement à long terme) :
   ```bash
   ./scripts/reinstall-daemon.sh
   ```

> **Configuration requise**
> - **Ubuntu 22.04** est recommandé
> - L'environnement **Windows WSL2** est pris en charge
> - **macOS** est pris en charge
> - L'exécution directe sur **Windows natif** n'est **pas prise en charge**

### [Alternative] Installation manuelle

> Note : Vous devez d'abord télécharger et déployer openclaw_for_business depuis : https://github.com/TeamWiseFlow/openclaw_for_business/releases

Copiez le dossier `wiseflow` de ce dépôt (pas le dépôt lui-même) dans le répertoire `addons/` d'openclaw_for_business :

```bash
# Option 1 : Cloner depuis le dépôt wiseflow
git clone https://github.com/TeamWiseFlow/wiseflow.git /tmp/wiseflow
cp -r /tmp/wiseflow/wiseflow <openclaw_for_business>/addons/wiseflow
```

Redémarrez openclaw_for_business après l'installation pour que les changements prennent effet.

## Structure des répertoires

```
wiseflow/                         # package addon (copier dans le répertoire addons/)
├── addon.json                    # Métadonnées
├── overrides.sh                  # pnpm overrides + désactiver web_search intégré
├── patches/
│   ├── 001-browser-tab-recovery.patch        # Patch de récupération d'onglets
│   ├── 002-disable-web-search-env-var.patch  # Désactiver web_search intégré (env var)
│   └── 003-act-field-validation.patch        # Patch de validation des champs ACT
├── skills/                       # Skills globaux (disponibles pour tous les Agents)
│   ├── browser-guide/SKILL.md    # Bonnes pratiques du navigateur (connexion/CAPTCHA/chargement différé, etc.)
│   ├── smart-search/SKILL.md     # Constructeur d'URL de recherche multi-plateforme (remplace web_search intégré)
│   └── rss-reader/               # Lecteur de flux RSS/Atom
│       ├── SKILL.md
│       ├── package.json
│       └── scripts/fetch-rss.mjs
└── crew/                         # Agents IA préconfigurés (modèles Crew)
    └── new-media-editor/         # New Media Editor (création de contenu social media chinois)
        ├── IDENTITY.md / SOUL.md / AGENTS.md / TOOLS.md / ...
        └── skills/               # Skills spécifiques au Crew
            ├── siliconflow-img-gen/   # Génération d'images IA (API SiliconFlow)
            ├── siliconflow-video-gen/ # Génération de vidéos IA (API SiliconFlow)
            └── wenyan-formatter/      # Markdown → HTML WeChat / envoi brouillon

docs/                             # Documentation technique (racine du dépôt)
├── anti-detection-research.md
└── more_powerful_search_skill/

scripts/                          # Scripts utilitaires (racine du dépôt)
└── generate-patch.sh

tests/                            # Cas de test et scripts (racine du dépôt)
├── README.md
└── run-managed-tests.mjs
```

## WiseFlow Pro est maintenant disponible !

Des capacités de scraping plus puissantes, un support plus complet des réseaux sociaux, avec interface graphique et package d'installation en un clic — aucun déploiement nécessaire !

https://github.com/user-attachments/assets/57f8569c-e20a-4564-a669-1200d56c5725

🔥 **La version Pro est en vente** : https://shouxiqingbaoguan.com/

🌹 Dès aujourd'hui, contribuez des PRs à la version open source de wiseflow (code, documentation et partage de cas d'utilisation réussis sont les bienvenus). Une fois acceptées, les contributeurs recevront une licence d'un an pour wiseflow Pro !

## 🛡️ Licence

Depuis la version 4.2, nous avons mis à jour notre licence open source. Veuillez consulter : [LICENSE](LICENSE)

Pour une coopération commerciale, veuillez contacter **Email : zm.zhao@foxmail.com**

## 📬 Contact

Pour toute question ou suggestion, n'hésitez pas à laisser un message via les [issues](https://github.com/TeamWiseFlow/wiseflow/issues).

🎉 wiseflow & OFB proposent désormais une **base de connaissances payante**, incluant des tutoriels d'installation pas à pas, des astuces d'application exclusives et un **groupe WeChat VIP** :

N'hésitez pas à ajouter « Keeper » sur WeChat Enterprise pour toute demande :

<img width="360" height="360" alt="wiseflow掌柜" src="https://github.com/user-attachments/assets/b013b3fd-546e-4176-b418-57bee419e761" />

🌹 L'open source demande beaucoup d'efforts — merci pour votre soutien !

## 🤝 wiseflow 5.x est construit sur les excellents projets open source suivants :

- Patchright (Version Python indétectable de la bibliothèque de test et d'automatisation Playwright) https://github.com/Kaliiiiiiiiii-Vinyzu/patchright-python
- Feedparser (Analyse de flux en Python) https://github.com/kurtmckee/feedparser
- SearXNG (un métamoteur de recherche internet gratuit qui agrège les résultats de divers services de recherche et bases de données) https://github.com/searxng/searxng
- Wenyan (outil de formatage et de publication Markdown multi-plateforme, utilisé par le New Media Editor Crew via le skill wenyan-formatter) https://github.com/caol64/wenyan

## Citation

Si vous référencez ou citez tout ou partie de ce projet dans votre travail, veuillez inclure les informations suivantes :

```
Author : Wiseflow Team
https://github.com/TeamWiseFlow/wiseflow
```

## Partenaires

[<img src="https://github.com/TeamWiseFlow/wiseflow/raw/4.x/docs/logos/SiliconFlow.png" alt="siliconflow" width="360">](https://siliconflow.com/)
