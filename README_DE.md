# WiseFlow

**[中文](README_CN.md) | [日本語](README_JP.md) | [Français](README_FR.md) | [English](README.md)**

**Wiseflow** ist ein agiles Informationsgewinnungstool, das Informationen aus verschiedenen Quellen wie Websites, WeChat-Accounts und sozialen Medien basierend auf vordefinierten Fokusbereichen extrahieren, automatisch kategorisieren und in die Datenbank hochladen kann.

🔥 **SiliconFlow hat offiziell bekannt gegeben, dass mehrere LLM-Online-Inferenzdienste, wie Qwen2-7B-Instruct und glm-4-9b-chat, ab sofort kostenlos sind. Das bedeutet, dass Sie Informationsgewinnung mit dem wiseflow zu „null Kosten“ durchführen können！** 🔥

Es mangelt uns nicht an Informationen, sondern wir müssen den Lärm herausfiltern, um wertvolle Informationen hervorzuheben! 

Sehen Siewie WiseFlow Ihnen hilft, Zeit zu sparen, irrelevante Informationen zu filtern und interessante Punkte zu organisieren!

https://github.com/TeamWiseFlow/wiseflow/assets/96130569/bd4b2091-c02d-4457-9ec6-c072d8ddfb16

<img alt="sample.png" src="asset/sample.png" width="1024"/>

## Wichtige Updates in V0.3.0

- ✅ Neuer universeller Web-Content-Parser, der auf GNE (ein Open-Source-Projekt) und LLM basiert und mehr als 90% der Nachrichtenseiten unterstützt.

- ✅ Neue asynchrone Aufgabenarchitektur.

- ✅ Neue Strategie zur Informationsextraktion und Tag-Klassifizierung, die präziser und feiner ist und Aufgaben mit nur einem 9B LLM perfekt ausführt.

## 🌟 Hauptfunktionen

- 🚀 **Native LLM-Anwendung**  
  Wir haben die am besten geeigneten Open-Source-Modelle von 7B~9B sorgfältig ausgewählt, um die Nutzungskosten zu minimieren und es datensensiblen Benutzern zu ermöglichen, jederzeit vollständig auf eine lokale Bereitstellung umzuschalten.


- 🌱 **Leichtes Design**  
  Ohne Vektormodelle ist das System minimal invasiv und benötigt keine GPUs, was es für jede Hardwareumgebung geeignet macht.


- 🗃️ **Intelligente Informationsextraktion und -klassifizierung**  
  Extrahiert automatisch Informationen aus verschiedenen Quellen und markiert und klassifiziert sie basierend auf den Interessen der Benutzer.

  😄 **Wiseflow ist besonders gut darin, Informationen aus WeChat-Official-Account-Artikeln zu extrahieren**; hierfür haben wir einen dedizierten Parser für mp-Artikel eingerichtet!


- 🌍 **Kann in jedes Agent-Projekt integriert werden**  
  Kann als dynamische Wissensdatenbank für jedes Agent-Projekt dienen, ohne dass der Code von Wiseflow verstanden werden muss. Es reicht, die Datenbank zu lesen!


- 📦 **Beliebte PocketBase-Datenbank**  
  Die Datenbank und das Interface nutzen PocketBase. Zusätzlich zur Webschnittstelle sind SDK für Go/JavaScript/Python verfügbar.
    
    - Go: https://pocketbase.io/docs/go-overview/
    - JavaScript: https://pocketbase.io/docs/js-overview/
    - Python: https://github.com/vaphes/pocketbase

## 🔄 Unterschiede und Zusammenhänge zwischen Wiseflow und allgemeinen Crawler-Tools und LLM-Agent Projekten

