# KI-Chefintelligenzoffizier (Wiseflow)

**[English](README_EN.md) | [日本語](README_JP.md) | [한국어](README_KR.md) | [Deutsch](README_DE.md) | [Français](README_FR.md)**

🚀 **Nutzen Sie große Sprachmodelle, um täglich Informationen zu finden, die Sie wirklich interessieren, aus riesigen Datenmengen und verschiedenen Quellen!**

Was uns fehlt, ist nicht Information, sondern die Fähigkeit, Rauschen aus massiven Informationen zu filtern, um wertvolle Erkenntnisse zu gewinnen.

🌱 Sehen Sie, wie der KI-Intelligenzoffizier Ihnen hilft, Zeit zu sparen, irrelevante Informationen zu filtern und wichtige Punkte zu organisieren! 🌱

https://github.com/user-attachments/assets/fc328977-2366-4271-9909-a89d9e34a07b

## 🔥🔥🔥 Wiseflow 4.0 Version offiziell veröffentlicht!

(Der Online-Dienst ist derzeit aus technischen Gründen noch nicht auf den 4.0-Kern umgestellt, wir beschleunigen das Upgrade)

Nach einer dreimonatigen Wartezeit begrüßen wir endlich die offizielle Veröffentlichung von Wiseflow 4.0!

Diese Version bringt eine brandneue 4.x-Architektur, führt Unterstützung für Social-Media-Quellen ein und bietet viele neue Funktionen.

🌟 4.x enthält WIS Crawler (tiefgreifend umstrukturiert und integriert basierend auf Crawl4ai, MediaCrawler und Nodriver), der jetzt Webseiten und Social Media perfekt unterstützt. Version 4.0 bietet zunächst Unterstützung für Weibo- und Kuaishou-Plattformen, mit Plänen, weitere Plattformen hinzuzufügen, darunter:
WeChat Official Accounts, Xiaohongshu, Douyin, Bilibili, Zhihu...

Andere neue Funktionen der 4.x-Architektur:

- Neue Architektur, hybride Nutzung von Async und Thread-Pools, deutlich verbesserte Verarbeitungseffizienz (bei gleichzeitiger Reduzierung des Speicherverbrauchs);
- Übernommene Dispatcher-Fähigkeiten von Crawl4ai 0.6.3, bietet verfeinerte Speicherverwaltung;
- Tiefe Integration von Pre-Process aus Version 3.9 und Crawl4ai's Markdown Generation-Prozess, vermeidet doppelte Verarbeitung;
- Optimierte Unterstützung für RSS-Quellen;
- Optimierte Repository-Dateistruktur, klarer und konformer mit zeitgenössischen Python-Projektstandards;
- Umstellung auf uv für die Abhängigkeitsverwaltung und Optimierung der requirement.txt-Datei;
- Optimierte Startskripte (mit Windows-Version), ermöglicht wirklich "One-Click-Start";
- Optimierter Konfigurations- und Bereitstellungsprozess, Backend-Programm ist nicht mehr von pocketbase-Service abhängig, daher keine Notwendigkeit für pocketbase-Anmeldedaten in .env und keine Versionsbeschränkungen für pocketbase.

## 🧐 'Deep Search' VS 'Wide Search'

Ich positioniere Wiseflow als "Wide Search", was im Gegensatz zum derzeit populären "Deep Search" steht.

Konkret ist "Deep Search", wo LLM für spezifische Fragen autonom Suchpfade plant, kontinuierlich verschiedene Seiten erkundet, ausreichend Informationen sammelt, um Antworten oder Berichte zu generieren. Manchmal suchen wir jedoch ohne spezifische Fragen und benötigen keine tiefe Exploration, sondern nur breite Informationssammlung (wie Branchenintelligenz, Hintergrundinformationssammlung, Kundeninformationssammlung etc.). In diesen Fällen ist Breite eindeutig sinnvoller. Während "Deep Search" diese Aufgabe auch erfüllen kann, ist es wie mit einer Kanone auf eine Mücke schießen - ineffizient und kostspielig. Wiseflow ist speziell für diese "Wide Search"-Szenarien entwickelt.

## ✋ Was macht Wiseflow anders als andere KI-gestützte Crawler?

- Vollständige Plattform-Erfassungsfähigkeiten, einschließlich Webseiten, Social Media (derzeit Unterstützung für Weibo- und Kuaishou-Plattformen), RSS-Quellen, Suchmaschinen etc.;
- Nicht nur Crawling, sondern automatische Analyse und Filterung, funktioniert gut mit nur einem 14b-Parameter-LLM;
- Benutzerfreundlich (nicht nur für Entwickler), keine Codierung erforderlich, "sofort einsatzbereit";
- Hohe Stabilität und Verfügbarkeit durch kontinuierliche Iteration und Verarbeitungseffizienz, die Systemressourcen und Geschwindigkeit ausbalanciert;
- (Zukunft) Fähigkeit, "versteckte Informationen" unter erworbenen Informationen durch das Insight-Modul zu erschließen

