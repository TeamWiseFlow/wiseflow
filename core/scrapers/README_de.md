**In diesem Ordner können Crawlers für spezifische Quellen abgelegt werden. Beachten Sie, dass die Crawlers hier in der Lage sein sollten, die URL der Artikelliste der Quelle zu analysieren und ein Wörterbuch mit Artikeldetails zurückzugeben.**
> 
> # Konfiguration des benutzerdefinierten Crawlers
> 
> Nachdem Sie den Crawler geschrieben haben, platzieren Sie das Crawler-Programm in diesem Ordner und registrieren Sie es in scraper_map in `__init__.py`, ähnlich wie:
> 
> ```python
> {'www.securityaffairs.com': securityaffairs_scraper}
> ```
> 
> Hier ist der Schlüssel die URL der Quelle und der Wert der Funktionsname.
> 
> Der Crawler sollte in Form einer Funktion geschrieben werden, mit den folgenden Eingabe- und Ausgabeparametern:
> 
> Eingabe:
> - expiration: Ein `datetime.date` Objekt, der Crawler sollte nur Artikel ab diesem Datum (einschließlich) abrufen.
> - existings: [str], eine Liste von URLs von Artikeln, die bereits in der Datenbank vorhanden sind. Der Crawler sollte die URLs in dieser Liste ignorieren.
> 
> Ausgabe:
> - [dict], eine Liste von Ergebnis-Wörterbüchern, wobei jedes Wörterbuch einen Artikel darstellt, formatiert wie folgt:
> `[{'url': str, 'title': str, 'author': str, 'publish_time': str, 'content': str, 'abstract': str, 'images': [Path]}, {...}, ...]`
> 
> Hinweis: Das Format von `publish_time` sollte `"%Y%m%d"` sein. Wenn der Crawler es nicht abrufen kann, kann das aktuelle Datum verwendet werden.
> 
> Darüber hinaus sind `title` und `content` Pflichtfelder.
> 
> # Generischer Seitenparser
> 
> Wir bieten hier einen generischen Seitenparser an, der intelligent Artikellisten von der Quelle abrufen kann. Für jede Artikel-URL wird zunächst versucht, mit gne zu parsen. Scheitert dies, wird versucht, mit llm zu parsen.
> 
> Durch diese Lösung ist es möglich, die meisten allgemeinen Nachrichtenquellen und Portale zu scannen und Informationen zu extrahieren.
> 
> **Wir empfehlen jedoch dringend, dass Benutzer eigene benutzerdefinierte Crawlers schreiben oder direkt unseren Datenservice abonnieren, um eine idealere und effizientere Erfassung zu erreichen.**