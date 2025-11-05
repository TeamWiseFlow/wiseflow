# KI-Chefintelligenzoffizier (Wiseflow)

**[简体中文](README.md) | [English](README_EN.md) | [日本語](README_JP.md) | [한국어](README_KR.md) | [Deutsch](README_DE.md) | [Français](README_FR.md) | [العربية](README_AR.md)**

[![Ask DeepWiki](https://deepwiki.com/badge.svg)](https://deepwiki.com/TeamWiseFlow/wiseflow)

🚀 **Nutzen Sie große Sprachmodelle, um täglich Informationen zu finden, die Sie wirklich interessieren, aus riesigen Datenmengen und verschiedenen Quellen!**

Was uns fehlt, ist nicht Information, sondern die Fähigkeit, Rauschen aus massiven Informationen zu filtern, um wertvolle Erkenntnisse zu gewinnen.

## 🎉  WiseFlow Pro Version jetzt verfügbar!

Erweiterte Crawling-Fähigkeiten, umfassende Social-Media-Unterstützung, UI-Oberfläche und One-Click-Installationspaket!

https://github.com/user-attachments/assets/880af7a3-7b28-44ff-86b6-aaedecd22761

🔥🔥 **Pro-Version ist jetzt weltweit verfügbar**: https://wiseflow.pro/ 

🔥 Mitwirkende, die PRs (Code, Dokumentation oder Erfolgsfall-Sharing) einreichen, erhalten bei Annahme ein Jahr lang Zugang zur WiseFlow Pro-Version (einschließlich verwandter LLM-Nutzungsgebühren)!

## 🔥🔥🔥 Wiseflow 4.2 Version offiziell veröffentlicht!

Version 4.2 verbessert die Web-Crawling-Fähigkeiten erheblich auf Basis der Versionen 4.0 und 4.1. Das Programm kann jetzt Ihren lokalen "echten" Chrome-Browser direkt zum Abrufen aufrufen. Dies reduziert nicht nur maximal die Wahrscheinlichkeit, von Zielseiten "risikokontrolliert" zu werden, sondern bringt auch neue Funktionen wie persistente Benutzerdaten und Unterstützung für Seitenoperationsskripte mit sich! (Zum Beispiel erfordern einige Websites eine Benutzeranmeldung, um vollständige Inhalte anzuzeigen. Sie können sich jetzt vorab anmelden und dann wiseflow verwenden, um vollständige Inhalte zu erhalten).

Da Version 4.2 Ihren lokalen Chrome-Browser direkt zum Crawlen verwendet, müssen Sie während der Bereitstellung nicht mehr `python -m playwright install --with-deps chromium` ausführen, aber Sie müssen **Google Chrome Browser mit dem Standard-Installationspfad installieren**.

Zusätzlich haben wir auch die Suchmaschinen-Lösung refaktoriert und eine vollständige Proxy-Lösung bereitgestellt. Details finden Sie im **[CHANGELOG](CHANGELOG.md)**

### 🔍 Benutzerdefinierte Suchquellen

4.1 Version unterstützt die präzise Konfiguration von Suchquellen für Fokuspunkte. Es werden derzeit bing, github und arxiv Suchquellen unterstützt, die alle native Plattform-APIs verwenden und keine zusätzlichen Drittanbieterdienste erfordern.

<img src="docs/select_search_source.gif" alt="search_source" width="360">

### 🧠 Lassen Sie die KI aus Ihrer Perspektive denken!

4.1 Version unterstützt die Einstellung von Rollen und Zielen für Fokuspunkte, um die LLM bei der Analyse und Extraktion von Informationen aus einer bestimmten Perspektive oder für einen bestimmten Zweck zu leiten. Bitte beachten Sie jedoch:

    - Wenn der Fokuspunkt selbst sehr spezifisch ist, hat die Einstellung von Rollen und Zielen nur geringe Auswirkungen auf die Ergebnisse.
    - Der wichtigste Faktor für die Qualität der Endergebnisse ist immer die Informationsquelle. Stellen Sie sicher, dass Sie Quellen bereitstellen, die für den Fokuspunkt von hoher Relevanz sind.

Testfälle zur Auswirkung der Einstellung von Rollen und Zielen auf die Extraktionsergebnisse finden Sie unter [task1](test/reports/report_v4x_llm/task1)

### ⚙️ Benutzerdefinierter Extraktionsmodus

Jetzt können Sie Ihre eigenen Formulare in der pb-Oberfläche erstellen und für bestimmte Fokuspunkte konfigurieren. Die LLM extrahiert dann Informationen genau nach den Formularfeldern.

### 👥 Creator-Suchmodus für Social-Media-Quellen

Jetzt können Sie das Programm anweisen, relevante Inhalte auf Social-Media-Plattformen basierend auf Fokuspunkten zu finden und die Homepage-Informationen der Inhaltsersteller weiter zu durchsuchen. In Kombination mit dem "Benutzerdefinierten Extraktionsmodus" kann Wiseflow Ihnen helfen, Kontaktinformationen von potenziellen Kunden, Partnern oder Investoren im gesamten Netzwerk zu suchen.

<img src="docs/find_person_by_wiseflow.png" alt="find_person_by_wiseflow" width="720">

## 🌹 Beste LLM-Konfigurationsanleitung

"Im LLM-Zeitalter sollten exzellente Entwickler mindestens 60% ihrer Zeit damit verbringen, das passende LLM-Modell auszuwählen" ☺️

Wir haben 7 Testsätze aus echten Projekten sorgfältig ausgewählt und eine breite Auswahl der Mainstream-Modelle mit Ausgabepreisen von nicht mehr als ￥4/M Tokens getestet. Dabei führten wir detaillierte wiseflow info extracting-Tests durch und kamen zu folgenden Nutzungsempfehlungen:

    - Für leistungsorientierte Szenarien empfehlen wir: ByteDance-Seed/Seed-OSS-36B-Instruct

    - Für kostenorientierte Szenarien empfehlen wir weiterhin: Qwen/Qwen3-14B

Für das visuelle Unterstützungsanalysemodell können Sie weiterhin verwenden: /Qwen/Qwen2.5-VL-7B-Instruct (wiseflow-Aufgaben sind derzeit wenig davon abhängig)

Detaillierte Testberichte finden Sie unter [LLM USE TEST](./test/reports/README_EN.md)

Es ist zu beachten, dass die obigen Testergebnisse nur die Leistung der Modelle bei wiseflow-Informationsextraktionsaufgaben repräsentieren und nicht die umfassenden Fähigkeiten der Modelle darstellen. Wiseflow-Informationsextraktionsaufgaben können sich deutlich von anderen Aufgabentypen (wie Planung, Schreiben usw.) unterscheiden. Außerdem sind die Kosten einer unserer Hauptfaktoren, da wiseflow-Aufgaben einen relativ hohen Modellverbrauch haben, insbesondere bei mehreren Informationsquellen und Fokuspunkten.

Wiseflow beschränkt sich nicht auf Modellanbieter, solange sie mit dem openaiSDK-Anfrageformat kompatibel sind. Sie können vorhandene Maas-Dienste oder lokale Modellbereitstellungsdienste wie Ollama wählen.

wir empfehlen die Nutzung des Modell-Service von [Siliconflow](https://www.siliconflow.com/).

Wenn Sie außerdem die openai-Serie bevorzugen, sind 'o3-mini' und 'openai/gpt-oss-20b' ebenfalls gute Optionen, für visuelle Unterstützungsanalyse können Sie gpt-4o-mini verwenden.

💰 Derzeit können Sie in der wiseflow-Anwendung offizielle openai-Serienmodelle über AiHubMix zum offiziellen Preis mit 10% Rabatt nutzen.

**Hinweis:** Um den Rabatt zu nutzen, müssen Sie zum aihubmix-Branch wechseln, siehe [README](https://github.com/TeamWiseFlow/wiseflow/blob/aihubmix/README.md)

## 🧐  Unterschied zu "ChatGPTs" / "Deepseeks" / "Doubao" etc.

Zunächst einmal wird wiseflow, wie diese Produkte, von LLM (großen Sprachmodellen) angetrieben. Da sie jedoch für unterschiedliche Zwecke entwickelt wurden, können "ChatGPTs" / "Deepseeks" / "Doubao" etc. in den folgenden beiden Szenarien Ihre Anforderungen möglicherweise nicht erfüllen (höchstwahrscheinlich finden Sie zu diesem Zeitpunkt kein Produkt, das besser für diese Anforderungen geeignet ist als wiseflow ☺️)

Sie müssen den neuesten Inhalt (innerhalb von Stunden veröffentlicht) von angegebenen Quellen abrufen und möchten keinen Teil verpassen, der Sie interessieren könnte

Zum Beispiel die Verfolgung von Richtlinienveröffentlichungen von autoritativen Institutionen, die Verfolgung von Branchen- oder Technologieinformationen, die Verfolgung von Wettbewerbsdynamiken oder Sie möchten einfach Informationen aus begrenzten hochwertigen Quellen erhalten (sich von der Kontrolle von Empfehlungsalgorithmen befreien 🤣) usw... "ChatGPTs" / "Deepseeks" / "Doubao" und andere allgemeine Q&A-Agenten überwachen keine angegebenen Quellen. Sie funktionieren wie Suchmaschinen, zielen auf Informationen im gesamten Netzwerk ab und können normalerweise nur "Second-Hand-Informationen" mit einer Verzögerung von 2-3 Tagen oder länger erhalten.

Sie müssen wiederholt angegebene Informationen aus dem Netzwerk (insbesondere sozialen Medien) entdecken und extrahieren

Zum Beispiel das Finden potenzieller Kunden, Lieferanten oder Investoren in bestimmten Bereichen aus sozialen Medien, das Sammeln ihrer Kontaktinformationen usw... Ebenso sind "ChatGPTs" / "Deepseeks" / "Doubao" und andere allgemeine Q&A-Agenten besser darin, Antworten zusammenzufassen und zu verfeinern, anstatt Informationen zu sammeln und zu organisieren.

## ✋ Unterschied zu "Crawlern" oder RPA

Zunächst einmal ist wiseflow kein Crawler und auch kein traditionelles RPA!

Wiseflow verwendet Ihren Browser, um in Ihrem Namen mit echtem menschlichem Verhalten zu operieren (dies basiert natürlich auf LLM, sogar visuelles LLM). In diesem Prozess gibt es kein nicht-konformes Verhalten. Für alle Anmelde- und Verifizierungsvorgänge wird wiseflow Benutzer nur benachrichtigen und nicht übertreten. Natürlich müssen Sie diese Vorgänge nur einmal während der Gültigkeitsdauer ausführen, und wiseflow behält den Anmeldestatus bei (aber nicht den Benutzernamen und das Passwort. Tatsächlich kann wiseflow überhaupt keine Benutzernamen oder Passwörter lesen, die Sie eingeben. Alle Ihre Vorgänge werden auf den echten offiziellen Seiten durchgeführt).

Da wiseflow echte Browser (anstatt headless Browser, virtuelle Browser usw.) verwendet und echtes Benutzer-Browsing-Verhalten vollständig simuliert, hat es stärkere Anti-Erkennungsfähigkeiten als "Crawler" und RPA. Darüber hinaus hat es die folgenden Funktionen:

- Vollständige Plattform-Erfassungsfähigkeiten: Unterstützt Websites, RSS, Weibo, Kuaishou, Bing, GitHub, arXiv, eBay usw. Die Pro-Version unterstützt zusätzlich WeChat Official Account, Xiaohongshu, Zhihu, Bilibili und Douyin.
- Innovativer HTML-Intelligenz-Analysemechanismus: Kann wichtige Informationen und Links, die es wert sind, weiter erforscht zu werden, automatisch identifizieren.
- "Crawl-and-Search-in-One"-Strategie: Echtzeit-LLM-Beurteilung und -Extraktion während des Crawlens, erfasst nur relevante Informationen und reduziert Risikokontrollrisiken erheblich.
- Wirklich sofort einsatzbereit: Keine Notwendigkeit für Xpath, Skripte oder manuelle Konfiguration. Gewöhnliche Benutzer können es leicht verwenden.
- Keine Sorge um LLM-Nutzungsgebühren: Alle LLM-Aufrufgebühren sind im Abonnement enthalten, keine Notwendigkeit, Dienste oder Schlüssel separat zu konfigurieren.

## 🌟 Schnellstart

**Nur drei Schritte zum Start!**

**Ab Version 4.2 muss zuerst Google Chrome Browser installiert werden (mit Standard-Installationspfad)**

**Windows-Benutzer laden bitte zuerst das Git Bash-Tool herunter und führen die folgenden Befehle in bash aus [Bash-Download-Link](https://git-scm.com/downloads/win)**

### 📋 Projektquellcode herunterladen und uv sowie pocketbase installieren

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
git clone https://github.com/TeamWiseFlow/wiseflow.git
```

Die obigen Operationen vervollständigen die Installation von uv.

Gehen Sie dann zu [pocketbase docs](https://pocketbase.io/docs/), um das entsprechende pocketbase-Programm für Ihr System herunterzuladen und in den [.pb](./pb/) Ordner zu legen.

Sie können auch versuchen, install_pocketbase.sh (für MacOS/Linux) oder install_pocketbase.ps1 (für Windows) zur Installation zu verwenden.

### 📥 .env-Datei basierend auf env_sample konfigurieren

Im wiseflow-Ordner (Projektstammverzeichnis) erstellen Sie eine .env-Datei basierend auf env_sample und füllen Sie die relevanten Einstellungen aus

Die Version 4.x erfordert keine pocketbase-Anmeldedaten in der .env-Datei und hat keine Versionsbeschränkungen für pocketbase. Außerdem haben wir vorübergehend die Secondary Model-Einstellung entfernt. Daher benötigen Sie nur vier Parameter für die Konfiguration:

- LLM_API_KEY=""
- LLM_API_BASE=""
- PRIMARY_MODEL=ByteDance-Seed/Seed-OSS-36B-Instruct # Für preissensitive und nicht komplexe Extraktionsszenarien kann Qwen3-14B verwendet werden
- VL_MODEL=Pro/Qwen/Qwen2.5-VL-7B-Instruct

### 🚀 Starten!

```bash
cd wiseflow
uv venv # nur beim ersten Starten benötigt
source .venv/bin/activate  # Linux/macOS
# oder Windows:
# .venv\Scripts\activate
uv sync # nur beim ersten Starten benötigt
chmod +x run.sh # nur beim ersten Starten benötigt
./run.sh  # Linux/macOS
.\run.bat  # Windows
```

Detaillierte Anweisungen finden Sie unter [docs/manual/manual_de.md](./docs/manual/manual_de.md)

## 📚 Wie Sie von Wiseflow gecrawlte Daten in Ihren eigenen Programmen verwenden können

Alle von Wiseflow gecrawlten Daten werden sofort in pocketbase gespeichert, sodass Sie direkt auf die pocketbase-Datenbank zugreifen können, um Daten zu erhalten.

Als beliebte leichte Datenbank bietet PocketBase derzeit SDKs für Go/Javascript/Python und andere Sprachen.

Wir laden Sie ein, Ihre Beispiele für sekundäre Entwicklungsanwendungen im folgenden Repository zu teilen und zu fördern!

- https://github.com/TeamWiseFlow/wiseflow-plus

(Beiträge von PRs zu diesem Repository gewähren ebenfalls ein Jahr lang Zugang zur WiseFlow Pro-Version bei Annahme)

## 🛡️ Lizenz

Ab Version 4.2 haben wir die Open-Source-Lizenz aktualisiert, bitte lesen Sie: [LICENSE](LICENSE)

Für kommerzielle Zusammenarbeit kontaktieren Sie bitte **Email: zm.zhao@foxmail.com**

## 📬 Kontakt

Bei Fragen oder Vorschlägen hinterlassen Sie bitte eine Nachricht über [issue](https://github.com/TeamWiseFlow/wiseflow/issues).

## 🤝 Dieses Projekt basiert auf folgenden hervorragenden Open-Source-Projekten:

- Crawl4ai (Open-Source LLM-freundlicher Web-Crawler & Scraper) https://github.com/unclecode/crawl4ai
- MediaCrawler (xhs/dy/wb/ks/bilibili/zhihu crawler) https://github.com/NanmiCoder/MediaCrawler
- Patchright(Undetected Python version of the Playwright testing and automation library) https://github.com/Kaliiiiiiiiii-Vinyzu/patchright-python
- NoDriver (Bietet ein blitzschnelles Framework für Web-Automatisierung, Web-Scraping, Bots und andere kreative Ideen...) https://github.com/ultrafunkamsterdam/nodriver
- Pocketbase (Open Source Echtzeit-Backend in 1 Datei) https://github.com/pocketbase/pocketbase
- Feedparser (Feeds in Python parsen) https://github.com/kurtmckee/feedparser
- SearXNG（a free internet metasearch engine which aggregates results from various search services and databases） https://github.com/searxng/searxng

## Zitation

Wenn Sie in verwandten Arbeiten auf dieses Projekt teilweise oder vollständig verweisen oder es zitieren, notieren Sie bitte die folgenden Informationen:

```
Autor: Wiseflow Team
https://github.com/TeamWiseFlow/wiseflow
```

## Freundliche Links

[<img src="docs/logos/SiliconFlow.png" alt="siliconflow" width="360">](https://siliconflow.com/)