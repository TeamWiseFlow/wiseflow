# KI-Chefintelligenzoffizier (Wiseflow)

**[简体中文](README.md) | [English](README_EN.md) | [日本語](README_JP.md) | [한국어](README_KR.md) | [Deutsch](README_DE.md) | [Français](README_FR.md) | [العربية](README_AR.md)**

🚀 **Nutzen Sie große Sprachmodelle, um täglich Informationen zu finden, die Sie wirklich interessieren, aus riesigen Datenmengen und verschiedenen Quellen!**

Was uns fehlt, ist nicht Information, sondern die Fähigkeit, Rauschen aus massiven Informationen zu filtern, um wertvolle Erkenntnisse zu gewinnen.

## 🔥🔥🔥 Wiseflow 4.0 Version offiziell veröffentlicht!

https://github.com/user-attachments/assets/2c52c010-6ae7-47f4-bc1c-5880c4bd76f3

(Der Online-Dienst ist derzeit aus technischen Gründen noch nicht auf den 4.0-Kern umgestellt, wir beschleunigen das Upgrade)

Nach drei Monaten Warten haben wir endlich die Freude, die offizielle Veröffentlichung der wiseflow 4.0-Version bekannt zu geben! Diese Version bringt eine völlig neue 4.x-Architektur, unterstützt soziale Medienquellen und bietet viele neue Funktionen.

4.x enthält WIS Crawler (basierend auf Crawl4ai, MediaCrawler und Nodriver, tief verändert und integriert), der jetzt Unterstützung für Webseiten und soziale Medienquellen bietet.

Die Open-Source-Version bietet Unterstützung für Weibo und Kuaishou, während die **Pro-Version** zusätzlich unterstützt:

WeChat-Offizielle Konten, Xiaohongshu, Douyin, Bilibili, Zhihu...

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
- Einzigartiger HTML-Verarbeitungsprozess, der automatisch Informationen basierend auf Fokuspunkten extrahiert und Links für weitere Erkundung entdeckt, funktioniert gut mit nur einem 14b-Parameter-LLM;
- Benutzerfreundlich (nicht nur für Entwickler), keine manuelle Xpath-Konfiguration erforderlich, "sofort einsatzbereit";
- Hohe Stabilität und Verfügbarkeit durch kontinuierliche Iteration und Verarbeitungseffizienz, die Systemressourcen und Geschwindigkeit ausbalanciert;
- Es wird mehr sein als nur ein "Crawler"...

<img src="docs/wiseflow4.xscope.png" alt="4.x full scope" width="720">

(4.x Architektur-Gesamtumfang. Der gestrichelte Kasten zeigt die unfertigen Teile. Wir hoffen, dass fähige Community-Entwickler sich uns anschließen und PRs beisteuern. Alle Beitragenden erhalten kostenlosen Zugang zur Pro-Version!)

## 🌟 Schnellstart

**Nur drei Schritte zum Start!**

**Windows-Benutzer laden bitte zuerst das Git Bash-Tool herunter und führen die folgenden Befehle in bash aus [Bash-Download-Link](https://git-scm.com/downloads/win)**

### 📋 Projektquellcode herunterladen und uv sowie pocketbase installieren

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
git clone https://github.com/TeamWiseFlow/wiseflow.git
```

Die obigen Operationen vervollständigen die Installation von uv. 

Next, go to [pocketbase docs](https://pocketbase.io/docs/) to download the corresponding pocketbase program for your system and place it in the [.pb](./pb/) folder.

Sie können auch versuchen, install_pocketbase.sh (für MacOS/Linux) oder install_pocketbase.ps1 (für Windows) zur Installation zu verwenden.

### 📥 .env-Datei basierend auf env_sample konfigurieren

Im wiseflow-Ordner (Projektstammverzeichnis) erstellen Sie eine .env-Datei basierend auf env_sample und füllen Sie die relevanten Einstellungen aus

Die Version 4.x erfordert keine pocketbase-Anmeldedaten in der .env-Datei und hat keine Versionsbeschränkungen für pocketbase. Außerdem haben wir vorübergehend die Secondary Model-Einstellung entfernt. Daher benötigen Sie nur vier Parameter für die Konfiguration:

- LLM_API_KEY="" # Schlüssel für den LLM-Dienst (jeder Modellanbieter mit OpenAI-Format-API, nicht erforderlich bei lokaler ollama-Installation)
- LLM_API_BASE="https://api.siliconflow.cn/v1" # LLM-Dienstschnittstellenadresse
- JINA_API_KEY="" # Schlüssel für den Suchmaschinendienst (Jina empfohlen, für persönliche Nutzung sogar ohne Registrierung verfügbar)
- PRIMARY_MODEL="Qwen/Qwen3-14B" # Qwen3-14B oder ein gleichwertiges Denkmodell empfohlen
- VL_MODEL="Pro/Qwen/Qwen2.5-VL-7B-Instruct" # besser zu haben

### 🚀 Starten!

```bash
cd wiseflow
uv venv # nur beim ersten Starten benötigt
source .venv/bin/activate  # Linux/macOS
# oder Windows:
# .venv\Scripts\activate
uv sync # nur beim ersten Starten benötigt
python -m playwright install --with-deps chromium # nur beim ersten Starten benötigt
chmod +x run.sh # nur beim ersten Starten benötigt
./run.sh
```

Detaillierte Anweisungen finden Sie unter [docs/manual/manual_de.md](./docs/manual/manual_de.md)

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