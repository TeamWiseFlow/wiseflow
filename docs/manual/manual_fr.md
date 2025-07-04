# Guide d'installation et d'utilisation de WiseFlow

**Les utilisateurs de la version 3.x doivent supprimer complètement le dépôt original et le dossier pb, puis cloner à nouveau le dépôt 4.x, sinon le programme ne pourra pas démarrer normalement.**

**Les utilisateurs de la version 4.0 qui souhaitent mettre à niveau vers la version 4.1, après avoir tiré le dernier code, doivent d'abord exécuter la commande ./pb/pocketbase migrate, sinon le programme ne pourra pas démarrer normalement.**

## 📋 Configuration système requise

- **Python**: 3.10 - 3.12 (3.12 recommandé)
- **Système d'exploitation**: macOS, Linux ou Windows
- **Configuration matérielle**: 8 Go de RAM ou plus (lors de l'utilisation de services LLM en ligne)

## 📥 Instructions d'utilisation

L'interface utilisateur de wiseflow 4.x utilise PocketBase (bien que je ne l'aime pas, il n'y a pas de meilleure alternative pour le moment)

### 1. Accès à l'interface

🌐 Après le démarrage réussi, ouvrez votre navigateur et visitez : **http://127.0.0.1:8090/_/**

### 2. Configuration des sources d'information et des points de focus

Passez au formulaire focus_point

Via ce formulaire, vous pouvez spécifier vos points de focus. Le LLM extraira, filtrera et classera les informations en conséquence.
    
Description des champs :
- focuspoint (obligatoire), description du point de focus, indiquez au LLM quelles informations vous recherchez, par exemple "Informations sur la transition du primaire au collège à Shanghai", "Annonces d'appels d'offres"
- restrictions (optionnel), contraintes de filtrage du point de focus, indiquez au LLM quelles informations doivent être exclues, par exemple "Uniquement les informations officielles sur la transition vers le collège à Shanghai", "Publications après le 1er janvier 2025 d'une valeur supérieure à 1 million"
- explanation (optionnel), explications pour des concepts spéciaux ou des termes techniques, pour éviter les malentendus, par exemple "La transition du primaire au collège signifie le passage de l'école primaire au collège"
- activated, si activé. Si désactivé, ce point de focus sera ignoré, mais pourra être réactivé plus tard
- freq, fréquence de crawling en heures, en nombre entier (nous recommandons de ne pas dépasser une fois par jour, c'est-à-dire 24, le minimum est 2, c'est-à-dire toutes les 2 heures)
- search, configurer des sources de recherche détaillées, prend actuellement en charge bing, github, arxiv et ebay
- sources, sélection des sources d'information correspondantes

#### 💡 La manière dont vous rédigez le point de mire est très importante, car elle détermine directement si l'extraction d'informations peut répondre à vos exigences. Spécifiquement :

  - Si votre cas d'utilisation est le suivi d'informations sectorielles, d'informations académiques, d'informations sur les politiques, etc., et que vos sources d'information incluent des recherches larges, le point de mire doit utiliser un modèle de mots-clés similaire à un moteur de recherche. En même temps, vous devez ajouter des contraintes et des explications, et si nécessaire, définir des rôles et des objectifs.

  - Si votre cas d'utilisation est le suivi de concurrents, les vérifications d'antécédents, etc., où les sources d'information sont très spécifiques, telles que les pages d'accueil des concurrents, les comptes officiels, etc., il vous suffit de saisir votre perspective d'intérêt comme point de mire, par exemple "informations sur les baisses de prix", "informations sur les nouveaux produits", etc.

**Les modifications de la configuration focus_point ne nécessitent pas de redémarrage du programme et prendront effet automatiquement lors de la prochaine exécution.**

Vous pouvez ajouter des sources d'information soit sur la page sources, soit sur la page de liaison des focus_points. Description des champs pour les sources d'information :

- type, type, actuellement pris en charge : web, rss, wb (Weibo), ks (Kuaishou), mp (Compte officiel WeChat (non pris en charge dans la version 4.0, en attente de la version 4.1))
- creators, IDs des créateurs à crawler (séparés par des virgules), valide uniquement pour ks, wb et mp, ks et mp prennent en charge 'homefeed' (représente le contenu poussé par le système). Ce champ peut également être laissé vide, la source sera alors utilisée uniquement pour la recherche

  *Note : L'ID doit être l'URL de la page web du profil correspondant, par exemple pour Weibo https://m.weibo.cn/profile/2656274875, alors l'ID est 2656274875*

- url, lien vers la source d'information, valide uniquement pour les types rss et web.

### 3. Affichage des résultats

- page infos stocke les informations utiles extraites
- page crawled_data stocke les données brutes crawlees
- page ks_cache stocke les données en cache de Kuaishou
- page wb_cache stocke les données en cache de Weibo

## 🌟 Installation et déploiement

**L'installation se fait en seulement trois étapes !**

**Les utilisateurs Windows doivent d'abord télécharger l'outil Git Bash et exécuter les commandes suivantes dans bash [Lien de téléchargement Bash](https://git-scm.com/downloads/win)**

### 📋 Télécharger le code source du projet et installer uv et pocketbase

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
git clone https://github.com/TeamWiseFlow/wiseflow.git
```

Les opérations ci-dessus complètent l'installation de uv. 

Ensuite, téléchargez le programme pocketbase correspondant à votre système depuis [pocketbase docs](https://pocketbase.io/docs/) et placez-le dans le dossier [.pb](./pb/).

Ces opérations installent uv. Pour l'installation de pocketbase, voir [pocketbase docs](https://pocketbase.io/docs/)

Vous pouvez également essayer d'utiliser install_pocketbase.sh (pour MacOS/Linux) ou install_pocketbase.ps1 (pour Windows).

### 📥 Configuration du fichier .env basé sur env_sample

Dans le dossier wiseflow (répertoire racine du projet), créez un fichier .env basé sur env_sample et remplissez les paramètres pertinents.

La version 4.x ne nécessite pas d'identifiants PocketBase dans le fichier .env et ne limite pas non plus la version de PocketBase. De plus, nous avons temporairement supprimé le paramètre Secondary Model. Vous n'avez donc besoin que de quatre paramètres minimum :

- LLM_API_KEY="" # Clé de service LLM (tout fournisseur avec un format d'API compatible OpenAI est approprié, non requis pour l'utilisation locale d'ollama)
- LLM_API_BASE="" # Adresse de l'interface du service LLM (si nécessaire. Pour les utilisateurs OpenAI, laissez-le vide)
- PRIMARY_MODEL=Qwen/Qwen3-14B # Recommandé Qwen3-14B ou un modèle de réflexion de niveau équivalent
- VL_MODEL="Pro/Qwen/Qwen2.5-VL-7B-Instruct" # Modèle visuel, optionnel mais recommandé. Utilisé pour analyser les images de page nécessaires (le programme décide en fonction du contexte si une analyse est nécessaire, pas chaque image n'est extraite), minimum Qwen2.5-VL-7B-Instruct requis

### 🚀  C'est parti !

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

✨ **C'est aussi simple que ça !** Le script de démarrage effectue automatiquement les tâches suivantes :
- ✅ Vérifie la configuration de l'environnement
- ✅ Synchronise les dépendances du projet
- ✅ Active l'environnement virtuel
- ✅ Démarre la base de données PocketBase
- ✅ Exécute l'application WiseFlow

Le programme effectue d'abord un crawl pour toutes les sources activées (activated défini sur true), puis exécute périodiquement à l'heure selon la fréquence définie.

⚠️ **Note :** Lorsque vous terminez le processus avec `Ctrl+C`, le processus PocketBase peut ne pas se terminer automatiquement et devra être fermé manuellement ou le terminal devra être redémarré.

### 📝 Installation manuelle (optionnel)

Si vous souhaitez contrôler manuellement chaque étape, vous pouvez également suivre ces étapes :

#### 1. Exécutez le script install_pocketbase dans le répertoire racine

Les utilisateurs Linux/macos doivent exécuter :

```bash
chmod +x install_pocketbase.sh
./install_pocketbase.sh
```

**Les utilisateurs Windows doivent exécuter :**
```powershell
.\install_pocketbase.ps1
```

#### 2. Créer et activer l'environnement virtuel

```bash
uv venv
source .venv/bin/activate  # Linux/macOS
# ou sous Windows :
# .venv\Scripts\activate
```

##### 4.2 Installer les dépendances

```bash
uv sync
```

Cela installe wiseflow et toutes ses dépendances et assure la cohérence des versions des dépendances. uv sync lit les déclarations de dépendances du projet et synchronise l'environnement virtuel.

Ensuite, installer les dépendances du navigateur :

```bash
python -m playwright install --with-deps chromium
```

Enfin, démarrer le service principal :

```bash
python core/run_task.py
# ou sous Windows :
# python core\run_task.py
```

Lorsque vous avez besoin de l'interface utilisateur PocketBase, démarrez le service PocketBase :

```bash
cd wiseflow/pb
./pocketbase serve
```

ou sous Windows :

```powershell
cd wiseflow\pb
.\pocketbase.exe serve
```

### 🔧 Configuration des variables d'environnement

Que ce soit pour le démarrage rapide ou l'installation manuelle, vous devez utiliser le fichier env_sample comme référence et créer un fichier .env :

#### 1. Configuration liée au LLM

wiseflow est une application native LLM. Veuillez vous assurer de fournir un service LLM stable au programme.

🌟 **wiseflow ne limite pas les fournisseurs de services de modèles, tant que le service est compatible avec le SDK OpenAI, y compris les services déployés localement comme ollama, Xinference, etc.**

##### Recommandation 1 : Utilisation du service MaaS de SiliconFlow

SiliconFlow propose des services MaaS pour la plupart des modèles open source courants. Grâce à leur propre technologie d'accélération d'inférence, ils ont de grands avantages en termes de vitesse et de prix. Lors de l'utilisation du service SiliconFlow, la configuration .env peut ressembler à ceci :

```
LLM_API_KEY=Votre_clé_API
LLM_API_BASE="https://api.siliconflow.com/v1" # Adresse de l'interface du service LLM (si nécessaire. Pour les utilisateurs OpenAI, laissez-le vide)
PRIMARY_MODEL=Qwen/Qwen3-14B # Recommandé Qwen3-14B ou un modèle de réflexion de niveau équivalent
VL_MODEL="Pro/Qwen/Qwen2.5-VL-7B-Instruct"
CONCURRENT_NUMBER=8
```
      
😄 Si vous le souhaitez, vous pouvez utiliser mon [lien d'invitation SiliconFlow](https://cloud.siliconflow.com/i/WNLYbBpi) pour que je puisse obtenir plus de récompenses de tokens 🌹

##### Recommandation 2 : Utilisation d'AiHubMix comme proxy pour OpenAI, Claude, Gemini et autres modèles commerciaux

Si vos sources d'information sont principalement des pages non chinoises et que vous ne demandez pas non plus que les informations extraites soient en chinois, nous recommandons d'utiliser OpenAI, Claude, Gemini et d'autres modèles commerciaux. Vous pouvez essayer le proxy tiers **AiHubMix**, qui prend en charge les connexions directes dans les réseaux chinois, les paiements pratiques via Alipay et évite le risque de blocage de compte.
Lors de l'utilisation des modèles AiHubMix, la configuration .env peut ressembler à ceci :

```
LLM_API_KEY=Votre_clé_API
LLM_API_BASE="https://aihubmix.com/v1" # voir https://doc.aihubmix.com/
PRIMARY_MODEL="gpt-4o-mini"
VL_MODEL="gpt-4o"
CONCURRENT_NUMBER=8
```

😄 Bienvenue pour vous inscrire via le [lien d'invitation AiHubMix](https://aihubmix.com?aff=Gp54) 🌹

##### Déploiement local du service LLM

En prenant l'exemple de Xinference, la configuration .env peut ressembler à ceci :

```
# LLM_API_KEY='' non requis pour les services locaux, veuillez commenter ou supprimer
LLM_API_BASE='http://127.0.0.1:9997' # 'http://127.0.0.1:11434/v1' pour ollama
PRIMARY_MODEL=ID_du_modèle_démarré
VL_MODEL=ID_du_modèle_démarré
CONCURRENT_NUMBER=1 # basé sur les ressources matérielles réelles
```

#### 3. Autres configurations optionnelles

Les suivantes sont des configurations optionnelles :
- #VERBOSE="true" 

  Si le mode d'observation doit être activé. Si activé, les informations de débogage seront enregistrées dans le fichier logger (par défaut, uniquement affichées dans la console)

- #CONCURRENT_NUMBER=8 

  Contrôle le nombre de requêtes LLM simultanées, par défaut 1 si non défini (veuillez vous assurer que le fournisseur LLM prend en charge la concurrence définie, à utiliser avec précaution pour les LLM locaux, sauf si vous êtes confiant dans votre base matérielle)

## 🐳 Déploiement Docker

Le schéma de déploiement Docker pour la version 4.x suivra plus tard. Nous espérons également des contributions PR de développeurs intéressés~

## 🌹 Services payants

L'open source n'est pas facile ☺️ La documentation et les conseils prennent beaucoup de temps. Si vous êtes prêt à fournir un soutien, nous offrons de meilleurs services~

- Vidéo tutoriel détaillée + 3 sessions de questions-réponses par e-mail + adhésion au groupe WeChat des utilisateurs payants : 36,88 ¥

Mode de paiement : Scannez le code QR ci-dessous, puis ajoutez WeChat : bigbrother666sh, et fournissez une capture d'écran du paiement.

(Les demandes d'ami seront acceptées dans un délai de 8 heures. Vous pouvez également nous contacter par e-mail à 35252986@qq.com)

<img src="alipay.png" alt="Code QR Alipay" width="300">      <img src="weixinpay.jpg" alt="Code QR WeChat Pay" width="300"> 