| Merkmal                | WiseFlow                                           | Crawler / Scraper                        | LLM-Agent                                                 |
|------------------------|----------------------------------------------------|------------------------------------------|-----------------------------------------------------------|
| **Hauptproblem gelöst** | Datenverarbeitung (Filterung, Extraktion, Tagging) | Rohdaten-Erfassung                       | Downstream-Anwendungen                                    |
| **Zusammenhang**       |                                                    | Kann in Wiseflow integriert werden, um leistungsfähigere Rohdaten-Erfassung zu ermöglichen | Kann Wiseflow als dynamische Wissensdatenbank integrieren |

## 📥 Installation und Verwendung

WiseFlow hat fast keine Hardwareanforderungen, minimale Systemlast und benötigt keine GPU oder CUDA (bei Verwendung von Online-LLM-Diensten).

1. **Repository klonen**

     😄 Star und Forken sind gute Gewohnheiten

    ```bash
    git clone https://github.com/TeamWiseFlow/wiseflow.git
    cd wiseflow
    ```

2. **Dringend empfohlen: Docker verwenden**

    ```bash
    docker compose up
    ```
   `compose.yaml` kann nach Bedarf angepasst werden.

    **Hinweis:**
    - Führen Sie den obigen Befehl im Stammverzeichnis des wiseflow-Repositories aus.
    - Erstellen und bearbeiten Sie vor dem Ausführen eine `.env`-Datei im gleichen Verzeichnis wie die Dockerfile (Stammverzeichnis des wiseflow-Repositories). Orientieren Sie sich an `env_sample` für die `.env`-Datei.
    - Beim ersten Start des Docker-Containers kann ein Fehler auftreten, da Sie noch kein Admin-Konto für das pb-Repository erstellt haben.

    Halten Sie in diesem Fall den Container am Laufen, öffnen Sie `http://127.0.0.1:8090/_/` in Ihrem Browser und folgen Sie den Anweisungen, um ein Admin-Konto zu erstellen (stellen Sie sicher, dass Sie eine E-Mail verwenden). Geben Sie dann die erstellte Admin-E-Mail (nochmals, stellen Sie sicher, dass es sich um eine E-Mail handelt) und das Passwort in die `.env`-Datei ein und starten Sie den Container neu.

    _Falls Sie die Zeitzone und Sprache des Containers ändern möchten [was die Sprache der Prompts bestimmt, aber wenig Einfluss auf die Ergebnisse hat], führen Sie das Image mit folgendem Befehl aus_

    ```bash
    docker run -e LANG=de_DE.UTF-8 -e LC_CTYPE=de_DE.UTF-8 your_image
    ```

3. **[Alternative] Direkt mit Python ausführen**

    ```bash
    conda create -n wiseflow python=3.10
    conda activate wiseflow
    cd core
    pip install -r requirement.txt
    ```

    Sie können dann pb, task und backend einzeln mit den Skripten im core/scripts-Verzeichnis starten (verschieben Sie die Skriptdateien in das core-Verzeichnis).

    Hinweis:
    - Starten Sie zuerst pb; task und backend sind unabhängige Prozesse und die Reihenfolge spielt keine Rolle. Sie können auch nur einen der beiden nach Bedarf starten.
    - Laden Sie den passenden pocketbase-Client für Ihr Gerät von https://pocketbase.io/docs/ herunter und platzieren Sie ihn im Verzeichnis /core/pb.
    - Bei Problemen mit pb (einschließlich Fehlern beim ersten Start) siehe [core/pb/README.md](/core/pb/README.md).
    - Erstellen und bearbeiten Sie vor der Nutzung eine `.env`-Datei und platzieren Sie diese im Stammverzeichnis des wiseflow-Repositories (oberes Verzeichnis von core). Orientieren Sie sich an `env_sample` für die `.env`-Datei, und sehen Sie unten für detaillierte Konfigurationen.


    📚 Für Entwickler, siehe [/core/README.md](/core/README.md) für mehr Informationen.

        Zugriff auf Daten über pocketbase:
        - http://127.0.0.1:8090/_/ - Admin-Dashboard-Oberfläche
        - http://127.0.0.1:8090/api/ - REST API


