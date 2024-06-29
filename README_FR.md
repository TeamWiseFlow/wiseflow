# WiseFlow

**[中文](README_CN.md) | [日本語](README_JP.md) | [English](README.md) | [Deutsch](README_DE.md)**

**Wiseflow** est un outil agile d'extraction d'informations qui peut extraire des informations à partir de diverses sources telles que des sites Web, des comptes officiels WeChat et des plateformes de médias sociaux, en fonction des points d'intérêt prédéfinis, catégoriser automatiquement les tags et les télécharger dans la base de données.

🔥 **SiliconFlow a officiellement annoncé que plusieurs services d'inférence en ligne de LLM, tels que Qwen2-7B-Instruct et glm-4-9b-chat, sont désormais gratuits à partir d'aujourd'hui. Cela signifie que vous pouvez effectuer des recherches d'information avec le wiseflow à "zéro coût" !** 🔥

Nous ne manquons pas d'informations, mais nous avons besoin de filtrer le bruit pour faire ressortir les informations de valeur ! 

Voyez comment WiseFlow vous aide à gagner du temps, à filtrer les informations non pertinentes, et à organiser les points d'intérêt !

https://github.com/TeamWiseFlow/wiseflow/assets/96130569/bd4b2091-c02d-4457-9ec6-c072d8ddfb16

<img alt="sample.png" src="asset/sample.png" width="1024"/>

## Mise à Jour Majeure V0.3.0

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


- 🌍 **Peut Être Intégré dans Tout Projet Agent**  
  Peut servir de base de connaissances dynamique pour tout projet Agent, sans besoin de comprendre le code de Wiseflow, il suffit de lire via la base de données !


- 📦 **Base de Données Populaire Pocketbase**  
  La base de données et l'interface utilisent PocketBase. Outre l'interface web, des SDK pour les langages Go/Javascript/Python sont disponibles.
    
    - Go : https://pocketbase.io/docs/go-overview/
    - Javascript : https://pocketbase.io/docs/js-overview/
    - Python : https://github.com/vaphes/pocketbase

## 🔄 Quelles Sont les Différences et Connexions entre Wiseflow et les Outils de Crawling, les Projets LLM-Agent Communs ?

| Caractéristique       | Wiseflow | Crawler / Scraper                         | LLM-Agent                                                    |
|-----------------------|-------------------------------------|-------------------------------------------|--------------------------------------------------------------|
| **Problème Principal Résolu** | Traitement des données (filtrage, extraction, étiquetage) | Acquisition de données brutes             | Applications en aval                                         |
| **Connexion**         |                                     | Peut être intégré dans Wiseflow pour une acquisition de données brutes plus puissante | Peut intégrer Wiseflow comme base de connaissances dynamique |

## 📥 Installation et Utilisation

WiseFlow n'a pratiquement aucune exigence matérielle, avec une empreinte système minimale, et ne nécessite pas de GPU dédié ni CUDA (en utilisant des services LLM en ligne).
1. **Cloner le dépôt**

     😄 Starring et forker sont de bonnes habitudes

    ```bash
    git clone https://github.com/TeamWiseFlow/wiseflow.git
    cd wiseflow
    ```

2. **Fortement recommandé : Utiliser Docker**

    ```bash
    docker compose up
    ```
   Vous pouvez modifier `compose.yaml` selon vos besoins.

    **Remarque :**
    - Exécutez la commande ci-dessus dans le répertoire racine du dépôt wiseflow.
    - Avant d'exécuter, créez et éditez un fichier `.env` dans le même répertoire que le Dockerfile (répertoire racine du dépôt wiseflow). Référez-vous à `env_sample` pour le fichier `.env`.
    - La première fois que vous exécutez le conteneur Docker, une erreur peut se produire car vous n'avez pas encore créé de compte administrateur pour le dépôt pb.

    À ce stade, gardez le conteneur en cours d'exécution, ouvrez `http://127.0.0.1:8090/_/` dans votre navigateur, et suivez les instructions pour créer un compte administrateur (assurez-vous d'utiliser un e-mail). Ensuite, entrez l'email administrateur créé (encore une fois, assurez-vous qu'il s'agit d'un e-mail) et le mot de passe dans le fichier `.env`, et redémarrez le conteneur.

    _Si vous souhaitez modifier le fuseau horaire et la langue du conteneur [ce qui déterminera la langue de l'invite, mais a peu d'effet sur les résultats], exécutez l'image avec la commande suivante_

    ```bash
    docker run -e LANG=fr_FR.UTF-8 -e LC_CTYPE=fr_FR.UTF-8 your_image
    ```

3. **[Alternative] Exécuter directement avec Python**

    ```bash
    conda create -n wiseflow python=3.10
    conda activate wiseflow
    cd core
    pip install -r requirement.txt
    ```

    Vous pouvez ensuite démarrer pb, task, et backend individuellement en utilisant les scripts dans core/scripts (déplacez les fichiers de script dans le répertoire core).

    Remarque :
    - Commencez par démarrer pb ; task et backend sont des processus indépendants, et l'ordre n'a pas d'importance. Vous pouvez démarrer l'un d'entre eux selon vos besoins.
    - Téléchargez le client pocketbase adapté à votre appareil depuis https://pocketbase.io/docs/ et placez-le dans le répertoire /core/pb.
    - Pour les problèmes avec pb (y compris les erreurs au premier démarrage), référez-vous à [core/pb/README.md](/core/pb/README.md).
    - Avant utilisation, créez et éditez un fichier `.env` et placez-le dans le répertoire racine du dépôt wiseflow (le répertoire supérieur à core). Référez-vous à `env_sample` pour le fichier `.env`, et consultez ci-dessous pour une configuration détaillée.


    📚 Pour les développeurs, consultez [/core/README.md](/core/README.md) pour plus d'informations.

        Accédez aux données via pocketbase :
        - http://127.0.0.1:8090/_/ - Interface de tableau de bord administrateur
        - http://127.0.0.1:8090/api/ - REST API


