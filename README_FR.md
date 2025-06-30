# Officier en Chef de l'Intelligence Artificielle (Wiseflow)

**[简体中文](README.md) | [English](README_EN.md) | [日本語](README_JP.md) | [한국어](README_KR.md) | [Deutsch](README_DE.md) | [Français](README_FR.md) | [العربية](README_AR.md)**

🚀 **Utilisez les grands modèles de langage pour extraire quotidiennement les informations qui vous intéressent vraiment, à partir de données massives et de diverses sources !**

Ce qui nous manque, ce n'est pas l'information, mais la capacité à filtrer le bruit des informations massives pour faire émerger des informations précieuses.

https://github.com/user-attachments/assets/2c52c010-6ae7-47f4-bc1c-5880c4bd76f3

## 🔥🔥🔥 Lancement officiel de la version 4.1 de Wiseflow !

La version 4.1 apporte de nombreuses nouvelles fonctionnalités intéressantes par rapport à la version 4.0 !

### 🔍 Sources de recherche personnalisées

La version 4.1 prend en charge la configuration précise des sources de recherche pour les points de focalisation. Elle prend actuellement en charge quatre sources de recherche : bing, github, arxiv et ebay, toutes utilisant des interfaces de plateforme natives sans nécessiter de services tiers supplémentaires.

<img src="docs/select_search_source.gif" alt="search_source" width="360">


### 🧠 Laissez l'IA penser de votre point de vue !

La version 4.1 prend en charge la définition de rôles et d'objectifs pour les points de focalisation afin de guider le LLM dans l'analyse et l'extraction d'informations d'un point de vue spécifique ou dans un but précis. Cependant, veuillez noter :

    - Si le point de focalisation lui-même est très spécifique, la définition de rôles et d'objectifs aura peu d'impact sur les résultats.
    - Le facteur le plus important affectant la qualité des résultats finaux est toujours la source d'information. Assurez-vous de fournir des sources très pertinentes pour le point de focalisation.

Pour des cas de test sur la manière dont la définition de rôles et d'objectifs affecte les résultats d'extraction, veuillez vous référer à [task1](test/reports/report_v4x_llm/task1).


### ⚙️ Mode d'extraction personnalisé

Vous pouvez désormais créer vos propres formulaires dans l'interface pb et les configurer pour des points de focalisation spécifiques. Le LLM extraira ensuite les informations avec précision en fonction des champs du formulaire.


### 👥 Mode de recherche de créateurs pour les sources de médias sociaux

Vous pouvez désormais spécifier que le programme recherche du contenu pertinent sur les plateformes de médias sociaux en fonction des points de focalisation, et trouve également les informations de la page d'accueil des créateurs de contenu. Combiné avec le "Mode d'extraction personnalisé", wiseflow peut vous aider à rechercher les coordonnées de clients potentiels, de partenaires ou d'investisseurs sur l'ensemble du réseau.

<img src="docs/find_person_by_wiseflow.png" alt="find_person_by_wiseflow" width="720">


**Pour plus d'informations sur les mises à jour de la version 4.1, veuillez consulter le [CHANGELOG](CHANGELOG.md)**

## 🧐 'Recherche Profonde' VS 'Recherche Large'

Je positionne Wiseflow comme une "Recherche Large", par opposition à la "Recherche Profonde" actuellement populaire.

Concrètement, la "Recherche Profonde" est où le LLM planifie de manière autonome des chemins de recherche pour des questions spécifiques, explore continuellement différentes pages, collecte suffisamment d'informations pour générer des réponses ou des rapports. Cependant, parfois nous ne recherchons pas avec des questions spécifiques et n'avons pas besoin d'une exploration profonde, juste d'une collecte large d'informations (comme la collecte d'intelligence sectorielle, la collecte d'informations de fond, la collecte d'informations clients, etc.). Dans ces cas, la largeur est clairement plus significative. Bien que la "Recherche Profonde" puisse aussi accomplir cette tâche, c'est comme utiliser un canon pour tuer une mouche - inefficace et coûteux. Wiseflow est spécialement conçu pour ces scénarios de "Recherche Large".

## ✋ Qu'est-ce qui rend Wiseflow différent des autres crawlers alimentés par l'IA ?

- Capacités d'acquisition sur toutes les plateformes, y compris les pages web, les médias sociaux (supportant actuellement les plateformes Weibo et Kuaishou), les sources RSS, ainsi que des sources de recherche telles que Bing, GitHub, arXiv et eBay, etc. ;
- Flux de traitement HTML unique qui extrait automatiquement les informations en fonction des points d'intérêt et découvre des liens méritant une exploration plus approfondie, fonctionnant bien avec seulement un LLM de 14b paramètres ;
- Convivial (pas seulement pour les développeurs), pas besoin de configuration manuelle de Xpath, "prêt à l'emploi" ;
- Haute stabilité et disponibilité grâce à une itération continue, et une efficacité de traitement qui équilibre les ressources système et la vitesse ;
- Ce sera plus qu'un simple "crawler"...