……… Wir freuen uns auch auf interessierte Entwickler, die uns beitreten, um einen KI-Chefintelligenzoffizier zu bauen, der für jeden zugänglich ist!

## 🚀 Schnellstart

**Nur drei Schritte zum Start!**

### 📋 Projektquellcode herunterladen und uv sowie pocketbase installieren

- für MacOS/Linux:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
git clone https://github.com/TeamWiseFlow/wiseflow.git
```

- für Windows:

**Windows-Benutzer laden bitte zuerst das Git Bash-Tool herunter und führen die folgenden Befehle in bash aus [Bash-Download-Link](https://git-scm.com/downloads/win)**

```bash
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
git clone https://github.com/TeamWiseFlow/wiseflow.git
```

🌟 Die obigen Operationen vervollständigen die Installation von uv. Für die pocketbase-Installation siehe [pocketbase docs](https://pocketbase.io/docs/)

Sie können auch versuchen, install_pocketbase.sh (für MacOS/Linux) oder install_pocketbase.ps1 (für Windows) zur Installation zu verwenden.

### 📥 .env-Datei basierend auf env_sample konfigurieren

Im wiseflow-Ordner (Projektstammverzeichnis) erstellen Sie eine .env-Datei basierend auf env_sample und füllen Sie die relevanten Einstellungen aus

### 🚀 Starten!

- für MacOS/Linux:

```bash
cd wiseflow
./run.sh
```

(Hinweis: Möglicherweise müssen Sie zuerst `chmod +x run.sh` ausführen, um Ausführungsrechte zu gewähren)

- für Windows:

```bash
cd wiseflow
.\run.ps1
```

(Hinweis: Möglicherweise müssen Sie zuerst `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser` ausführen, um Ausführungsrechte zu gewähren)

Bei Problemen mit dem Start des virtuellen Browsers können Sie folgenden Befehl ausführen:

```bash
python -m playwright install --with-deps chromium
```

Detaillierte Anweisungen finden Sie unter [docs/manual.md](./docs/manual.md)

## 📚 Wie Sie von Wiseflow gecrawlte Daten in Ihren eigenen Programmen verwenden können

Alle von Wiseflow gecrawlten Daten werden sofort in pocketbase gespeichert, sodass Sie direkt auf die pocketbase-Datenbank zugreifen können, um Daten zu erhalten.

Als beliebte leichte Datenbank bietet PocketBase derzeit SDKs für Go/Javascript/Python und andere Sprachen.

Der Online-Dienst wird bald eine Sync-API einführen, die die Synchronisierung von Online-Crawling-Ergebnissen lokal unterstützt, für den Aufbau von "dynamischen Wissensbasen" und mehr, bleiben Sie dran:

  - Online-Erfahrungsadresse: https://www.aiqingbaoguan.com/
  - Online-Dienst-API-Nutzungsbeispiele: https://github.com/TeamWiseFlow/wiseflow_plus

## 🛡️ Lizenz

Dieses Projekt ist unter [Apache2.0](LICENSE) Open Source.

Für kommerzielle Zusammenarbeit kontaktieren Sie bitte **Email: zm.zhao@foxmail.com**

- Kommerzielle Kunden kontaktieren Sie uns bitte zur Registrierung, die Open-Source-Version verspricht, für immer kostenlos zu sein.

## 📬 Kontakt

Bei Fragen oder Vorschlägen hinterlassen Sie bitte eine Nachricht über [issue](https://github.com/TeamWiseFlow/wiseflow/issues).

## 🤝 Dieses Projekt basiert auf folgenden hervorragenden Open-Source-Projekten:

- Crawl4ai (Open-Source LLM-freundlicher Web-Crawler & Scraper) https://github.com/unclecode/crawl4ai
- MediaCrawler (xhs/dy/wb/ks/bilibili/zhihu crawler) https://github.com/NanmiCoder/MediaCrawler
- NoDriver (Bietet ein blitzschnelles Framework für Web-Automatisierung, Web-Scraping, Bots und andere kreative Ideen...) https://github.com/ultrafunkamsterdam/nodriver
- Pocketbase (Open Source Echtzeit-Backend in 1 Datei) https://github.com/pocketbase/pocketbase
- Feedparser (Feeds in Python parsen) https://github.com/kurtmckee/feedparser

Die Entwicklung dieses Projekts wurde inspiriert von [GNE](https://github.com/GeneralNewsExtractor/GeneralNewsExtractor), [AutoCrawler](https://github.com/kingname/AutoCrawler) und [SeeAct](https://github.com/OSU-NLP-Group/SeeAct).

## Zitation

Wenn Sie in verwandten Arbeiten auf dieses Projekt teilweise oder vollständig verweisen oder es zitieren, notieren Sie bitte die folgenden Informationen:

```
Autor: Wiseflow Team
https://github.com/TeamWiseFlow/wiseflow
Lizenziert unter Apache2.0
``` 