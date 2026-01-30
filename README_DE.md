# AI-Chefintelligenzoffizier (Wiseflow)

**[简体中文](README.md) | [English](README_EN.md) | [日本語](README_JP.md) | [한국어](README_KR.md) | [Deutsch](README_DE.md) | [Français](README_FR.md) | [العربية](README_AR.md)**

[![Ask DeepWiki](https://deepwiki.com/badge.svg)](https://deepwiki.com/TeamWiseFlow/wiseflow)

🚀 **Kontinuierliche Extraktion der benötigten Informationen aus dem gesamten Internet**

Unterstützt gängige Self-Media-Plattformen, Websites, die eine Voranmeldung erfordern, gezieltes Tracking von Quellen, tägliche Erfassung über geplante Aufgaben, automatische Extraktion durch große Sprachmodelle (Zusammenfassungsmodus, benutzerdefinierter Formularmodus)……

## 🎉 WiseFlow Pro Version jetzt verfügbar!

Stärkere Crawling-Fähigkeiten, umfassendere Social-Media-Unterstützung, inklusive Web-UI und installationsfreies One-Click-Ausführungspaket!

https://github.com/user-attachments/assets/880af7a3-7b28-44ff-86b6-aaedecd22761

🔥🔥 **Pro-Version ist jetzt weltweit verfügbar**: https://shouxiqingbaoguan.com/ 

🌹 Ab heute erhalten Mitwirkende, die PRs (Code, Dokumentation, Teilen von Erfolgsgeschichten sind willkommen) für die Open-Source-Version von wiseflow einreichen, nach Annahme eine einjährige Nutzungslizenz für die wiseflow pro Version!

## Wiseflow Open-Source-Version

Ab Version 4.30 wurde die wiseflow Open-Source-Version auf die gleiche Architektur wie die Pro-Version aktualisiert, verfügt über dieselbe API und kann nahtlos in das [wiseflow+](https://github.com/TeamWiseFlow/wiseflow-plus) Ökosystem integriert werden!

## Sponsoren

Powered By <a href="https://www.baotianqi.cn" target="_blank"><img src="./docs/logos/tianqibao.png" alt="Tianqibao" height="40"/></a>

[Thordata](https://www.thordata.com/products/serp-api?ls=github&lk=wiseflow): Erhalten Sie zuverlässige globale Proxys zu einem unschlagbaren Preis. Datenerfassung mit einem Klick mit Stabilität und Compliance auf Unternehmensniveau. Schließen Sie sich Tausenden von Entwicklern an, die ThorData für hochskalierte Operationen nutzen.

🎁 Exklusives Angebot: Melden Sie sich für eine kostenlose Testversion von Wohn-Proxies und 2.000 KOSTENLOSE SERP-API-Aufrufe an!

<a href="https://www.thordata.com/products/serp-api?ls=github&lk=wiseflow" target="_blank"><img src="./docs/logos/thordata_en.png" alt="Thordata" height="120"/></a>

## Vergleich zwischen wiseflow Open Source und Pro Versionen

| Funktionsmerkmale | Open Source Version | Pro Version |
| :--- | :---: | :---: |
| **Überwachungsquellen** | web, rss | web, rss, plus 7 große chinesische Self-Media-Plattformen |
| **Suchquellen** | bing, github, arxiv | bing, github, arxiv, plus 6 große chinesische Self-Media-Plattformen |
| **Installation & Bereitstellung** | Manuelle Einrichtung der Umgebung erforderlich | Keine Installation nötig, One-Click-Ausführung |
| **Benutzeroberfläche** | Keine | Chinesische Web-UI |
| **LLM-Kosten** | Nutzer abonniert LLM-Dienst selbst oder lokales LLM | Abonnement enthält LLM-Kosten (keine Konfiguration nötig) |
| **Technischer Support** | GitHub Issues | WeChat-Gruppe für zahlende Nutzer |
| **Preis** | Kostenlos | ￥488/Jahr |
| **Zielgruppe** | Community-Erkundung und Projektlernen | Täglicher Gebrauch (Privat oder Unternehmen) |

## 🧐 wiseflow Produktpositionierung

wiseflow ist kein Allzweck-Agent wie ChatGPT oder Manus; es konzentriert sich auf Informationsüberwachung und -extraktion, unterstützt benutzerdefinierte Quellen und garantiert durch regelmäßige Aufgaben den Erhalt aktuellster Informationen (bis zu 4 Mal täglich, d.h. alle 6 Stunden). Gleichzeitig unterstützt wiseflow die umfassende Informationssuche auf bestimmten Plattformen (z.B. "Personensuche").

Aber setzen Sie wiseflow nicht mit herkömmlichen Crawlern oder RPA gleich! Das Erfassungsverhalten von wiseflow wird vollständig von LLMs gesteuert, verwendet echte Browser (anstatt Headless- oder virtuelle Browser), und die Erfassungs- und Extraktionsvorgänge erfolgen gleichzeitig:

- Innovativer intelligenter HTML-Analysemechanismus: Erkennt automatisch Schlüsselinformationen und weiterführende Links.
- "Crawl-and-Search-in-One"-Strategie: Echtzeit-Beurteilung und -Extraktion durch das LLM während des Crawlens, erfasst nur relevante Informationen und reduziert das Risiko von Sperren erheblich.
- Echte Out-of-the-Box-Lösung: Kein Xpath, keine Skripte oder manuelle Konfiguration erforderlich – auch für normale Nutzer einfach zu bedienen.

    ……

Mehr Informationen unter: https://shouxiqingbaoguan.com/

## 🌟 Schnellstart

**In nur drei Schritten startklar!**

**Ab Version 4.2 muss Google Chrome installiert sein (Standard-Installationspfad verwenden).**

**Windows-Nutzer laden bitte vorab das Git Bash-Tool herunter und führen die folgenden Befehle in der Bash aus [Bash Download Link](https://git-scm.com/downloads/win)**

### 📋 Umweltmanagement-Tool uv installieren und wiseflow Quellcode herunterladen

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
git clone https://github.com/TeamWiseFlow/wiseflow.git
```

Diese Schritte installieren uv und laden den Quellcode von wiseflow herunter.

### 📥 .env Datei basierend auf env_sample konfigurieren

Erstellen Sie im wiseflow-Ordner (Projektstammverzeichnis) eine .env-Datei basierend auf env_sample und geben Sie die entsprechenden Einstellungen ein (hauptsächlich LLM-Dienstkonfiguration).

**Die Open-Source-Version von wiseflow erfordert die eigene Konfiguration des LLM-Dienstes durch den Nutzer.**

wiseflow schränkt Modellanbieter nicht ein, solange sie mit dem OpenAI SDK-Anfrageformat kompatibel sind. Sie können bestehende MaaS-Dienste oder lokal bereitgestellte Modelldienste wie Ollama wählen.

Für Benutzer in Festlandchina empfehlen wir die Nutzung des Siliconflow-Modelldienstes.

😄 Nutzen Sie gerne meinen [Empfehlungslink](https://cloud.siliconflow.cn/i/WNLYbBpi), um sich anzumelden – Sie und ich erhalten beide eine Plattformbelohnung von ￥14.

Wenn Sie lieber ausländische Closed-Source-Modelle wie OpenAI verwenden möchten, können Sie den AiHubMix-Modelldienst nutzen, der in Festlandchina reibungslos funktioniert:

😄 Sie können sich gerne über meinen [AiHubMix-Einladungslink](https://aihubmix.com?aff=Gp54) registrieren.

Übersee-Benutzer können die internationale Version von Siliconflow verwenden: https://www.siliconflow.com/

### 🚀 Abflug!

```bash
cd wiseflow
uv venv # nur beim ersten Mal nötig
source .venv/bin/activate  # Linux/macOS
# oder unter Windows:
# .venv\Scripts\activate
uv sync # nur beim ersten Mal nötig
python core/entry.py
```

## 📚 Wie Sie die von wiseflow gesammelten Daten in Ihren eigenen Programmen verwenden

Siehe [wiseflow backend api](./core/backend/README.md)

Egal ob auf Basis von wiseflow oder wiseflow-pro, wir freuen uns, wenn Sie Ihre Anwendungsbeispiele im folgenden Repo teilen und bewerben!

- https://github.com/TeamWiseFlow/wiseflow-plus

(PR-Beiträge zu diesem Repo erhalten nach Annahme ebenfalls eine einjährige Nutzungslizenz für wiseflow-pro)

**Die Architektur der Version 4.2x ist nicht vollständig mit 4.30 kompatibel. Die letzte Version von 4.2x (v4.29) wird nicht mehr gewartet. Für Code-Referenzen können Sie zum Branch "2025" wechseln.**

## 🛡️ Lizenz

Seit Version 4.2 haben wir die Open-Source-Lizenzvereinbarung aktualisiert, bitte prüfen Sie: [LICENSE](LICENSE) 

Für kommerzielle Kooperationen kontaktieren Sie bitte **E-Mail: zm.zhao@foxmail.com**

## 📬 Kontakt

Bei Fragen oder Anregungen hinterlassen Sie bitte eine Nachricht über [issue](https://github.com/TeamWiseFlow/wiseflow/issues).

Für Anfragen zur Pro-Version oder Feedback zur Zusammenarbeit wenden Sie sich bitte an den "Manager" von AI Chief Intelligence Officer via WeChat:

<img src="docs/wechat.jpg" alt="wechat" width="360">

## 🤝 Dieses Projekt basiert auf den folgenden exzellenten Open-Source-Projekten:

- Crawl4ai (Open-source LLM Friendly Web Crawler & Scraper) https://github.com/unclecode/crawl4ai
- Patchright (Undetected Python version of the Playwright testing and automation library) https://github.com/Kaliiiiiiiiii-Vinyzu/patchright-python
- MediaCrawler (xhs/dy/wb/ks/bilibili/zhihu crawler) https://github.com/NanmiCoder/MediaCrawler
- NoDriver (Bietet ein blitzschnelles Framework für Web-Automatisierung, Web-Scraping, Bots und andere kreative Ideen...) https://github.com/ultrafunkamsterdam/nodriver
- Feedparser (Parsen von Feeds in Python) https://github.com/kurtmckee/feedparser
- SearXNG (Eine freie Internet-Metasuchmaschine, die Ergebnisse aus verschiedenen Suchdiensten und Datenbanken zusammenführt) https://github.com/searxng/searxng

## Zitation

Wenn Sie dieses Projekt in verwandten Arbeiten teilweise oder vollständig referenzieren oder zitieren, geben Sie bitte folgende Informationen an:

```
Autor: Wiseflow Team
https://github.com/TeamWiseFlow/wiseflow
```

## Freundliche Links

[<img src="docs/logos/SiliconFlow.png" alt="siliconflow" width="360">](https://siliconflow.com/)
