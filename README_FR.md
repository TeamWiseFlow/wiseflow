# Officier en Chef de l'Intelligence Artificielle (Wiseflow)

**[English](README_EN.md) | [日本語](README_JP.md) | [한국어](README_KR.md) | [Deutsch](README_DE.md) | [Français](README_FR.md)**

🚀 **Utilisez les grands modèles de langage pour extraire quotidiennement les informations qui vous intéressent vraiment, à partir de données massives et de diverses sources !**

Ce qui nous manque, ce n'est pas l'information, mais la capacité à filtrer le bruit des informations massives pour faire émerger des informations précieuses.

🌱 Découvrez comment l'Officier d'Intelligence IA vous aide à gagner du temps, à filtrer les informations non pertinentes et à organiser les points clés ! 🌱

https://github.com/user-attachments/assets/fc328977-2366-4271-9909-a89d9e34a07b

## 🔥🔥🔥 Version Wiseflow 4.0 Officiellement Lancée !

(Le service en ligne n'est pas encore passé au cœur 4.0 pour des raisons techniques, nous accélérons la mise à niveau)

Après trois mois d'attente, nous accueillons enfin le lancement officiel de Wiseflow 4.0 !

Cette version apporte une toute nouvelle architecture 4.x, introduit le support des sources de médias sociaux et offre de nombreuses nouvelles fonctionnalités.

🌟 4.x inclut WIS Crawler (profondément restructuré et intégré basé sur Crawl4ai, MediaCrawler et Nodriver), qui prend maintenant en charge parfaitement les pages web et les médias sociaux. La version 4.0 offre initialement le support des plateformes Weibo et Kuaishou, avec des plans pour ajouter progressivement d'autres plateformes, notamment :
Comptes Officiels WeChat, Xiaohongshu, Douyin, Bilibili, Zhihu...

Autres nouvelles fonctionnalités apportées par l'architecture 4.x :

- Nouvelle architecture, utilisation hybride d'async et de pools de threads, amélioration significative de l'efficacité du traitement (tout en réduisant la consommation de mémoire) ;
- Capacités de dispatcher héritées de Crawl4ai 0.6.3, offrant une gestion de la mémoire plus raffinée ;
- Intégration profonde du Pre-Process de la version 3.9 et du processus de Génération Markdown de Crawl4ai, évitant le traitement en double ;
- Support optimisé des sources RSS ;
- Structure de fichiers du dépôt optimisée, plus claire et conforme aux standards modernes de projets Python ;
- Passage à uv pour la gestion des dépendances et optimisation du fichier requirement.txt ;
- Scripts de démarrage optimisés (avec version Windows), permettant un véritable "démarrage en un clic" ;
- Processus de configuration et de déploiement optimisé, le programme backend ne dépend plus du service pocketbase, donc pas besoin de fournir les identifiants pocketbase dans .env et pas de restrictions de version pour pocketbase.

## 🧐 'Recherche Profonde' VS 'Recherche Large'

Je positionne Wiseflow comme une "Recherche Large", par opposition à la "Recherche Profonde" actuellement populaire.

Concrètement, la "Recherche Profonde" est où le LLM planifie de manière autonome des chemins de recherche pour des questions spécifiques, explore continuellement différentes pages, collecte suffisamment d'informations pour générer des réponses ou des rapports. Cependant, parfois nous ne recherchons pas avec des questions spécifiques et n'avons pas besoin d'une exploration profonde, juste d'une collecte large d'informations (comme la collecte d'intelligence sectorielle, la collecte d'informations de fond, la collecte d'informations clients, etc.). Dans ces cas, la largeur est clairement plus significative. Bien que la "Recherche Profonde" puisse aussi accomplir cette tâche, c'est comme utiliser un canon pour tuer une mouche - inefficace et coûteux. Wiseflow est spécialement conçu pour ces scénarios de "Recherche Large".

## ✋ Qu'est-ce qui rend Wiseflow différent des autres crawlers alimentés par l'IA ?

