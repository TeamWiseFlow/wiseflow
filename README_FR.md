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
    ```


2. **Configuration**

    Copier `env_sample` dans le répertoire et le renommer `.env`, puis remplir vos informations de configuration (comme les tokens de service LLM) comme suit :

   - LLM_API_KEY # Clé API pour le service d'inférence de grand modèle (si vous utilisez le service OpenAI, vous pouvez omettre cela en supprimant cette entrée)
   - LLM_API_BASE # URL de base pour le service de modèle compatible avec OpenAI (à omettre si vous utilisez le service OpenAI)
   - WS_LOG="verbose"  # Activer la journalisation de débogage, à supprimer si non nécessaire
   - GET_INFO_MODEL # Modèle pour les tâches d'extraction d'informations et d'étiquetage, par défaut gpt-3.5-turbo
   - REWRITE_MODEL # Modèle pour les tâches de fusion et de réécriture d'informations proches, par défaut gpt-3.5-turbo
   - HTML_PARSE_MODEL # Modèle de parsing de page web (activé intelligemment lorsque l'algorithme GNE est insuffisant), par défaut gpt-3.5-turbo
   - PROJECT_DIR # Emplacement pour stocker le cache et les fichiers journaux, relatif au dépôt de code ; par défaut, le dépôt de code lui-même si non spécifié
   - PB_API_AUTH='email|password' # E-mail et mot de passe admin pour la base de données pb (utilisez un e-mail valide pour la première utilisation, il peut être fictif mais doit être un e-mail)
   - PB_API_BASE  # Non requis pour une utilisation normale, seulement nécessaire si vous n'utilisez pas l'interface PocketBase locale par défaut (port 8090)


3. **Recommandation de Modèle**

    Après des tests approfondis (sur des tâches en chinois et en anglais), pour un effet global et un coût optimaux, nous recommandons les suivants pour **GET_INFO_MODEL**, **REWRITE_MODEL**, et **HTML_PARSE_MODEL** : **"zhipuai/glm4-9B-chat"**, **"alibaba/Qwen2-7B-Instruct"**, **"alibaba/Qwen2-7B-Instruct"**.

    Ces modèles s'adaptent bien au projet, avec une adhésion stable aux commandes et d'excellents effets de génération. Les prompts liés à ce projet sont également optimisés pour ces trois modèles. (**HTML_PARSE_MODEL** peut également utiliser **"01-ai/Yi-1.5-9B-Chat"**, qui performe également très bien dans les tests)

⚠️ Nous recommandons vivement d'utiliser le service d'inférence en ligne **SiliconFlow** pour des coûts plus bas, des vitesses plus rapides, et des quotas gratuits plus élevés ! ⚠️

Le service d'inférence en ligne SiliconFlow est compatible avec le SDK OpenAI et fournit des services open-source pour les trois modèles ci-dessus. Il suffit de configurer LLM_API_BASE comme "https://api.siliconflow.cn/v1" et de configurer LLM_API_KEY pour l'utiliser.


4. **Déploiement Local**

    Comme vous pouvez le voir, ce projet utilise des LLM de 7B/9B et ne nécessite pas de modèles vectoriels, ce qui signifie que vous pouvez déployer complètement ce projet en local avec juste un RTX 3090 (24GB VRAM).

    Assurez-vous que votre service LLM local est compatible avec le SDK OpenAI et configurez LLM_API_BASE en conséquence.


5. **Exécuter le Programme**

    **Pour les utilisateurs réguliers, il est fortement recommandé d'utiliser Docker pour exécuter Chef Intelligence Officer.**

    📚 Pour les développeurs, voir [/core/README.md](/core/README.md) pour plus d'informations.

    Accéder aux données obtenues via PocketBase :

    - http://127.0.0.1:8090/_/ - Interface du tableau de bord admin
    - http://127.0.0.1:8090/api/ - API REST
    - https://pocketbase.io/docs/ pour en savoir plus


6. **Ajouter un Scanning de Source Programmé**

    Après avoir démarré le programme, ouvrez l'interface du tableau de bord admin de PocketBase (http://127.0.0.1:8090/_/)

    Ouvrez le formulaire **sites**.

    À travers ce formulaire, vous pouvez spécifier des sources personnalisées, et le système démarrera des tâches en arrière-plan pour scanner, parser et analyser les sources localement.

    Description des champs du formulaire sites :

   - url : L'URL de la source. La source n'a pas besoin de spécifier la page de l'article spécifique, juste la page de la liste des articles. Le client Wiseflow inclut deux parseurs de pages généraux qui peuvent acquérir et parser efficacement plus de 90% des pages web de type nouvelles statiques.
   - per_hours : Fréquence de scanning, en heures, type entier (intervalle 1~24 ; nous recommandons une fréquence de scanning d'une fois par jour, soit réglée à 24).
   - activated : Si activé. Si désactivé, la source sera ignorée ; elle peut être réactivée plus tard

## 🛡️ Licence

Ce projet est open-source sous la licence [Apache 2.0](LICENSE).

Pour une utilisation commerciale et des coopérations de personnalisation, veuillez contacter **Email : 35252986@qq.com**.

- Clients commerciaux, veuillez vous inscrire auprès de nous. Le produit promet d'être gratuit pour toujours.
- Pour les clients ayant des besoins spécifiques, nous offrons les services suivants en fonction de vos sources et besoins commerciaux :
  - Parseurs propriétaires personnalisés
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