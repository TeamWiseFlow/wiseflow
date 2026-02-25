# Officier en Chef de l'Intelligence Artificielle (Wiseflow)

**[简体中文](README.md) | [English](README_EN.md) | [日本語](README_JP.md) | [한국어](README_KR.md) | [Deutsch](README_DE.md) | [Français](README_FR.md) | [العربية](README_AR.md)**

[![Ask DeepWiki](https://deepwiki.com/badge.svg)](https://deepwiki.com/TeamWiseFlow/wiseflow)

🚀 **Extrayez en continu les informations dont vous avez besoin de tout l'Internet**

Prend en charge les principales plateformes d'auto-média, les sites nécessitant une pré-connexion, le suivi de sources spécifiques, la collecte quotidienne via des tâches planifiées, l'extraction automatique par de grands modèles de langage (mode résumé, mode formulaire personnalisé)……

## 🎉 La version WiseFlow Pro est maintenant disponible !

Capacités de crawling plus puissantes, support des médias sociaux plus complet, incluant une interface Web et un package d'exécution en un clic sans installation !

https://github.com/user-attachments/assets/880af7a3-7b28-44ff-86b6-aaedecd22761

🔥🔥 **La version Pro est maintenant en vente dans le monde entier** : https://shouxiqingbaoguan.com/ 

🌹 À partir d'aujourd'hui, les contributeurs qui soumettent des PR (code, documentation, partage de cas de succès sont les bienvenus) pour la version open source de wiseflow recevront un droit d'utilisation d'un an pour la version wiseflow pro une fois acceptés !

## Version Open Source de Wiseflow

Depuis la version 4.30, la version open source de wiseflow a été mise à jour avec la même architecture que la version pro, dispose de la même API et peut partager de manière transparente l'écosystème [wiseflow+](https://github.com/TeamWiseFlow/wiseflow-plus) !

## Comparaison entre les versions Open Source et Pro de wiseflow

| Caractéristiques | Version Open Source | Version Pro |
| :--- | :---: | :---: |
| **Sources surveillées** | web, rss | web, rss, plus 7 plateformes majeures de self-média chinois |
| **Sources de recherche** | bing, github, arxiv | bing, github, arxiv, plus 6 plateformes majeures de self-média chinois |
| **Installation et déploiement** | Nécessite une installation manuelle de l'environnement | Pas d'installation, exécution en un clic |
| **Interface utilisateur** | Aucune | UI Web en chinois |
| **Coût du LLM** | L'utilisateur s'abonne lui-même ou utilise un LLM local | L'abonnement inclut les frais d'appel LLM (aucune configuration requise) |
| **Support technique** | GitHub Issues | Groupe WeChat pour les utilisateurs payants |
| **Prix** | Gratuit | 488 ￥/an |
| **Groupe cible** | Exploration communautaire et apprentissage de projet | Utilisation quotidienne (individuelle ou entreprise) |

## 🧐 Positionnement du produit wiseflow

wiseflow n'est pas un agent à usage général comme ChatGPT ou Manus ; il se concentre sur la surveillance et l'extraction d'informations, prend en charge des sources spécifiées par l'utilisateur et garantit l'obtention des dernières informations grâce à un mode de tâches périodiques (jusqu'à 4 fois par jour, soit toutes les 6 heures). Parallèlement, wiseflow permet une recherche d'informations complète sur des plateformes spécifiées (par exemple, "recherche de personnes").

Mais n'assimilez pas wiseflow à un crawler traditionnel ou à un RPA ! Le comportement d'acquisition de wiseflow est entièrement piloté par LLM, utilise de vrais navigateurs (plutôt que des navigateurs sans tête ou virtuels), et ses actions d'acquisition et d'extraction sont effectuées simultanément :

- Mécanisme innovant d'analyse intelligente HTML : identifie automatiquement les informations clés et les liens explorables.
- Stratégie « Crawl-and-Search-in-One » : jugement et extraction par le LLM en temps réel pendant le crawling, ne capturant que les informations pertinentes, ce qui réduit considérablement les risques de contrôle des risques.
- Véritable solution prête à l'emploi : aucun Xpath, script ou configuration manuelle n'est requis – facile à utiliser même pour les utilisateurs ordinaires.

    ……

Pour plus de détails, veuillez vous référer à : https://shouxiqingbaoguan.com/

## 🌟 Démarrage rapide

**Prêt en seulement trois étapes !**

**À partir de la version 4.2, l'installation de Google Chrome est obligatoire (utilisez le chemin d'installation par défaut).**