4. **Konfiguration**

    Kopieren Sie `env_sample` aus dem Verzeichnis und benennen Sie es in `.env` um, füllen Sie dann Ihre Konfigurationsinformationen (wie LLM-Dienst-Token) wie folgt aus:

   - LLM_API_KEY # API-Schlüssel für Großes Sprachmodell-Inferenzdienst
   - LLM_API_BASE # Dieses Projekt verwendet das OpenAI SDK. Konfigurieren Sie diese Option, wenn Ihr Modellsystem die OpenAI-API unterstützt. Falls Sie den OpenAI-Dienst nutzen, können Sie diese Option weglassen.
   - WS_LOG="verbose"  # Setzen, um Debug-Beobachtung zu aktivieren. Löschen, falls nicht erforderlich.
   - GET_INFO_MODEL # Modell für Informationsentnahme und Tag-Matching-Aufgaben, standardmäßig gpt-3.5-turbo
   - REWRITE_MODEL # Modell für annähernde Informationsfusion und Umschreibaufgaben, standardmäßig gpt-3.5-turbo
   - HTML_PARSE_MODEL # Modell für Webseiten-Parsing (intelligent aktiviert, wenn der GNE-Algorithmus schlecht funktioniert), standardmäßig gpt-3.5-turbo
   - PROJECT_DIR # Speicherort für Daten, Cache und Protokolldateien, relativ zum Repository. Standardmäßig im Repository.
   - PB_API_AUTH='email|password' # E-Mail und Passwort für den pb-Datenbank-Admin (muss eine E-Mail sein, kann eine fiktive E-Mail sein)
   - PB_API_BASE  # Normalerweise nicht erforderlich. Nur konfigurieren, wenn Sie nicht die Standard-poketbase-Local-Schnittstelle (8090) verwenden.