- Capacités complètes de capture de plateforme, incluant les pages web, les médias sociaux (support actuel des plateformes Weibo et Kuaishou), les sources RSS, les moteurs de recherche, etc. ;
- Non seulement le crawling, mais aussi l'analyse et le filtrage automatiques, fonctionnant bien avec seulement un LLM de 14b paramètres ;
- Convivial (pas seulement pour les développeurs), pas besoin de codage, "prêt à l'emploi" ;
- Haute stabilité et disponibilité grâce à l'itération continue, et efficacité de traitement équilibrant les ressources système et la vitesse ;
- (Futur) Capacité à extraire les "informations cachées" sous les informations acquises via le module insight

……… Nous attendons également avec impatience les développeurs intéressés qui nous rejoindront pour construire ensemble un Officier en Chef de l'Intelligence IA accessible à tous !

## 🚀 Démarrage Rapide

**Seulement trois étapes pour commencer !**

### 📋 Télécharger le code source du projet et installer uv et pocketbase

- pour MacOS/Linux :

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
git clone https://github.com/TeamWiseFlow/wiseflow.git
```

- pour Windows :

**Les utilisateurs Windows doivent d'abord télécharger l'outil Git Bash et exécuter les commandes suivantes dans bash [Lien de téléchargement Bash](https://git-scm.com/downloads/win)**

```bash
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
git clone https://github.com/TeamWiseFlow/wiseflow.git
```

🌟 Les opérations ci-dessus complètent l'installation de uv. Pour l'installation de pocketbase, voir [pocketbase docs](https://pocketbase.io/docs/)

Vous pouvez également essayer d'utiliser install_pocketbase.sh (pour MacOS/Linux) ou install_pocketbase.ps1 (pour Windows) pour l'installation.

### 📥 Configurer le fichier .env basé sur env_sample

Dans le dossier wiseflow (répertoire racine du projet), créez un fichier .env basé sur env_sample et remplissez les paramètres pertinents

### 🚀 Décollage !

- pour MacOS/Linux :

```bash
cd wiseflow
./run.sh
```

(Note : Vous devrez peut-être d'abord exécuter `chmod +x run.sh` pour accorder les permissions d'exécution)

- pour Windows :

```bash
cd wiseflow
.\run.ps1
```

(Note : Vous devrez peut-être d'abord exécuter `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser` pour accorder les permissions d'exécution)

Si vous rencontrez des problèmes pour démarrer le navigateur virtuel, vous pouvez exécuter la commande suivante :

```bash
python -m playwright install --with-deps chromium
```

Pour des instructions détaillées, voir [docs/manual.md](./docs/manual.md)

## 📚 Comment utiliser les données crawlees par Wiseflow dans vos propres programmes

Toutes les données crawlees par Wiseflow sont instantanément stockées dans pocketbase, vous pouvez donc accéder directement à la base de données pocketbase pour obtenir les données.

En tant que base de données légère populaire, PocketBase propose actuellement des SDK pour Go/Javascript/Python et d'autres langages.

Le service en ligne lancera bientôt une API de synchronisation, supportant la synchronisation des résultats de crawling en ligne localement, pour la construction de "bases de connaissances dynamiques" et plus encore, restez à l'écoute :

  - Adresse d'expérience en ligne : https://www.aiqingbaoguan.com/
  - Exemples d'utilisation de l'API du service en ligne : https://github.com/TeamWiseFlow/wiseflow_plus

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

Le développement de ce projet a été inspiré par [GNE](https://github.com/GeneralNewsExtractor/GeneralNewsExtractor), [AutoCrawler](https://github.com/kingname/AutoCrawler) et [SeeAct](https://github.com/OSU-NLP-Group/SeeAct).

## Citation

Si vous référencez ou citez en partie ou en totalité ce projet dans des travaux connexes, veuillez noter les informations suivantes :

```
Auteur : Wiseflow Team
https://github.com/TeamWiseFlow/wiseflow
Sous licence Apache2.0
``` 