**Les utilisateurs Windows sont priés de télécharger l'outil Git Bash à l'avance et d'exécuter les commandes suivantes dans le bash [Lien de téléchargement Bash](https://git-scm.com/downloads/win)**

### 📋 Installer l'outil de gestion d'environnement uv et télécharger le code source de wiseflow

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
git clone https://github.com/TeamWiseFlow/wiseflow.git
```

Ces étapes installent uv et téléchargent le code source de wiseflow.

### 📥 Configurer le fichier .env basé on env_sample

Dans le dossier wiseflow (répertoire racine du projet), créez un fichier .env basé sur env_sample et saisissez les paramètres correspondants (principalement la configuration du service LLM).

**La version open source de wiseflow nécessite que l'utilisateur configure son propre service LLM.**

wiseflow ne limite pas les fournisseurs de modèles, tant qu'ils sont compatibles avec le format de requête OpenAI SDK. Vous pouvez choisir des services MaaS existants ou des services de modèles déployés localement comme Ollama.

Pour les utilisateurs en Chine continentale, nous recommandons d'utiliser le service de modèle Siliconflow.

😄 N'hésitez pas à utiliser mon [lien de parrainage](https://cloud.siliconflow.cn/i/WNLYbBpi) pour postuler — vous et moi recevrons une récompense de plateforme de ￥14.

Si vous préférez utiliser des modèles fermés étrangers tels qu'OpenAI, vous pouvez utiliser le service de modèle AiHubMix, qui fonctionne parfaitement en Chine continentale :

😄 Vous pouvez vous inscrire via mon [lien d'invitation AiHubMix](https://aihubmix.com?aff=Gp54).

Les utilisateurs étrangers peuvent utiliser la version internationale de Siliconflow : https://www.siliconflow.com/

### 🚀 Décollage !

```bash
cd wiseflow
uv venv # requis uniquement la première fois
source .venv/bin/activate  # Linux/macOS
# ou sous Windows :
# .venv\Scripts\activate
uv sync # requis uniquement la première fois
python core/entry.py
```

## 📚 Comment utiliser les données collectées par wiseflow dans vos propres programmes

Consultez [wiseflow backend api](./core/backend/README.md)

Qu'il s'agisse de la version wiseflow ou wiseflow-pro, nous vous invitons à partager et à promouvoir vos exemples d'applications dans le dépôt suivant !

- https://github.com/TeamWiseFlow/wiseflow-plus

(Les contributions par PR à ce dépôt recevront également un droit d'utilisation d'un an pour wiseflow-pro une fois acceptées)

**L'architecture de la version 4.2x n'est pas entièrement compatible avec la version 4.30. La dernière version de 4.2x (v4.29) n'est plus maintenue. Pour des références de code, vous pouvez passer à la branche "2025".**

## 🛡️ Licence

Depuis la version 4.2, nous avons mis à jour l'accord de licence open source. Veuillez consulter : [LICENSE](LICENSE) 

Pour toute coopération commerciale, veuillez contacter **E-mail : zm.zhao@foxmail.com**

## 📬 Contact

Pour toute question ou suggestion, n'hésitez pas à laisser un message via [issue](https://github.com/TeamWiseFlow/wiseflow/issues).

Pour les demandes concernant la version Pro ou les commentaires sur la coopération, veuillez contacter le « Manager » d'AI Chief Intelligence Officer via WeChat :

<img src="docs/wechat.jpg" alt="wechat" width="360">

## 🤝 Ce projet est basé sur les excellents projets open source suivants :

- Crawl4ai (Open-source LLM Friendly Web Crawler & Scraper) https://github.com/unclecode/crawl4ai
- Patchright (Undetected Python version of the Playwright testing and automation library) https://github.com/Kaliiiiiiiiii-Vinyzu/patchright-python
- MediaCrawler (xhs/dy/wb/ks/bilibili/zhihu crawler) https://github.com/NanmiCoder/MediaCrawler
- NoDriver (Fournit un framework ultra-rapide pour l'automatisation Web, le webscraping, les bots et d'autres idées créatives...) https://github.com/ultrafunkamsterdam/nodriver
- Feedparser (Analyse de flux en Python) https://github.com/kurtmckee/feedparser
- SearXNG (Un moteur de métarecherche Internet gratuit qui agrège les résultats de divers services de recherche et bases de données) https://github.com/searxng/searxng

## Citation

Si vous référencez ou citez ce projet en tout ou en partie dans des travaux connexes, veuillez fournir les informations suivantes :

```
Auteur : Wiseflow Team
https://github.com/TeamWiseFlow/wiseflow
```

## Liens amicaux

[<img src="docs/logos/SiliconFlow.png" alt="siliconflow" width="360">](https://siliconflow.com/)