5. **Modell-Empfehlungen**

    Basierend auf umfangreichen Tests (für chinesische und englische Aufgaben), empfehlen wir **"zhipuai/glm4-9B-chat"** für **GET_INFO_MODEL**, **"alibaba/Qwen2-7B-Instruct"** für **REWRITE_MODEL**, und **"alibaba/Qwen2-7B-Instruct"** für **HTML_PARSE_MODEL**.

    Diese Modelle sind gut für dieses Projekt geeignet, mit stabiler Einhaltung der Anweisungen und ausgezeichneter Generationsqualität. Die Prompts dieses Projekts wurden für diese drei Modelle optimiert. (**HTML_PARSE_MODEL** kann auch **"01-ai/Yi-1.5-9B-Chat"** verwenden, was ebenfalls hervorragende Ergebnisse zeigt.)


    ⚠️ Wir empfehlen dringend die Nutzung des **SiliconFlow**-Online-Inferenzdienstes für geringere Kosten, schnellere Geschwindigkeit und höhere Freikontingente! ⚠️

    Der Online-Inferenzdienst von SiliconFlow ist kompatibel mit dem OpenAI SDK und bietet Open-Source-Dienste für die oben genannten drei Modelle. Konfigurieren Sie einfach `LLM_API_BASE` auf "https://api.siliconflow.cn/v1" und setzen Sie `LLM_API_KEY`, um ihn zu nutzen.

    😄 Alternativ können Sie meinen [Einladungslink](https://cloud.siliconflow.cn?referrer=clx6wrtca00045766ahvexw92) verwenden, wodurch ich auch mehr Token-Belohnungen erhalte 😄


6. **Fokuspunkte und Hinzufügen von geplanten Quellenscans**

    Nach dem Start des Programms öffnen Sie die pocketbase Admin-Dashboard-Oberfläche (http://127.0.0.1:8090/_/)

        6.1 Öffnen Sie das **tags-Formular**

        Verwenden Sie dieses Formular, um Ihre Fokuspunkte anzugeben. Das LLM wird Informationen basierend auf diesen extrahieren, filtern und klassifizieren.

        Beschreibung des tags-Felds:

        - name, Beschreibung des Fokuspunkts. **Hinweis: Seien Sie spezifisch.** Gutes Beispiel: `Trends im Wettbewerb zwischen den USA und China`. Schlechtes Beispiel: `Internationale Lage`.
        - activated, Ob aktiviert. Wenn deaktiviert, wird der Fokuspunkt ignoriert. Er kann später wieder aktiviert werden. Aktivierung und Deaktivierung erfordern keinen Neustart des Docker-Containers und werden bei der nächsten geplanten Aufgabe aktualisiert.

        6.2 Öffnen Sie das **sites-Formular**

        Verwenden Sie dieses Formular, um benutzerdefinierte Quellen anzugeben. Das System startet Hintergrundaufgaben, um diese Quellen lokal zu scannen, zu analysieren und auszuwerten.

        Beschreibung des sites-Felds:

        - url, URL der Quelle. Geben Sie eine URL zur Listen-Seite anstelle einer spezifischen Artikel-Seite an.
        - per_hours, Scanhäufigkeit in Stunden, als Ganzzahl (Bereich 1-24; wir empfehlen nicht mehr als einmal täglich, d.h. auf 24 eingestellt).
        - activated, Ob aktiviert. Wenn deaktiviert, wird die Quelle ignoriert. Sie kann später wieder aktiviert werden. Aktivierung und Deaktivierung erfordern keinen Neustart des Docker-Containers und werden bei der nächsten geplanten Aufgabe aktualisiert.


7. **Lokale Bereitstellung**

    Wie Sie sehen können, verwendet dieses Projekt 7B/9B LLMs und benötigt keine Vektormodelle, was bedeutet, dass Sie nur eine RTX 3090 (24 GB VRAM) benötigen, um dieses Projekt vollständig lokal bereitzustellen.

    Stellen Sie sicher, dass Ihr lokaler LLM-Dienst mit dem OpenAI SDK kompatibel ist und konfigurieren Sie `LLM_API_BASE` entsprechend.


## 🛡️ Lizenz

Dieses Projekt ist unter der [Apache 2.0](LICENSE) Lizenz als Open-Source verfügbar.

Für kommerzielle Nutzung und maßgeschneiderte Kooperationen kontaktieren Sie uns bitte unter **E-Mail: 35252986@qq.com**.

- Kommerzielle Kunden, bitte registrieren Sie sich bei uns. Das Produkt verspricht für immer kostenlos zu sein.
- Für maßgeschneiderte Kunden bieten wir folgende Dienstleistungen basierend auf Ihren Quellen und geschäftlichen Anforderungen:
  - Dedizierter Crawler und Parser für Kunden-Geschäftsszenario-Quellen
  - Angepasste Strategien zur Informationsextraktion und -klassifizierung
  - Zielgerichtete LLM-Empfehlungen oder sogar Feinabstimmungsdienste
  - Dienstleistungen für private Bereitstellungen
  - Anpassung der Benutzeroberfläche

## 📬 Kontaktinformationen

Wenn Sie Fragen oder Anregungen haben, können Sie uns gerne über [Issue](https://github.com/TeamWiseFlow/wiseflow/issues) kontaktieren.

## 🤝 Dieses Projekt basiert auf den folgenden ausgezeichneten Open-Source-Projekten:

- GeneralNewsExtractor (General Extractor of News Web Page Body Based on Statistical Learning) https://github.com/GeneralNewsExtractor/GeneralNewsExtractor
- json_repair (Reparatur ungültiger JSON-Dokumente) https://github.com/josdejong/jsonrepair/tree/main 
- python-pocketbase (PocketBase Client SDK für Python) https://github.com/vaphes/pocketbase

# Zitierung

Wenn Sie Teile oder das gesamte Projekt in Ihrer Arbeit verwenden oder zitieren, geben Sie bitte die folgenden Informationen an:

```
Author: Wiseflow Team
https://openi.pcl.ac.cn/wiseflow/wiseflow
https://github.com/TeamWiseFlow/wiseflow
Licensed under Apache2.0
```