4. **Configuration**

    Copiez `env_sample` du répertoire et renommez-le en `.env`, puis remplissez vos informations de configuration (comme les tokens de service LLM) comme suit :

   - LLM_API_KEY # Clé API pour les services d'inférence de modèles de langue large
   - LLM_API_BASE # Ce projet repose sur le SDK OpenAI. Configurez cette option si votre service de modèle prend en charge l'API OpenAI. Si vous utilisez le service OpenAI, vous pouvez omettre cette option.
   - WS_LOG="verbose"  # Définir pour activer l'observation du débogage. Supprimez si non nécessaire.
   - GET_INFO_MODEL # Modèle pour les tâches d'extraction d'informations et de correspondance de tags, par défaut gpt-3.5-turbo
   - REWRITE_MODEL # Modèle pour les tâches de fusion approximative et de réécriture d'informations, par défaut gpt-3.5-turbo
   - HTML_PARSE_MODEL # Modèle pour l'analyse des pages Web (activé intelligemment si l'algorithme GNE fonctionne mal), par défaut gpt-3.5-turbo
   - PROJECT_DIR # Emplacement de stockage pour les données, le cache et les fichiers journaux, par rapport au dépôt. Par défaut, dans le dépôt.
   - PB_API_AUTH='email|password' # Email et mot de passe pour l'admin de la base de données pb (doit être un email, peut être fictif)
   - PB_API_BASE  # Normalement inutile. Configurez-le seulement si vous n'utilisez pas l'interface locale pocketbase par défaut (8090).


5. **Recommandations de Modèle**

    Basé sur des tests intensifs (pour les tâches en chinois et en anglais), nous recommandons **"zhipuai/glm4-9B-chat"** pour **GET_INFO_MODEL**, **"alibaba/Qwen2-7B-Instruct"** pour **REWRITE_MODEL**, et **"alibaba/Qwen2-7B-Instruct"** pour **HTML_PARSE_MODEL**.

    Ces modèles sont bien adaptés à ce projet, avec une adhérence stable aux instructions et une qualité de génération excellente. Les invites de ce projet ont été optimisées pour ces trois modèles. (**HTML_PARSE_MODEL** peut également utiliser **"01-ai/Yi-1.5-9B-Chat"**, qui a été testé et fonctionne très bien.)


    ⚠️ Nous recommandons fortement d'utiliser le service d'inférence en ligne de **SiliconFlow** pour des coûts inférieurs, des vitesses plus rapides, et des quotas gratuits plus élevés ! ⚠️

    Le service d'inférence en ligne de SiliconFlow est compatible avec le SDK OpenAI et fournit des services open-source pour les trois modèles ci-dessus. Configurez simplement `LLM_API_BASE` à "https://api.siliconflow.cn/v1" et définissez `LLM_API_KEY` pour l'utiliser.

    😄 Alternativement, vous pouvez utiliser mon [lien d'invitation](https://cloud.siliconflow.cn?referrer=clx6wrtca00045766ahvexw92), ce qui me récompense également avec plus de tokens 😄


6. **Points d'Intérêt et Ajout de Sources de Scannage Programmées**

    Après avoir démarré le programme, ouvrez l'interface de tableau de bord administrateur pocketbase (http://127.0.0.1:8090/_/)

        6.1 Ouvrez le **formulaire tags**

        Utilisez ce formulaire pour spécifier vos points d'intérêt. Le LLM extraira, filtrera, et classera les informations en fonction de ces points.

        Description des champs tags :

        - name, Description du point d'intérêt. **Remarque : Soyez spécifique.** Bon exemple : `Tendances dans la compétition USA-Chine`. Mauvais exemple : `Situation internationale`.
        - activated, Activé ou non. Si désactivé, le point d'intérêt sera ignoré. Il peut être réactivé plus tard. L'activation et la désactivation ne nécessitent pas de redémarrage du conteneur Docker et seront mises à jour lors de la prochaine tâche programmée.

        6.2 Ouvrez le **formulaire sites**

        Utilisez ce formulaire pour spécifier des sources personnalisées. Le système démarrera des tâches en arrière-plan pour scanner, analyser et interpréter ces sources localement.

        Description des champs sites :

        - url, URL de la source. Fournissez une URL vers la page de liste plutôt qu'une page d'article spécifique.
        - per_hours, Fréquence de scannage en heures, sous forme d'entier (intervalle 1-24 ; nous recommandons pas plus d'une fois par jour, c.-à-d. réglé sur 24).
        - activated, Activé ou non. Si désactivé, la source sera ignorée. Elle peut être réactivée plus tard. L'activation et la désactivation ne nécessitent pas de redémarrage du conteneur Docker et seront mises à jour lors de la prochaine tâche programmée.


7. **Déploiement Local**

    Comme vous pouvez le voir, ce projet utilise des LLMs de taille 7B/9B et ne nécessite aucun modèle vectoriel, ce qui signifie que vous n'avez besoin que d'un seul RTX 3090 (24 Go de VRAM) pour déployer complètement ce projet localement.

    Assurez-vous que votre service LLM local est compatible avec le SDK OpenAI et configurez `LLM_API_BASE` en conséquence.


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