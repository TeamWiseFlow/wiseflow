Wir bieten einen allgemeinen Seitenparser an, der intelligent Artikellisten von Quellen abrufen kann. Für jede Artikel-URL wird zuerst versucht, `gne` zur Analyse zu verwenden. Falls dies fehlschlägt, wird `llm` als Alternative genutzt.

Diese Lösung ermöglicht das Scannen und Extrahieren von Informationen aus den meisten allgemeinen Nachrichtenquellen und Portalen.

**Wir empfehlen jedoch dringend, benutzerdefinierte Parser für spezifische Quellen zu entwickeln, die auf Ihre tatsächlichen Geschäftsszenarien abgestimmt sind, um eine idealere und effizientere Erfassung zu erreichen.**

Wir stellen auch einen speziellen Parser für WeChat-Artikel (mp.weixin.qq.com) bereit.

**Falls Sie bereit sind, Ihre speziell entwickelten Parser für bestimmte Quellen zu diesem Code-Repository beizutragen, wären wir Ihnen sehr dankbar!**

## Entwicklungsspezifikationen für benutzerdefinierte Quellparser

### Spezifikationen

**Denken Sie daran: Es sollte eine asynchrone Funktion sein**

1. **Der Parser sollte in der Lage sein, intelligent zwischen Artikel-Listen-Seiten und Artikel-Detailseiten zu unterscheiden.**
2. **Die Eingabeparameter des Parsers sollten nur `url` und `logger` umfassen:**
   - `url` ist die vollständige Adresse der Quelle (Typ `str`).
   - `logger` ist das Protokollierungsobjekt (bitte konfigurieren Sie keinen separaten Logger für Ihren benutzerdefinierten Quellparser).
3. **Die Ausgabe des Parsers sollte `flag` und `result` umfassen, im Format `tuple[int, Union[set, dict]]`:**
   - Wenn die `url` eine Artikellisten-Seite ist, gibt `flag` `1` zurück, und `result` gibt eine satz aller Artikel-URLs (`set`) zurück.
   - Wenn die `url` eine Artikelseite ist, gibt `flag` `11` zurück, und `result` gibt alle Artikeldetails (`dict`) zurück, im folgenden Format:

     ```python
     {'url': str, 'title': str, 'author': str, 'publish_time': str, 'content': str, 'abstract': str, 'images': [str]}
     ```

     _Hinweis: `title` und `content` dürfen nicht leer sein._

     **Hinweis: Das `publish_time`-Format muss `"%Y%m%d"` (nur Datum, ohne `-`) sein. Wenn der Scraper es nicht erfassen kann, verwenden Sie das aktuelle Datum.**

   - Wenn die Analyse fehlschlägt, gibt `flag` `0` zurück, und `result` gibt ein leeres Wörterbuch `{}` zurück.

     _Der `pipeline` versucht andere Analysemethoden (falls vorhanden), wenn `flag` 0 zurückgegeben wird._

   - Wenn das Abrufen der Seite fehlschlägt (z. B. aufgrund von Netzwerkproblemen), gibt `flag` `-7` zurück, und `result` gibt ein leeres Wörterbuch `{}` zurück.

     _Der `pipeline` wird im gleichen Prozess keine weiteren Versuche zur Analyse unternehmen, wenn `flag` -7 zurückgegeben wird._

### Registrierung

Nach dem Schreiben Ihres Scrapers platzieren Sie das Scraper-Programm in diesem Ordner und registrieren den Scraper in `scraper_map` in `__init__.py`, wie folgt:

```python
{'domain': 'Crawler-Funktionsname'}
```

Es wird empfohlen, urllib.parse zur Ermittlung der domain zu verwenden:

```python
from urllib.parse import urlparse

parsed_url = urlparse("l'URL du site")
domain = parsed_url.netloc
```