Nous proposons un analyseur de pages général capable de récupérer intelligemment les listes d'articles de sources d'information. Pour chaque URL d'article, il tente d'abord d'utiliser `gne` pour l'analyse, et en cas d'échec, il essaie d'utiliser `llm`.

Cette solution permet de scanner et d'extraire des informations de la plupart des sources de nouvelles générales et des portails d'information.

**Cependant, nous recommandons vivement aux utilisateurs de développer des analyseurs personnalisés pour des sources spécifiques en fonction de leurs scénarios d'affaires réels afin d'obtenir une analyse plus idéale et plus efficace.**

Nous fournissons également un analyseur spécialement conçu pour les articles publics WeChat (mp.weixin.qq.com).

**Si vous êtes disposé à contribuer vos analyseurs spécifiques à certaines sources à ce dépôt de code, nous vous en serions très reconnaissants !**

## Spécifications pour le Développement d'Analyseurs Spécifiques

### Spécifications

**N'oubliez pas : il devrait s'agir d'une fonction asynchrone**

1. **L'analyseur doit être capable de distinguer intelligemment entre les pages de liste d'articles et les pages de détail des articles.**
2. **Les paramètres d'entrée de l'analyseur doivent uniquement inclure `url` et `logger` :**
   - `url` est l'adresse complète de la source (type `str`).
   - `logger` est l'objet de journalisation (ne configurez pas de logger séparé pour votre analyseur spécifique).
3. **Les paramètres de sortie de l'analyseur doivent inclure `flag` et `result`, formatés comme `tuple[int, Union[list, dict]]` :**
   - Si l'URL est une page de liste d'articles, `flag` renvoie `1` et `result` renvoie la liste de toutes les URL des pages d'articles (`list`).
   - Si l'URL est une page d'article, `flag` renvoie `11` et `result` renvoie tous les détails de l'article (`dict`), au format suivant :

     ```python
     {'url': str, 'title': str, 'author': str, 'publish_time': str, 'content': str, 'abstract': str, 'images': [str]}
     ```

     _Remarque : `title` et `content` ne peuvent pas être vides._

     **Remarque : `publish_time` doit être au format `"%Y%m%d"` (date uniquement, sans `-`). Si le scraper ne peut pas le récupérer, utilisez la date du jour.**

   - En cas d'échec de l'analyse, `flag` renvoie `0` et `result` renvoie un dictionnaire vide `{}`.

     _Le `pipeline` essaiera d'autres solutions d'analyse (si disponibles) après avoir reçu `flag` 0._

   - En cas d'échec de la récupération de la page (par exemple, problème réseau), `flag` renvoie `-7` et `result` renvoie un dictionnaire vide `{}`.

     _Le `pipeline` n'essaiera pas de réanalyser dans le même processus après avoir reçu `flag` -7._

### Enregistrement

Après avoir écrit votre scraper, placez le programme du scraper dans ce dossier et enregistrez le scraper dans `scraper_map` sous `__init__.py`, de manière similaire :

```python
{'domain': 'nom de la fonction de crawler'}
```

Il est recommandé d'utiliser urllib.parse pour obtenir le domain :

```python
from urllib.parse import urlparse

parsed_url = urlparse("l'URL du site")
domain = parsed_url.netloc
```