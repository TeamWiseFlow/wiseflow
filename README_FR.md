# WiseFlow

**[中文](README_CN.md) | [日本語](README_JP.md) | [English](README.md) | [Deutsch](README_DE.md)**

**Wiseflow** est un outil agile de fouille d'informations capable d'extraire des messages concis à partir de diverses sources telles que des sites web, des comptes officiels WeChat, des plateformes sociales, etc. Il classe automatiquement les informations par étiquettes et les télécharge dans une base de données.

Nous ne manquons pas d'informations, mais nous avons besoin de filtrer le bruit pour faire ressortir les informations de valeur ! 

Voyez comment WiseFlow vous aide à gagner du temps, à filtrer les informations non pertinentes, et à organiser les points d'intérêt !

https://github.com/TeamWiseFlow/wiseflow/assets/96130569/bd4b2091-c02d-4457-9ec6-c072d8ddfb16

<img alt="sample.png" src="asset/sample.png" width="1024"/>

## 🔥 Mise à Jour Majeure V0.3.0

- ✅ Nouveau parseur de contenu web réécrit, utilisant une combinaison de l'apprentissage statistique (en se basant sur le projet open-source GNE) et de LLM, adapté à plus de 90% des pages de nouvelles ;


- ✅ Nouvelle architecture de tâches asynchrones ;


- ✅ Nouvelle stratégie d'extraction d'informations et de classification par étiquettes, plus précise, plus fine, et qui exécute les tâches parfaitement avec seulement un LLM de 9B !

## 🌟 Fonctionnalités Clés

- 🚀 **Application LLM Native**  
  Nous avons soigneusement sélectionné les modèles open-source les plus adaptés de 7B~9B pour minimiser les coûts d'utilisation et permettre aux utilisateurs sensibles aux données de basculer à tout moment vers un déploiement local.


- 🌱 **Conception Légère**  
  Sans utiliser de modèles vectoriels, le système a une empreinte minimale et ne nécessite pas de GPU, ce qui le rend adapté à n'importe quel environnement matériel.


- 🗃️ **Extraction Intelligente d'Informations et Classification**  
  Extrait automatiquement les informations de diverses sources et les étiquette et les classe selon les intérêts des utilisateurs.


  😄 **Wiseflow est particulièrement bon pour extraire des informations à partir des articles de comptes officiels WeChat**; pour cela, nous avons configuré un parseur dédié aux articles mp !


- 🌍 **Peut Être Intégré dans Tout Projet RAG**  
  Peut servir de base de connaissances dynamique pour tout projet RAG, sans besoin de comprendre le code de Wiseflow, il suffit de lire via la base de données !


- 📦 **Base de Données Populaire Pocketbase**  
  La base de données et l'interface utilisent PocketBase. Outre l'interface web, des API pour les langages Go/Javascript/Python sont disponibles.
    
    - Go : https://pocketbase.io/docs/go-overview/
    - Javascript : https://pocketbase.io/docs/js-overview/
    - Python : https://github.com/vaphes/pocketbase

## 🔄 Quelles Sont les Différences et Connexions entre Wiseflow et les Outils de Crawling, les Projets RAG Communs ?

| Caractéristique       | Wiseflow | Crawler / Scraper                         | Projets RAG              |
|-----------------------|-------------------------------------|-------------------------------------------|--------------------------|
| **Problème Principal Résolu** | Traitement des données (filtrage, extraction, étiquetage) | Acquisition de données brutes             | Applications en aval     |
| **Connexion**         |                                     | Peut être intégré dans Wiseflow pour une acquisition de données brutes plus puissante | Peut intégrer Wiseflow comme base de connaissances dynamique |

## 📥 Installation et Utilisation

WiseFlow n'a pratiquement aucune exigence matérielle, avec une empreinte système minimale, et ne nécessite pas de GPU dédié ni CUDA (en utilisant des services LLM en ligne).

1. **Cloner le Dépôt de Code**

     😄 Liker et forker est une bonne habitude

    ```bash
    git clone https://github.com/TeamWiseFlow/wiseflow.git
    cd wiseflow
   
    conda create -n wiseflow python=3.10
    conda activate wiseflow
    cd core
    pip install -r requirement.txt
    ```
    
Vous pouvez démarrer `pb`, `task` et `backend` en utilisant les scripts dans le répertoire `core/scripts` (déplacez les fichiers de script dans le répertoire `core`).

