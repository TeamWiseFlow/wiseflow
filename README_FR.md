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

Plus remarquable encore, grâce à nos expériences et explorations préliminaires, nous avons découvert que l'intégration des capacités d'acquisition de wiseflow dans openclaw sous forme de « plugins » résout parfaitement les deux limitations mentionnées ci-dessus. Nous publierons prochainement des vidéos de démonstration passionnantes, tout en rendant ces « plugins » open source.

Il convient de noter que le système de plugins d'openclaw diffère considérablement de ce que nous comprenons traditionnellement par « plugins » (similaires aux plugins de Claude Code). Nous avons donc dû introduire le concept d'« add-on ». Pour être précis, wiseflow 5.x apparaîtra sous la forme d'un add-on openclaw. L'openclaw original ne dispose pas d'une architecture « add-on », mais en pratique, vous n'avez besoin que de quelques commandes shell simples pour effectuer cette « transformation ». Nous avons également préparé une version améliorée d'openclaw prête à l'emploi avec des configurations prédéfinies pour des scénarios commerciaux réels : [openclaw_for_business](https://github.com/TeamWiseFlow/openclaw_for_business). Vous pouvez simplement le cloner et extraire la release wiseflow dans le dossier add-on d'openclaw_for_business.

## 🌟 Démarrage rapide

Téléchargez le package intégré (qui inclut openclaw_for_business et le wiseflow addon) directement depuis les [Releases](https://github.com/TeamWiseFlow/wiseflow/releases) de ce dépôt, extrayez-le et exécutez le script de déploiement en un clic.

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
wiseflow/
├── addon.json                    # Métadonnées
├── overrides.sh                  # pnpm overrides : playwright-core → patchright-core
├── patches/
│   └── 001-browser-tab-recovery.patch  # Patch de récupération d'onglets
├── skills/
│   └── browser-guide/SKILL.md    # Bonnes pratiques d'utilisation du navigateur
├── docs/                         # Documentation technique
│   ├── anti-detection-research.md
│   └── openclaw-extension-architecture.md
└── tests/                        # Cas de test et scripts
    ├── README.md
    └── run-managed-tests.mjs
```

## WiseFlow Pro est maintenant disponible !

Des capacités de scraping plus puissantes, un support plus complet des réseaux sociaux, avec interface graphique et package d'installation en un clic — aucun déploiement nécessaire !

https://github.com/user-attachments/assets/57f8569c-e20a-4564-a669-1200d56c5725

🔥 **La version Pro est en vente** : https://shouxiqingbaoguan.com/

🌹 Dès aujourd'hui, contribuez des PRs à la version open source de wiseflow (code, documentation et partage de cas d'utilisation réussis sont les bienvenus). Une fois acceptées, les contributeurs recevront une licence d'un an pour wiseflow Pro !

📥 🎉 📚

## 🛡️ Licence

Depuis la version 4.2, nous avons mis à jour notre licence open source. Veuillez consulter : [LICENSE](LICENSE)

Pour une coopération commerciale, veuillez contacter **Email : zm.zhao@foxmail.com**

## 📬 Contact

Pour toute question ou suggestion, n'hésitez pas à laisser un message via les [issues](https://github.com/TeamWiseFlow/wiseflow/issues).

Pour les exigences relatives à la version Pro ou les retours de coopération, veuillez nous contacter via WeChat :

<img src="docs/wechat.jpg" alt="wechat" width="360">

## 🤝 wiseflow 5.x est construit sur les excellents projets open source suivants :

- Patchright (Version Python indétectable de la bibliothèque de test et d'automatisation Playwright) https://github.com/Kaliiiiiiiiii-Vinyzu/patchright-python
- Feedparser (Analyse de flux en Python) https://github.com/kurtmckee/feedparser
- SearXNG (un métamoteur de recherche internet gratuit qui agrège les résultats de divers services de recherche et bases de données) https://github.com/searxng/searxng

## Citation

Si vous référencez ou citez tout ou partie de ce projet dans votre travail, veuillez inclure les informations suivantes :

```
Author : Wiseflow Team
https://github.com/TeamWiseFlow/wiseflow
```

## Partenaires

[<img src="docs/logos/SiliconFlow.png" alt="siliconflow" width="360">](https://siliconflow.com/)
