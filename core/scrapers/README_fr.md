**Ce dossier est destiné à accueillir des crawlers spécifiques à des sources particulières. Notez que les crawlers ici doivent être capables de parser l'URL de la liste des articles de la source et de retourner un dictionnaire de détails des articles.**
> 
> # Configuration du Crawler Personnalisé
> 
> Après avoir écrit le crawler, placez le programme du crawler dans ce dossier et enregistrez-le dans scraper_map dans `__init__.py`, comme suit :
> 
> ```python
> {'www.securityaffairs.com': securityaffairs_scraper}
> ```
> 
> Ici, la clé est l'URL de la source, et la valeur est le nom de la fonction.
> 
> Le crawler doit être écrit sous forme de fonction avec les spécifications suivantes pour les entrées et sorties :
> 
> Entrée :
> - expiration : Un objet `datetime.date`, le crawler ne doit récupérer que les articles à partir de cette date (incluse).
> - existings : [str], une liste d'URLs d'articles déjà présents dans la base de données. Le crawler doit ignorer les URLs de cette liste.
> 
> Sortie :
> - [dict], une liste de dictionnaires de résultats, chaque dictionnaire représentant un article, formaté comme suit :
> `[{'url': str, 'title': str, 'author': str, 'publish_time': str, 'content': str, 'abstract': str, 'images': [Path]}, {...}, ...]`
> 
> Remarque : Le format de `publish_time` doit être `"%Y%m%d"`. Si le crawler ne peut pas le récupérer, la date du jour peut être utilisée.
> 
> De plus, `title` et `content` sont des champs obligatoires.
> 
> # Analyseur de Page Générique
> 
> Nous fournissons ici un analyseur de page générique, qui peut récupérer intelligemment les listes d'articles de la source. Pour chaque URL d'article, il tentera d'abord de parser avec gne. En cas d'échec, il tentera de parser avec llm.
> 
> Grâce à cette solution, il est possible de scanner et d'extraire des informations à partir de la plupart des sources de type actualités générales et portails.
> 
> **Cependant, nous recommandons vivement aux utilisateurs de rédiger eux-mêmes des crawlers personnalisés ou de s'abonner directement à notre service de données pour un scan plus idéal et plus efficace.**