<img src="docs/wiseflow4.xscope.png" alt="4.x full scope" width="720">

(Périmètre global de l'architecture 4.x. La boîte en pointillés indique les parties non terminées. Nous espérons que des développeurs communautaires compétents nous rejoindront et contribueront avec des PRs. Tous les contributeurs recevront un accès gratuit à la version pro !)

## 🌟 Démarrage Rapide

**Seulement trois étapes pour commencer !**

**Les utilisateurs Windows doivent d'abord télécharger l'outil Git Bash et exécuter les commandes suivantes dans bash [Lien de téléchargement Bash](https://git-scm.com/downloads/win)**

### 📋 Télécharger le code source du projet et installer uv et pocketbase

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
git clone https://github.com/TeamWiseFlow/wiseflow.git
```

Les opérations ci-dessus complètent l'installation de uv. 

Ensuite, téléchargez le programme pocketbase correspondant à votre système depuis [pocketbase docs](https://pocketbase.io/docs/) et placez-le dans le dossier [.pb](./pb/).

Vous pouvez également essayer d'utiliser install_pocketbase.sh (pour MacOS/Linux) ou install_pocketbase.ps1 (pour Windows) pour l'installation.

### 📥 Configurer le fichier .env basé sur env_sample

Dans le dossier wiseflow (répertoire racine du projet), créez un fichier .env basé sur env_sample et remplissez les paramètres pertinents

La version 4.x ne nécessite pas que l'utilisateur fournisse les identifiants pocketbase dans .env, ni ne limite la version de pocketbase. De plus, nous avons temporairement supprimé le paramètre Secondary Model. Par conséquent, vous n'avez besoin que de quatre paramètres minimum pour compléter la configuration :

- LLM_API_KEY="" # Clé du service LLM (tout fournisseur de modèle offrant une API au format OpenAI, pas nécessaire si vous utilisez ollama en local)
- LLM_API_BASE="https://api.siliconflow.com/v1" # Adresse de l'interface du service LLM
- PRIMARY_MODEL=Qwen/Qwen3-14B # Recommandé Qwen3-14B ou un modèle de réflexion de niveau équivalent
- VL_MODEL=Pro/Qwen/Qwen2.5-VL-7B-Instruct # préférable

### 🚀 Décollage !

```bash
cd wiseflow
uv venv # nécessaire uniquement lors de la première exécution
source .venv/bin/activate  # Linux/macOS
# ou Windows :
# .venv\Scripts\activate
uv sync # nécessaire uniquement lors de la première exécution
python -m playwright install --with-deps chromium # nécessaire uniquement lors de la première exécution
chmod +x run.sh # nécessaire uniquement lors de la première exécution
./run.sh
```

Pour des instructions détaillées, voir [docs/manual/manual_fr.md](./docs/manual/manual_fr.md)

## 📚 Comment utiliser les données crawlees par Wiseflow dans vos propres programmes

Toutes les données crawlees par Wiseflow sont instantanément stockées dans pocketbase, vous pouvez donc accéder directement à la base de données pocketbase pour obtenir les données.

En tant que base de données légère populaire, PocketBase propose actuellement des SDK pour Go/Javascript/Python et d'autres langages.

Nous vous invitons à partager et promouvoir vos exemples d'applications de développement secondaire dans le dépôt suivant !

- https://github.com/TeamWiseFlow/wiseflow_plus

## 🛡️ Licence

Ce projet est open source sous [Apache2.0](LICENSE).

Pour la coopération commerciale, veuillez contacter **Email : zm.zhao@foxmail.com**

- Les clients commerciaux doivent nous contacter pour l'enregistrement, la version open source promet d'être gratuite pour toujours.

## 📬 Contact

Pour toute question ou suggestion, n'hésitez pas à laisser un message via [issue](https://github.com/TeamWiseFlow/wiseflow/issues).

## 🤝 Ce projet est basé sur les excellents projets open source suivants :

- Crawl4ai (Crawler & Scraper Web convivial pour LLM open source) https://github.com/unclecode/crawl4ai
- MediaCrawler (crawler xhs/dy/wb/ks/bilibili/zhihu) https://github.com/NanmiCoder/MediaCrawler
- NoDriver (Fournissant un framework ultra-rapide pour l'automatisation web, le webscraping, les bots et d'autres idées créatives...) https://github.com/ultrafunkamsterdam/nodriver
- Pocketbase (Backend temps réel open source en 1 fichier) https://github.com/pocketbase/pocketbase
- Feedparser (Parser de flux en Python) https://github.com/kurtmckee/feedparser
- SearXNG（a free internet metasearch engine which aggregates results from various search services and databases） https://github.com/searxng/searxng

## Citation

Si vous référencez ou citez en partie ou en totalité ce projet dans des travaux connexes, veuillez noter les informations suivantes :

```
Auteur : Wiseflow Team
https://github.com/TeamWiseFlow/wiseflow
Sous licence Apache2.0
```

## Liens Amicaux

[<img src="docs/logo/siliconflow.png" alt="siliconflow" width="360">](https://siliconflow.com/)