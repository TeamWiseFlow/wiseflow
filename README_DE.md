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

Noch bemerkenswerter ist, dass wir durch frühe Experimente und Erforschung entdeckt haben, dass die Integration der Erfassungsfähigkeiten von wiseflow als „Plugins" in openclaw die beiden oben genannten Einschränkungen perfekt löst. Wir werden in Kürze aufregende echte Demo-Videos veröffentlichen und diese „Plugins" als Open Source bereitstellen.

Es ist jedoch zu beachten, dass das Plugin-System von openclaw sich erheblich von dem unterscheidet, was wir traditionell unter „Plugins" verstehen (ähnlich den Plugins von Claude Code). Daher mussten wir das Konzept des „Add-ons" einführen. Genau genommen wird wiseflow 5.x als openclaw Add-on erscheinen. Das originale openclaw verfügt nicht über eine „Add-on"-Architektur, aber in der Praxis benötigen Sie nur wenige einfache Shell-Befehle, um diese „Umgestaltung" durchzuführen. Wir haben auch eine sofort einsatzbereite, erweiterte Version von openclaw mit voreingestellten Konfigurationen für reale Geschäftsszenarien vorbereitet: [openclaw_for_business](https://github.com/TeamWiseFlow/openclaw_for_business). Sie können es einfach klonen und das wiseflow-Release in den Add-on-Ordner von openclaw_for_business entpacken.

## ✨ Hauptfunktionen

Das wiseflow Add-on bietet derzeit drei zentrale Verbesserungen für openclaw:

### 1. Anti-Erkennungs-Browser

Ersetzt das in openclaw integrierte Playwright durch [Patchright](https://github.com/Kaliiiiiiiiii-Vinyzu/patchright) (ein unerkannter Fork von Playwright) und reduziert damit erheblich die Wahrscheinlichkeit, dass automatisierte Browser von Ziel-Websites erkannt und blockiert werden.

### 2. Automatische Tab-Wiederherstellung

Wenn ein Ziel-Browser-Tab während eines Agent-Vorgangs unerwartet geschlossen oder verloren geht, führt das System automatisch eine snapshot-basierte Tab-Wiederherstellung durch, damit Aufgaben nicht durch Tab-Verlust unterbrochen werden.

### 3. Smart Search

Ersetzt die eingebaute `web_search` von openclaw durch leistungsfähigere Suchfunktionen. Im Vergleich zu ähnlichen Lösungen auf dem Markt bietet Smart Search drei zentrale Vorteile:

- **Völlig kostenlos, kein API-Schlüssel erforderlich**: Keine Abhängigkeit von Drittanbieter-Such-APIs — null Kosten
- **Echtzeit-Suche für maximale Aktualität**: Steuert den Browser direkt zu Zielseiten oder großen Social-Media-Plattformen (Weibo, Twitter/X, Reddit usw.), um die zuletzt veröffentlichten Inhalte sofort abzurufen
- **Benutzerdefinierbare Suchquellen**: Benutzer können ihre Suchquellen frei festlegen, um präzise und zielgerichtete Informationsabfragen zu ermöglichen

## 🌟 Schnellstart

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
wiseflow/
├── addon.json                    # Metadaten
├── overrides.sh                  # pnpm overrides + integrierte web_search deaktivieren
├── patches/
│   ├── 001-browser-tab-recovery.patch        # Tab-Wiederherstellungs-Patch
│   └── 002-disable-web-search-env-var.patch  # Integrierte web_search deaktivieren (env var)
├── skills/
│   ├── browser-guide/SKILL.md    # Best Practices für den Browser (Login/CAPTCHA/Lazy-Loading etc.)
│   ├── smart-search/SKILL.md     # Multiplattform-Such-URL-Builder (ersetzt integrierte web_search)
│   └── rss-reader/               # RSS/Atom Feed-Reader
│       ├── SKILL.md
│       ├── package.json
│       └── scripts/fetch-rss.mjs
├── docs/                         # Technische Dokumentation
│   ├── anti-detection-research.md
│   └── more_powerful_search_skill/
└── tests/                        # Testfälle und Skripte
    ├── README.md
    └── run-managed-tests.mjs
```

## WiseFlow Pro ist jetzt verfügbar!

Stärkere Scraping-Fähigkeiten, umfassendere Social-Media-Unterstützung, mit UI-Oberfläche und Ein-Klick-Installationspaket — keine Bereitstellung erforderlich!

https://github.com/user-attachments/assets/57f8569c-e20a-4564-a669-1200d56c5725

🔥 **Pro-Version ist jetzt im Verkauf**: https://shouxiqingbaoguan.com/

🌹 Ab sofort: Beiträge (PRs) zur Open-Source-Version von wiseflow (Code, Dokumentation und erfolgreiche Fallstudien sind willkommen) — bei Annahme erhalten Mitwirkende eine einjährige Lizenz für wiseflow Pro!

📥 🎉 📚

## 🛡️ Lizenz

Seit Version 4.2 haben wir unsere Open-Source-Lizenz aktualisiert. Bitte beachten Sie: [LICENSE](LICENSE)

Für kommerzielle Zusammenarbeit kontaktieren Sie bitte **Email: zm.zhao@foxmail.com**

## 📬 Kontakt

Bei Fragen oder Vorschlägen hinterlassen Sie gerne eine Nachricht über [Issues](https://github.com/TeamWiseFlow/wiseflow/issues).

Für Anforderungen oder Feedback zur Pro-Version kontaktieren Sie uns bitte über WeChat:

<img src="docs/wechat.jpg" alt="wechat" width="360">

## 🤝 wiseflow 5.x basiert auf folgenden hervorragenden Open-Source-Projekten:

- Patchright (Unerkannte Python-Version der Playwright Test- und Automatisierungsbibliothek) https://github.com/Kaliiiiiiiiii-Vinyzu/patchright-python
- Feedparser (Feeds in Python parsen) https://github.com/kurtmckee/feedparser
- SearXNG (eine freie Internet-Metasuchmaschine, die Ergebnisse verschiedener Suchdienste und Datenbanken aggregiert) https://github.com/searxng/searxng

## Citation

Wenn Sie Teile oder das gesamte Projekt in Ihrer Arbeit referenzieren oder zitieren, geben Sie bitte folgende Informationen an:

```
Author: Wiseflow Team
https://github.com/TeamWiseFlow/wiseflow
```

## Partner

[<img src="docs/logos/SiliconFlow.png" alt="siliconflow" width="360">](https://siliconflow.com/)
