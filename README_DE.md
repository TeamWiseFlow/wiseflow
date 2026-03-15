# Wiseflow

**[中文](README.md) | [English](README_EN.md) | [日本語](README_JP.md) | [한국어](README_KR.md) | [Français](README_FR.md) | [العربية](README_AR.md)**

🚀 **STEP INTO 5.x**

> 📌 **Suchen Sie 4.x?** Der ursprüngliche Code von v4.30 und früheren Versionen ist im [`4.x`-Branch](https://github.com/TeamWiseFlow/wiseflow/tree/4.x) verfügbar.

```
„Mein Leben hat Grenzen, doch das Wissen hat keine. Mit dem Begrenzten dem Grenzenlosen zu folgen — das ist gefährlich!" — Zhuangzi, Innere Kapitel, Die Pflege des Lebensprinzips
```

Wiseflow 4.x (einschließlich früherer Versionen) erreichte durch eine Reihe präziser Workflows leistungsstarke Datenerfassungsfähigkeiten in bestimmten Szenarien, hatte jedoch weiterhin erhebliche Einschränkungen:

- 1. Interaktive Inhalte konnten nicht erfasst werden (Inhalte, die erst nach einem Klick erscheinen, insbesondere bei dynamischem Laden)
- 2. Beschränkung auf Informationsfilterung und -extraktion, praktisch keine Fähigkeit zur Verarbeitung nachgelagerter Aufgaben
- ……

Obwohl wir stets daran gearbeitet haben, die Funktionalität zu verbessern und die Grenzen zu erweitern, ist die reale Welt komplex — und das Internet ebenso. Regeln können niemals vollständig sein, daher kann ein fester Workflow niemals alle Szenarien abdecken. Dies ist kein Problem von wiseflow — es ist ein Problem traditioneller Software!

Die rasante Entwicklung von Agenten im vergangenen Jahr hat uns jedoch die technische Möglichkeit gezeigt, menschliches Internetverhalten durch große Sprachmodelle vollständig zu simulieren. Das Erscheinen von [openclaw](https://github.com/openclaw/openclaw) hat diese Überzeugung weiter gestärkt.

Noch bemerkenswerter ist, dass wir durch frühe Experimente und Erforschung entdeckt haben, dass die Integration der Erfassungsfähigkeiten von wiseflow als „Plugins" in openclaw die beiden oben genannten Einschränkungen perfekt löst.

https://github.com/user-attachments/assets/8d097b3b-f9ab-42eb-98bb-88af5d28b089

Es ist jedoch zu beachten, dass das Plugin-System von openclaw sich erheblich von dem unterscheidet, was wir traditionell unter „Plugins" verstehen (ähnlich den Plugins von Claude Code). Daher mussten wir das Konzept des „Add-ons" einführen. Genau genommen wird wiseflow 5.x als openclaw Add-on erscheinen. Das originale openclaw verfügt nicht über eine „Add-on"-Architektur, aber in der Praxis benötigen Sie nur wenige einfache Shell-Befehle, um diese „Umgestaltung" durchzuführen. Wir haben auch eine sofort einsatzbereite, erweiterte Version von openclaw mit voreingestellten Konfigurationen für reale Geschäftsszenarien vorbereitet: [openclaw_for_business](https://github.com/TeamWiseFlow/openclaw_for_business). Sie können es einfach klonen und das wiseflow-Release in den Add-on-Ordner von openclaw_for_business entpacken.

## ✨ Was erhalten Sie durch die Installation von wiseflow (überlegen dem originalen openclaw)?

### 1. Anti-Erkennungs-Browser, keine Browser-Erweiterungen erforderlich

wiseflow's patch-001 ersetzt das in openclaw integrierte Playwright durch [Patchright](https://github.com/Kaliiiiiiiiii-Vinyzu/patchright) (ein unerkannter Fork von Playwright) und reduziert damit erheblich die Wahrscheinlichkeit, dass automatisierte Browser von Ziel-Websites erkannt und blockiert werden. Dadurch lassen sich ohne die Installation einer Chrome-Relay-Extension mit einem verwalteten Browser gleichwertige oder sogar überlegene Web-Erfassungs- und Bedienungsfähigkeiten gegenüber einer Relay-Konfiguration erzielen.

📥 *Wir haben alle derzeit populären Browser-Automatisierungs-Frameworks bewertet, darunter nodriver, browser-use und Vercels agent-browser. Wir können bestätigen, dass zwar alle über CDP arbeiten und beständige openclaw-spezifische Profile bereitstellen, aber nur Patchright eine vollständige Entfernung von CDP-Fingerprints bietet. Mit anderen Worten: Selbst der direkteste CDP-Verbindungsansatz hinterlässt nachweisbare Merkmale. Andere Frameworks sind für automatisierte Tests konzipiert, nicht für Datenerfassung, während Patchright speziell für die Erfassung entwickelt wurde. Da es sich im Wesentlichen um einen Patch auf Playwright handelt, erbt es fast alle High-Level-APIs von Playwright — und ist dadurch nativ mit openclaw kompatibel, ohne dass zusätzliche Erweiterungen oder MCP installiert werden müssen.*

### 2. Automatischer Tab-Wiederherstellungsmechanismus

Wenn ein Ziel-Browser-Tab während eines Agent-Vorgangs unerwartet geschlossen oder verloren geht, führt das System automatisch eine snapshot-basierte Tab-Wiederherstellung durch, damit Aufgaben nicht durch Tab-Verlust unterbrochen werden.

### 3. Smart Search Skill

Ersetzt die eingebaute `web_search` von openclaw durch leistungsfähigere Suchfunktionen. Im Vergleich zum ursprünglich integrierten web search tool bietet Smart Search drei zentrale Vorteile:

- **Völlig kostenlos, kein API-Schlüssel erforderlich**: Keine Abhängigkeit von Drittanbieter-Such-APIs — null Kosten
- **Echtzeit-Suche für maximale Aktualität**: Steuert den Browser direkt zu Zielseiten oder großen Social-Media-Plattformen (Weibo, Twitter/X, Facebook usw.), um die zuletzt veröffentlichten Inhalte sofort abzurufen
- **Benutzerdefinierbare Suchquellen**: Benutzer können ihre Suchquellen frei festlegen, um präzise und zielgerichtete Informationsabfragen zu ermöglichen

### 4. New-Media-Editor Crew (vorkonfigurierter KI-Agent)

Ein sofort einsatzbereiter KI-Agent zur Erstellung chinesischer Social-Media-Inhalte, spezialisiert auf die wichtigsten chinesischen Plattformen wie Weibo, Xiaohongshu, Zhihu, Bilibili und Douyin.

**Hauptfähigkeiten:**

- Themenrecherche + Trendanalyse (Modus A)
- Entwurfserweiterung + Online-Belegung (Modus B)
- Nach der Fertigstellung automatischer Aufruf von [Wenyan](https://github.com/caol64/wenyan) zur Darstellung als WeChat-Public-Account-HTML mit 7 integrierten Themen
- Direktes Pushen in den WeChat-Public-Account-Entwurfsbereich (Modus C, erfordert `WECHAT_APP_ID`/`WECHAT_APP_SECRET`)
- KI-Bild-/Videogenerierung ([SiliconFlow](https://www.siliconflow.com/) Bild/Video-Generierung, erfordert `SILICONFLOW_API_KEY`)

## 🌟 Schnellstart

> **💡 Hinweis zu API-Kosten**
>
> wiseflow 5.x basiert auf dem Agent-Workflow von openclaw und benötigt LLM-API-Zugang. Wir empfehlen, Ihre API-Zugangsdaten vorab vorzubereiten:
>
> - **Internationale Benutzer (empfohlen)**: [SiliconFlow](https://www.siliconflow.com/) — nach der Registrierung werden kostenlose Credits gutgeschrieben, die die Anfangskosten abdecken
> - **OpenAI / Anthropic und andere Anbieter**: Jede kompatible API ist verwendbar

Laden Sie das integrierte Paket (enthält openclaw_for_business und das wiseflow Addon) direkt aus den [Releases](https://github.com/TeamWiseFlow/wiseflow/releases) dieses Repositories herunter.

1. Das Archiv herunterladen und entpacken
2. In den entpackten Ordner wechseln
3. Startmodus auswählen:

   **Debug-Modus** (Einzelstart, für Tests und Entwicklung):
   ```bash
   ./scripts/dev.sh gateway
   ```

   **Produktionsmodus** (als Systemdienst installieren, für den Dauerbetrieb):
   ```bash
   ./scripts/reinstall-daemon.sh
   ```

> **Systemanforderungen**
> - **Ubuntu 22.04** wird empfohlen
> - **Windows WSL2**-Umgebung wird unterstützt
> - **macOS** wird unterstützt
> - Die direkte Ausführung unter **nativem Windows** wird **nicht unterstützt**

### [Alternative] Manuelle Installation

> Hinweis: Sie müssen zuerst openclaw_for_business herunterladen und deployen. Download-Adresse: https://github.com/TeamWiseFlow/openclaw_for_business/releases

Kopieren Sie den `wiseflow`-Ordner aus diesem Repository (nicht das Repository selbst) in das `addons/`-Verzeichnis von openclaw_for_business:

```bash
# Option 1: Aus dem wiseflow-Repository klonen
git clone https://github.com/TeamWiseFlow/wiseflow.git /tmp/wiseflow
cp -r /tmp/wiseflow/wiseflow <openclaw_for_business>/addons/wiseflow
```

Nach der Installation openclaw_for_business neu starten, um die Änderungen zu aktivieren.

## Verzeichnisstruktur

```
wiseflow/                         # addon-Paket (in addons/-Verzeichnis kopieren)
├── addon.json                    # Metadaten
├── overrides.sh                  # pnpm overrides + integrierte web_search deaktivieren
├── patches/
│   ├── 001-browser-tab-recovery.patch        # Tab-Wiederherstellungs-Patch
│   ├── 002-disable-web-search-env-var.patch  # Integrierte web_search deaktivieren (env var)
│   └── 003-act-field-validation.patch        # ACT-Feldvalidierungs-Patch
├── skills/                       # Globale Skills (für alle Agents verfügbar)
│   ├── browser-guide/SKILL.md    # Best Practices für den Browser (Login/CAPTCHA/Lazy-Loading etc.)
│   ├── smart-search/SKILL.md     # Multiplattform-Such-URL-Builder (ersetzt integrierte web_search)
│   └── rss-reader/               # RSS/Atom Feed-Reader
│       ├── SKILL.md
│       ├── package.json
│       └── scripts/fetch-rss.mjs
└── crew/                         # Vorkonfigurierte KI-Agents (Crew-Vorlagen)
    └── new-media-editor/         # New-Media-Editor (Chinesische Social-Media-Inhaltserstellung)
        ├── IDENTITY.md / SOUL.md / AGENTS.md / TOOLS.md / ...
        └── skills/               # Crew-spezifische Skills
            ├── siliconflow-img-gen/   # KI-Bildgenerierung (SiliconFlow API)
            ├── siliconflow-video-gen/ # KI-Videogenerierung (SiliconFlow API)
            └── wenyan-formatter/      # Markdown → WeChat HTML / Entwurf pushen

docs/                             # Technische Dokumentation (Repository-Root)
├── anti-detection-research.md
└── more_powerful_search_skill/

scripts/                          # Hilfsskripte (Repository-Root)
└── generate-patch.sh

tests/                            # Testfälle und Skripte (Repository-Root)
├── README.md
└── run-managed-tests.mjs
```

## WiseFlow Pro ist jetzt verfügbar!

Stärkere Scraping-Fähigkeiten, umfassendere Social-Media-Unterstützung, mit UI-Oberfläche und Ein-Klick-Installationspaket — keine Bereitstellung erforderlich!

https://github.com/user-attachments/assets/57f8569c-e20a-4564-a669-1200d56c5725

🔥 **Pro-Version ist jetzt im Verkauf**: https://shouxiqingbaoguan.com/

🌹 Ab sofort: Beiträge (PRs) zur Open-Source-Version von wiseflow (Code, Dokumentation und erfolgreiche Fallstudien sind willkommen) — bei Annahme erhalten Mitwirkende eine einjährige Lizenz für wiseflow Pro!

## 🛡️ Lizenz

Seit Version 4.2 haben wir unsere Open-Source-Lizenz aktualisiert. Bitte beachten Sie: [LICENSE](LICENSE)

Für kommerzielle Zusammenarbeit kontaktieren Sie bitte **Email: zm.zhao@foxmail.com**

## 📬 Kontakt

Bei Fragen oder Vorschlägen hinterlassen Sie gerne eine Nachricht über [Issues](https://github.com/TeamWiseFlow/wiseflow/issues).

🎉 wiseflow & OFB bieten jetzt eine **kostenpflichtige Wissensdatenbank** an, einschließlich Schritt-für-Schritt-Installationstutorials, exklusiver Anwendungstipps und einer **VIP-WeChat-Gruppe**:

Fügen Sie „Keeper" auf WeChat Enterprise für Anfragen hinzu:

<img width="360" height="360" alt="wiseflow掌柜" src="https://github.com/user-attachments/assets/b013b3fd-546e-4176-b418-57bee419e761" />

🌹 Open Source erfordert viel Aufwand — vielen Dank für Ihre Unterstützung!

## 🤝 wiseflow 5.x basiert auf folgenden hervorragenden Open-Source-Projekten:

- Patchright (Unerkannte Python-Version der Playwright Test- und Automatisierungsbibliothek) https://github.com/Kaliiiiiiiiii-Vinyzu/patchright-python
- Feedparser (Feeds in Python parsen) https://github.com/kurtmckee/feedparser
- SearXNG (eine freie Internet-Metasuchmaschine, die Ergebnisse verschiedener Suchdienste und Datenbanken aggregiert) https://github.com/searxng/searxng
- Wenyan (plattformübergreifendes Markdown-Formatierungs- und Veröffentlichungstool, vom New-Media-Editor-Crew über das wenyan-formatter-Skill verwendet) https://github.com/caol64/wenyan

## Citation

Wenn Sie Teile oder das gesamte Projekt in Ihrer Arbeit referenzieren oder zitieren, geben Sie bitte folgende Informationen an:

```
Author: Wiseflow Team
https://github.com/TeamWiseFlow/wiseflow
```

## Partner

[<img src="https://github.com/TeamWiseFlow/wiseflow/raw/4.x/docs/logos/SiliconFlow.png" alt="siliconflow" width="360">](https://siliconflow.com/)