**Remarque :**
- Démarrez toujours `pb` en premier. `task` et `backend` sont des processus indépendants et peuvent être démarrés dans n'importe quel ordre ou seulement l'un d'entre eux peut être démarré selon les besoins.
- Téléchargez d'abord le client PocketBase correspondant à votre appareil depuis [ici](https://pocketbase.io/docs/) et placez-le dans le répertoire `/core/pb`.
- Pour les problèmes de fonctionnement de `pb` (y compris les erreurs lors de la première exécution, etc.), consultez [`core/pb/README.md`](/core/pb/README.md).
- Avant l'utilisation, créez et modifiez le fichier `.env` et placez-le dans le répertoire racine du dépôt de code wiseflow (un niveau au-dessus du répertoire `core`). Le fichier `.env` peut se référer à `env_sample`. Les instructions de configuration détaillées sont ci-dessous.
- Il est fortement recommandé d'utiliser l'approche Docker, voir le cinquième point ci-dessous.

📚 Pour les développeurs, voir [/core/README.md](/core/README.md) pour plus d'informations.

Accéder aux données obtenues via PocketBase :
- http://127.0.0.1:8090/_/ - Interface du tableau de bord admin
- http://127.0.0.1:8090/api/ - API REST


2. **Configuration**

    Copier `env_sample` dans le répertoire et le renommer `.env`, puis remplir vos informations de configuration (comme les tokens de service LLM) comme suit :

   - LLM_API_KEY # Clé API pour le service d'inférence de grand modèle (si vous utilisez le service OpenAI, vous pouvez omettre cela en supprimant cette entrée)
   - LLM_API_BASE # URL de base pour le service de modèle compatible avec OpenAI (à omettre si vous utilisez le service OpenAI)
   - WS_LOG="verbose"  # Activer la journalisation de débogage, à supprimer si non nécessaire
   - GET_INFO_MODEL # Modèle pour les tâches d'extraction d'informations et d'étiquetage, par défaut gpt-3.5-turbo
   - REWRITE_MODEL # Modèle pour les tâches de fusion et de réécriture d'informations proches, par défaut gpt-3.5-turbo
   - HTML_PARSE_MODEL # Modèle de parsing de page web (activé intelligemment lorsque l'algorithme GNE est insuffisant), par défaut gpt-3.5-turbo
   - PROJECT_DIR # Emplacement pour stocker données le cache et les fichiers journaux, relatif au dépôt de code ; par défaut, le dépôt de code lui-même si non spécifié
   - PB_API_AUTH='email|password' # E-mail et mot de passe admin pour la base de données pb (**il peut être fictif mais doit être un e-mail**)
   - PB_API_BASE  # Non requis pour une utilisation normale, seulement nécessaire si vous n'utilisez pas l'interface PocketBase locale par défaut (port 8090)


3. **Recommandation de Modèle**

    Après des tests approfondis (sur des tâches en chinois et en anglais), pour un effet global et un coût optimaux, nous recommandons les suivants pour **GET_INFO_MODEL**, **REWRITE_MODEL**, et **HTML_PARSE_MODEL** : **"zhipuai/glm4-9B-chat"**, **"alibaba/Qwen2-7B-Instruct"**, **"alibaba/Qwen2-7B-Instruct"**.

    Ces modèles s'adaptent bien au projet, avec une adhésion stable aux commandes et d'excellents effets de génération. Les prompts liés à ce projet sont également optimisés pour ces trois modèles. (**HTML_PARSE_MODEL** peut également utiliser **"01-ai/Yi-1.5-9B-Chat"**, qui performe également très bien dans les tests)

⚠️ Nous recommandons vivement d'utiliser le service d'inférence en ligne **SiliconFlow** pour des coûts plus bas, des vitesses plus rapides, et des quotas gratuits plus élevés ! ⚠️

Le service d'inférence en ligne SiliconFlow est compatible avec le SDK OpenAI et fournit des services open-source pour les trois modèles ci-dessus. Il suffit de configurer LLM_API_BASE comme "https://api.siliconflow.cn/v1" et de configurer LLM_API_KEY pour l'utiliser.

😄 Ou peut-être préférez-vous utiliser mon [lien d'invitation](https://cloud.siliconflow.cn?referrer=clx6wrtca00045766ahvexw92), afin que je puisse également obtenir plus de récompenses en tokens 😄


4. **Déploiement Local**

    Comme vous pouvez le voir, ce projet utilise des LLM de 7B/9B et ne nécessite pas de modèles vectoriels, ce qui signifie que vous pouvez déployer complètement ce projet en local avec juste un RTX 3090 (24GB VRAM).

    Assurez-vous que votre service LLM local est compatible avec le SDK OpenAI et configurez LLM_API_BASE en conséquence.


5. **Exécuter le Programme**

    ```bash
    docker compose up
    ```

    **Remarque :**
   - Exécutez les commandes ci-dessus dans le répertoire racine du dépôt de code wiseflow.
   - Avant de les exécuter, créez et modifiez le fichier `.env` dans le même répertoire que le Dockerfile (répertoire racine du dépôt de code wiseflow). Le fichier `.env` peut se référer à `env_sample`.
   - Vous pouvez rencontrer des erreurs lors de la première exécution du conteneur Docker. C'est normal car vous n'avez pas encore créé de compte admin pour le dépôt `pb`.

    À ce stade, laissez le conteneur en cours d'exécution, ouvrez `http://127.0.0.1:8090/_/` dans votre navigateur, et suivez les instructions pour créer un compte admin (assurez-vous d'utiliser une adresse e-mail). Ensuite, remplissez l'adresse e-mail de l'admin créée (encore une fois, assurez-vous d'utiliser une adresse e-mail) et le mot de passe dans le fichier `.env`, puis redémarrez le conteneur.


6. **Ajouter un Scanning de Source Programmé**

    Après avoir démarré le programme, ouvrez l'interface de gestion PocketBase Admin à l'adresse [http://127.0.0.1:8090/_/](http://127.0.0.1:8090/_/).

    6.1 Ouvrez le **formulaire des tags**

    Ce formulaire vous permet de spécifier vos points d'intérêt. Le LLM affinera, filtrera et catégorisera les informations en conséquence.

    **Description des champs des tags :**
   - `name` : Description du point d'intérêt. **Remarque : Soyez précis**. Un bon exemple est `Tendances dans la concurrence entre les États-Unis et la Chine`; un mauvais exemple est `Situation internationale`.
   - `activated` : Indique si le tag est activé. S'il est désactivé, ce point d'intérêt sera ignoré. Il peut être activé et désactivé sans redémarrer le conteneur Docker ; les mises à jour seront appliquées lors de la prochaine tâche planifiée.

    6.2 Ouvrez le **formulaire des sites**

    Ce formulaire vous permet de spécifier des sources d'information personnalisées. Le système lancera des tâches planifiées en arrière-plan pour scanner, analyser et traiter ces sources localement.

    **Description des champs du formulaire sites :**
   - url : L'URL de la source. La source n'a pas besoin de spécifier la page de l'article spécifique, juste la page de la liste des articles. 
   - per_hours : Fréquence de scanning, en heures, type entier (intervalle 1~24 ; nous recommandons une fréquence de scanning d'une fois par jour, soit réglée à 24).
   - activated : Si activé. Si désactivé, la source sera ignorée ; elle peut être réactivée plus tard


## 🛡️ Licence

Ce projet est open-source sous la licence [Apache 2.0](LICENSE).

Pour une utilisation commerciale et des coopérations de personnalisation, veuillez contacter **Email : 35252986@qq.com**.

- Clients commerciaux, veuillez vous inscrire auprès de nous. Le produit promet d'être gratuit pour toujours.
- Pour les clients ayant des besoins spécifiques, nous offrons les services suivants en fonction de vos sources et besoins commerciaux :
  - Crawler et analyseur dédiés pour les sources de scénarios commerciaux des clients
  - Stratégies d'extraction et de classification de l'information sur mesure
  - Recommandations LLM ciblées ou même services de fine-tuning
  - Services de déploiement privé
  - Personnalisation de l'interface utilisateur

## 📬 Informations de Contact

Si vous avez des questions ou des suggestions, n'hésitez pas à nous contacter via [issue](https://github.com/TeamWiseFlow/wiseflow/issues).

## 🤝 Ce Projet est Basé sur les Excellents Projets Open-source Suivants :

- GeneralNewsExtractor (Extracteur général du corps de la page Web de nouvelles basé sur l'apprentissage statistique) https://github.com/GeneralNewsExtractor/GeneralNewsExtractor
- json_repair (Réparation de documents JSON invalides) https://github.com/josdejong/jsonrepair/tree/main 
- python-pocketbase (SDK client PocketBase pour Python) https://github.com/vaphes/pocketbase

# Citation

Si vous référez à ou citez tout ou partie de ce projet dans des travaux connexes, veuillez indiquer les informations suivantes :
```
Author: Wiseflow Team
https://openi.pcl.ac.cn/wiseflow/wiseflow
https://github.com/TeamWiseFlow/wiseflow
Licensed under Apache2.0
```